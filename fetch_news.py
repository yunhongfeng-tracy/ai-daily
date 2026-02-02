#!/usr/bin/env python3
"""
AI Daily - 多来源新闻抓取器
支持：Brave Search API, RSS订阅
"""

import json
import os
import sys
import re
import requests
from datetime import datetime
from urllib.parse import urlparse

# 尝试导入 feedparser（RSS解析）
try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False
    print("警告: feedparser 未安装，RSS功能不可用", file=sys.stderr)


def clean_text(text):
    """清理文本"""
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
    text = text.replace('&lt;', '<').replace('&gt;', '>')
    return text.strip()


class NewsSource:
    """新闻源基类"""
    def __init__(self, config):
        self.config = config

    def fetch(self) -> list:
        raise NotImplementedError


class BraveSearchSource(NewsSource):
    """Brave Search API 新闻源"""
    def __init__(self, config):
        super().__init__(config)
        self.query = config.get('query', 'AI news')
        self.count = config.get('count', 5)
        self.api_key = os.getenv('BRAVE_API_KEY', '')

    def fetch(self):
        if not self.api_key:
            print("警告: 未设置 BRAVE_API_KEY", file=sys.stderr)
            return []

        try:
            resp = requests.get(
                'https://api.search.brave.com/res/v1/web/search',
                params={'q': self.query, 'count': self.count},
                headers={
                    'Accept': 'application/json',
                    'X-Subscription-Token': self.api_key
                },
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()

            results = []
            for item in data.get('web', {}).get('results', []):
                url = item.get('url', '')
                source = urlparse(url).netloc.replace('www.', '') if url else '未知来源'

                results.append({
                    'title': clean_text(item.get('title', '')),
                    'url': url,
                    'description': clean_text(item.get('description', '')),
                    'source_name': source,
                    'published_at': item.get('page_age', '')
                })
            return results

        except Exception as e:
            print(f"Brave API 错误: {e}", file=sys.stderr)
            return []


class RSSSource(NewsSource):
    """RSS 订阅源"""
    def __init__(self, config):
        super().__init__(config)
        self.url = config.get('url', '')
        self.max_items = config.get('max_items', 5)

    def fetch(self):
        if not HAS_FEEDPARSER:
            print("警告: feedparser 未安装，跳过 RSS 源", file=sys.stderr)
            return []

        if not self.url:
            return []

        try:
            feed = feedparser.parse(self.url)
            results = []

            for entry in feed.entries[:self.max_items]:
                url = entry.get('link', '')
                source = urlparse(url).netloc.replace('www.', '') if url else '未知来源'

                # 提取发布时间
                published = ''
                if hasattr(entry, 'published'):
                    published = entry.published
                elif hasattr(entry, 'updated'):
                    published = entry.updated

                results.append({
                    'title': clean_text(entry.get('title', '')),
                    'url': url,
                    'description': clean_text(entry.get('summary', ''))[:200],
                    'source_name': source,
                    'published_at': published
                })
            return results

        except Exception as e:
            print(f"RSS 解析错误 ({self.url}): {e}", file=sys.stderr)
            return []


def load_config(config_path='sources.json'):
    """加载配置文件"""
    if not os.path.exists(config_path):
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"配置文件加载失败: {e}", file=sys.stderr)
        return None


def fetch_all_news(config_path='sources.json'):
    """从所有启用的来源获取新闻"""
    config = load_config(config_path)

    if not config:
        print("未找到配置文件，使用默认 Brave Search", file=sys.stderr)
        source = BraveSearchSource({'query': 'AI artificial intelligence news today', 'count': 5})
        return source.fetch()

    all_news = []
    sources = config.get('sources', [])
    global_settings = config.get('global_settings', {})
    total_limit = global_settings.get('total_news_limit', 10)
    max_per_source = global_settings.get('max_news_per_source', 3)

    # 按优先级排序
    sources = sorted(sources, key=lambda x: x.get('priority', 99))

    for source_config in sources:
        if not source_config.get('enabled', True):
            continue

        source_type = source_config.get('type')
        source_name = source_config.get('name', 'Unknown')
        inner_config = source_config.get('config', {})

        print(f"正在获取: {source_name} ({source_type})", file=sys.stderr)

        fetcher = None
        if source_type == 'brave_api':
            fetcher = BraveSearchSource(inner_config)
        elif source_type == 'rss':
            fetcher = RSSSource(inner_config)

        if fetcher:
            try:
                news = fetcher.fetch()[:max_per_source]
                for item in news:
                    item['source_id'] = source_config.get('id')
                    item['source_display'] = source_name
                    item['priority'] = source_config.get('priority', 99)
                all_news.extend(news)
                print(f"  获取到 {len(news)} 条新闻", file=sys.stderr)
            except Exception as e:
                print(f"  获取失败: {e}", file=sys.stderr)

    # 应用过滤器
    filters = config.get('filters', {})
    exclude_domains = filters.get('exclude_domains', [])
    exclude_keywords = filters.get('exclude_keywords', [])

    filtered_news = []
    for item in all_news:
        url = item.get('url', '')
        domain = urlparse(url).netloc.lower()
        title = item.get('title', '').lower()

        # 检查排除域名
        if any(d in domain for d in exclude_domains):
            continue

        # 检查排除关键词
        if any(kw.lower() in title for kw in exclude_keywords):
            continue

        filtered_news.append(item)

    # 按优先级排序并限制数量
    filtered_news.sort(key=lambda x: x.get('priority', 99))
    return filtered_news[:total_limit]


def main():
    """主函数"""
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'sources.json'
    news = fetch_all_news(config_path)
    print(json.dumps(news, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
