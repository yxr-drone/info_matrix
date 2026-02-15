import json
import time
import re
import os

# 配置人物和源
SOURCES = {
    "Andrej Karpathy": [
        "https://karpathy.github.io/",
        "https://x.com/karpathy"
    ],
    "Fei-Fei Li": [
        "https://profiles.stanford.edu/fei-fei-li",
        "https://hai.stanford.edu/"
    ]
}

DATA_PATH = "/home/skywork/workspace/karpathy_hub/core/data/matrix.json"
HTML_PATH = "/home/skywork/workspace/karpathy_hub/index.html"

def run_sync():
    print(f"[{time.ctime()}] 启动情报矩阵同步任务...")
    
    # 这里是爬虫核心逻辑的入口 (伪代码形式，由 AI 在执行时调用 browser 工具补充新数据)
    # 本脚本负责将捕获的数据持久化并推送到 Git
    
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r') as f:
            data = json.load(f)
            
        # 更新 index.html 内部的 allPosts 变量
        with open(HTML_PATH, 'r') as f:
            html = f.read()
            
        new_js = f"const matrixData = {json.dumps(data, ensure_ascii=False, indent=2)};"
        pattern = r"const matrixData = \[[\s\S]*?\];"
        updated_html = re.sub(pattern, new_js, html)
        
        with open(HTML_PATH, 'w') as f:
            f.write(updated_html)
            
        # 执行 Git 推送
        os.system("cd /home/skywork/workspace/karpathy_hub && git add . && git commit -m 'chore: auto-sync intelligence matrix' && git push origin main")
        print("同步完成并已推送到 GitHub。")

if __name__ == "__main__":
    run_sync()
