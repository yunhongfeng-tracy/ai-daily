#!/usr/bin/env python3
"""记录 AI Daily 更新日志（JSON + Markdown + state）"""

import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

HISTORY_JSON = os.path.join(LOG_DIR, "update-history.json")
HISTORY_MD = os.path.join(LOG_DIR, "update-history.md")
STATE_JSON = os.path.join(LOG_DIR, "update-state.json")


def _load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    run_id = os.environ.get("UPDATE_RUN_ID", "")
    trigger = os.environ.get("UPDATE_TRIGGER", "cron")
    status = os.environ.get("UPDATE_STATUS", "success")
    started_at = os.environ.get("UPDATE_STARTED_AT", datetime.now().astimezone().isoformat())
    finished_at = os.environ.get("UPDATE_FINISHED_AT", datetime.now().astimezone().isoformat())
    summary = os.environ.get("UPDATE_SUMMARY", "生成 AI Daily 页面")
    details = os.environ.get("UPDATE_DETAILS", "")

    if not run_id:
        run_id = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")

    history = _load_json(HISTORY_JSON, [])
    item = {
        "run_id": run_id,
        "trigger": trigger,
        "status": status,
        "started_at": started_at,
        "finished_at": finished_at,
        "summary": summary,
        "details": details,
    }
    history.insert(0, item)
    history = history[:200]
    _save_json(HISTORY_JSON, history)

    state = {
        "last_run": finished_at,
        "last_success": next((x["finished_at"] for x in history if x.get("status") == "success"), None),
        "status": status,
        "last_trigger": trigger,
        "last_run_id": run_id,
    }
    _save_json(STATE_JSON, state)

    lines = ["# AI Daily 更新日志", "", "| 时间 | 触发方式 | 状态 | 更新内容 |", "|---|---|---|---|"]
    for x in history[:50]:
        emoji = "✅" if x.get("status") == "success" else "❌"
        lines.append(f"| {x.get('finished_at','')} | {x.get('trigger','')} | {emoji} {x.get('status','')} | {x.get('summary','')} |")

    with open(HISTORY_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
