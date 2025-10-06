# market_scanner.py
import requests
import json
from datetime import datetime

class LightweightScanner:
    def __init__(self):
        self.api_base = "https://server-test-ovta.onrender.com"
        self.timeout = 15  # افزایش تایم‌اوت
    
    def scan_market(self, limit=100):
        """اسکن بازار - هماهنگ با سرور میانی (حداکثر ۱۰۰ ارز)"""
        try:
            print(f"🔍 درخواست {limit} ارز از سرور...")
            
            # تلاش برای اتصال به API
            response = requests.get(
                f"{self.api_base}/api/scan/vortexai?limit={limit}",
                timeout=self.timeout
            )
            
            print(f"📡 وضعیت پاسخ سرور: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 ساختار داده دریافتی: {list(data.keys())}")
                
                if data.get('success'):
                    raw_coins = data.get('coins', [])
                    print(f"✅ سرور {len(raw_coins)} ارز برگردوند")
                    
                    coins = self._process_coins(raw_coins)
                    print(f"🎯 {len(coins)} ارز با موفقیت پردازش شد")
                    
                    return {
                        'success': True,
                        'coins': coins,
                        'count': len(coins),
                        'source': 'api',
                        'timestamp': datetime.now().isoformat(),
                        'server_limit': 100  # اطلاعات محدودیت سرور
                    }
                else:
                    print(f"❌ سرور success: false - {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ خطای HTTP: {response.status_code}")
                print(f"📝 متن پاسخ: {response.text[:200]}...")
            
            # اگر API جواب نداد، از داده نمونه استفاده کن
            print("⚠️ استفاده از داده نمونه به دلیل خطای API")
            return self._get_fallback_data()
            
        except Exception as e:
            print(f"❌ خطا در اسکن: {e}")
            import traceback
            print(f"🔍 جزئیات خطا: {traceback.format_exc()}")
            return self._get_fallback_data()
    
    def _process_coins(self, raw_coins):
        """پردازش امن داده‌های ارزها - بدون محدودیت"""
        processed_coins = []
        
        print(f"🔧 شروع پردازش {len(raw_coins)} ارز خام...")
        
        for i, coin in enumerate(raw_coins):
            try:
                processed_coin = {
                    'name': str(coin.get('name', f'Unknown_{i}')),
                    'symbol': str(coin.get('symbol', f'UNK_{i}')),
                    'price': float(coin.get('price') or coin.get('realtime_price') or 0),
                    'priceChange24h': float(coin.get('priceChange24h') or coin.get('priceChange1d') or 0),
                    'priceChange1h': float(coin.get('priceChange1h') or 0),
                    'volume': float(coin.get('volume') or coin.get('realtime_volume') or 0),
                    'marketCap': float(coin.get('marketCap') or 0),
                    'index': i  # اضافه کردن ایندکس برای ردیابی
                }
                processed_coins.append(processed_coin)
                
                # لاگ هر 10 ارز
                if (i + 1) % 10 == 0:
                    print(f"   ✅ {i + 1} ارز پردازش شد...")
                    
            except Exception as e:
                print(f"   ⚠️ خطا در پردازش ارز {i}: {e}")
                continue  # اگر خطا داشت، برو به بعدی
        
        print(f"🎉 پردازش کامل: {len(processed_coins)} از {len(raw_coins)} ارز موفق")
        return processed_coins
    
    def _get_fallback_data(self):
        """داده نمونه با کیفیت - ۱۰ ارز برای تست"""
        print("🔄 استفاده از داده نمونه داخلی")
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
                    'marketCap': 1287654321098,
                    'index': 0
                },
                {
                    'name': 'Ethereum',
                    'symbol': 'ETH',
                    'price': 3456.78,
                    'priceChange24h': 1.87,
                    'priceChange1h': -0.15,
                    'volume': 18765432987,
                    'marketCap': 415678901234,
                    'index': 1
                },
                {
                    'name': 'BNB',
                    'symbol': 'BNB',
                    'price': 567.89,
                    'priceChange24h': 3.21,
                    'priceChange1h': 0.45,
                    'volume': 2987654321,
                    'marketCap': 87654321098,
                    'index': 2
                },
                {
                    'name': 'Solana',
                    'symbol': 'SOL',
                    'price': 123.45,
                    'priceChange24h': -1.23,
                    'priceChange1h': -0.32,
                    'volume': 1987654321,
                    'marketCap': 54321098765,
                    'index': 3
                },
                {
                    'name': 'XRP',
                    'symbol': 'XRP',
                    'price': 0.567,
                    'priceChange24h': 0.45,
                    'priceChange1h': 0.12,
                    'volume': 987654321,
                    'marketCap': 30456789012,
                    'index': 4
                },
                {
                    'name': 'Cardano',
                    'symbol': 'ADA',
                    'price': 0.456,
                    'priceChange24h': 1.23,
                    'priceChange1h': 0.08,
                    'volume': 876543210,
                    'marketCap': 16234567890,
                    'index': 5
                },
                {
                    'name': 'Dogecoin',
                    'symbol': 'DOGE',
                    'price': 0.123,
                    'priceChange24h': 4.56,
                    'priceChange1h': 0.25,
                    'volume': 765432109,
                    'marketCap': 17654321098,
                    'index': 6
                },
                {
                    'name': 'Polkadot',
                    'symbol': 'DOT',
                    'price': 6.78,
                    'priceChange24h': -0.89,
                    'priceChange1h': -0.12,
                    'volume': 654321098,
                    'marketCap': 8765432109,
                    'index': 7
                },
                {
                    'name': 'Litecoin',
                    'symbol': 'LTC',
                    'price': 78.90,
                    'priceChange24h': 0.67,
                    'priceChange1h': 0.05,
                    'volume': 543210987,
                    'marketCap': 5654321098,
                    'index': 8
                },
                {
                    'name': 'Chainlink',
                    'symbol': 'LINK',
                    'price': 12.34,
                    'priceChange24h': 2.34,
                    'priceChange1h': 0.15,
                    'volume': 432109876,
                    'marketCap': 6543210987,
                    'index': 9
                }
            ],
            'count': 10,
            'source': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'server_limit': 100
        }
