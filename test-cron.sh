#!/bin/bash
# AI Daily Cron 任务（支持 cron/manual 触发）

set -e

LOG_FILE="/tmp/ai-daily-cron.log"
REPO_DIR="/root/.openclaw/workspace/ai-daily"
TODAY=$(date +%Y-%m-%d)
RUN_ID=$(date +%Y%m%dT%H%M%S%z)
TRIGGER=${UPDATE_TRIGGER:-cron}
STARTED_AT=$(date -Iseconds)
STATUS="success"
SUMMARY="生成 AI Daily (${TODAY})"
DETAILS=""

# 记录日志
{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="
  echo "触发方式: $TRIGGER"
  echo "RUN_ID: $RUN_ID"
  echo "工作目录: $REPO_DIR"
} >> "$LOG_FILE"

finish_log() {
  local finished_at
  finished_at=$(date -Iseconds)
  UPDATE_RUN_ID="$RUN_ID" \
  UPDATE_TRIGGER="$TRIGGER" \
  UPDATE_STATUS="$STATUS" \
  UPDATE_STARTED_AT="$STARTED_AT" \
  UPDATE_FINISHED_AT="$finished_at" \
  UPDATE_SUMMARY="$SUMMARY" \
  UPDATE_DETAILS="$DETAILS" \
  python3 "$REPO_DIR/update_log.py" >> "$LOG_FILE" 2>&1 || true

  # 更新首页里的“更新日志”模块
  cd "$REPO_DIR"
  python3 convert.py >> "$LOG_FILE" 2>&1 || true

  {
    echo "状态: $STATUS"
    [ -n "$DETAILS" ] && echo "详情: $DETAILS"
    echo "=== 结束 ==="
  } >> "$LOG_FILE"
}

trap 'STATUS="failed"; DETAILS="脚本异常退出（line:$LINENO）"; finish_log' ERR

cd "$REPO_DIR"

# Load secrets (cron has a minimal env)
source /root/.openclaw/workspace/.secrets/credentials.env
export DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:?missing DEEPSEEK_API_KEY}"
export BRAVE_API_KEY="${BRAVE_API_KEY:?missing BRAVE_API_KEY}"
export GITHUB_TOKEN="${GITHUB_TOKEN:?missing GITHUB_TOKEN}"

echo "环境变量检查: [ok]" >> "$LOG_FILE"

# 运行生成
python3 generate-daily.py >> "$LOG_FILE" 2>&1

DETAILS="日报与首页已刷新；可在 ai-daily/logs/update-history.md 查看记录"
finish_log
