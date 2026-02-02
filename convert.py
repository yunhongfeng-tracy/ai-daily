#!/usr/bin/env python3
"""
AI Daily - 简单美观的首页 + 每日归档生成器
"""

import os
import re
from datetime import datetime
from markdown import Markdown
import html

CSS = """
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f5f5f7;
    min-height: 100vh;
    padding: 40px 20px;
}
.container { max-width: 1100px; margin: 0 auto; }
.logo {
    text-align: center;
    margin-bottom: 30px;
}
.logo h1 {
    font-size: 2rem;
    color: #1d1d1f;
    font-weight: 700;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
}
.logo p { color: #86868b; font-size: 1rem; }

/* 归档列表 */
.archive-list {
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    overflow: hidden;
}
.archive-item {
    display: flex;
    align-items: center;
    padding: 18px 20px;
    text-decoration: none;
    color: inherit;
    border-bottom: 1px solid #f0f0f0;
    transition: all 0.2s ease;
}
.archive-item:last-child { border-bottom: none; }
.archive-item:hover { background: #fafafa; }
.archive-date {
    font-size: 0.8rem;
    color: #86868b;
    min-width: 90px;
}
.archive-title {
    flex: 1;
    font-size: 1rem;
    color: #1d1d1f;
    font-weight: 500;
}
.archive-arrow {
    color: #86868b;
    font-size: 1rem;
    transition: transform 0.2s;
}
.archive-item:hover .archive-arrow { transform: translateX(3px); color: #1d1d1f; }
footer {
    text-align: center;
    margin-top: 40px;
    color: #86868b;
    font-size: 0.85rem;
}

/* 当日页面样式 */
.day-page {
    background: white;
    border-radius: 20px;
    box-shadow: 0 4px 30px rgba(0,0,0,0.04);
    overflow: hidden;
    max-width: 100%;
    margin: 0 auto;
}
.day-header {
    background: #1d1d1f;
    padding: 40px;
    color: white;
}
.day-header h1 {
    font-size: 2.2rem;
    margin-bottom: 8px;
    font-weight: 700;
    letter-spacing: -0.5px;
}
.day-header .date {
    opacity: 0.6;
    font-size: 1rem;
}
.day-content { padding: 32px 40px; }

/* 新闻网格布局 */
.news-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-top: 20px;
}
@media (max-width: 768px) {
    .news-grid { grid-template-columns: 1fr; }
}
.section-title {
    font-size: 1.4rem;
    color: #1d1d1f;
    margin: 40px 0 24px;
    font-weight: 700;
    letter-spacing: -0.3px;
}

/* 新闻卡片 - Apple风格 */
.card {
    background: #fff;
    border-radius: 16px;
    padding: 0;
    border: 1px solid #e8e8ed;
    transition: all 0.25s ease;
    display: flex;
    flex-direction: column;
}
.card:hover {
    box-shadow: 0 12px 40px rgba(0,0,0,0.1);
    transform: translateY(-4px);
    border-color: transparent;
}
.card-content {
    padding: 24px;
    display: flex;
    flex-direction: column;
    flex: 1;
}
.card h3 {
    font-size: 1.1rem;
    color: #1d1d1f;
    margin-bottom: 10px;
    font-weight: 600;
    letter-spacing: -0.2px;
    line-height: 1.4;
}
.card .source {
    font-size: 0.8rem;
    color: #86868b;
    margin-bottom: 12px;
}
.card .source a {
    color: #0066cc;
    text-decoration: none;
}
.card .source a:hover { text-decoration: underline; }
.card p {
    font-size: 0.95rem;
    color: #515154;
    line-height: 1.6;
    margin-bottom: 16px;
    flex: 1;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.card .read-more {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.9rem;
    color: #0066cc;
    text-decoration: none;
    font-weight: 500;
    margin-top: auto;
}
.card .read-more:hover { text-decoration: underline; }

/* 工具卡片网格 */
.tools-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    margin-top: 20px;
}
@media (max-width: 600px) {
    .tools-grid { grid-template-columns: 1fr; }
}
.tool-card {
    background: #fff;
    border-radius: 16px;
    padding: 20px;
    border: 1px solid #e8e8ed;
    transition: all 0.25s ease;
    display: flex;
    flex-direction: column;
}
.tool-card:hover {
    box-shadow: 0 12px 40px rgba(0,0,0,0.1);
    transform: translateY(-4px);
    border-color: transparent;
}
.tool-header {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 12px;
}
.tool-icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    flex-shrink: 0;
}
.tool-icon.purple { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.tool-icon.blue { background: linear-gradient(135deg, #0066cc 0%, #5ac8fa 100%); }
.tool-icon.green { background: linear-gradient(135deg, #34c759 0%, #30d158 100%); }
.tool-icon.orange { background: linear-gradient(135deg, #ff9500 0%, #ff6b00 100%); }
.tool-icon.pink { background: linear-gradient(135deg, #ff2d55 0%, #ff6b9d 100%); }
.tool-icon.teal { background: linear-gradient(135deg, #5ac8fa 0%, #64d2ff 100%); }
.tool-info { flex: 1; min-width: 0; }
.tool-name {
    font-size: 1rem;
    font-weight: 600;
    color: #1d1d1f;
    margin-bottom: 4px;
    line-height: 1.3;
}
.tool-desc {
    font-size: 0.85rem;
    color: #6e6e73;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.tool-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    background: transparent;
    color: #0066cc;
    padding: 8px 16px;
    border-radius: 8px;
    border: 1.5px solid #0066cc;
    text-decoration: none;
    font-size: 0.85rem;
    font-weight: 500;
    margin-top: auto;
    transition: all 0.2s;
}
.tool-link:hover {
    background: #0066cc;
    color: white;
}
.back-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 24px;
    color: #515154;
    text-decoration: none;
    font-size: 0.95rem;
    transition: color 0.2s;
}
.back-link:hover { color: #1d1d1f; }
</style>
"""

def get_daily_files():
    """获取所有日报文件"""
    daily_dir = 'daily'
    if not os.path.exists(daily_dir):
        return []
    files = sorted([f for f in os.listdir(daily_dir) if f.endswith('.md')])
    return files

def parse_daily_file(filepath):
    """解析日报文件，提取标题和日期"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    date_match = re.search(r'^日期: (\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?)', content, re.MULTILINE)
    
    title = title_match.group(1) if title_match else 'AI Daily'
    date = date_match.group(1) if date_match else ''
    
    return title, date, content

def convert_markdown(content):
    """简单Markdown转HTML"""
    md = Markdown(extensions=['tables', 'fenced_code'])
    html_content = md.convert(content)
    return html_content

def generate_index_html():
    """生成首页"""
    files = get_daily_files()
    
    items_html = ''
    for f in files:
        date_str = f.replace('.md', '')
        title, date, _ = parse_daily_file(f'daily/{f}')
        
        # 格式化日期显示（精确到分钟）
        try:
            if ' ' in date and ':' in date:
                # 格式: 2026-02-02 09:30
                date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M')
                date_display = date_obj.strftime('%Y年%m月%d日 %H:%M')
            else:
                # 格式: 2026-02-02
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                date_display = date_obj.strftime('%Y年%m月%d日')
        except:
            date_display = date
        
        items_html += f'''
<a href="./daily/{f.replace('.md', '.html')}" class="archive-item">
    <div class="archive-date">{date_display}</div>
    <div class="archive-title">{title}</div>
    <span class="archive-arrow">→</span>
</a>'''
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Daily - 每日AI新闻与工具</title>
    {CSS}
</head>
<body>
    <a href="./index.html" class="back-link" style="display:none;">← 返回首页</a>
    <div class="container">
        <div class="logo">
            <h1>🤖 AI Daily</h1>
            <p>每日AI新闻与工具推荐精选</p>
        </div>
        
        <div class="archive-list">
            {items_html if items_html else '<div class="archive-item"><div class="archive-title" style="padding:20px;color:#666;">暂无日报内容</div></div>'}
        </div>
        
        <footer>
            Powered by OpenClaw 🤗 | <a href="https://github.com/yunhongfeng-tracy/ai-daily" style="color:#0066cc;">GitHub</a>
        </footer>
    </div>
</body>
</html>"""
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✓ 生成首页: index.html")

def generate_daily_pages():
    """生成每个日报页面"""
    files = get_daily_files()
    
    # 工具图标和颜色配置
    tool_config = {
        'v0': {'icon': '🎨', 'color': 'purple'},
        'cursor': {'icon': '💻', 'color': 'blue'},
        'perplexity': {'icon': '🔍', 'color': 'teal'},
        'langchain': {'icon': '⛓️', 'color': 'orange'},
        'hugging': {'icon': '🤗', 'color': 'pink'},
        'claude': {'icon': '🤖', 'color': 'orange'},
        'chatgpt': {'icon': '💬', 'color': 'green'},
        'midjourney': {'icon': '🎭', 'color': 'purple'},
        'notion': {'icon': '📝', 'color': 'blue'},
        'github': {'icon': '🐙', 'color': 'purple'},
        'default': {'icon': '🛠️', 'color': 'blue'}
    }

    def get_tool_config(name):
        name_lower = name.lower()
        for key, config in tool_config.items():
            if key in name_lower:
                return config
        return tool_config['default']
    
    for f in files:
        title, date, content = parse_daily_file(f'daily/{f}')
        
        # 格式化日期（精确到分钟）
        try:
            if ' ' in date and ':' in date:
                date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M')
                date_display = date_obj.strftime('%Y年%m月%d日 %H:%M')
            else:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                date_display = date_obj.strftime('%Y年%m月%d日')
        except:
            date_display = date
        
        html_content = convert_markdown(content)

        # 移除标题行和日期行（因为我们在header中显示）
        html_content = re.sub(r'^<h1>.*?</h1>', '', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^<p>日期:.*?</p>', '', html_content, flags=re.MULTILINE)

        # 处理新闻卡片
        news_cards = []
        def replace_news(match):
            title = match.group(1)
            source_link = match.group(2)
            source_name = match.group(3)
            source_date = match.group(4)
            summary = match.group(5)
            read_link = match.group(6)

            card = f'''<div class="card">
    <div class="card-content">
        <h3>{title}</h3>
        <div class="source"><a href="{source_link}">{source_name}</a> · {source_date}</div>
        <p>{summary}</p>
        <a href="{read_link}" class="read-more" target="_blank">阅读原文 →</a>
    </div>
</div>'''
            news_cards.append(card)
            return '<!--NEWS_PLACEHOLDER-->'

        # 转换新闻格式: <h3>标题</h3><p>来源: <a>...</a> · 日期</p><p>摘要</p><p><a>阅读原文</a></p>
        html_content = re.sub(
            r'<h3>([^<]+)</h3>\s*<p>来源:\s*<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>\s*·\s*([^<]+)</p>\s*<p>([^<]+)</p>\s*<p><a[^>]*href="([^"]*)"[^>]*>阅读原文</a></p>\s*(?:<hr\s*/?>)?',
            replace_news,
            html_content,
            flags=re.DOTALL
        )

        # 将新闻卡片包装在网格容器中
        if news_cards:
            news_grid = '<div class="news-grid">\n' + '\n'.join(news_cards) + '\n</div>'
            html_content = html_content.replace('<!--NEWS_PLACEHOLDER-->', news_grid, 1)
            html_content = html_content.replace('<!--NEWS_PLACEHOLDER-->', '')

        # 处理工具卡片 - 添加图标和颜色
        tool_cards = []
        def replace_tool(match):
            tool_name = match.group(1) if match.group(1) else ''
            tool_desc = match.group(2) if match.group(2) else ''
            tool_link = match.group(3) if match.group(3) else '#'
            config = get_tool_config(tool_name)

            card = f'''<div class="tool-card">
    <div class="tool-header">
        <div class="tool-icon {config['color']}">{config['icon']}</div>
        <div class="tool-info">
            <div class="tool-name">{tool_name}</div>
            <div class="tool-desc">{tool_desc}</div>
        </div>
    </div>
    <a href="{tool_link}" class="tool-link" target="_blank">访问 →</a>
</div>'''
            tool_cards.append(card)
            return '<!--TOOL_PLACEHOLDER-->'

        # 转换工具推荐格式: <h3>工具名</h3><p>📝 描述</p><p>🔗 <a>访问</a></p>
        html_content = re.sub(
            r'<h3>([^<]+)</h3>\s*<p>📝\s*([^<]+)</p>\s*<p>🔗\s*<a[^>]*href="([^"]*)"[^>]*>[^<]*</a></p>\s*(?:<hr\s*/?>)?',
            replace_tool,
            html_content,
            flags=re.DOTALL
        )

        # 将工具卡片包装在网格容器中
        if tool_cards:
            tools_grid = '<div class="tools-grid">\n' + '\n'.join(tool_cards) + '\n</div>'
            # 替换第一个占位符为网格，删除其余占位符
            html_content = html_content.replace('<!--TOOL_PLACEHOLDER-->', tools_grid, 1)
            html_content = html_content.replace('<!--TOOL_PLACEHOLDER-->', '')

        # 清理多余的 <hr> 标签
        html_content = re.sub(r'<hr\s*/?>', '', html_content)
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {CSS}
</head>
<body>
    <div class="container">
        <a href="../index.html" class="back-link">← 返回首页</a>
        
        <div class="day-page">
            <div class="day-header">
                <h1>{title}</h1>
                <p class="date">{date_display}</p>
            </div>
            <div class="day-content">
                {html_content}
            </div>
        </div>
        
        <footer>
            Powered by OpenClaw 🤗 | <a href="https://github.com/yunhongfeng-tracy/ai-daily" style="color:#0066cc;">GitHub</a>
        </footer>
    </div>
</body>
</html>"""
        
        os.makedirs('daily', exist_ok=True)
        with open(f'daily/{f.replace(".md", ".html")}', 'w', encoding='utf-8') as file:
            file.write(html)
        print(f"✓ 生成日报: daily/{f.replace('.md', '.html')}")

def main():
    print("🤖 AI Daily Generator\n")
    generate_index_html()
    generate_daily_pages()
    print("\n✨ 完成！")

if __name__ == '__main__':
    main()
