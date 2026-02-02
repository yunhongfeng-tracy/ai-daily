#!/usr/bin/env python3
"""
AI Daily Generator - 自动生成每日AI新闻和工具推荐
"""

import os
import re
import json
import subprocess
import urllib.request
from datetime import datetime
from urllib.parse import urlparse

# 配置
REPO_DIR = "/root/.openclaw/workspace/ai-daily"
TODAY = datetime.now().strftime('%Y-%m-%d')
NOW = datetime.now().strftime('%Y-%m-%d %H:%M')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'sk-7bc8f2dcf1734756bd81c55af2413f80')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

# DeepSeek翻译函数
def translate_with_deepseek(text):
    """使用DeepSeek API翻译为中文"""
    if not text or len(text.strip()) < 5:
        return text
    
    # 简单术语直接查词典（快速）
    simple_trans = {
        'AI': '人工智能',
        'Artificial Intelligence': '人工智能',
        'Machine Learning': '机器学习',
        'Deep Learning': '深度学习',
        'LLM': '大语言模型',
        'OpenAI': 'OpenAI',
        'Anthropic': 'Anthropic',
        'Google': '谷歌',
        'Microsoft': '微软',
        'Reuters': '路透社',
        'BBC': 'BBC',
        'MIT': '麻省理工',
        'TechCrunch': 'TechCrunch',
        'NVIDIA': '英伟达',
        'Meta': 'Meta',
        'Amazon': '亚马逊',
        'Apple': '苹果',
    }
    
    # 先做简单替换
    result = text
    for eng, chi in simple_trans.items():
        result = re.sub(r'\b' + re.escape(eng) + r'\b', chi, result, flags=re.IGNORECASE)
    
    # 如果包含复杂句子，用DeepSeek翻译
    if len(text) > 30 and not text.startswith('http'):
        try:
            url = "https://api.deepseek.com/chat/completions"
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的AI科技新闻翻译。请将英文翻译成简洁的中文，保留专业术语的准确性。只需输出翻译结果，不要其他内容。"
                    },
                    {
                        "role": "user",
                        "content": f"翻译这段英文新闻标题和摘要：\n\n{text}"
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.3
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, method='POST')
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', f'Bearer {DEEPSEEK_API_KEY}')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result_data = json.loads(response.read().decode('utf-8'))
                translated = result_data['choices'][0]['message']['content'].strip()
                # 清理可能的引号
                translated = re.sub(r'^["\']|["\']$', '', translated)
                return translated
        except Exception as e:
            print(f"  翻译API调用失败: {e}")
            return result
    
    return result

def clean_text(text):
    """清理文本"""
    if not text:
        return ''
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 替换HTML实体
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&#x27;', "'").replace('&#39;', "'").replace('&quot;', '"')
    text = text.replace('&ldquo;', '"').replace('&rdquo;', '"').replace('&lsquo;', "'").replace('&rsquo;', "'")
    # 移除多余空格和换行
    text = re.sub(r'\s+', ' ', text).strip()
    # 移除推广信息
    text = re.sub(r'Subscribe.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Register.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Login.*', '', text, flags=re.IGNORECASE)
    return text.strip()

def get_source_name(url):
    """从URL提取来源"""
    if not url:
        return '未知来源'
    try:
        parsed = urlparse(url)
        source = parsed.netloc.replace('www.', '').split('/')[0]
        # 常见来源映射
        source_map = {
            'reuters.com': '路透社',
            'bbc.com': 'BBC',
            'techcrunch.com': 'TechCrunch',
            'mit.edu': '麻省理工',
            'theverge.com': 'The Verge',
            'wired.com': 'Wired',
            'artificialintelligence-news.com': 'AI新闻',
        }
        for eng, chi in source_map.items():
            if eng in source:
                return chi
        return source.split('.')[0].title()
    except:
        return '未知来源'

def search_news():
    """搜索AI新闻"""
    print(f"🤖 AI Daily Generator - {TODAY}")
    print("📰 搜索AI新闻...")
    
    BRAVE_API_KEY = os.environ.get('BRAVE_API_KEY', 'BSABJykguZY7fMv9-C0etQUd4zEs1Yt')
    url = f"https://api.search.brave.com/res/v1/web/search?q=AI+artificial+intelligence+news+today&count=8"
    req = urllib.request.Request(url, headers={
        'Accept': 'application/json',
        'X-Subscription-Token': BRAVE_API_KEY
    })
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except Exception as e:
        print(f"搜索失败: {e}")
        return None

def generate_daily():
    """生成日报"""
    data = search_news()
    
    md_file = os.path.join(REPO_DIR, 'daily', f'{TODAY}.md')
    
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# AI Daily · {TODAY}\n\n")
        f.write(f"日期: {TODAY} {datetime.now().strftime('%H:%M')}\n\n")
        
        # 今日新闻
        f.write("## 📰 今日新闻\n\n")
        
        if data and 'web' in data:
            for item in data.get('web', {}).get('results', [])[:5]:
                title = clean_text(item.get('title', ''))
                url = item.get('url', '')
                desc = clean_text(item.get('description', ''))
                
                if title and url:
                    # 使用DeepSeek翻译标题
                    title_cn = translate_with_deepseek(title)
                    
                    source = get_source_name(url)
                    
                    f.write(f"### {title_cn}\n\n")
                    f.write(f"来源: [{source}]({url})\n\n")
                    if desc:
                        # 使用DeepSeek翻译描述
                        desc_cn = translate_with_deepseek(desc)
                        f.write(f"{desc_cn}\n\n")
                    f.write(f"[阅读原文]({url})\n\n")
                    f.write("---\n\n")
        
        # 工具推荐
        f.write("## 🛠️ 工具推荐\n\n")
        tools = [
            ("v0.dev - AI UI生成器", "由Vercel推出的AI界面生成器，只需描述需求即可自动生成React/Tailwind组件。", "https://v0.app"),
            ("Cursor - AI代码编辑器", "专为AI辅助编程设计的IDE，基于VS Code，支持智能代码补全和重构建议。", "https://cursor.com"),
            ("Perplexity - AI搜索引擎", "结合大语言模型的搜索引擎，提供带有引用来源的答案，支持多种语言。", "https://www.perplexity.ai"),
        ]
        
        for name, desc, link in tools:
            f.write(f"### {name}\n\n")
            f.write(f"📝 {desc}\n\n")
            f.write(f"🔗 [访问]({link})\n\n")
            f.write("---\n\n")
        
        # 归档
        f.write("## 📚 归档\n")
        f.write(f"- [{TODAY}](./{TODAY}.html)\n")
    
    print(f"✓ 创建日报: {md_file}")
    
    # 更新README
    readme_file = os.path.join(REPO_DIR, 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除旧条目，添加新条目
        content = re.sub(r'- \[{}\].*\n'.format(TODAY), '', content)
        content = re.sub(r'(\n## 📚 归档)', f'\n- [{TODAY}](./daily/{TODAY}.md)\n\\1', content)
        
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✓ 更新README")
    
    return md_file

def generate_html():
    """生成HTML"""
    print("🔄 生成HTML页面...")
    convert_script = os.path.join(REPO_DIR, 'convert.py')
    result = subprocess.run(['python3', convert_script], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ 生成HTML页面")
    else:
        print(f"✗ HTML生成失败: {result.stderr}")

def commit_and_push():
    """提交并推送"""
    print("📤 推送到GitHub...")
    
    # 设置remote
    if GITHUB_TOKEN:
        remote_url = f"https://{GITHUB_TOKEN}@github.com/yunhongfeng-tracy/ai-daily.git"
        subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url], cwd=REPO_DIR, capture_output=True)
    
    # 配置git
    subprocess.run(['git', 'config', 'user.name', 'tracy-bot'], cwd=REPO_DIR, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'bot@tracy.ai'], cwd=REPO_DIR, capture_output=True)
    
    # 添加并提交
    subprocess.run(['git', 'add', '-A'], cwd=REPO_DIR, capture_output=True)
    result = subprocess.run(['git', 'status', '--porcelain'], cwd=REPO_DIR, capture_output=True, text=True)
    
    if result.stdout.strip():
        subprocess.run(['git', 'commit', '-m', f'AI Daily: {TODAY}'], cwd=REPO_DIR, capture_output=True)
        if GITHUB_TOKEN:
            subprocess.run(['git', 'push', 'origin', 'main'], cwd=REPO_DIR, capture_output=True)
            print("✓ 已推送到GitHub")
    else:
        print("✓ 无新内容，跳过提交")

def main():
    print("=" * 40)
    md_file = generate_daily()
    generate_html()
    commit_and_push()
    print("=" * 40)
    print(f"🎉 AI日报生成完成！")
    print(f"📅 日期: {TODAY}")

if __name__ == '__main__':
    main()
