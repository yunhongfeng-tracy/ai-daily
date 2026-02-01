#!/usr/bin/env bash
#
# AI Daily Generator
# 每日自动生成AI新闻和工具推荐
#

set -e

REPO_DIR="/root/.openclaw/workspace/ai-daily"
TODAY=$(date +%Y-%m-%d)
BRAVE_API_KEY="${BRAVE_API_KEY}"
GITHUB_TOKEN="${GITHUB_TOKEN}"

echo "🤖 AI Daily Generator - ${TODAY}"
cd "$REPO_DIR"

# 1. 搜索AI新闻
echo "📰 搜索AI新闻..."
NEWS_JSON=$(curl -s "https://api.search.brave.com/res/v1/web/search?q=AI+artificial+intelligence+news+today&count=8" \
    -H "Accept: application/json" \
    -H "X-Subscription-Token: $BRAVE_API_KEY" 2>/dev/null || echo "")

# 2. 生成日报内容
cat > "daily/${TODAY}.md" << 'HEADER'
# AI Daily · DATE

日期: DATE

HEADER

# 添加新闻部分
echo "## 📰 今日新闻" >> "daily/${TODAY}.md"

# 解析新闻并添加（简化版：使用搜索结果标题和链接）
if [ -n "$NEWS_JSON" ]; then
    echo "$NEWS_JSON" | python3 -c "
import sys, json, re
try:
    d = json.load(sys.stdin)
    for r in d.get('web', {}).get('results', [])[:5]:
        title = r.get('title', '')[:50]
        url = r.get('url', '')
        desc = r.get('description', '')[:100] if r.get('description') else ''
        source = r.get('display_url', '').replace('https://', '').split('/')[0]
        print(f'''
### {title}

来源: [{source}]({url})

{desc}

[阅读原文]({url})

---''')
except: pass
" >> "daily/${TODAY}.md"
fi

# 添加工具推荐（复用之前的工具）
echo "## 🛠️ 工具推荐" >> "daily/${TODAY}.md"
cat >> "daily/${TODAY}.md" << 'TOOLS'

### v0.dev - AI UI生成器

📝 由Vercel推出的AI界面生成器，只需描述需求即可自动生成React/Tailwind组件。

🔗 [访问](https://v0.app)

---

### Cursor - AI代码编辑器

📝 专为AI辅助编程设计的IDE，基于VS Code，支持智能代码补全和重构建议。

🔗 [访问](https://cursor.com)

---

### Perplexity - AI搜索引擎

📝 结合大语言模型的搜索引擎，提供带有引用来源的答案，支持多种语言。

🔗 [访问](https://www.perplexity.ai)

---

TOOLS

# 添加归档
echo "## 📚 归档" >> "daily/${TODAY}.md"
echo "- [${TODAY}](./${TODAY}.html)" >> "daily/${TODAY}.md"

# 替换日期占位符
sed -i "s/DATE/$TODAY/g" "daily/${TODAY}.md"

echo "✓ 创建日报: daily/${TODAY}.md"

# 3. 更新README归档
sed -i "/^- \[$TODAY/d" README.md
sed -i "/^- \[20/a- [${TODAY}](./daily/${TODAY}.md)" README.md
echo "✓ 更新README"

# 4. 生成HTML
python3 convert.py
echo "✓ 生成HTML页面"

# 5. 提交并推送
if [ -n "$GITHUB_TOKEN" ]; then
    git config user.name "tracy-bot"
    git config user.email "bot@tracy.ai"
    
    git add -A
    git status
    
    if [ -n "$(git status --porcelain)" ]; then
        git commit -m "AI Daily: ${TODAY}"
        git push origin main
        echo "✓ 已推送到GitHub"
    else
        echo "✓ 无变更，跳过提交"
    fi
else
    echo "⚠️ 未设置GITHUB_TOKEN"
fi

echo ""
echo "🎉 AI日报生成完成！"
echo "📅 日期: $TODAY"
