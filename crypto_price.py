#!/usr/bin/env python3
"""
Ivy - Simple Crypto Price Checker
測試用小程式
"""

import requests
import json
import sys

def get_crypto_price(symbol="BTC"):
    """從 CoinGecko 取得加密貨幣價格"""
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": symbol.lower(),
        "vs_currencies": "usd"
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data.get(symbol.lower(), {}).get("usd", None)
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    crypto = sys.argv[1].upper() if len(sys.argv) > 1 else "BTC"
    price = get_crypto_price(crypto)
    
    if price:
        print(f"{crypto}: ${price:,.2f} USD")
    else:
        print(f"無法取得 {crypto} 價格")

if __name__ == "__main__":
    main()
