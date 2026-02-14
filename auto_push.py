import os
import time
import shutil
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO_PATH = "/Users/chenweibin/Documents/movie_DVD_repo"
WATCH_FILES = ["index.html", "commodity_data.json"]
INTERVAL_SECONDS = 2

def resolve_repo_path():
    env_path = os.environ.get("JARVIS_REPO_PATH")
    candidate = env_path if env_path else DEFAULT_REPO_PATH
    if os.path.isdir(os.path.join(candidate, ".git")):
        return candidate
    if os.path.isdir(os.path.join(SOURCE_DIR, ".git")):
        return SOURCE_DIR
    return candidate

def snapshot(path):
    try:
        stat = os.stat(path)
        return (stat.st_mtime, stat.st_size)
    except FileNotFoundError:
        return None

def sync_files(source_dir, repo_path, files):
    if not os.path.isdir(repo_path):
        return
    for name in files:
        src = os.path.join(source_dir, name)
        if not os.path.isfile(src):
            continue
        dst = os.path.join(repo_path, name)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

def git_status_dirty(repo_path):
    result = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True)
    return result.returncode == 0 and result.stdout.strip() != ""

def git_commit_push(repo_path, message):
    subprocess.run(["git", "add", "-A"], cwd=repo_path)
    if git_status_dirty(repo_path):
        subprocess.run(["git", "commit", "-m", message], cwd=repo_path)
        subprocess.run(["git", "push", "origin", "main"], cwd=repo_path)

def main():
    repo_path = resolve_repo_path()
    last = {name: snapshot(os.path.join(SOURCE_DIR, name)) for name in WATCH_FILES}
    while True:
        time.sleep(INTERVAL_SECONDS)
        changed = False
        for name in WATCH_FILES:
            sig = snapshot(os.path.join(SOURCE_DIR, name))
            if sig and sig != last.get(name):
                last[name] = sig
                changed = True
        if changed:
            sync_files(SOURCE_DIR, repo_path, WATCH_FILES)
            now = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
            git_commit_push(repo_path, f"AUTO PUSH: {now}")

if __name__ == "__main__":
    main()
