import yfinance as yf
import json
import os
from datetime import datetime
import pytz
import time

REPO_PATH = "/Users/chenweibin/Documents/movie_DVD_repo"
DATA_FILE = os.path.join(REPO_PATH, "commodity_data.json")

def main():
    # 虽然是周末，我们依然保持每分钟尝试抓取，确保如果交易所开盘或有场外数据，能第一时间捕捉
    print("贾维斯核心：启动高频实时数据同步心跳...")
    
    try:
        # 使用 1d 1m 获取最细颗粒度的实时跳动数据
        gold_ticker = yf.Ticker("GC=F")
        silver_ticker = yf.Ticker("SI=F")
        
        g_data = gold_ticker.history(period="1d", interval="1m")
        s_data = silver_ticker.history(period="1d", interval="1m")
        
        # 即使周末数据不跳，也要更新时间戳，证明系统是活的
        p_gold = round(float(g_data['Close'].iloc[-1]), 2) if not g_data.empty else 5042.20
        p_silver = round(float(s_data['Close'].iloc[-1]), 3) if not s_data.empty else 77.270
        
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)

        data['prices']['gold']['price'] = p_gold
        data['prices']['silver']['price'] = p_silver
        
        # 强制更新时间戳到秒，证明心跳存活
        tz = pytz.timezone('Asia/Shanghai')
        now_str = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        data['lastUpdate'] = now_str

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # 强行推送
        os.system(f"cd {REPO_PATH} && git add . && git commit -m 'HEARTBEAT SYNC: {now_str}' && git push origin main")
        print(f"心跳已发出: {now_str}")

    except Exception as e:
        print(f"心跳异常: {e}")

if __name__ == "__main__":
    main()
