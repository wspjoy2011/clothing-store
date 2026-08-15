---
name: e2e-docker
description: Run the application end to end against the real compose stack — Postgres and the API in containers — then undo every change. Records each container, volume, file and database row it creates into a ledger under the system temp directory, and cleans them up afterwards. Use when asked to verify a change for real, test against a live database, or confirm behaviour that unit tests with fakes cannot prove.
---

# End-to-end run on the compose stack

Unit tests use fakes. This skill proves the code works against a real Postgres and a real HTTP surface, then leaves the machine exactly as it was found.

## The ledger

Every change is appended to `ledger.jsonl` under the system temp directory before it is applied, so an interrupted run still leaves a complete trail. Entries record containers and volumes started, files generated, and rows written to the database. `cleanup` replays the ledger backwards.

Never delete data that is not in the ledger. If a row, container or volume was not created by this run, it stays.

## Commands

```
python .claude/skills/e2e-docker/scripts/e2e.py up          # start stack, apply migrations
python .claude/skills/e2e-docker/scripts/e2e.py scenarios   # run the checks
python .claude/skills/e2e-docker/scripts/e2e.py monitor     # poll the stack, print problems
python .claude/skills/e2e-docker/scripts/e2e.py report      # show what this run changed
python .claude/skills/e2e-docker/scripts/e2e.py cleanup     # undo everything
```

`up` starts a new run and prints its identifier. The other commands reuse the latest run unless `--run-id` is given.

The script finds a docker client itself: the `docker` binary when it is on PATH, otherwise a docker engine inside WSL. Pass `--distro` when several distributions carry one.

If the backend has no `.env`, the script generates a disposable one from `.env.sample`, records it in the ledger and deletes it during cleanup. An existing `.env` is used as is and never modified.

`up` also writes a compose override that runs the API without the reloading development server. The reloader watches a bind mount, sees phantom changes and restarts every couple of minutes, which drops in-flight requests and makes every scenario fail at random. The override is recorded in the ledger and removed during cleanup.

## Monitoring

Run `monitor` alongside a long check to see the stack state on a timer:

```
python .claude/skills/e2e-docker/scripts/e2e.py monitor --interval 60 --duration 600
```

It samples container status, restart counts and API reachability, prints a line whenever the state changes and a `PROBLEM` line for anything unreachable, exited, restarting or restarted. Samples are appended to `monitor.log` in the run directory.

Polling on a timer rather than subscribing to events is deliberate: a dropped event is silent and a crashed listener stops reporting, while a missed poll is corrected by the next one.

## Rules

1. **Always clean up.** Run `cleanup` when the checks finish, including when they fail and including when you are interrupted. Report what was removed.
2. **Test data is marked.** Accounts created by scenarios use the `e2e-` email prefix so cleanup can identify them without touching real rows.
3. **Report the ledger.** After a run, print what was created and what was removed. The user must be able to see that nothing was left behind.
4. **Failures are results.** A failing scenario is reported with its status code and response body, not retried until it passes and not silently dropped.

## Steps

1. Run `up` and wait for the API to answer. If it never does, print the last lines of the web service logs and stop — do not run scenarios against a stack that is not ready.
2. Run `scenarios`.
3. Read the results. For every failure, look at the container logs before drawing a conclusion; a failure may be a broken environment rather than broken code.
4. Run `cleanup`.
5. Report: which scenarios passed, which failed and why, what the ledger recorded, and confirmation that cleanup completed.

## Permanent scenarios versus one-off checks

The skill and its scripts hold **permanent rules** — the setup every run needs and the scenarios worth re-running forever. A one-off probe written to answer a single question does not belong here.

**Permanent** — add it to `command_scenarios` in `scripts/e2e.py`. A scenario sends real HTTP requests and returns a name, a boolean and a detail string. Anything it writes to the database is recorded in the ledger in the same step, before the request that creates it.

Prefer scenarios that unit tests cannot express: concurrent requests competing for the same resource, behaviour that depends on real transaction boundaries, constraints enforced by the database itself.

**One-off** — write the throwaway script, record it in the ledger as a created file, run it, then delete it during cleanup. It never gets committed.

## When the run teaches you something

A run that exposes a trap — a service that will not build, a setting that makes results flaky, a missing prerequisite — is a signal to change the skill, not to work around it by hand. Fix `SKILL.md` or the scripts immediately, so the next run does not hit the same wall, and land that fix as its own commit separate from the work being verified.
