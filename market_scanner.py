# market_scanner.py - نسخه کاملاً اصلاح شده

import requests
from datetime import datetime
import random

class LightweightScanner:
    def __init__(self):
        self.api_base = "https://server-test-ovta.onrender.com"
        self.timeout = 30
        self.version = "5.0"

    def scan_market(self, limit=100):
        """اسکن بازار - نسخه کاملاً اصلاح شده"""
        try:
            print(f"🚀 شروع اسکن از: {self.api_base}")
            
            # تست مستقیم endpoint اصلی
            scan_url = f"{self.api_base}/api/scan/vortexai?limit={limit}&filter=volume"
            print(f"📡 درخواست به: {scan_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate, br',
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
                        self._debug_first_coin(raw_coins[0])
                    
                    # پردازش داده‌ها
                    processed_coins = self._process_coins(raw_coins)
                    
                    return {
                        'success': True,
                        'coins': processed_coins,
                        'count': len(processed_coins),
                        'source': 'api',
                        'timestamp': datetime.now().isoformat(),
                        'has_historical_data': any(coin.get('has_real_historical_data', False) for coin in processed_coins),
                        'server_status': 'connected',
                        'raw_data_sample': raw_coins[0] if raw_coins else None
                    }
                else:
                    print(f"❌ سرور success: false برگردوند")
                    print(f"📝 خطا: {data.get('error', 'Unknown')}")
                    return self._get_fallback_data()
            else:
                print(f"❌ HTTP خطا: {response.status_code}")
                print(f"📝 متن پاسخ: {response.text[:500]}...")
                return self._get_fallback_data()

        except Exception as e:
            print(f"❌ خطا در اسکن: {e}")
            import traceback
            print(f"🔍 جزئیات: {traceback.format_exc()}")
            return self._get_fallback_data()

    def _debug_first_coin(self, coin):
        """دیباگ اولین ارز"""
        print(f"\n🔍 دیباگ اولین ارز:")
        print(f"   نام: {coin.get('name')}")
        print(f"   نماد: {coin.get('symbol')}")
        print(f"   قیمت: {coin.get('price')}")
        print(f"   حجم: {coin.get('volume')}")
        
        # بررسی فیلدهای تاریخی
        historical_fields = ['change_1h', 'change_4h', 'change_24h', 'change_7d', 'change_30d', 'change_180d']
        print("   📊 فیلدهای تاریخی:")
        has_historical = False
        for field in historical_fields:
            value = coin.get(field)
            if value not in [None, 0, '0', '']:
                has_historical = True
                print(f"     ✅ {field}: {value}")
            else:
                print(f"     ❌ {field}: {value}")
        
        print(f"   📈 داده تاریخی: {'✅ دارد' if has_historical else '❌ ندارد'}")

    def _process_coins(self, raw_coins):
        """پردازش ارزها"""
        processed_coins = []
        
        print(f"🔧 شروع پردازش {len(raw_coins)} ارز...")
        
        for i, coin in enumerate(raw_coins):
            try:
                # تشخیص داده تاریخی واقعی
                has_real_data = self._has_real_historical_data(coin)
                
                # پردازش داده‌ها
                processed_coin = {
                    'name': coin.get('name', 'Unknown'),
                    'symbol': coin.get('symbol', 'UNK'),
                    'price': self._safe_float(coin.get('price')),
                    
                    # داده‌های تاریخی
                    'priceChange1h': self._safe_float(coin.get('change_1h')),
                    'priceChange4h': self._safe_float(coin.get('change_4h')),
                    'priceChange24h': self._safe_float(coin.get('change_24h')),
                    'priceChange7d': self._safe_float(coin.get('change_7d')),
                    'priceChange30d': self._safe_float(coin.get('change_30d')),
                    'priceChange180d': self._safe_float(coin.get('change_180d')),
                    
                    'volume': self._safe_float(coin.get('volume')),
                    'marketCap': self._safe_float(coin.get('marketCap')),
                    'has_real_historical_data': has_real_data,
                    'data_source': 'real_api' if has_real_data else 'api_no_historical',
                    'raw_coin': coin  # نگه داشتن داده خام برای دیباگ
                }
                
                # اضافه کردن تحلیل VortexAI
                vortex_data = coin.get('VortexAI_analysis') or coin.get('vortexai_analysis') or {}
                if vortex_data:
                    processed_coin['VortexAI_analysis'] = vortex_data
                
                processed_coins.append(processed_coin)
                
                # دیباگ ۳ ارز اول
                if i < 3:
                    print(f"   🎯 ارز {i+1}: {processed_coin['symbol']} - داده تاریخی: {'✅' if has_real_data else '❌'}")
                
            except Exception as e:
                print(f"❌ خطا در پردازش ارز {i}: {e}")
                continue
        
        print(f"📊 پردازش کامل: {len(processed_coins)} ارز")
        return processed_coins

    def _has_real_historical_data(self, coin):
        """تشخیص وجود داده تاریخی واقعی"""
        historical_fields = ['change_1h', 'change_4h', 'change_24h', 'change_7d', 'change_30d', 'change_180d']
        for field in historical_fields:
            if coin.get(field) not in [None, 0, '0', '']:
                return True
        return False

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
            },
            {
                'name': 'Ethereum',
                'symbol': 'ETH',
                'price': 2389.12,
                'priceChange1h': -0.34,
                'priceChange4h': 0.89,
                'priceChange24h': 1.23,
                'priceChange7d': 3.45,
                'priceChange30d': 12.34,
                'priceChange180d': 38.76,
                'volume': 14567890000,
                'marketCap': 287123456789,
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

    def test_direct_connection(self):
        """تست مستقیم اتصال"""
        print("\n" + "="*50)
        print("🔧 تست مستقیم اتصال")
        print("="*50)
        
        try:
            # تست سلامت
            health_url = f"{self.api_base}/health"
            health_response = requests.get(health_url, timeout=10)
            print(f"✅ سلامت: {health_response.status_code}")
            
            # تست endpoint اصلی
            scan_url = f"{self.api_base}/api/scan/vortexai?limit=3"
            response = requests.get(scan_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ اسکن: {data.get('success')}")
                
                if data.get('success') and data.get('coins'):
                    coins = data['coins']
                    print(f"💰 ارزها: {len(coins)}")
                    
                    # بررسی اولین ارز
                    if coins:
                        coin = coins[0]
                        print(f"🎯 اولین ارز: {coin.get('name')} ({coin.get('symbol')})")
                        
                        # بررسی فیلدهای تاریخی
                        hist_fields = [k for k in coin.keys() if 'change' in k.lower()]
                        print(f"📊 فیلدهای تاریخی: {hist_fields}")
                        
                        for field in hist_fields[:3]:  # فقط ۳ فیلد اول
                            print(f"   {field}: {coin.get(field)}")
                    
                    return True, data
                else:
                    print(f"❌ داده نامعتبر: {data}")
                    return False, data
            else:
                print(f"❌ HTTP: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"❌ خطا: {e}")
            return False, None


# تست مستقیم
if __name__ == "__main__":
    scanner = LightweightScanner()
    
    print("🎯 تست مستقیم اسکنر")
    print("="*50)
    
    # تست اتصال
    connection_ok, test_data = scanner.test_direct_connection()
    
    if connection_ok:
        print("\n🔍 اجرای اسکن اصلی...")
        result = scanner.scan_market(limit=10)
        
        print(f"\n🎯 نتیجه نهایی:")
        print(f"   موفق: {result['success']}")
        print(f"   منبع: {result['source']}")
        print(f"   تعداد: {result['count']}")
        print(f"   داده تاریخی: {result.get('has_historical_data')}")
        print(f"   وضعیت سرور: {result.get('server_status')}")
        
        if result['coins']:
            print(f"\n📈 نمونه ارزها:")
            for coin in result['coins'][:3]:
                status = "✅ واقعی" if coin.get('has_real_historical_data') else "❌ دمو"
                print(f"   {coin['symbol']}: ${coin['price']:.2f} | 24h: {coin['priceChange24h']}% | {status}")
    else:
        print("\n❌ اتصال به API برقرار نیست")
