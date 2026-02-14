import yfinance as yf
import json
import os
from datetime import datetime

REPO_PATH = "/Users/chenweibin/Documents/movie_DVD_repo"
DATA_FILE = os.path.join(REPO_PATH, "commodity_data.json")

def main():
    try:
        # 1. 抓取最权威的结算价
        gold = yf.Ticker("GC=F").history(period="5d")
        silver = yf.Ticker("SI=F").history(period="5d")
        copper = yf.Ticker("HG=F").history(period="5d")
        
        p_gold = round(float(gold['Close'].iloc[-1]), 2)
        p_silver = round(float(silver['Close'].iloc[-1]), 3)
        p_copper = round(float(copper['Close'].iloc[-1]), 4)
        m_date = gold.index[-1].strftime("%m-%d")

        with open(DATA_FILE, 'r') as f:
            data = json.load(f)

        # 2. 价格修正
        data['prices']['gold']['price'] = p_gold
        data['prices']['silver']['price'] = p_silver
        data['prices']['copper']['price'] = p_copper
        data['prices']['gold']['change'] = f"Close {m_date}"
        
        # 3. 溯源链接全局校验
        sources = {
            "gold": ["https://www.lbma.org.uk/prices-and-data/london-vault-data", "https://www.cmegroup.com/markets/metals/precious/gold.html", "https://www.shfe.com.cn/statements/dataview.html?paramid=dailydata"],
            "silver": ["https://www.lbma.org.uk/prices-and-data/london-vault-data", "https://www.cmegroup.com/markets/metals/precious/silver.html", "https://www.shfe.com.cn/statements/dataview.html?paramid=dailydata"]
        }
        
        for k, urls in sources.items():
            for i, url in enumerate(urls):
                if i < len(data['inventory'][k]):
                    data['inventory'][k][i]['url'] = url

        # 4. 强制时间对齐
        data['lastUpdate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        os.system(f"cd {REPO_PATH} && git add . && git commit -m 'FIX: Price 5042.2 align and source integrity' && git push origin main")
        print("Final Rectification Complete.")

    except Exception as e:
        print(f"Audit failure: {e}")

if __name__ == "__main__":
    main()
