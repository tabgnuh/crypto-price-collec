# collector.py - Tự động thu thập giá crypto và lưu vào CSV
import requests
import pandas as pd
import time
from datetime import datetime
import os

# Danh sách coin bạn muốn theo dõi (id từ CoinGecko)
COINS = [
    'bitcoin', 'ethereum', 'solana', 'ripple', 'cardano',
    'binancecoin', 'dogecoin', 'avalanche-2', 'chainlink', 'polkadot'
]

# File lưu dữ liệu
DATA_FILE = "crypto_prices.csv"

def get_crypto_data():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': ','.join(COINS),
        'vs_currencies': 'usd',
        'include_market_cap': 'true',
        'include_24hr_vol': 'true',
        'include_24hr_change': 'true',
        'include_last_updated_at': 'true'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Lỗi khi gọi API: {e}")
        return None

def append_to_csv(data):
    if not data:
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    
    for coin_id, info in data.items():
        rows.append({
            'timestamp': timestamp,
            'coin': coin_id.capitalize(),
            'price_usd': info.get('usd', 0),
            'market_cap_usd': info.get('usd_market_cap', 0),
            '24h_volume_usd': info.get('usd_24h_vol', 0),
            '24h_change_percent': info.get('usd_24h_change', 0)
        })
    
    df_new = pd.DataFrame(rows)
    
    if os.path.exists(DATA_FILE):
        df_old = pd.read_csv(DATA_FILE)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new
    
    df.to_csv(DATA_FILE, index=False)
    print(f"Đã lưu dữ liệu lúc {timestamp} - {len(rows)} coins")

def main():
    print("Bắt đầu thu thập dữ liệu crypto... Nhấn Ctrl+C để dừng.")
    interval_seconds = 300  # 5 phút = 300 giây (có thể đổi thành 60 để test nhanh)
    
    while True:
        data = get_crypto_data()
        if data:
            append_to_csv(data)
        else:
            print("Không lấy được dữ liệu, thử lại sau 1 phút...")
            time.sleep(60)
            continue
        
        print(f"Chờ {interval_seconds//60} phút cho lần thu thập tiếp theo...")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nĐã dừng chương trình. Dữ liệu đã lưu trong crypto_prices.csv")
