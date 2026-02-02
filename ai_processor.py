#!/usr/bin/env python3
"""
AI Daily - AI内容处理器
使用 DeepSeek API 进行标题翻译和摘要生成
"""

import os
import sys
import json
import re
from openai import OpenAI

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_BASE = 'https://api.deepseek.com'
DEEPSEEK_MODEL = 'deepseek-chat'


def get_client():
    """获取 DeepSeek API 客户端"""
    if not DEEPSEEK_API_KEY:
        return None
    return OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_BASE)


def process_news_batch(news_items: list) -> list:
    """
    批量处理新闻：翻译标题 + 生成摘要

    Args:
        news_items: [{"title": "...", "description": "...", "url": "..."}]

    Returns:
        处理后的新闻列表，每项增加 title_zh 和 summary_zh 字段
    """
    client = get_client()
    if not client:
        print("警告: 未设置 DEEPSEEK_API_KEY，跳过翻译", file=sys.stderr)
        return news_items

    if not news_items:
        return news_items

    # 构建批量处理的 prompt
    prompt = """请处理以下AI新闻列表，对每条新闻：
1. 将英文标题翻译成简洁的中文标题（保持专业术语准确，不超过40字）
2. 根据描述生成一句话中文摘要（提炼核心信息，不超过80字）

请严格按照以下JSON格式返回，确保数组长度与输入一致：
{"results": [{"title_zh": "中文标题", "summary_zh": "中文摘要"}, ...]}

新闻列表：
"""

    for i, item in enumerate(news_items):
        title = item.get('title', '')
        desc = item.get('description', '')
        prompt += f"\n{i+1}. 标题: {title}\n   描述: {desc}\n"

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "你是一个专业的AI科技新闻翻译助手。请准确翻译技术术语，保持专业性。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )

        content = response.choices[0].message.content

        # 提取JSON部分
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            result = json.loads(json_match.group())
            results = result.get('results', [])

            # 合并结果
            for i, item in enumerate(news_items):
                if i < len(results):
                    item['title_zh'] = results[i].get('title_zh', item.get('title', ''))
                    item['summary_zh'] = results[i].get('summary_zh', item.get('description', '')[:80])
                else:
                    item['title_zh'] = item.get('title', '')
                    item['summary_zh'] = item.get('description', '')[:80]
        else:
            print("警告: 无法解析AI响应，使用原始内容", file=sys.stderr)

    except Exception as e:
        print(f"AI处理失败: {e}", file=sys.stderr)
        # 降级处理：保留原始内容
        for item in news_items:
            item['title_zh'] = item.get('title', '')
            item['summary_zh'] = item.get('description', '')[:80]

    return news_items


def process_from_stdin():
    """从标准输入读取JSON并处理"""
    try:
        data = json.load(sys.stdin)
        results = data.get('web', {}).get('results', [])[:5]

        # 提取新闻信息
        news_items = []
        for r in results:
            news_items.append({
                'title': r.get('title', ''),
                'url': r.get('url', ''),
                'description': r.get('description', '')
            })

        # AI处理
        processed = process_news_batch(news_items)

        # 输出处理后的结果
        print(json.dumps(processed, ensure_ascii=False))

    except Exception as e:
        print(f"处理失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    process_from_stdin()
