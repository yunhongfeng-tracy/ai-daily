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
.container { max-width: 800px; margin: 0 auto; }
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
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    overflow: hidden;
}
.day-header {
    background: #1d1d1f;
    padding: 30px;
    color: white;
}
.day-header h1 { 
    font-size: 1.6rem; 
    margin-bottom: 6px; 
    font-weight: 600;
}
.day-header .date { 
    opacity: 0.6; 
    font-size: 0.9rem;
}
.day-content { padding: 30px; }
.section-title {
    font-size: 1.1rem;
    color: #1d1d1f;
    margin: 28px 0 16px;
    padding-bottom: 10px;
    font-weight: 600;
    border-bottom: 2px solid #f0f0f0;
}
.card {
    background: #fafafa;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 14px;
    border: 1px solid #f0f0f0;
}
.card h3 { font-size: 1rem; color: #1d1d1f; margin-bottom: 8px; font-weight: 600; }
.card .source { font-size: 0.8rem; color: #86868b; margin-bottom: 8px; }
.card .source a { color: #0066cc; text-decoration: none; }
.card p { font-size: 0.9rem; color: #515154; line-height: 1.6; margin-bottom: 12px; }
.card .read-more {
    display: inline-block;
    font-size: 0.85rem;
    color: #0066cc;
    text-decoration: none;
    font-weight: 500;
}
.card .read-more:hover { text-decoration: underline; }
.tool-card {
    display: flex;
    align-items: center;
    background: #fafafa;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 12px;
    border: 1px solid #f0f0f0;
}
.tool-info { flex: 1; }
.tool-name { font-size: 1rem; font-weight: 600; color: #1d1d1f; margin-bottom: 3px; }
.tool-desc { font-size: 0.85rem; color: #515154; }
.tool-link {
    background: #1d1d1f;
    color: white;
    padding: 8px 16px;
    border-radius: 8px;
    text-decoration: none;
    font-size: 0.85rem;
    font-weight: 500;
    transition: background 0.2s;
}
.tool-link:hover { background: #424245; }
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
