# market_scanner.py - نسخه مستقیم به سرور تو

import requests
from datetime import datetime
import time

class LightweightScanner:
    def __init__(self):
        self.api_base = "https://server-test-ovta.onrender.com"
        self.timeout = 25
        self.version = "7.0"

    def scan_market(self, limit=50):
        """اسکن مستقیم از سرور شما"""
        try:
            print(f"🚀 شروع اسکن از سرور: {self.api_base}")
            
            # تست سلامت سرور
            health_url = f"{self.api_base}/health"
            print(f"🔍 تست سلامت: {health_url}")
            
            health_response = requests.get(health_url, timeout=10)
            print(f"📊 وضعیت سلامت: {health_response.status_code}")
            
            if health_response.status_code != 200:
                print("❌ سرور سلامت نیست")
                return self._get_fallback_data()

            # درخواست اصلی به endpoint اسکن
            scan_url = f"{self.api_base}/api/scan/vortexai?limit={limit}&filter=volume"
            print(f"📡 درخواست به: {scan_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
            }
            
            response = requests.get(scan_url, headers=headers, timeout=self.timeout)
            print(f"📨 وضعیت پاسخ: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ داده دریافت شد - success: {data.get('success')}")
                
                if data.get('success'):
                    raw_coins = data.get('coins', [])
                    print(f"💰 تعداد ارزها از سرور: {len(raw_coins)}")
                    
                    # دیباگ کامل
                    if raw_coins:
                        self._debug_coin_data(raw_coins[0])
                    
                    # پردازش ساده داده‌ها
                    processed_coins = self._process_simple_coins(raw_coins)
                    
                    return {
                        'success': True,
                        'coins': processed_coins,
                        'count': len(processed_coins),
                        'source': 'api',
                        'timestamp': datetime.now().isoformat(),
                        'has_historical_data': True,  # چون از سرور تو میاد
                        'server_status': 'connected',
                        'raw_response': data  # برای دیباگ
                    }
                else:
                    print(f"❌ سرور success: false برگردوند")
                    return self._get_fallback_data()
            else:
                print(f"❌ HTTP خطا: {response.status_code}")
                print(f"📝 متن پاسخ: {response.text[:200]}...")
                return self._get_fallback_data()

        except Exception as e:
            print(f"❌ خطا در اسکن: {e}")
            return self._get_fallback_data()

    def _debug_coin_data(self, coin):
        """دیباگ داده‌های ارز"""
        print(f"\n🔍 دیباگ اولین ارز:")
        print(f"   نام: {coin.get('name')}")
        print(f"   نماد: {coin.get('symbol')}")
        print(f"   قیمت: {coin.get('price')}")
        
        # بررسی فیلدهای اصلی
        important_fields = ['change_1h', 'change_24h', 'volume', 'marketCap']
        for field in important_fields:
            value = coin.get(field)
            print(f"   {field}: {value}")

    def _process_simple_coins(self, raw_coins):
        """پردازش ساده ارزها"""
        processed_coins = []
        
        for coin in raw_coins:
            try:
                processed_coin = {
                    'name': coin.get('name', 'Unknown'),
                    'symbol': coin.get('symbol', 'UNK'),
                    'price': self._safe_float(coin.get('price')),
                    
                    # استفاده از change_* که از سرور میاد
                    'priceChange1h': self._safe_float(coin.get('change_1h')),
                    'priceChange4h': self._safe_float(coin.get('change_4h')),
                    'priceChange24h': self._safe_float(coin.get('change_24h')),
                    'priceChange7d': self._safe_float(coin.get('change_7d')),
                    'priceChange30d': self._safe_float(coin.get('change_30d')),
                    'priceChange180d': self._safe_float(coin.get('change_180d')),
                    
                    'volume': self._safe_float(coin.get('volume')),
                    'marketCap': self._safe_float(coin.get('marketCap')),
                    'has_real_historical_data': True,  # چون از سرور میاد
                    'data_source': 'direct_api'
                }
                
                processed_coins.append(processed_coin)
                
            except Exception as e:
                print(f"❌ خطا در پردازش ارز: {e}")
                continue
        
        return processed_coins

    def _safe_float(self, value):
        """تبدیل ایمن به float"""
        try:
            if value is None:
                return 0.0
            if isinstance(value, str):
                value = value.replace(',', '').replace('$', '').replace('%', '').strip()
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def _get_fallback_data(self):
        """داده‌های جایگزین"""
        print("🔄 فعال شدن حالت fallback")
        
        fallback_coins = [
            {
                'name': 'Bitcoin',
                'symbol': 'BTC',
                'price': 45234.56,
                'priceChange1h': 0.56,
                'priceChange4h': 1.23,
                'priceChange24h': 2.34,
                'priceChange7d': 5.67,
                'priceChange30d': 15.89,
                'priceChange180d': 45.12,
                'volume': 25467890000,
                'marketCap': 885234567890,
                'has_real_historical_data': False,
                'data_source': 'fallback'
            }
        ]
        
        return {
            'success': True,
            'coins': fallback_coins,
            'count': len(fallback_coins),
            'source': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'has_historical_data': False,
            'server_status': 'disconnected'
        }

    def test_direct_endpoints(self):
        """تست مستقیم endpoint های سرور"""
        print("\n" + "="*50)
        print("🔧 تست مستقیم endpoint ها")
        print("="*50)
        
        endpoints = [
            "/health",
            "/api/health",
            "/api/scan/vortexai?limit=3",
            "/api/health-combined"
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{self.api_base}{endpoint}"
                print(f"\n🔍 تست: {url}")
                
                response = requests.get(url, timeout=10)
                print(f"   وضعیت: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ موفق")
                    if endpoint == "/api/scan/vortexai?limit=3":
                        print(f"   ارزها: {len(data.get('coins', []))}")
                else:
                    print(f"   ❌ خطا: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   ❌ استثنا: {e}")


# تست مستقیم
if __name__ == "__main__":
    scanner = LightweightScanner()
    
    print("🎯 تست مستقیم اتصال به سرور")
    print("="*50)
    
    # تست endpoint ها
    scanner.test_direct_endpoints()
    
    print("\n🔍 اجرای اسکن اصلی...")
    result = scanner.scan_market(limit=10)
    
    print(f"\n🎯 نتیجه نهایی:")
    print(f"   موفق: {result['success']}")
    print(f"   منبع: {result['source']}")
    print(f"   تعداد: {result['count']}")
    print(f"   وضعیت سرور: {result.get('server_status')}")
