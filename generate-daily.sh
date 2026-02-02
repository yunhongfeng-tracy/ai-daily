#!/usr/bin/env bash
#
# AI Daily Generator - 自动生成每日AI新闻和工具推荐
#

set -e

REPO_DIR="/root/.openclaw/workspace/ai-daily"
TODAY=$(date +%Y-%m-%d)
# Token配置（cron环境变量可能不生效，使用默认值）
BRAVE_API_KEY="${BRAVE_API_KEY:-BSABJykguZY7fMv9-C0etQUd4zEs1Yt}"
GITHUB_TOKEN="${GITHUB_TOKEN:-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}"

echo "🤖 AI Daily Generator - ${TODAY}"
cd "$REPO_DIR"

# 1. 搜索AI新闻
echo "📰 搜索AI新闻..."
SEARCH_JSON=$(curl -s "https://api.search.brave.com/res/v1/web/search?q=AI+artificial+intelligence+news+today&count=10" \
    -H "Accept: application/json" \
    -H "X-Subscription-Token: $BRAVE_API_KEY" 2>/dev/null || echo "")

# 2. 构建新闻卡片
build_news_card() {
    local title="$1"
    local url="$2"
    local desc="$3"
    local source="$4"
    
    # 清理描述（限制长度）
    desc=$(echo "$desc" | sed 's/<[^>]*>//g' | sed 's/&[^;]*;//g' | xargs -I {} echo "{}" | head -c 150)
    [[ ${#desc} -ge 150 ]] && desc="${desc}..."
    
    cat << EOF

### $title

来源: [$source]($url)

$desc

[阅读原文]($url)

---
EOF
}

# 3. 生成日报
echo "📝 生成日报..."

cat > "daily/${TODAY}.md" << EOF
# AI Daily · $TODAY

日期: $TODAY

## 📰 今日新闻

EOF

# 解析搜索结果并生成新闻卡片
if [ -n "$SEARCH_JSON" ]; then
    # 使用Python解析JSON更可靠
    echo "$SEARCH_JSON" | python3 -c "
import sys, json, re

def clean_text(text):
    if not text:
        return ''
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 替换HTML实体
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return text.strip()

try:
    data = json.load(sys.stdin)
    results = data.get('web', {}).get('results', [])[:5]
    
    for r in results:
        title = clean_text(r.get('title', ''))
        url = r.get('url', '')
        desc = clean_text(r.get('description', ''))
        
        # 提取来源域名
        source = '未知来源'
        if url:
            from urllib.parse import urlparse
            source = urlparse(url).netloc
            source = source.replace('www.', '').split('/')[0]
        
        # 清理标题中的特殊字符
        title = re.sub(r'^[^a-zA-Z0-9]*', '', title)
        
        if title and url:
            print()
            print(f'### {title}')
            print(f'Source: [{source}]({url})')
            print()
            if desc:
                print(f'{desc[:150]}...' if len(desc) > 150 else desc)
            print()
            print(f'[阅读原文]({url})')
            print()
            print('---')
            
except Exception as e:
    print(f'# 解析失败，使用备用方案', file=sys.stderr)
" >> "daily/${TODAY}.md"
fi

# 如果没有搜索到结果，使用备用内容
if ! grep -q "### " "daily/${TODAY}.md" 2>/dev/null; then
    cat >> "daily/${TODAY}.md" << 'EOF'
### AI行业动态

来源: [综合报道]()

今日暂无具体新闻更新，请关注AI领域的最新发展。

[阅读原文]()

---
EOF
fi

# 4. 添加工具推荐
cat >> "daily/${TODAY}.md" << 'EOF'
## 🛠️ 工具推荐

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

EOF

# 5. 添加归档
echo "## 📚 归档" >> "daily/${TODAY}.md"
echo "- [$TODAY](./$TODAY.html)" >> "daily/${TODAY}.md"

echo "✓ 创建日报: daily/${TODAY}.md"

# 6. 更新README归档
if ! grep -q "$TODAY" README.md 2>/dev/null; then
    sed -i "/^- \[$TODAY/d" README.md
    sed -i "/^- \[20/a- [$TODAY](./daily/${TODAY}.md)" README.md
    echo "✓ 更新README"
fi

# 7. 生成HTML
python3 convert.py
echo "✓ 生成HTML页面"

# 8. 设置Git远程（使用token）
GIT_TOKEN="${GITHUB_TOKEN}"
if [ -n "$GIT_TOKEN" ]; then
    # 更新remote URL以包含token
    git remote set-url origin "https://${GIT_TOKEN}@github.com/yunhongfeng-tracy/ai-daily.git" 2>/dev/null || \
    git remote add origin "https://${GIT_TOKEN}@github.com/yunhongfeng-tracy/ai-daily.git"
    
    git config user.name "tracy-bot" 2>/dev/null || true
    git config user.email "bot@tracy.ai" 2>/dev/null || true
    
    git add -A
    
    if [ -n "$(git status --porcelain)" ]; then
        git commit -m "AI Daily: $TODAY"
        git push origin main
        echo "✓ 已推送到GitHub"
    else
        echo "✓ 无新内容，跳过提交"
    fi
else
    echo "⚠️ 未设置GITHUB_TOKEN，跳过推送"
fi

echo ""
echo "🎉 AI日报生成完成！"
echo "📅 日期: $TODAY"
