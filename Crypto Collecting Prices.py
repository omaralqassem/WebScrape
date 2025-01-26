import requests
import pandas as pd
from datetime import datetime
import time

COINGECKO_COINS_URL = 'https://api.coingecko.com/api/v3/coins/markets'
COINGECKO_HISTORICAL_URL = 'https://api.coingecko.com/api/v3/coins/{id}/market_chart'

def fetch_data(url, params=None, retries=5, delay=10):
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  
                print(f"Attempt {attempt + 1}: Rate limit exceeded. Waiting {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Attempt {attempt + 1} failed: Status code {response.status_code}")
                print(f"Error: {response.text}")
                return None
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
    print("Max retries reached. Failed to fetch data.")
    return None

def get_all_coins(currency='usd'):
    params = {
        'vs_currency': currency,
        'order': 'market_cap_desc',
        'per_page': 250,  
        'page': 1,
        'sparkline': False,
    }
    return fetch_data(COINGECKO_COINS_URL, params=params)

def get_coin_historical_data(coin_id, currency='usd', days=365):
    url = COINGECKO_HISTORICAL_URL.format(id=coin_id)
    params = {
        'vs_currency': currency,
        'days': days,  
    }
    return fetch_data(url, params=params)

def main():
    print("Fetching list of all coins...")
    coins_data = get_all_coins()

    if not coins_data:
        print("Failed to fetch coins data.")
        return

    all_historical_data = []
    num_coins_to_scrape = 5  
    for coin in coins_data[:num_coins_to_scrape]:
        coin_id = coin['id']
        coin_name = coin['name']
        print(f"Fetching historical data for {coin_name} ({coin_id})...")

        historical_data = get_coin_historical_data(coin_id, days=365)

        if historical_data:
            prices = historical_data.get('prices', [])
            for price in prices:
                timestamp = datetime.fromtimestamp(price[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                all_historical_data.append({
                    'Coin ID': coin_id,
                    'Coin Name': coin_name,
                    'Timestamp': timestamp,
                    'Price (USD)': price[1],
                })
        else:
            print(f"Skipping {coin_name} due to missing data.")

        time.sleep(12) 

    df = pd.DataFrame(all_historical_data)
    df.to_csv('crypto_historical_prices.csv', index=False)
    print("Historical data saved to 'crypto_historical_prices.csv'")

if __name__ == '__main__':
    main()