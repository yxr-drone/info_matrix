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
        if date_span and link_tag:
            posts.append({
                "author": "Andrej Karpathy",
                "date": date_span.text.strip(),
                "id": f"ak_{link_tag['href'].strip('/').replace('/', '_')}",
                "title": link_tag.text.strip(),
                "original": item.get_text(" ", strip=True).replace(date_span.text, "").replace(link_tag.text, "").strip(),
                "url": f"https://karpathy.github.io{link_tag['href']}",
                "isHot": "microgpt" in link_tag.text.lower()
            })
    return posts

def fetch_openai():
    print("正在搜集 OpenAI 官方动态...")
    soup = get_soup("https://openai.com/news/")
    if not soup: return []
    posts = []
    # 简单的结构提取，实际可根据 OpenAI 变动微调
    for article in soup.find_all('article')[:5]:
        link_tag = article.find('a')
        title_tag = article.find('h3')
        if link_tag and title_tag:
            posts.append({
                "author": "OpenAI",
                "date": datetime.now().strftime("%b %d, %Y"), # 动态日期
                "id": f"oa_{hash(link_tag['href'])}",
                "title": title_tag.text.strip(),
                "original": "Latest announcement from OpenAI regarding their models and safety research.",
                "url": f"https://openai.com{link_tag['href']}"
            })
    return posts

def fetch_altman():
    print("正在搜集 Sam Altman 的博客...")
    soup = get_soup("https://blog.samaltman.com/")
    if not soup: return []
    posts = []
    for a in soup.select('h1 a')[:3]:
        posts.append({
            "author": "Sam Altman",
            "date": datetime.now().strftime("%b %d, %Y"),
            "id": f"sa_{hash(a['href'])}",
            "title": a.text.strip(),
            "original": "Musings on the future of AI and Silicon Valley.",
            "url": a['href']
        })
    return posts

def update_all():
    all_data = fetch_karpathy() + fetch_openai() + fetch_altman()
    
    # 强制加入已知的重大情报
    feifei = {
        "author": "Fei-Fei Li", "date": "Feb 15, 2026", "id": "ff_2025", 
        "title": "荣获 2025 伊丽莎白女王工程奖", "isHot": True,
        "original": "For the creation of ImageNet and leadership in AI.",
        "url": "https://profiles.stanford.edu/fei-fei-li"
    }
    all_data.append(feifei)

    if os.path.exists(DATA_JSON):
        with open(DATA_JSON, 'r', encoding='utf-8') as f:
            stored = json.load(f)
    else: stored = []
    
    stored_ids = {p['id'] for p in stored}
    for post in all_data:
        if post['id'] not in stored_ids:
            # 统一由我后续补充翻译
            post['translation'] = f"（同步中：{post['title']}）"
            stored.insert(0, post)

    with open(DATA_JSON, 'w', encoding='utf-8') as f:
        json.dump(stored, f, ensure_ascii=False, indent=2)
    with open(DATA_JS, 'w', encoding='utf-8') as f:
        f.write(f"const matrixData = {json.dumps(stored, ensure_ascii=False, indent=2)};")
    print(f"情报搜集完成。当前矩阵条目总数: {len(stored)}")

if __name__ == "__main__":
    update_all()
