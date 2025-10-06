# market_scanner.py
import requests
from datetime import datetime

class LightweightScanner:
    def __init__(self):
        self.api_base = "https://server-test-ovta.onrender.com"
        self.timeout = 15
    
    def scan_market(self, limit=100):
        """اسکنر ساده شده"""
        try:
            print(f"🔍 اسکن بازار با limit={limit}")
            response = requests.get(f"{self.api_base}/api/scan/vortexai?limit={limit}", timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    coins = data.get('coins', [])
                    print(f"✅ {len(coins)} ارز دریافت شد")
                    
                    # پردازش ساده
                    processed_coins = []
                    for coin in coins:
                        processed_coins.append({
                            'name': coin.get('name', 'Unknown'),
                            'symbol': coin.get('symbol', 'UNK'),
                            'price': float(coin.get('price', 0)),
                            'priceChange24h': float(coin.get('priceChange24h', 0)),
                            'priceChange1h': float(coin.get('priceChange1h', 0)),
                            'volume': float(coin.get('volume', 0)),
                            'marketCap': float(coin.get('marketCap', 0))
                        })
                    
                    return {
                        'success': True,
                        'coins': processed_coins,
                        'count': len(processed_coins),
                        'source': 'api'
                    }
            
            # Fallback
            return self._get_fallback_data()
            
        except Exception as e:
            print(f"❌ خطا: {e}")
            return self._get_fallback_data()
    
    def _get_fallback_data(self):
        """داده نمونه"""
        return {
            'success': True,
            'coins': [
                {'name': 'Bitcoin', 'symbol': 'BTC', 'price': 50000, 'priceChange24h': 2.5, 'priceChange1h': 0.1, 'volume': 1000000, 'marketCap': 1000000000},
                {'name': 'Ethereum', 'symbol': 'ETH', 'price': 3000, 'priceChange24h': 1.8, 'priceChange1h': 0.2, 'volume': 500000, 'marketCap': 500000000},
                {'name': 'BNB', 'symbol': 'BNB', 'price': 400, 'priceChange24h': 3.2, 'priceChange1h': 0.3, 'volume': 200000, 'marketCap': 60000000},
            ],
            'count': 3,
            'source': 'fallback'
        }
