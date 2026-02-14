import yfinance as yf
import json
import os
from datetime import datetime
import pytz

REPO_PATH = "/Users/chenweibin/Documents/movie_DVD_repo"
DATA_FILE = os.path.join(REPO_PATH, "commodity_data.json")

def main():
    try:
        # 1. 抓取实时/结算价
        gold = yf.Ticker("GC=F").history(period="1d")
        silver = yf.Ticker("SI=F").history(period="1d")
        copper = yf.Ticker("HG=F").history(period="1d")
        
        p_gold = round(float(gold['Close'].iloc[-1]), 2)
        p_silver = round(float(silver['Close'].iloc[-1]), 3)
        p_copper = round(float(copper['Close'].iloc[-1]), 4)

        with open(DATA_FILE, 'r') as f:
            data = json.load(f)

        data['prices']['gold']['price'] = p_gold
        data['prices']['silver']['price'] = p_silver
        data['prices']['copper']['price'] = p_copper
        
        # 2. 关键修复：强制使用北京时间 (Asia/Shanghai)
        tz = pytz.timezone('Asia/Shanghai')
        now_beijing = datetime.now(tz)
        data['lastUpdate'] = now_beijing.strftime("%Y-%m-%d %H:%M:%S")

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # 3. 推送
        os.system(f"cd {REPO_PATH} && git add . && git commit -m 'CLOCK FIX: Forced Beijing Time Sync inside JSON' && git push origin main")
        print(f"Sync Success: {data['lastUpdate']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
