#!/bin/bash
#
# AI Daily Cron 测试脚本
# 测试定时任务是否正常工作
#

set -e

LOG_FILE="/tmp/ai-daily-cron.log"
REPO_DIR="/root/.openclaw/workspace/ai-daily"
TODAY=$(date +%Y-%m-%d)

# 记录日志
echo "=== $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"
echo "工作目录: $REPO_DIR" >> "$LOG_FILE"

# 进入目录
cd "$REPO_DIR"

# Load secrets (cron has a minimal env)
source /root/.openclaw/workspace/.secrets/credentials.env
export DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:?missing DEEPSEEK_API_KEY}"
export BRAVE_API_KEY="${BRAVE_API_KEY:?missing BRAVE_API_KEY}"
export GITHUB_TOKEN="${GITHUB_TOKEN:?missing GITHUB_TOKEN}"

# 只记录是否存在，不写入任何前缀/片段
echo "环境变量检查:" >> "$LOG_FILE"
echo "  DEEPSEEK_API_KEY: [set]" >> "$LOG_FILE"
echo "  BRAVE_API_KEY: [set]" >> "$LOG_FILE"
echo "  GITHUB_TOKEN: [set]" >> "$LOG_FILE"

# 运行Python脚本
echo "运行 generate-daily.py..." >> "$LOG_FILE"
python3 generate-daily.py >> "$LOG_FILE" 2>&1

echo "完成! 日志: $LOG_FILE" >> "$LOG_FILE"
echo "=== 结束 ===" >> "$LOG_FILE"
