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
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 40px 20px;
}
.container { max-width: 800px; margin: 0 auto; }
.logo {
    text-align: center;
    margin-bottom: 40px;
}
.logo h1 {
    font-size: 2.5rem;
    color: white;
    margin-bottom: 8px;
}
.logo p { color: rgba(255,255,255,0.8); font-size: 1rem; }

/* 归档列表 */
.archive-list {
    background: white;
    border-radius: 16px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    overflow: hidden;
}
.archive-item {
    display: block;
    padding: 20px 24px;
    text-decoration: none;
    color: inherit;
    border-bottom: 1px solid #eee;
    transition: background 0.2s;
}
.archive-item:last-child { border-bottom: none; }
.archive-item:hover { background: #f8f9ff; }
.archive-date {
    font-size: 0.85rem;
    color: #667eea;
    font-weight: 600;
    margin-bottom: 4px;
}
.archive-title {
    font-size: 1.1rem;
    color: #333;
    font-weight: 500;
}
.archive-arrow {
    float: right;
    color: #667eea;
    font-size: 1.2rem;
}
footer {
    text-align: center;
    margin-top: 40px;
    color: rgba(255,255,255,0.7);
    font-size: 0.9rem;
}

/* 当日页面样式 */
.day-page {
    background: white;
    border-radius: 16px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    overflow: hidden;
}
.day-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 30px;
    color: white;
}
.day-header h1 { font-size: 1.8rem; margin-bottom: 5px; }
.day-header .date { opacity: 0.8; }
.day-content { padding: 30px; }
.section-title {
    font-size: 1.2rem;
    color: #667eea;
    margin: 25px 0 15px;
    padding-bottom: 8px;
    border-bottom: 2px solid #667eea;
}
.card {
    background: #f8f9ff;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 15px;
}
.card h3 { font-size: 1rem; color: #333; margin-bottom: 8px; }
.card .source { font-size: 0.8rem; color: #667eea; margin-bottom: 8px; }
.card .source a { color: #667eea; text-decoration: none; }
.card p { font-size: 0.9rem; color: #666; line-height: 1.6; margin-bottom: 10px; }
.card .read-more {
    display: inline-block;
    font-size: 0.85rem;
    color: #667eea;
    text-decoration: none;
    font-weight: 500;
}
.tool-card {
    display: flex;
    align-items: center;
    background: #f8f9ff;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 12px;
}
.tool-info { flex: 1; }
.tool-name { font-size: 1rem; font-weight: 600; color: #333; margin-bottom: 4px; }
.tool-desc { font-size: 0.85rem; color: #666; }
.tool-link {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 8px 16px;
    border-radius: 8px;
    text-decoration: none;
    font-size: 0.85rem;
}
.back-link {
    display: inline-block;
    margin-bottom: 20px;
    color: white;
    text-decoration: none;
    font-size: 0.95rem;
}
.back-link:hover { text-decoration: underline; }
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
    date_match = re.search(r'^日期: (\d{4}-\d{2}-\d{2})$', content, re.MULTILINE)
    
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
        
        # 格式化日期显示
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            date_display = date_obj.strftime('%Y年%m月%d日')
        except:
            date_display = date
        
        items_html += f'''
<a href="./daily/{f.replace('.md', '.html')}" class="archive-item">
    <span class="archive-arrow">→</span>
    <div class="archive-date">{date_display}</div>
    <div class="archive-title">{title}</div>
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
            Powered by OpenClaw 🤗 | <a href="https://github.com/yunhongfeng-tracy/ai-daily" style="color:rgba(255,255,255,0.8);">GitHub</a>
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
    
    for f in files:
        title, date, content = parse_daily_file(f'daily/{f}')
        
        # 格式化日期
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            date_display = date_obj.strftime('%Y年%m月%d日')
        except:
            date_display = date
        
        html_content = convert_markdown(content)
        
        # 移除标题行（因为我们在header中显示）
        html_content = re.sub(r'^<h1>.*?</h1>', '', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^<p>日期:.*?</p>', '', html_content, flags=re.MULTILINE)
        
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
            Powered by OpenClaw 🤗 | <a href="https://github.com/yunhongfeng-tracy/ai-daily" style="color:rgba(255,255,255,0.8);">GitHub</a>
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
