"""One-way status sync. No dependencies; does not create or delete Notion pages."""
import argparse
import json
import os
import sys
import time
import uuid
import urllib.request
import urllib.error
from pathlib import Path

STATUSES = {"Planned", "Pending review", "In progress", "Completed"}

def normalize(value):
    return str(uuid.UUID(value))

def load_tasks(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    source = normalize(data["data_source_id"])
    seen = set()
    for task in data["tasks"]:
        task["page_id"] = normalize(task["page_id"])
        if task["page_id"] in seen or task["status"] not in STATUSES:
            raise ValueError("Duplicate page or invalid task status")
        if not isinstance(task.get("managed"), bool):
            raise ValueError("Every task needs a boolean managed field")
        seen.add(task["page_id"])
    return source, data["tasks"]

def request(token, page_id, payload=None):
    req = urllib.request.Request(
        "https://api.notion.com/v1/pages/" + page_id,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": "Bearer " + token,
                 "Notion-Version": "2025-09-03",
                 "Content-Type": "application/json"},
        method="PATCH" if payload is not None else "GET")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.load(response)
            time.sleep(0.4)
            return result
        except urllib.error.HTTPError as error:
            if error.code == 429 or error.code >= 500:
                if attempt < 3:
                    delay = min(30, max(1, int(error.headers.get("Retry-After", 2 ** attempt))))
                    time.sleep(delay)
                    continue
            # Do not print tokens or raw response bodies.
            raise RuntimeError(f"Notion HTTP {error.code}; check token, page access and schema") from None
        except urllib.error.URLError:
            raise RuntimeError("Notion network failure; rerun the workflow") from None

def sync(source, tasks, token, api=request):
    pending = []
    # Check all managed pages before writing any changes.
    for task in tasks:
        if not task["managed"]:
            continue
        page = api(token, task["page_id"])
        if page.get("archived") or page.get("in_trash"):
            raise ValueError("A managed task is archived; resolve mapping first")
        if normalize(page.get("parent", {}).get("data_source_id", "")) != source:
            raise ValueError("Task does not belong to the configured tracker")
        prop = page.get("properties", {}).get("Status", {})
        if prop.get("type") != "status":
            raise ValueError("Tracker Status property must have type status")
        current = (prop.get("status") or {}).get("name")
        if current != task["status"]:
            pending.append(task)
    for task in pending:
        payload = {"properties": {"Status": {"status": {"name": task["status"]}}}}
        result = api(token, task["page_id"], payload)
        actual = result.get("properties", {}).get("Status", {}).get("status") or {}
        if actual.get("name") != task["status"]:
            raise RuntimeError("Notion did not confirm requested status; rerun after checking")
        print("Updated: " + task["name"])
    print(f"Sync complete: {len(pending)} changed; manual tasks untouched.")
    return len(pending)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--file", default="project/tasks.json")
    args = parser.parse_args()
    source, tasks = load_tasks(args.file)
    if args.validate_only:
        print(f"Valid manifest: {len(tasks)} tasks")
        return
    token = os.environ.get("NOTION_TOKEN", "").strip()
    if not token:
        raise RuntimeError("NOTION_TOKEN is not configured; sync is not activated")
    sync(source, tasks, token)

if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, RuntimeError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
