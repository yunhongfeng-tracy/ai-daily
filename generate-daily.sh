#!/usr/bin/env bash
#
# AI Daily Generator
# 每日自动生成AI新闻和工具推荐
#

set -e

REPO_DIR="/root/.openclaw/workspace/ai-daily"
TODAY=$(date +%Y-%m-%d)
GITHUB_TOKEN="${GITHUB_TOKEN}"

echo "🤖 AI Daily Generator - ${TODAY}"

# 切换到工作目录
cd "$REPO_DIR"

# 1. 搜索AI新闻
echo "📰 搜索AI新闻..."
NEWS_RESULT=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
    "https://api.brave.com/v1/news?country=US&category=technology" 2>/dev/null || echo "")

# 使用web_search工具搜索（备用）
if [ -z "$NEWS_RESULT" ]; then
    echo "使用备用搜索..."
fi

# 2. 创建今日日报模板
TEMPLATE=$(cat <<EOF
# AI Daily · ${TODAY}

日期: ${TODAY}

## 📰 今日新闻

### 

来源: []() · 

[阅读原文]()

---

## 🛠️ 工具推荐

### 

📝 

🔗 [访问]()

---

## 📚 归档
EOF
)

echo "$TEMPLATE" > "daily/${TODAY}.md"
echo "✓ 创建日报模板: daily/${TODAY}.md"

# 3. 更新README归档
sed -i "/^- \[${TODAY}/d" README.md
sed -i "/^- \[20/a- [${TODAY}](./daily/${TODAY}.md)" README.md

echo "✓ 更新README归档"

# 4. 提交并推送
if [ -n "$GITHUB_TOKEN" ]; then
    git config user.name "tracy-bot"
    git config user.email "bot@tracy.ai"
    
    git add -A
    git status && git diff --stat
    
    if [ -n "$(git status --porcelain)" ]; then
        git commit -m "AI Daily: ${TODAY}"
        git push origin main
        echo "✓ 已推送到GitHub"
    else
        echo "✓ 无变更，跳过提交"
    fi
else
    echo "⚠️ 未设置GITHUB_TOKEN，请手动推送"
fi

echo "✨ 完成！"
