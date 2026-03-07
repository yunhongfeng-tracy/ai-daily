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
DOC_UPDATE_ITEMS="[]"

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
  SYSTEM_LOG_FILE="$LOG_FILE" \
  DOC_UPDATE_ITEMS="$DOC_UPDATE_ITEMS" \
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

# 构建“文档更新记录”内容（供前端模块展示）
DOC_UPDATE_ITEMS=$(python3 - <<'PY'
import os, json, re
from datetime import datetime
repo = '/root/.openclaw/workspace/ai-daily'
today = datetime.now().strftime('%Y-%m-%d')
items = []

md_path = os.path.join(repo, 'daily', f'{today}.md')
if os.path.exists(md_path):
    content = open(md_path, 'r', encoding='utf-8').read()
    m = re.search(r'^#\s+(.+)$', content, re.M)
    title = m.group(1).strip() if m else f'AI Daily {today}'
    snippet = ''
    for line in content.splitlines():
        s = line.strip()
        if s and not s.startswith('#') and not s.startswith('日期:') and s != '---':
            snippet = s[:80]
            break
    summary = f'{title}；{snippet}' if snippet else title
    items.append({'path': f'daily/{today}.md', 'summary': summary})

html_path = os.path.join(repo, 'daily', f'{today}.html')
if os.path.exists(html_path):
    items.append({'path': f'daily/{today}.html', 'summary': '当日日报页面已重新生成'})

index_path = os.path.join(repo, 'index.html')
if os.path.exists(index_path):
    items.append({'path': 'index.html', 'summary': '首页归档与日志模块已刷新'})

readme_path = os.path.join(repo, 'README.md')
if os.path.exists(readme_path):
    items.append({'path': 'README.md', 'summary': f'归档索引已包含 {today} 条目'})

print(json.dumps(items, ensure_ascii=False))
PY
)

DETAILS="日报与首页已刷新；可在 ai-daily/logs/update-history.md 查看记录"
finish_log
