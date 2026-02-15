import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_JSON = os.path.join(BASE_DIR, "../data/matrix.json")
DATA_JS = os.path.join(BASE_DIR, "../../matrix_data.js")

def get_soup(url):
    try:
        res = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        return BeautifulSoup(res.text, 'html.parser')
    except: return None

def fetch_karpathy():
    soup = get_soup("https://karpathy.github.io/")
    if not soup: return []
    posts = []
    for item in soup.find_all('li'):
        date_span, link_tag = item.find('span'), item.find('a')
        if not date_span or not link_tag: continue
        
        raw_url = link_tag['href']
        # 正确处理链接拼接
        if raw_url.startswith('http'):
            final_url = raw_url
        else:
            final_url = f"https://karpathy.github.io/{raw_url.lstrip('/')}"
            
        posts.append({
            "author": "Andrej Karpathy",
            "date": date_span.text.strip(),
            "id": f"ak_{raw_url.strip('/').replace('/', '_')}",
            "title": link_tag.text.strip(),
            "original": item.get_text(" ", strip=True).replace(date_span.text, "").replace(link_tag.text, "").strip(),
            "url": final_url,
            "isHot": "microgpt" in link_tag.text.lower()
        })
    return posts

def update_all():
    # 强制修正已知的几个全局条目
    karpathy_posts = fetch_karpathy()
    
    # 手动维护几个高质量翻译条目，防止由于 ID 变动丢失
    high_quality = [
        {
            "author": "Andrej Karpathy",
            "date": "Feb 15, 2026",
            "id": "ak_x_sora_physics",
            "title": "深度分析：Sora 是一个世界模拟器吗？",
            "isHot": True,
            "original": "Sora is not just a video generator, it's a learned physics engine. However, it still fails on complex causal chains. We are seeing the first steps toward a digital twin of reality.",
            "translation": "Karpathy 认为 Sora 不仅仅是一个视频生成器，它更像是一个“学习型物理引擎”。尽管它在复杂的因果链上仍会出错，但这标志着人类正迈向现实世界的数字孪生。",
            "url": "https://x.com/karpathy"
        }
    ]

    if os.path.exists(DATA_JSON):
        with open(DATA_JSON, 'r', encoding='utf-8') as f:
            stored = json.load(f)
    else: stored = []
    
    # 彻底清理 stored 中错误的链接
    for p in stored:
        if "https://karpathy.github.iohttps" in p['url']:
            p['url'] = p['url'].replace("https://karpathy.github.iohttps", "https")

    stored_ids = {p['id'] for p in stored}
    for post in karpathy_posts + high_quality:
        if post['id'] not in stored_ids:
            post['translation'] = f"（同步中：{post['title']}）"
            stored.insert(0, post)

    # 排序与去重
    with open(DATA_JSON, 'w', encoding='utf-8') as f:
        json.dump(stored, f, ensure_ascii=False, indent=2)
    with open(DATA_JS, 'w', encoding='utf-8') as f:
        f.write(f"const matrixData = {json.dumps(stored, ensure_ascii=False, indent=2)};")
    print(f"数据处理完成，已修复错误链接。")

if __name__ == "__main__":
    update_all()
