"""Append-only journal of everything an end-to-end run creates.

Each entry is written before the change is applied, so an interrupted run still
leaves a complete trail for cleanup to follow.
"""

import json
import os
import tempfile
import time
from typing import Any, Dict, List, Optional

LEDGER_ROOT = os.path.join(tempfile.gettempdir(), "clothing-store-e2e")


def run_directory(run_id: str) -> str:
    """
    Build the directory holding the artefacts of one run

    Args:
        run_id: Identifier of the run

    Returns:
        Absolute path to the run directory
    """
    return os.path.join(LEDGER_ROOT, run_id)


def new_run_id() -> str:
    """
    Build an identifier for a new run

    Returns:
        Identifier based on the current time
    """
    return time.strftime("run-%Y%m%d-%H%M%S")


def latest_run_id() -> Optional[str]:
    """
    Find the most recent run that left a ledger behind

    Returns:
        Identifier of the latest run, or None when no run was recorded
    """
    if not os.path.isdir(LEDGER_ROOT):
        return None

    candidates = [
        entry for entry in sorted(os.listdir(LEDGER_ROOT))
        if os.path.isfile(os.path.join(LEDGER_ROOT, entry, "ledger.jsonl"))
    ]
    return candidates[-1] if candidates else None


class Ledger:
    """Journal recording created resources and the state changed during a run"""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.directory = run_directory(run_id)
        os.makedirs(self.directory, exist_ok=True)
        self.path = os.path.join(self.directory, "ledger.jsonl")

    def record(self, action: str, resource: str, identifier: str, **details: Any) -> None:
        """
        Append an entry describing a change

        Args:
            action: What is being done, such as created or modified
            resource: Kind of resource, such as container, volume, db_row or file
            identifier: Value cleanup needs to undo the change
            details: Any extra context worth keeping
        """
        entry = {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "resource": resource,
            "identifier": identifier,
            "details": details,
        }
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def note(self, message: str) -> None:
        """
        Append a human-readable note that requires no cleanup

        Args:
            message: Text to record
        """
        self.record("note", "message", message)

    def entries(self) -> List[Dict[str, Any]]:
        """
        Read every entry of this run

        Returns:
            Entries in the order they were written
        """
        if not os.path.isfile(self.path):
            return []

        with open(self.path, encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    def cleanup_entries(self) -> List[Dict[str, Any]]:
        """
        Read the entries cleanup has to undo, newest first

        Returns:
            Entries describing resources that must be removed
        """
        undoable = [entry for entry in self.entries() if entry["resource"] != "message"]
        return list(reversed(undoable))

    def summary(self) -> str:
        """
        Render the run as a readable report

        Returns:
            Markdown summary of every recorded change
        """
        entries = self.entries()
        if not entries:
            return f"Run {self.run_id}: nothing recorded"

        lines = [f"# Run {self.run_id}", "", f"Ledger: {self.path}", ""]
        for entry in entries:
            if entry["resource"] == "message":
                lines.append(f"- {entry['time']}  {entry['identifier']}")
                continue

            detail = ", ".join(f"{key}={value}" for key, value in entry["details"].items())
            suffix = f" ({detail})" if detail else ""
            lines.append(
                f"- {entry['time']}  {entry['action']} {entry['resource']}: {entry['identifier']}{suffix}"
            )

        return "\n".join(lines)
