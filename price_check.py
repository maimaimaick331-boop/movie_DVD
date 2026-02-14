import yfinance as yf
from datetime import datetime

def get_realtime_prices():
    # 同步抓取纽约金、纽约银
    gold = yf.Ticker("GC=F").history(period="1d")
    silver = yf.Ticker("SI=F").history(period="1d")
    copper = yf.Ticker("HG=F").history(period="1d")
    
    # 现货黄金
    xau = yf.Ticker("XAUUSD=X")
    try:
        xau_p = xau.history(period="1d")['Close'].iloc[-1]
    except:
        # 备选代码
        xau_p = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1]
    
    return {
        "gold_futures": gold['Close'].iloc[-1],
        "silver_futures": silver['Close'].iloc[-1],
        "copper_futures": copper['Close'].iloc[-1],
        "gold_spot": xau_p,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

if __name__ == "__main__":
    prices = get_realtime_prices()
    print(prices)
