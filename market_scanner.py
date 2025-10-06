# market_scanner.py
import requests
import json
from datetime import datetime

class LightweightScanner:
    def __init__(self):
        self.api_base = "https://server-test-ovta.onrender.com"
        self.timeout = 10
    
    def scan_market(self, limit=50):
        """اسکن بازار - نسخه سبک با مدیریت خطا"""
        try:
            print(f"🔍 در حال اسکن بازار از {self.api_base}...")
            
            # تلاش برای اتصال به API
            response = requests.get(
                f"{self.api_base}/api/scan/vortexai?limit={limit}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    coins = self._process_coins(data.get('coins', []))
                    print(f"✅ اسکن موفق: {len(coins)} ارز دریافت شد")
                    return {
                        'success': True,
                        'coins': coins,
                        'count': len(coins),
                        'source': 'api',
                        'timestamp': datetime.now().isoformat()
                    }
            
            # اگر API جواب نداد، از داده نمونه استفاده کن
            print("⚠️ استفاده از داده نمونه به دلیل خطای API")
            return self._get_fallback_data()
            
        except Exception as e:
            print(f"❌ خطا در اسکن: {e}")
            return self._get_fallback_data()
    
    def _process_coins(self, raw_coins):
        """پردازش امن داده‌های ارزها"""
        processed_coins = []
        
        for coin in raw_coins[:20]:  # فقط 20 ارز اول برای سرعت
            try:
                processed_coin = {
                    'name': str(coin.get('name', 'Unknown')),
                    'symbol': str(coin.get('symbol', 'UNK')),
                    'price': float(coin.get('price') or coin.get('realtime_price') or 0),
                    'priceChange24h': float(coin.get('priceChange24h') or coin.get('priceChange1d') or 0),
                    'priceChange1h': float(coin.get('priceChange1h') or 0),
                    'volume': float(coin.get('volume') or coin.get('realtime_volume') or 0),
                    'marketCap': float(coin.get('marketCap') or 0)
                }
                processed_coins.append(processed_coin)
            except:
                continue  # اگر خطا داشت، برو به بعدی
        
        return processed_coins
    
    def _get_fallback_data(self):
        """داده نمونه با کیفیت"""
        return {
            'success': True,
            'coins': [
                {
                    'name': 'Bitcoin',
                    'symbol': 'BTC', 
                    'price': 65432.10,
                    'priceChange24h': 2.15,
                    'priceChange1h': 0.32,
                    'volume': 39245678901,
                    'marketCap': 1287654321098
                },
                {
                    'name': 'Ethereum',
                    'symbol': 'ETH',
                    'price': 3456.78,
                    'priceChange24h': 1.87,
                    'priceChange1h': -0.15,
                    'volume': 18765432987,
                    'marketCap': 415678901234
                },
                {
                    'name': 'BNB',
                    'symbol': 'BNB',
                    'price': 567.89,
                    'priceChange24h': 3.21,
                    'priceChange1h': 0.45,
                    'volume': 2987654321,
                    'marketCap': 87654321098
                },
                {
                    'name': 'Solana',
                    'symbol': 'SOL',
                    'price': 123.45,
                    'priceChange24h': -1.23,
                    'priceChange1h': -0.32,
                    'volume': 1987654321,
                    'marketCap': 54321098765
                },
                {
                    'name': 'XRP',
                    'symbol': 'XRP',
                    'price': 0.567,
                    'priceChange24h': 0.45,
                    'priceChange1h': 0.12,
                    'volume': 987654321,
                    'marketCap': 30456789012
                }
            ],
            'count': 5,
            'source': 'fallback',
            'timestamp': datetime.now().isoformat()
        }
