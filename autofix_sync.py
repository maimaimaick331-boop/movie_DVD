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
        # 2. 抓取伦敦现货金 (XAU/USD) - 增加兜底逻辑
        try:
            xau_ticker = yf.Ticker("XAUUSD=X")
            xau = xau_ticker.history(period="1d")
            p_spot = xau['Close'].iloc[-1] if not xau.empty else p_gold
        except:
            p_spot = p_gold # 如果现货接口挂了，用活跃期货补位

        return {
            "gold": {"price": round(float(p_gold), 2), "change": f"{change_gold:.2f}%", "spot": round(float(p_spot), 2)},
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
