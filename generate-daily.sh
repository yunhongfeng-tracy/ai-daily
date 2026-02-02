#!/usr/bin/env bash
#
# AI Daily Generator - 自动生成每日AI新闻和工具推荐
#

set -e

REPO_DIR="/root/.openclaw/workspace/ai-daily"
TODAY=$(date +%Y-%m-%d)
NOW_TIME=$(date +%H:%M)
BRAVE_API_KEY="${BRAVE_API_KEY:-BSABJykguZY7fMv9-C0etQUd4zEs1Yt}"
GITHUB_TOKEN="${GITHUB_TOKEN}"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"

echo "🤖 AI Daily Generator - ${TODAY} ${NOW_TIME}"
cd "$REPO_DIR"

# 读取源配置
SOURCES_FILE="sources.json"
if [ -f "$SOURCES_FILE" ]; then
    echo "📋 读取配置文件..."
fi

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
发布时间: $NOW_TIME

## 📰 今日新闻

EOF

# 解析搜索结果并生成新闻卡片（带翻译和概述）
if [ -n "$SEARCH_JSON" ]; then
    # 使用Python解析JSON，带有翻译和概述功能
    echo "$SEARCH_JSON" | python3 -c "
import sys, json, re, os
import urllib.request
import urllib.parse

def clean_text(text):
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return text.strip()

def translate_and_summarize(title, desc, api_key=None):
    '''使用AI翻译标题并生成概述'''
    # 如果有Anthropic API，使用Claude
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '')
    openai_key = os.environ.get('OPENAI_API_KEY', '')

    if anthropic_key:
        try:
            import json as json_lib
            url = 'https://api.anthropic.com/v1/messages'
            prompt = f'''请将以下英文标题翻译为中文，并根据描述写一个简短的中文概述（30-50字）。
标题: {title}
描述: {desc}

请只返回JSON格式：{{\"title_zh\": \"中文标题\", \"summary\": \"中文概述\"}}'''

            data = json_lib.dumps({
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 200,
                'messages': [{'role': 'user', 'content': prompt}]
            }).encode('utf-8')

            req = urllib.request.Request(url, data=data, headers={
                'Content-Type': 'application/json',
                'x-api-key': anthropic_key,
                'anthropic-version': '2023-06-01'
            })

            with urllib.request.urlopen(req, timeout=10) as response:
                result = json_lib.loads(response.read().decode('utf-8'))
                content = result.get('content', [{}])[0].get('text', '{}')
                parsed = json_lib.loads(content)
                return parsed.get('title_zh', title), parsed.get('summary', desc[:100])
        except Exception as e:
            pass

    if openai_key:
        try:
            import json as json_lib
            url = 'https://api.openai.com/v1/chat/completions'
            prompt = f'''将英文标题翻译为中文，并写简短中文概述（30-50字）。
标题: {title}
描述: {desc}

返回JSON: {{\"title_zh\": \"中文标题\", \"summary\": \"中文概述\"}}'''

            data = json_lib.dumps({
                'model': 'gpt-3.5-turbo',
                'max_tokens': 200,
                'messages': [{'role': 'user', 'content': prompt}]
            }).encode('utf-8')

            req = urllib.request.Request(url, data=data, headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {openai_key}'
            })

            with urllib.request.urlopen(req, timeout=10) as response:
                result = json_lib.loads(response.read().decode('utf-8'))
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
                parsed = json_lib.loads(content)
                return parsed.get('title_zh', title), parsed.get('summary', desc[:100])
        except:
            pass

    # 无API时的简单处理：保持原标题，截取描述作为概述
    return title, desc[:100] + '...' if len(desc) > 100 else desc

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

        # 清理标题
        title = re.sub(r'^[^a-zA-Z0-9\u4e00-\u9fff]*', '', title)

        if title and url:
            # 翻译并生成概述
            title_zh, summary = translate_and_summarize(title, desc)

            print()
            print(f'### {title_zh}')
            print(f'原标题: {title}')
            print(f'来源: [{source}]({url})')
            print()
            print(f'> {summary}')
            print()
            print(f'[阅读原文]({url})')
            print()
            print('---')

except Exception as e:
    print(f'# 解析失败: {e}', file=sys.stderr)
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
