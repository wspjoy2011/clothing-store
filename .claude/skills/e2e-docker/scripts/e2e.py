"""Drive the compose stack for end-to-end checks and undo everything afterwards.

Every change is written to a ledger before it is applied, so `cleanup` can undo
a run even when it was interrupted.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ledger import Ledger, latest_run_id, new_run_id, run_directory

PROJECT_MARKER = "docker-compose.yml"
TEST_EMAIL_PREFIX = "e2e-"
PARALLEL_REGISTRATION_BUDGET_SECONDS = 5.0
SCENARIO_RATE_LIMIT = "200/minute"
EMAIL_DISPATCH_RATE_LIMIT = "3/second"
EMAIL_DISPATCH_BURST = 8
DEFAULT_API = "http://localhost:8000/api/v1"
ANCHOR_PROCESS = "wsl.exe"
STACK_SERVICES = ("db", "mailhog", "web")
REQUEST_TIMEOUT = 120
STOCK_PROBE_PRODUCT_ID = 999_000_001
STOCK_PROBE_UNITS = 3
PAGINATION_PROBE_PRODUCT_ID = 999_000_100
PAGINATION_PROBE_PRODUCTS = 2
API_ORIGIN = "http://localhost:8000"


def find_project_root() -> str:
    """
    Locate the repository root by walking up from this script

    Returns:
        Absolute path to the directory holding the compose file

    Raises:
        RuntimeError: If the compose file is not found
    """
    current = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.isfile(os.path.join(current, PROJECT_MARKER)):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            raise RuntimeError(f"{PROJECT_MARKER} not found above {__file__}")
        current = parent


def detect_docker(distro: Optional[str]) -> List[str]:
    """
    Build the command prefix that reaches a working docker client

    Args:
        distro: WSL distribution to fall back to when docker is not on PATH

    Returns:
        Command prefix, for example ["docker"] or ["wsl", "-d", "Ubuntu", "-u", "root", "-e", "docker"]

    Raises:
        RuntimeError: If no docker client can be reached
    """
    if shutil.which("docker"):
        return ["docker"]

    if shutil.which("wsl"):
        distributions = [distro] if distro else ["Ubuntu-22.04", "Ubuntu"]
        for candidate in distributions:
            probe = subprocess.run(
                ["wsl", "-d", candidate, "-u", "root", "-e", "docker", "version", "--format", "{{.Server.Version}}"],
                capture_output=True,
                text=True
            )
            if probe.returncode == 0:
                return ["wsl", "-d", candidate, "-u", "root", "-e", "docker"]

    raise RuntimeError("No docker client available on PATH or inside WSL")


def open_wsl_anchor(docker: List[str], ledger: Ledger) -> None:
    """
    Hold a WSL session open for as long as the stack runs

    WSL stops the containers of a distribution once its last session closes, so a
    stack started by one short command dies seconds later, with the containers
    reporting exit code 255 and nothing in their logs. Keeping one idle session
    alive prevents that (microsoft/WSL issue 9667).

    Args:
        docker: Docker command prefix
        ledger: Journal recording the session
    """
    if docker[0] != "wsl":
        return

    process = subprocess.Popen(
        ["wsl", "-d", docker[2], "-u", "root", "-e", "sleep", "infinity"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    )
    ledger.record("started", "wsl_anchor", str(process.pid), distribution=docker[2], image=ANCHOR_PROCESS)
    print(f"holding a WSL session open (pid {process.pid}) so the containers survive")


def close_wsl_anchor(pid: str) -> str:
    """
    Release the WSL session held for the stack

    The identity of the process is confirmed before killing it: a recorded pid
    may already be gone and reassigned by the operating system, and killing it
    blindly would take down an unrelated process tree.

    Args:
        pid: Process identifier recorded when the session was opened

    Returns:
        What happened, for the caller to report
    """
    if os.name != "nt":
        result = subprocess.run(["kill", pid], capture_output=True, text=True)
        return "released" if result.returncode == 0 else f"not released ({result.stderr.strip() or 'no such process'})"

    listing = subprocess.run(
        ["tasklist", "/FI", f"PID eq {pid}", "/NH", "/FO", "CSV"],
        capture_output=True, text=True
    )
    if ANCHOR_PROCESS.lower() not in listing.stdout.lower():
        return f"already gone (pid {pid} is not {ANCHOR_PROCESS})"

    killed = subprocess.run(["taskkill", "/PID", pid, "/F", "/T"], capture_output=True, text=True)
    if killed.returncode != 0:
        return f"not released ({killed.stdout.strip() or killed.stderr.strip()})"

    return "released"


def to_docker_path(docker: List[str], path: str) -> str:
    """
    Translate a host path into the path the docker client expects

    Args:
        docker: Docker command prefix
        path: Path on the machine running this script

    Returns:
        Path usable by the docker client
    """
    if docker[0] != "wsl":
        return path

    translated = subprocess.run(
        ["wsl", "-d", docker[2], "-e", "wslpath", "-a", path.replace("\\", "/")],
        capture_output=True,
        text=True
    )
    return translated.stdout.strip() or path


def run(command: List[str], timeout: int = 900) -> Tuple[int, str]:
    """
    Run a command and capture its combined output

    Args:
        command: Command and arguments
        timeout: Seconds before the command is abandoned

    Returns:
        Exit code and captured output
    """
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return 1, f"timed out after {timeout}s"

    return completed.returncode, (completed.stdout or "") + (completed.stderr or "")


def compose(docker: List[str], project_root: str, env_file: str, arguments: List[str], timeout: int = 900):
    """
    Run docker compose for this project

    Args:
        docker: Docker command prefix
        project_root: Repository root on the host
        env_file: Path to the environment file on the host
        arguments: Compose arguments
        timeout: Seconds before the command is abandoned

    Returns:
        Exit code and captured output
    """
    files = ["-f", to_docker_path(docker, os.path.join(project_root, "docker-compose.yml"))]

    override = os.path.join(project_root, "docker-compose.e2e.yml")
    if os.path.isfile(override):
        files += ["-f", to_docker_path(docker, override)]

    env_path = to_docker_path(docker, env_file)
    return run(
        [*docker, "compose", "--env-file", env_path, *files, *arguments],
        timeout=timeout
    )


def ensure_env_file(project_root: str, ledger: Ledger) -> str:
    """
    Make sure the backend environment file exists, creating a disposable one if needed

    Args:
        project_root: Repository root
        ledger: Journal recording the change

    Returns:
        Path to the environment file
    """
    env_path = os.path.join(project_root, "services", "backend", ".env")
    if os.path.isfile(env_path):
        ledger.note(f"using existing environment file {env_path}")
        return env_path

    sample_path = os.path.join(project_root, "services", "backend", ".env.sample")
    with open(sample_path, encoding="utf-8") as handle:
        sample = handle.read()

    values = {
        "POSTGRES_DB": "clothing_store_e2e",
        "POSTGRES_DB_PORT": "5432",
        "POSTGRES_USER": "admin",
        "POSTGRES_PASSWORD": "e2e_password",
        "POSTGRES_HOST": "db",
        "PGADMIN_DEFAULT_EMAIL": "admin@example.com",
        "PGADMIN_DEFAULT_PASSWORD": "e2e_password",
        "DATASET_DIR": "/usr/src/dataset",
        "LOG_DIR": "/usr/src/logs",
        "FRONTEND_CORS_ORIGINS": "http://localhost:5000",
        "ELASTICSEARCH_HOST": "elasticsearch",
        "ELASTICSEARCH_PORT": "9200",
        "ELASTICSEARCH_USER": "elastic",
        "ELASTICSEARCH_PASSWORD": "e2e_password",
        "ELASTICSEARCH_SCHEME": "http",
        "ELASTICSEARCH_PRODUCTS_INDEX": "products",
        "EMAIL_HOST": "mailhog",
        "EMAIL_PORT": "1025",
        "EMAIL_HOST_USER": "e2e",
        "EMAIL_HOST_PASSWORD": "e2e",
        "EMAIL_USE_TLS": "False",
        "EMAIL_USE_SSL": "False",
        "JWT_SECRET_KEY_ACCESS": "e2e_access_secret",
        "JWT_SECRET_KEY_REFRESH": "e2e_refresh_secret",
        "JWT_SIGNING_ALGORITHM": "HS256",
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "JWT_REFRESH_TOKEN_EXPIRE_MINUTES": "10080",
        "GOOGLE_CLIENT_ID": "e2e_google_id",
        "GOOGLE_CLIENT_SECRET": "e2e_google_secret",
        "FACEBOOK_CLIENT_ID": "e2e_facebook_id",
        "FACEBOOK_CLIENT_SECRET": "e2e_facebook_secret",
    }

    lines = []
    for line in sample.splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key = line.split("=", 1)[0].strip()
            if key in values:
                lines.append(f"{key}={values[key]}")
                continue
        lines.append(line)

    with open(env_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")

    ledger.record("created", "file", env_path, reason="no .env present, generated from .env.sample")
    return env_path


def ensure_override(project_root: str, ledger: Ledger) -> str:
    """
    Write the compose override that makes the stack suitable for end-to-end runs

    The development command runs uvicorn with --reload and forced polling. On a
    bind mount backed by a host filesystem the watcher sees phantom changes and
    restarts the server every couple of minutes, which drops in-flight requests
    and makes every scenario flaky. End-to-end runs use a plain server instead.

    The override also raises the limits the scenarios spend themselves. Left at
    production values, a suite that registers a dozen accounts exhausts its own
    quota and a rerun inside the same minute fails on 429 rather than on code.
    The email dispatch limit stays low on purpose: one scenario proves the
    limiter still refuses a burst.

    Args:
        project_root: Repository root
        ledger: Journal recording the change

    Returns:
        Path to the override file
    """
    override_path = os.path.join(project_root, "docker-compose.e2e.yml")
    content = (
        "services:\n"
        "  web:\n"
        "    command: [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n"
        "    environment:\n"
        f"      RATE_LIMIT_REGISTRATION: {SCENARIO_RATE_LIMIT}\n"
        f"      RATE_LIMIT_CREDENTIAL_GUESS: {SCENARIO_RATE_LIMIT}\n"
        f"      RATE_LIMIT_EMAIL_DISPATCH: {EMAIL_DISPATCH_RATE_LIMIT}\n"
    )

    with open(override_path, "w", encoding="utf-8") as handle:
        handle.write(content)

    ledger.record("created", "file", override_path, reason="runs the API without the reloading development server")
    return override_path


def ensure_mailhog_env(project_root: str, ledger: Ledger) -> None:
    """
    Make sure the mailhog environment file exists, since compose refuses to start without it

    Args:
        project_root: Repository root
        ledger: Journal recording the change
    """
    env_path = os.path.join(project_root, "services", "mailhog", ".env")
    if os.path.isfile(env_path):
        return

    with open(env_path, "w", encoding="utf-8") as handle:
        handle.write("MAILHOG_USER=e2e\nMAILHOG_PASSWORD=e2e\n")

    ledger.record("created", "file", env_path, reason="required by compose, generated for this run")


def wait_for_api(base_url: str, attempts: int = 60, delay: float = 3.0, stable_answers: int = 4) -> bool:
    """
    Wait until the API answers consistently

    A single successful response is not enough: the development server reloads
    itself after startup, so the stack must answer several times in a row before
    scenarios may run against it.

    Args:
        base_url: API base URL
        attempts: How many times to poll
        delay: Seconds between attempts
        stable_answers: Consecutive successful responses required

    Returns:
        True when the API answered consistently
    """
    probe = base_url.replace("/api/v1", "/docs")
    consecutive = 0

    for _ in range(attempts):
        try:
            with urllib.request.urlopen(probe, timeout=5) as response:
                consecutive = consecutive + 1 if response.status < 500 else 0
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ConnectionError):
            consecutive = 0

        if consecutive >= stable_answers:
            return True

        time.sleep(delay)

    return False


def request(method: str, url: str, payload: Optional[dict] = None, token: Optional[str] = None) -> Tuple[int, dict]:
    """
    Send a JSON request to the API

    Args:
        method: HTTP method
        url: Absolute URL
        payload: Body to send as JSON
        token: Bearer token

    Returns:
        Status code and decoded body
    """
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    http_request = urllib.request.Request(url, data=data, method=method)
    http_request.add_header("Content-Type", "application/json")
    if token:
        http_request.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(http_request, timeout=REQUEST_TIMEOUT) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8")
        try:
            return error.code, json.loads(body) if body else {}
        except json.JSONDecodeError:
            return error.code, {"raw": body}
    except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
        return 0, {"error": str(error)}


def command_up(arguments, ledger: Ledger) -> int:
    """
    Start the stack and apply migrations

    Args:
        arguments: Parsed command line arguments
        ledger: Journal recording the changes

    Returns:
        Process exit code
    """
    project_root = find_project_root()
    docker = detect_docker(arguments.distro)
    ledger.note(f"docker client: {' '.join(docker)}")
    open_wsl_anchor(docker, ledger)

    env_file = ensure_env_file(project_root, ledger)
    ensure_mailhog_env(project_root, ledger)
    ensure_override(project_root, ledger)

    ledger.record("started", "compose_stack", ",".join(STACK_SERVICES), project_root=project_root)
    code, output = compose(docker, project_root, env_file, ["up", "-d", "--build", *STACK_SERVICES])
    if code != 0:
        print(output[-3000:])
        return code

    print("stack starting, waiting for the API")
    if not wait_for_api(arguments.api):
        code, output = compose(docker, project_root, env_file, ["logs", "--tail", "40", "web"])
        print(output[-3000:])
        return 1

    ledger.record("applied", "migrations", "migrations.cli migrate --force")
    code, output = compose(
        docker,
        project_root,
        env_file,
        ["--profile", "tools", "run", "--rm", "backend-runner", "python", "-m", "migrations.cli", "migrate", "--force"]
    )
    print(output[-1500:])

    print(f"stack is up, ledger: {ledger.path}")
    return 0


def command_scenarios(arguments, ledger: Ledger) -> int:
    """
    Run the end-to-end scenarios against the running stack

    Args:
        arguments: Parsed command line arguments
        ledger: Journal recording created data

    Returns:
        Process exit code
    """
    base = arguments.api.rstrip("/")
    results: List[Tuple[str, bool, str]] = []

    status, _ = request("GET", f"{base}/catalog/products?page=1&per_page=1")
    results.append(("catalog responds", status in (200, 404), f"status {status}"))

    email = f"{TEST_EMAIL_PREFIX}{uuid.uuid4().hex[:12]}@example.com"
    status, body = request("POST", f"{base}/accounts/register", {"email": email, "password": "E2ePassword123!"})
    registered = status == 201
    if registered:
        ledger.record("created", "db_row", email, table="accounts_users", note="registration scenario")
    results.append(("registration returns 201", registered, f"status {status} {str(body)[:120]}"))

    status, body = request("POST", f"{base}/accounts/register", {"email": email, "password": "E2ePassword123!"})
    results.append(("duplicate registration rejected", status == 409, f"status {status}"))

    concurrent_emails = [f"{TEST_EMAIL_PREFIX}{uuid.uuid4().hex[:12]}@example.com" for _ in range(arguments.parallel)]
    for address in concurrent_emails:
        ledger.record("created", "db_row", address, table="accounts_users", note="concurrency scenario")

    started = time.time()
    codes = run_parallel_registrations(base, concurrent_emails)
    elapsed = time.time() - started

    accepted = sum(1 for code in codes if code == 201)
    throttled = sum(1 for code in codes if code == 429)
    unexpected = sorted({code for code in codes if code not in (201, 429)})
    within_budget = elapsed < PARALLEL_REGISTRATION_BUDGET_SECONDS

    results.append((
        f"{arguments.parallel} parallel registrations are served or throttled, never broken",
        accepted + throttled == len(codes) and not unexpected and accepted > 0,
        f"{accepted} created, {throttled} throttled, unexpected {unexpected}"
    ))
    results.append((
        "hashing does not block the event loop",
        within_budget,
        f"{len(codes)} concurrent registrations answered in {elapsed:.2f}s"
    ))

    status, body = request("POST", f"{base}/checkout/cart/token")
    cart_token = body.get("cart_token") or body.get("token")
    if cart_token:
        ledger.record("created", "db_row", cart_token, table="checkout_cart_tokens", note="cart scenario")
    results.append(("cart token created", status == 201 and bool(cart_token), f"status {status}"))

    if cart_token:
        status, body = request("POST", f"{base}/checkout/cart/token/get", {"token": cart_token})
        results.append(("cart readable by token", status == 200, f"status {status}"))

        if seed_test_product(arguments, ledger, STOCK_PROBE_PRODUCT_ID, STOCK_PROBE_UNITS):
            results.extend(check_stock_limit(base, cart_token, STOCK_PROBE_PRODUCT_ID))
            results.extend(check_concurrent_stock_limit(base, STOCK_PROBE_PRODUCT_ID, STOCK_PROBE_UNITS))

    results.extend(check_pagination_links(arguments, base, ledger))
    results.extend(check_refresh_rotation(arguments, base, ledger))
    results.extend(check_rate_limit(base))

    print_results(results)
    write_report(ledger, results)
    return 0 if all(passed for _, passed, _ in results) else 1


def seed_test_product(arguments, ledger: Ledger, product_id: int, stock: int) -> bool:
    """
    Insert one product with a known stock level

    Scenarios must not depend on the dataset being loaded, and must not reuse a
    real product whose stock they would then disturb.

    Args:
        arguments: Parsed command line arguments
        ledger: Journal recording the rows
        product_id: Identifier to insert
        stock: Units to make available

    Returns:
        True when the product is in place
    """
    project_root = find_project_root()
    docker = detect_docker(arguments.distro)
    env_file = os.path.join(project_root, "services", "backend", ".env")

    if not isinstance(product_id, int) or not isinstance(stock, int):
        raise TypeError("product_id and stock must be integers: they are interpolated into SQL")

    ledger.record("created", "db_row", str(product_id), table="catalog_products", note="stock scenario")
    ledger.record("created", "db_row", str(product_id), table="catalog_product_inventory", note="stock scenario")

    statement = (
        f"INSERT INTO catalog_products "
        f"(product_id, gender, year, product_display_name, image_url, slug) "
        f"VALUES ({product_id}, 'Unisex', 2026, 'E2E Stock Probe', "
        f"'http://example.com/e2e.jpg', 'e2e-stock-probe-{product_id}') "
        f"ON CONFLICT (product_id) DO NOTHING; "
        f"INSERT INTO catalog_product_inventory (product_id, base_price, stock_quantity, is_active) "
        f"VALUES ({product_id}, 10.00, {stock}, TRUE) "
        f"ON CONFLICT (product_id) DO UPDATE SET stock_quantity = {stock};"
    )

    user = read_env_value(env_file, "POSTGRES_USER") or "admin"
    database = read_env_value(env_file, "POSTGRES_DB") or "clothing_store"
    code, output = compose(
        docker, project_root, env_file,
        ["exec", "-T", "db", "psql", "-U", user, "-d", database, "-c", statement],
        timeout=120
    )

    if code != 0:
        print(f"could not seed the stock probe product: {output.strip()[:200]}")

    return code == 0


def check_stock_limit(base: str, cart_token: str, product_id: int) -> List[Tuple[str, bool, str]]:
    """
    Check that the database refuses a cart quantity beyond the available stock

    The guard lives in the UPDATE statement itself, so only a real database can
    prove it: unit tests run against a repository double and would pass either way.

    Args:
        base: API base URL
        cart_token: Token of an existing anonymous cart

    Returns:
        Scenario results
    """
    results: List[Tuple[str, bool, str]] = []

    status, added = request(
        "POST",
        f"{base}/checkout/cart/token/{cart_token}/items",
        {"product_id": product_id, "quantity": 1}
    )
    if status != 201:
        results.append(("stock limit enforced by the database", False, f"could not add item, status {status}"))
        return results

    item_id = added.get("id")
    status, body = request(
        "PUT",
        f"{base}/checkout/cart/token/{cart_token}/items/{item_id}",
        {"cart_item_id": item_id, "quantity": STOCK_PROBE_UNITS + 5}
    )
    results.append((
        "stock limit enforced by the database",
        status == 400,
        f"status {status} {str(body)[:80]}"
    ))

    return results


def check_concurrent_stock_limit(base: str, product_id: int, stock: int) -> List[Tuple[str, bool, str]]:
    """
    Check that concurrent additions to one cart cannot exceed the stock

    Only a real database proves this: the guard is a row lock held for the length of
    a transaction, and a repository double cannot reproduce it.

    Args:
        base: API base URL
        product_id: Product to compete for
        stock: Units the warehouse holds

    Returns:
        Scenario results
    """
    from concurrent.futures import ThreadPoolExecutor

    status, body = request("POST", f"{base}/checkout/cart/token")
    token = body.get("token")
    if status != 201 or not token:
        return [("concurrent additions respect the stock", False, f"no cart token, status {status}")]

    def add_one(_: int) -> int:
        code, _body = request(
            "POST",
            f"{base}/checkout/cart/token/{token}/items",
            {"product_id": product_id, "quantity": 1}
        )
        return code

    attempts = stock + 2
    with ThreadPoolExecutor(max_workers=attempts) as pool:
        codes = list(pool.map(add_one, range(attempts)))

    status, cart = request("POST", f"{base}/checkout/cart/token/get", {"token": token})
    stored = sum(item.get("quantity", 0) for item in cart.get("items", []))

    accepted = codes.count(201)
    refused = codes.count(400)
    broken = [code for code in codes if code not in (201, 400)]

    passed = (
        stored == stock
        and accepted == stock
        and refused == attempts - stock
        and not broken
    )

    return [(
        "concurrent additions respect the stock",
        passed,
        f"{attempts} at once -> {accepted} accepted, {refused} refused, "
        f"{len(broken)} neither ({sorted(set(broken))}), cart holds {stored} of {stock}"
    )]


def check_rate_limit(base: str) -> List[Tuple[str, bool, str]]:
    """
    Prove the limiter still refuses a burst on the real stack

    Password reset is used because no other scenario spends its quota, and an
    address nobody registered writes no row and sends no mail: the limiter counts
    the request either way.

    The stand configures a per-second window, so the burst proves the mechanism
    without leaving a spent quota behind: a rerun a second later starts clean.
    The assertion is therefore that a burst is partly served and partly refused,
    which fails both when the limiter is absent and when it refuses everything.

    Args:
        base: API base URL

    Returns:
        One scenario result
    """
    unknown_address = f"{TEST_EMAIL_PREFIX}{uuid.uuid4().hex[:12]}@example.com"

    codes = []
    for _ in range(EMAIL_DISPATCH_BURST):
        status, _ = request("POST", f"{base}/accounts/password-reset/request", {"email": unknown_address})
        codes.append(status)

    served = sum(1 for code in codes if code == 200)
    refused = sum(1 for code in codes if code == 429)

    return [(
        "a burst beyond the limit is partly refused",
        served > 0 and refused > 0 and served + refused == len(codes),
        f"{EMAIL_DISPATCH_BURST} in a row -> {served} served, {refused} refused, "
        f"other {sorted({code for code in codes if code not in (200, 429)})}"
    )]


def activate_user(arguments, address: str) -> bool:
    """
    Activate a registered account straight in the database

    The activation link is delivered by mail, which a scenario cannot read, so the
    row is flipped directly. Nothing else about the account is touched.

    Args:
        arguments: Parsed command line arguments
        address: Address of the account to activate

    Returns:
        True when the account is active
    """
    project_root = find_project_root()
    docker = detect_docker(arguments.distro)
    env_file = os.path.join(project_root, "services", "backend", ".env")

    if not address.startswith(TEST_EMAIL_PREFIX):
        raise ValueError(f"refusing to activate an account outside the {TEST_EMAIL_PREFIX} prefix")

    statement = f"UPDATE accounts_users SET is_active = TRUE WHERE email = '{address}';"

    user = read_env_value(env_file, "POSTGRES_USER") or "admin"
    database = read_env_value(env_file, "POSTGRES_DB") or "clothing_store"
    code, output = compose(
        docker, project_root, env_file,
        ["exec", "-T", "db", "psql", "-U", user, "-d", database, "-c", statement],
        timeout=120
    )

    if code != 0:
        print(f"could not activate {address}: {output.strip()[:200]}")

    return code == 0


def check_refresh_rotation(arguments, base: str, ledger: Ledger) -> List[Tuple[str, bool, str]]:
    """
    Check that refreshing replaces the token it was given

    Rotation spans the token store and two requests, so only a live stack shows
    whether the presented token really stopped working.

    Args:
        arguments: Parsed command line arguments
        base: API base URL
        ledger: Journal recording the account

    Returns:
        Scenario results
    """
    address = f"{TEST_EMAIL_PREFIX}{uuid.uuid4().hex[:12]}@example.com"
    password = "E2ePassword123!"
    ledger.record("created", "db_row", address, table="accounts_users", note="refresh rotation scenario")

    status, _ = request("POST", f"{base}/accounts/register", {"email": address, "password": password})
    if status != 201 or not activate_user(arguments, address):
        return [("refresh rotation could be checked", False, f"account could not be prepared (register {status})")]

    status, body = request("POST", f"{base}/accounts/login", {"email": address, "password": password})
    first_refresh = body.get("refresh_token")
    if status != 200 or not first_refresh:
        return [("refresh rotation could be checked", False, f"login answered {status}")]

    status, body = request("POST", f"{base}/accounts/refresh", {"refresh_token": first_refresh})
    second_refresh = body.get("refresh_token")

    results = [(
        "refreshing returns a new refresh token",
        status == 200 and bool(second_refresh) and second_refresh != first_refresh,
        f"status {status}, token changed: {bool(second_refresh) and second_refresh != first_refresh}"
    )]

    replayed, _ = request("POST", f"{base}/accounts/refresh", {"refresh_token": first_refresh})
    results.append((
        "the replaced refresh token stops working",
        replayed == 401,
        f"replaying the old token answered {replayed}"
    ))

    if second_refresh:
        status, body = request("POST", f"{base}/accounts/refresh", {"refresh_token": second_refresh})
        results.append((
            "the new refresh token works",
            status == 200 and bool(body.get("access_token")),
            f"status {status}"
        ))

    return results


def check_pagination_links(arguments, base: str, ledger: Ledger) -> List[Tuple[str, bool, str]]:
    """
    Check that the link the catalogue hands the client can be followed

    Two products are seeded so the listing spans more than one page: the dataset is
    not loaded on the stand, and an empty catalogue returns no links to follow.

    Args:
        arguments: Parsed command line arguments
        base: API base URL
        ledger: Journal recording the rows

    Returns:
        Scenario results
    """
    for offset in range(PAGINATION_PROBE_PRODUCTS):
        if not seed_test_product(arguments, ledger, PAGINATION_PROBE_PRODUCT_ID + offset, 1):
            return [("pagination links could be checked", False, "probe products could not be seeded")]

    status, body = request("GET", f"{base}/catalog/products?page=1&per_page=1")
    next_page = body.get("next_page") if isinstance(body, dict) else None

    if status != 200 or not next_page:
        return [("the catalogue offers a next page link", False, f"status {status}, link {next_page}")]

    followed, _ = request("GET", f"{API_ORIGIN}{next_page}")

    return [(
        "the next page link the catalogue returns can be followed",
        followed == 200,
        f"following {next_page} answered {followed}"
    )]


def run_parallel_registrations(base: str, emails: List[str]) -> List[int]:
    """
    Register several accounts at the same time

    Args:
        base: API base URL
        emails: Addresses to register

    Returns:
        Status code of every request
    """
    from concurrent.futures import ThreadPoolExecutor

    def register(address: str) -> int:
        status, _ = request("POST", f"{base}/accounts/register", {"email": address, "password": "E2ePassword123!"})
        return status

    with ThreadPoolExecutor(max_workers=len(emails)) as pool:
        return list(pool.map(register, emails))


def print_results(results: List[Tuple[str, bool, str]]) -> None:
    """
    Print scenario results

    Args:
        results: Name, outcome and detail of every scenario
    """
    print("\nScenarios")
    for name, passed, detail in results:
        marker = "PASS" if passed else "FAIL"
        print(f"  [{marker}] {name} — {detail}")

    failed = [name for name, passed, _ in results if not passed]
    print(f"\n{len(results) - len(failed)}/{len(results)} passed")


def write_report(ledger: Ledger, results: List[Tuple[str, bool, str]]) -> None:
    """
    Store scenario results next to the ledger

    Args:
        ledger: Journal of the run
        results: Scenario outcomes
    """
    path = os.path.join(ledger.directory, "scenarios.md")
    lines = ["# Scenario results", ""]
    for name, passed, detail in results:
        lines.append(f"- [{'PASS' if passed else 'FAIL'}] {name} — {detail}")

    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def command_cleanup(arguments, ledger: Ledger) -> int:
    """
    Undo every change recorded in the ledger

    Args:
        arguments: Parsed command line arguments
        ledger: Journal to replay backwards

    Returns:
        Process exit code
    """
    project_root = find_project_root()
    docker = detect_docker(arguments.distro)
    env_file = os.path.join(project_root, "services", "backend", ".env")

    marker = os.path.join(ledger.directory, "cleaned")
    if os.path.isfile(marker):
        print(f"{ledger.run_id} was already cleaned up; nothing to undo twice")
        return 0

    entries = ledger.cleanup_entries()
    if not entries:
        print(f"nothing recorded for {ledger.run_id}")
        return 0

    removed_rows = [entry for entry in entries if entry["resource"] == "db_row"]
    if removed_rows:
        delete_test_rows(docker, project_root, env_file, removed_rows)

    if any(entry["resource"] == "compose_stack" for entry in entries):
        print("stopping stack and removing volumes")
        compose(docker, project_root, env_file, ["down", "-v", "--remove-orphans"])

    for entry in entries:
        if entry["resource"] == "wsl_anchor":
            outcome = close_wsl_anchor(entry["identifier"])
            print(f"WSL session pid {entry['identifier']}: {outcome}")

        if entry["resource"] == "file" and entry["action"] == "created":
            if os.path.isfile(entry["identifier"]):
                os.remove(entry["identifier"])
                print(f"removed generated file {entry['identifier']}")

    with open(marker, "w", encoding="utf-8") as handle:
        handle.write("cleanup completed\n")

    print(f"cleanup finished for {ledger.run_id}")
    return 0


def delete_test_rows(docker: List[str], project_root: str, env_file: str, entries: List[Dict]) -> None:
    """
    Delete rows created during the run

    Args:
        docker: Docker command prefix
        project_root: Repository root
        env_file: Environment file used by compose
        entries: Ledger entries describing created rows
    """
    emails = [entry["identifier"] for entry in entries if entry["details"].get("table") == "accounts_users"]
    tokens = [entry["identifier"] for entry in entries if entry["details"].get("table") == "checkout_cart_tokens"]

    statements = []
    if emails:
        statements.append(f"DELETE FROM accounts_users WHERE email IN ({format_in_list(emails)});")
    if tokens:
        statements.append(f"DELETE FROM checkout_cart_tokens WHERE token IN ({format_in_list(tokens)});")

    if not statements:
        return

    user = read_env_value(env_file, "POSTGRES_USER") or "admin"
    database = read_env_value(env_file, "POSTGRES_DB") or "clothing_store"

    for statement in statements:
        code, output = compose(
            docker,
            project_root,
            env_file,
            ["exec", "-T", "db", "psql", "-U", user, "-d", database, "-c", statement],
            timeout=120
        )
        print(f"{statement.strip()} -> {'ok' if code == 0 else output.strip()[:200]}")


def format_in_list(values: List[str]) -> str:
    """
    Render values for an SQL IN clause

    Args:
        values: Literal values

    Returns:
        Comma separated quoted list
    """
    escaped = [value.replace("'", "''") for value in values]
    return ", ".join(f"'{value}'" for value in escaped)


def read_env_value(env_file: str, key: str) -> Optional[str]:
    """
    Read a single value from an environment file

    Args:
        env_file: Path to the file
        key: Name to look up

    Returns:
        Value, or None when the key is absent
    """
    if not os.path.isfile(env_file):
        return None

    with open(env_file, encoding="utf-8") as handle:
        for line in handle:
            if line.strip().startswith(f"{key}="):
                return line.split("=", 1)[1].strip()
    return None


def probe_stack(docker: List[str], api_url: str) -> Dict[str, str]:
    """
    Take one health sample of the stack

    Args:
        docker: Docker command prefix
        api_url: API base URL

    Returns:
        Mapping of container names to status, plus the API state
    """
    sample: Dict[str, str] = {}

    code, output = run(
        [*docker, "ps", "-a", "--format", "{{.Names}}|{{.Status}}"],
        timeout=60
    )
    if code == 0:
        for line in output.splitlines():
            if "|" in line and "clothing" in line or "postgres" in line:
                name, _, status = line.partition("|")
                sample[name.strip()] = status.strip()

    for name in list(sample):
        code, restarts = run([*docker, "inspect", "-f", "{{.RestartCount}}", name], timeout=60)
        if code == 0 and restarts.strip().isdigit() and int(restarts.strip()) > 0:
            sample[name] = f"{sample[name]} restarts={restarts.strip()}"

    probe = api_url.replace("/api/v1", "/docs")
    try:
        with urllib.request.urlopen(probe, timeout=8) as response:
            sample["api"] = f"HTTP {response.status}"
    except urllib.error.HTTPError as error:
        sample["api"] = f"HTTP {error.code}"
    except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
        sample["api"] = f"unreachable ({type(error).__name__})"

    return sample


def command_monitor(arguments, ledger: Ledger) -> int:
    """
    Poll the stack on a timer and print state changes to the console

    Polling is used rather than event subscription: a dropped event is silent,
    while a missed poll is corrected by the next one.

    The destination of the log is resolved at every sample unless a run was named
    explicitly. A monitor started before the stack, as the skill asks, would
    otherwise keep writing into the previous run's directory for its whole life,
    and the run it was meant to document would end up with an empty log.

    Args:
        arguments: Parsed command line arguments
        ledger: Journal of the run

    Returns:
        Process exit code, non-zero when a failure was observed
    """
    docker = detect_docker(arguments.distro)
    pinned_run = bool(getattr(arguments, "run_id", None))
    log_path = os.path.join(ledger.directory, "monitor.log")
    deadline = time.time() + arguments.duration if arguments.duration else None

    previous: Dict[str, str] = {}
    failures = 0

    print(f"monitoring every {arguments.interval}s, log: {log_path}")

    while deadline is None or time.time() < deadline:
        if not pinned_run:
            log_path = os.path.join(run_directory(latest_run_id()), "monitor.log")

        sample = probe_stack(docker, arguments.api)
        stamp = time.strftime("%H:%M:%S")

        unhealthy = [
            f"{name}={state}" for name, state in sample.items()
            if "unreachable" in state or "Exited" in state or "Restarting" in state or "restarts=" in state
        ]

        if sample != previous:
            summary = ", ".join(f"{name}: {state}" for name, state in sorted(sample.items()))
            line = f"[{stamp}] {summary}"
            print(line)
            with open(log_path, "a", encoding="utf-8") as handle:
                handle.write(line + "\n")
            previous = sample

        if unhealthy:
            failures += 1
            alert = f"[{stamp}] PROBLEM: {'; '.join(unhealthy)}"
            print(alert)
            with open(log_path, "a", encoding="utf-8") as handle:
                handle.write(alert + "\n")

        time.sleep(arguments.interval)

    print(f"monitoring finished, {failures} problem samples")
    return 1 if failures else 0


def command_report(arguments, ledger: Ledger) -> int:
    """
    Print the ledger of a run

    Args:
        arguments: Parsed command line arguments
        ledger: Journal to render

    Returns:
        Process exit code
    """
    print(ledger.summary())
    return 0


def main() -> int:
    """
    Parse arguments and dispatch the requested command

    Returns:
        Process exit code
    """
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Run the compose stack for end-to-end checks")
    parser.add_argument("command", choices=("up", "scenarios", "monitor", "cleanup", "report"))
    parser.add_argument("--run-id", default=None, help="Reuse an existing run instead of starting a new one")
    parser.add_argument("--api", default=DEFAULT_API)
    parser.add_argument("--distro", default=None, help="WSL distribution hosting docker")
    parser.add_argument("--parallel", type=int, default=10, help="Concurrent registrations in the race scenario")
    parser.add_argument("--interval", type=int, default=60, help="Seconds between monitor samples")
    parser.add_argument("--duration", type=int, default=0, help="Seconds to monitor, 0 runs until interrupted")
    arguments = parser.parse_args()

    if arguments.command == "up":
        run_id = arguments.run_id or new_run_id()
    else:
        run_id = arguments.run_id or latest_run_id()
        if run_id is None:
            print("no recorded run found; start with: e2e.py up")
            return 1

    ledger = Ledger(run_id)
    print(f"run {run_id} — {run_directory(run_id)}")

    handlers = {
        "up": command_up,
        "scenarios": command_scenarios,
        "monitor": command_monitor,
        "cleanup": command_cleanup,
        "report": command_report,
    }
    return handlers[arguments.command](arguments, ledger)


if __name__ == "__main__":
    sys.exit(main())
