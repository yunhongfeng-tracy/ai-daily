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

# 设置环境变量（确保cron能读取）
export DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-sk-7bc8f2dcf1734756bd81c55af2413f80}"
export BRAVE_API_KEY="${BRAVE_API_KEY:-BSABJykguZY7fMv9-C0etQUd4zEs1Yt}"
export GITHUB_TOKEN="${GITHUB_TOKEN:-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}"

echo "环境变量检查:" >> "$LOG_FILE"
echo "  DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY:0:10}..." >> "$LOG_FILE"
echo "  BRAVE_API_KEY: ${BRAVE_API_KEY:0:10}..." >> "$LOG_FILE"
echo "  GITHUB_TOKEN: ${GITHUB_TOKEN:0:10}..." >> "$LOG_FILE"

# 运行Python脚本
echo "运行 generate-daily.py..." >> "$LOG_FILE"
python3 generate-daily.py >> "$LOG_FILE" 2>&1

echo "完成! 日志: $LOG_FILE" >> "$LOG_FILE"
echo "=== 结束 ===" >> "$LOG_FILE"
