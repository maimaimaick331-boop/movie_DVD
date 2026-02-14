import yfinance as yf
import json
import os
from datetime import datetime
import pytz

REPO_PATH = "/Users/chenweibin/Documents/movie_DVD_repo"
DATA_FILE = os.path.join(REPO_PATH, "commodity_data.json")

def main():
    try:
        # 1. 抓取最权威价格
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
        
        # 2. 核心补丁：北京时间同步
        tz = pytz.timezone('Asia/Shanghai')
        now_beijing = datetime.now(tz)
        current_time_str = now_beijing.strftime("%Y-%m-%d %H:%M:%S")
        data['lastUpdate'] = current_time_str

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # 3. 强力推送并清除仓库残留
        os.system(f"cd {REPO_PATH} && git add . && git commit -m 'FORCE HEARTBEAT SYNC: {current_time_str}' && git push origin main")
        
        print(f"JARVIS_LOG: 同步核心任务完成。当前北京时间: {current_time_str}")

    except Exception as e:
        print(f"JARVIS_ERROR: {e}")

if __name__ == "__main__":
    main()
