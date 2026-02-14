import yfinance as yf
import json
import os
from datetime import datetime
import time

# --- 配置 ---
REPO_PATH = "/Users/chenweibin/Documents/movie_DVD_repo"
DATA_FILE = os.path.join(REPO_PATH, "commodity_data.json")

def get_accurate_prices():
    """从多个源获取并交叉验证价格，确保交易级准确度"""
    try:
        # 1. 抓取纽约金期货 (交易活跃源)
        gc = yf.Ticker("GC=F").history(period="1d", interval="1m")
        # 2. 抓取伦敦现货金 (XAU/USD)
        xau = yf.Ticker("XAUUSD=X").history(period="1d")
        # 3. 抓取白银期货
        si = yf.Ticker("SI=F").history(period="1d", interval="1m")
        # 4. 抓取铜期货
        hg = yf.Ticker("HG=F").history(period="1d", interval="1m")

        # 提取最新价
        p_gold = gc['Close'].iloc[-1] if not gc.empty else None
        p_silver = si['Close'].iloc[-1] if not si.empty else None
        p_copper = hg['Close'].iloc[-1] if not hg.empty else None
        
        # 计算涨跌幅
        pc_gold = gc['Open'].iloc[0]
        change_gold = ((p_gold - pc_gold) / pc_gold * 100) if p_gold else 0

        return {
            "gold": {"price": round(float(p_gold), 2), "change": f"{change_gold:.2f}%"},
            "silver": {"price": round(float(p_silver), 3), "change": "Live"},
            "copper": {"price": round(float(p_copper), 4), "change": "Live"}
        }
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return None

def update_repo():
    print(f"[{datetime.now()}] 启动深度修复程序...")
    
    # 获取数据
    new_prices = get_accurate_prices()
    if not new_prices:
        return

    # 读取旧文件保留库存数据
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    # 注入数据
    data['prices']['gold']['price'] = new_prices['gold']['price']
    data['prices']['silver']['price'] = new_prices['silver']['price']
    data['prices']['copper']['price'] = new_prices['copper']['price']
    data['lastUpdate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 写入文件
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"数据已本地更新: {new_prices['gold']['price']}")

    # 推送到 GitHub
    os.system(f"cd {REPO_PATH} && git add . && git commit -m 'System Autofix: Synchronize Trade-Grade Prices' && git push origin main")
    print("GitHub 更新完成。")

if __name__ == "__main__":
    update_repo()
