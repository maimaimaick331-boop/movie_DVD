import yfinance as yf
import json
import os
from datetime import datetime

# --- 配置 ---
REPO_PATH = "/Users/chenweibin/Documents/movie_DVD_repo"
DATA_FILE = os.path.join(REPO_PATH, "commodity_data.json")

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

        return {
            "gold": round(float(g_data['Close'].iloc[-1]), 2),
            "silver": round(float(s_data['Close'].iloc[-1]), 3),
            "copper": round(float(c_data['Close'].iloc[-1]), 4),
            "raw_time": g_data.index[-1].strftime("%Y-%m-%d %H:%M:%S") if not g_data.empty else "N/A"
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

def update_repo():
    prices = get_market_prices()
    if not prices: return

    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    # 1. 更新价格 (确保与交易软件收盘/实时对齐)
    data['prices']['gold']['price'] = prices['gold']
    data['prices']['silver']['price'] = prices['silver']
    data['prices']['copper']['price'] = prices['copper']
    
    # 2. 注入关联金属的精准溯源链接 (修复张冠李戴问题)
    # 每个交易所针对不同金属有不同的数据发布页
    source_links = {
        "gold": {
            "LBMA": "https://www.lbma.org.uk/prices-and-data/london-vault-data",
            "COMEX": "https://www.cmegroup.com/markets/metals/precious/gold.html",
            "SHFE": "https://www.shfe.com.cn/statements/dataview.html?paramid=dailydata"
        },
        "silver": {
            "LBMA": "https://www.lbma.org.uk/prices-and-data/london-vault-data",
            "COMEX": "https://www.cmegroup.com/markets/metals/precious/silver.html",
            "SHFE": "https://www.shfe.com.cn/statements/dataview.html?paramid=dailydata"
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

    # 3. 更新时间 (使用系统当前北京时间)
    data['lastUpdate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # 4. Git 推送
    os.system(f"cd {REPO_PATH} && git add . && git commit -m 'Strict Update: Fix URLs, Time and Close Prices' && git push origin main")

if __name__ == "__main__":
    update_repo()
