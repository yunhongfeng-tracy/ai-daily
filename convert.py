#!/usr/bin/env python3
"""
AI Daily - Markdown to HTML Converter
卡片式风格，支持新闻和工具推荐
"""

import os
import re
from datetime import datetime
from markdown import Markdown
from bs4 import BeautifulSoup

# 样式配置
CSS_STYLE = """
<style>
:root {
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --bg: #f8fafc;
    --card-bg: #ffffff;
    --text: #1e293b;
    --text-light: #64748b;
    --border: #e2e8f0;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    padding: 2rem;
}

.container { max-width: 900px; margin: 0 auto; }

header {
    text-align: center;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 2px solid var(--primary);
}

header h1 {
    font-size: 2rem;
    color: var(--primary);
    margin-bottom: 0.5rem;
}

header .date { color: var(--text-light); }

.section-title {
    font-size: 1.25rem;
    color: var(--text);
    margin: 2rem 0 1rem;
    padding-left: 0.5rem;
    border-left: 4px solid var(--primary);
}

/* 卡片网格 */
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.card h3 {
    font-size: 1rem;
    margin-bottom: 0.5rem;
    color: var(--text);
}

.card .source {
    font-size: 0.75rem;
    color: var(--text-light);
    margin-bottom: 0.5rem;
}

.card .source a {
    color: var(--primary);
    text-decoration: none;
}

.card .source a:hover { text-decoration: underline; }

.card p {
    font-size: 0.875rem;
    color: var(--text-light);
    margin-bottom: 0.75rem;
}

.card .read-more {
    display: inline-block;
    font-size: 0.875rem;
    color: var(--primary);
    text-decoration: none;
    font-weight: 500;
}

.card .read-more:hover { color: var(--primary-dark); }

/* 工具推荐样式 */
.tool-card {
    display: flex;
    flex-direction: column;
}

.tool-card .tool-icon {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

.tool-card .tool-desc {
    flex-grow: 1;
    margin-bottom: 0.75rem;
}

.tool-card .tool-link {
    display: inline-block;
    background: var(--primary);
    color: white;
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    font-size: 0.875rem;
    text-decoration: none;
    text-align: center;
}

.tool-card .tool-link:hover {
    background: var(--primary-dark);
}

/* 归档链接 */
.archive-link {
    display: block;
    padding: 0.75rem 1rem;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 0.5rem;
    text-decoration: none;
    color: var(--text);
    transition: background 0.2s;
}

.archive-link:hover {
    background: var(--border);
    border-color: var(--primary);
}

footer {
    margin-top: 3rem;
    text-align: center;
    color: var(--text-light);
    font-size: 0.875rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
}
</style>
"""

def extract_daily_content(md_content):
    """从Markdown提取新闻和工具"""
    news = []
    tools = []
    
    lines = md_content.split('\n')
    current_section = None
    
    for line in lines:
        if line.startswith('## 新闻') or line.startswith('## 📰'):
            current_section = 'news'
        elif line.startswith('## 工具') or line.startswith('## 🛠️'):
            current_section = 'tools'
        elif line.startswith('### '):
            title = line.replace('### ', '').strip()
            # 获取下一行的描述
            # 这里简化处理，实际需要更复杂的解析
            if current_section == 'news':
                news.append({'title': title})
            elif current_section == 'tools':
                tools.append({'title': title})
    
    return news, tools

def convert_markdown_to_html(md_file, output_file):
    """将Markdown转换为HTML"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析元数据
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else 'AI Daily'
    
    date_match = re.search(r'^日期: (\d{4}-\d{2}-\d{2})', content)
    date = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
    
    # 转换为HTML
    md = Markdown(extensions=['tables', 'fenced_code'])
    html_body = md.convert(content)
    
    # 生成完整HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {CSS_STYLE}
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 AI Daily</h1>
            <p class="date">{date}</p>
        </header>
        <main>
            {html_body}
        </main>
        <footer>
            <p>Powered by OpenClaw 🤗 | <a href="https://github.com/yunhongfeng-tracy/ai-daily">GitHub</a></p>
        </footer>
    </div>
</body>
</html>"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Generated: {output_file}")

def main():
    """主函数：转换所有Markdown文件"""
    daily_dir = 'daily'
    output_dir = '.'
    
    # 查找最新的日报
    md_files = sorted([f for f in os.listdir(daily_dir) if f.endswith('.md')])
    
    if not md_files:
        print("No daily files found!")
        return
    
    latest_md = os.path.join(daily_dir, md_files[-1])
    latest_html = os.path.join(output_dir, 'index.html')
    
    # 转换最新日报
    convert_markdown_to_html(latest_md, latest_html)
    
    # 转换所有历史日报（用于归档）
    for md_file in md_files:
        html_file = os.path.join(output_dir, 'daily', md_file.replace('.md', '.html'))
        os.makedirs(os.path.dirname(html_file), exist_ok=True)
        convert_markdown_to_html(os.path.join(daily_dir, md_file), html_file)

if __name__ == '__main__':
    main()
