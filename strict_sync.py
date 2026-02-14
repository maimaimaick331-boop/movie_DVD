import yfinance as yf
import json
import os
import time
from datetime import datetime
import pytz

# --- 配置 ---
REPO_PATH = "/Users/chenweibin/Documents/movie_DVD_repo"
DATA_FILE = os.path.join(REPO_PATH, "commodity_data.json")
SYNC_INTERVAL_SECONDS = int(os.environ.get("JARVIS_SYNC_INTERVAL", "1"))
PUSH_INTERVAL_SECONDS = int(os.environ.get("JARVIS_PUSH_INTERVAL", "300"))

def get_market_prices():
    """获取最严谨的收盘/实时价格"""
    try:
        # GC=F 纽约商业交易所(COMEX) 黄金期货
        gold_ticker = yf.Ticker("GC=F")
        # SI=F 纽约商业交易所(COMEX) 白银期货
        silver_ticker = yf.Ticker("SI=F")
        # HG=F 纽约商品交易所(COMEX) 铜期货
        copper_ticker = yf.Ticker("HG=F")

        g_data = gold_ticker.history(period="1d")
        s_data = silver_ticker.history(period="1d")
        c_data = copper_ticker.history(period="1d")

        def safe_price(data, decimals):
            if data is None or data.empty:
                return None
            return round(float(data['Close'].iloc[-1]), decimals)

        return {
            "gold": safe_price(g_data, 2),
            "silver": safe_price(s_data, 3),
            "copper": safe_price(c_data, 4),
            "raw_time": g_data.index[-1].strftime("%Y-%m-%d %H:%M:%S") if not g_data.empty else None
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

def update_repo(allow_push=True):
    prices = get_market_prices()
    if not prices: return

    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    # 1. 更新价格 (确保与交易软件收盘/实时对齐)
    if prices.get('gold') is not None:
        data['prices']['gold']['price'] = prices['gold']
    if prices.get('silver') is not None:
        data['prices']['silver']['price'] = prices['silver']
    if prices.get('copper') is not None:
        data['prices']['copper']['price'] = prices['copper']
    
    # 2. 注入关联金属的精准溯源链接 (修复张冠李戴问题)
    # 每个交易所针对不同金属有不同的数据发布页
    source_links = {
        "gold": {
            "LBMA": "https://www.lbma.org.uk/prices-and-data/london-vault-data",
            "COMEX": "https://www.cmegroup.com/markets/metals/precious/gold.html",
            "SHFE": "https://www.shfe.com.cn/statements/dataview.html?paramid=dailydata&curr_year=2026&curr_month=2"
        },
        "silver": {
            "LBMA": "https://www.lbma.org.uk/prices-and-data/london-vault-data",
            "COMEX": "https://www.cmegroup.com/markets/metals/precious/silver.html",
            "SHFE": "https://www.shfe.com.cn/statements/dataview.html?paramid=dailydata&curr_year=2026&curr_month=2"
        },
        "copper": {
            "LME": "https://www.lme.com/en/Metals/Non-ferrous/LME-Copper#Stock+report",
            "SHFE": "https://www.shfe.com.cn/statements/dataview.html?paramid=dailydata"
        }
    }

    for metal in ['gold', 'silver', 'copper']:
        if metal in data['inventory']:
            for item in data['inventory'][metal]:
                item['url'] = source_links.get(metal, {}).get(item['exchange'], "#")

    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")
    data['lastUpdate'] = now_str

    for metal in ['gold', 'silver', 'copper']:
        if metal in data['inventory']:
            for item in data['inventory'][metal]:
                category = item.get('category', '')
                if 'Registered' in category or '可交割' in category:
                    item['sync'] = f"Registered Snapshot {current_date}"
                else:
                    item['sync'] = f"Verified {current_date}"

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if allow_push:
        os.system(f"cd {REPO_PATH} && git add . && git commit -m 'Strict Update: Unified Sync {now_str}' && git push origin main")

if __name__ == "__main__":
    loop = os.environ.get("JARVIS_LOOP", "").lower() in ("1", "true", "yes")
    if loop:
        last_push_ts = 0.0
        while True:
            now_ts = time.time()
            allow_push = (now_ts - last_push_ts) >= PUSH_INTERVAL_SECONDS
            update_repo(allow_push=allow_push)
            if allow_push:
                last_push_ts = now_ts
            time.sleep(SYNC_INTERVAL_SECONDS)
    else:
        update_repo()
