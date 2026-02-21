#!/usr/bin/env python3
"""
AI Daily Generator - 自动生成每日AI新闻和工具推荐
"""

import os
import re
import json
import subprocess
import time
import urllib.request
import urllib.parse
from datetime import datetime
from urllib.parse import urlparse

# 配置
REPO_DIR = "/root/.openclaw/workspace/ai-daily"
TODAY = datetime.now().strftime('%Y-%m-%d')
NOW = datetime.now().strftime('%Y-%m-%d %H:%M')
def _load_env_from_secrets():
    p = "/root/.openclaw/workspace/.secrets/credentials.env"
    try:
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or not line.startswith("export "):
                    continue
                k, v = line[len("export "):].split("=", 1)
                v = v.strip().strip("'\"")
                os.environ.setdefault(k.strip(), v)
    except Exception:
        pass

_load_env_from_secrets()

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
if not DEEPSEEK_API_KEY:
    print("⚠️ DEEPSEEK_API_KEY not set; translations may fail")


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

def _parse_iso_dt(s: str):
    if not s:
        return None
    try:
        # Brave returns ISO timestamps like 2026-02-20T05:39:45
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _is_reputable_source(url: str) -> bool:
    """Very conservative allowlist for '有效新闻' quality."""
    if not url:
        return False
    host = urlparse(url).netloc.lower().replace("www.", "")

    # hard deny
    if host.endswith("wikipedia.org"):
        return False

    allow = {
        # mainstream tech/business
        "reuters.com",
        "bloomberg.com",
        "ft.com",
        "wsj.com",
        "cnbc.com",
        "axios.com",
        "theverge.com",
        "arstechnica.com",
        "wired.com",
        "techcrunch.com",
        "venturebeat.com",
        "spectrum.ieee.org",
        "sfchronicle.com",
        "pcmag.com",
        "bbc.com",
        "theguardian.com",
        "nytimes.com",
        "washingtonpost.com",
        "economist.com",
        "forbes.com",
        # science
        "nature.com",
        "science.org",
        "mit.edu",
        # vendor / labs / official
        "openai.com",
        "anthropic.com",
        "deepmind.google",
        "blog.google",
        "ai.google.dev",
        "cloud.google.com",
        "microsoft.com",
        "nvidia.com",
        "huggingface.co",
        # ecosystem
        "github.com",
    }

    return host in allow


def _is_probable_homepage_or_section(url: str, title: str) -> bool:
    """Reject non-article pages (homepages/sections/category indexes)."""
    try:
        p = urlparse(url)
        host = p.netloc.lower().replace("www.", "")
        path = (p.path or "/").rstrip("/")
        t = (title or "").lower()

        if "wikipedia" in host or "wikipedia" in t:
            return True

        # obvious home/section pages
        if path in {"", "/", "/technology", "/tech", "/ai"}:
            return True

        # Reuters section pages are common results; avoid them.
        if host == "reuters.com" and path in {"/technology", "/world", "/business"}:
            return True

        # generic “news hub” titles
        if re.search(r"\b(latest|today|news)\b", t) and ("/" not in (p.path or "").strip("/")):
            return True

        return False
    except Exception:
        return False


def _looks_like_real_news_item(title: str, desc: str) -> bool:
    t = (title or "").lower()
    d = (desc or "").lower()

    # avoid homepages/aggregators/SEO sludge
    bad_patterns = [
        r"\blatest news\b",
        r"\bai news\b\s*\|",
        r"\bhome\b",
        r"\bnewsletter\b",
        r"\bsubscribe\b",
        r"\bregister\b",
        r"\blogin\b",
        r"\bpricing\b",
        r"\bjobs\b",
    ]
    if any(re.search(p, t) for p in bad_patterns):
        return False

    # require at least some "event" signal
    signal_words = [
        "launch",
        "released",
        "release",
        "announces",
        "announced",
        "unveils",
        "debut",
        "funding",
        "raises",
        "acquires",
        "acquisition",
        "partnership",
        "regulation",
        "lawsuit",
        "ban",
        "policy",
        "model",
        "chip",
        "gpu",
        "security",
        "openai",
        "anthropic",
        "google",
        "microsoft",
        "nvidia",
        "deepseek",
        "qwen",
        "gemini",
        "claude",
    ]
    blob = f"{t} {d}"
    return any(w in blob for w in signal_words)


def _score_item(item: dict) -> float:
    """Cheap heuristic score: prioritize recency + reputable domains."""
    url = item.get("url", "")
    host = (item.get("meta_url") or {}).get("netloc", "")
    host = (host or urlparse(url).netloc).lower().replace("www.", "")

    # domain weights
    domain_boost = 0.0
    if host in {"reuters.com", "bloomberg.com", "ft.com", "wsj.com"}:
        domain_boost = 3.0
    elif host in {"theverge.com", "arstechnica.com", "wired.com", "techcrunch.com", "axios.com", "cnbc.com"}:
        domain_boost = 2.0
    elif host in {"openai.com", "anthropic.com", "ai.google.dev", "cloud.google.com", "microsoft.com", "nvidia.com"}:
        domain_boost = 2.5
    elif host:
        domain_boost = 0.5

    # recency: newer => higher
    page_age = _parse_iso_dt(item.get("page_age"))
    recency = 0.0
    if page_age:
        hours = (datetime.now() - page_age).total_seconds() / 3600
        # clamp (0..72h)
        hours = max(0.0, min(72.0, hours))
        recency = (72.0 - hours) / 24.0  # 0..3

    return domain_boost + recency


def search_news():
    """搜索AI新闻（并做筛选：近两天 + 可信来源 + 更像新闻的条目）"""
    print(f"🤖 AI Daily Generator - {TODAY}")
    print("📰 搜索AI新闻...")

    BRAVE_API_KEY = os.environ.get('BRAVE_API_KEY')
    if not BRAVE_API_KEY:
        print("搜索失败: BRAVE_API_KEY not set")
        return None

    # Freshness: past day; we do 2 queries (rate-limited to 1 QPS on free plan).
    queries = [
        "OpenAI Anthropic Google Microsoft NVIDIA DeepSeek Qwen Gemini Claude AI news",
        "AI model released benchmark safety regulation funding NVIDIA chip",
    ]

    merged_results = []
    data = {"web": {"results": merged_results}}

    try:
        for idx, q in enumerate(queries):
            params = {"q": q, "count": 20, "freshness": "pd"}
            url = "https://api.search.brave.com/res/v1/web/search?" + urllib.parse.urlencode(params)
            req = urllib.request.Request(url, headers={
                'Accept': 'application/json',
                'X-Subscription-Token': BRAVE_API_KEY
            })

            # avoid 429 on Free plan (1 QPS)
            if idx > 0:
                time.sleep(1.2)

            with urllib.request.urlopen(req, timeout=30) as response:
                chunk = json.loads(response.read().decode('utf-8'))
                merged_results.extend(((chunk.get('web', {}) or {}).get('results', [])) or [])

        # Filter + rank in-place so the rest of the pipeline stays simple.
        results = merged_results
        filtered = []
        seen = set()

        cutoff_hours = 48
        now = datetime.now()

        def recency_ok(item_):
            page_age_ = _parse_iso_dt(item_.get('page_age'))
            if not page_age_:
                return True  # keep unknown, but will be scored lower
            age_hours_ = (now - page_age_).total_seconds() / 3600
            return age_hours_ <= cutoff_hours

        def add_item(item_):
            title_ = clean_text(item_.get('title', ''))
            url_ = item_.get('url', '')
            if not title_ or not url_:
                return False
            key_ = (re.sub(r"\W+", "", title_.lower())[:80], urlparse(url_).netloc.lower())
            if key_ in seen:
                return False
            seen.add(key_)
            filtered.append(item_)
            return True

        # Pass 1: strict (reputable + looks like news + recency)
        for item in results:
            title = clean_text(item.get('title', ''))
            url_i = item.get('url', '')
            desc = clean_text(item.get('description', ''))

            if not title or not url_i:
                continue
            if not recency_ok(item):
                continue
            if _is_probable_homepage_or_section(url_i, title):
                continue
            if not _is_reputable_source(url_i):
                continue
            if not _looks_like_real_news_item(title, desc):
                continue
            add_item(item)

        # Pass 2: relax "news signal" if we have too few
        if len(filtered) < 5:
            for item in results:
                title = clean_text(item.get('title', ''))
                url_i = item.get('url', '')
                if not title or not url_i:
                    continue
                if not recency_ok(item):
                    continue
                if _is_probable_homepage_or_section(url_i, title):
                    continue
                if not _is_reputable_source(url_i):
                    continue
                add_item(item)
                if len(filtered) >= 7:
                    break

        # Pass 3: last resort — still require reputable sources, only relax the "news signal".
        if len(filtered) < 5:
            for item in results:
                title = clean_text(item.get('title', ''))
                url_i = item.get('url', '')
                if not title or not url_i:
                    continue
                if not recency_ok(item):
                    continue
                if _is_probable_homepage_or_section(url_i, title):
                    continue
                if not _is_reputable_source(url_i):
                    continue
                add_item(item)
                if len(filtered) >= 7:
                    break

        filtered.sort(key=_score_item, reverse=True)
        data.setdefault('web', {})['results'] = filtered
        print(f"✓ 原始结果 {len(results)} 条，筛选后 {len(filtered)} 条")
        return data

    except Exception as e:
        # Try to print response body for HTTPError (useful for 422 debugging)
        try:
            from urllib import error as urllib_error
            if isinstance(e, urllib_error.HTTPError):
                body = e.read().decode('utf-8', errors='ignore')
                print(f"搜索失败: HTTP {e.code} {e.reason}; body: {body[:300]}")
                return None
        except Exception:
            pass
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
