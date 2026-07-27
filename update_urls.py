import os
import json
import glob
import re

MAPPING = {
    "FastAPI": "FastAPI 非同步處理 (FastAPI Async)",
    "Github": "背景排程與監控 (Cron & Monitoring)",
    "React UI": "React 狀態管理 (React State)",
    "Telegram": "多智能體協作 (Multi-Agent Sync)",
    "Linux": "Linux 系統安全維護 (Linux Security)",
    "API": "FastAPI 非同步處理 (FastAPI Async)", # fallback
    "腳本": "背景排程與監控 (Cron & Monitoring)" # fallback
}

repo_dir = "/home/hoonsoropenclaw/.hermes/data_repo"
data_json_path = os.path.join(repo_dir, "data.json")

print(f"Reading {data_json_path}...")
with open(data_json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

def find_node(node, target_name):
    if node.get("name") == target_name:
        return node
    if "children" in node:
        for child in node["children"]:
            found = find_node(child, target_name)
            if found:
                return found
    return None

artifact_files = glob.glob(os.path.join(repo_dir, "artifacts", "*.md"))
print(f"Found {len(artifact_files)} artifacts.")

updated_nodes = 0
for filepath in artifact_files:
    filename = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        topic_line = f.readline().strip()
    
    target_node_name = None
    for keyword, node_name in MAPPING.items():
        if keyword.lower() in topic_line.lower():
            target_node_name = node_name
            break
            
    if target_node_name:
        node = find_node(data["mindmap"], target_node_name)
        if node:
            url = f"https://raphael-mindmap-data.vercel.app/artifacts/{filename}"
            # Only update if the URL is different (so we don't count it if it's already updated with this exact url, though we want the latest artifact)
            node["url"] = url
            node["status"] = "completed"
            updated_nodes += 1
            print(f"Mapped {filename} -> {target_node_name}")
        else:
            print(f"Warning: Node '{target_node_name}' not found for {filename}")
    else:
        print(f"Warning: Unmapped topic line in {filename}: {topic_line}")

if updated_nodes > 0:
    import datetime
    data["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(data_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Successfully injected URLs for {updated_nodes} artifacts.")
    
    # Try to push to github
    os.chdir(repo_dir)
    os.system("git config user.email 'bot@antigravity.ai' && git config user.name 'Antigravity Bot'")
    os.system("git add data.json artifacts/")
    os.system('git commit -m "chore: auto-update data.json URLs from Antigravity"')
    os.system("git push origin main")
else:
    print("No nodes were updated.")
