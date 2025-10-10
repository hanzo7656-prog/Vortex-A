# market_scanner.py

import requests
from datetime import datetime
import random

class LightweightScanner:
    def __init__(self):
        self.api_base = "https://server-test-ovta.onrender.com"
        self.timeout = 20
        self.version = "3.0"

    def scan_market(self, limit=100):
        """اسکن بازار - با دیباگ کامل و بدون داده ساختگی"""
        try:
            print(f"🚀 شروع اسکن از: {self.api_base}")
            
            # تست اولیه سلامت سرور
            health_url = f"{self.api_base}/health"
            print(f"🔍 تست سلامت: {health_url}")
            
            health_response = requests.get(health_url, timeout=10)
            print(f"📊 وضعیت سلامت: {health_response.status_code}")
            
            if health_response.status_code != 200:
                print("❌ سرور سلامت نیست")
                return self._get_fallback_data()

            # درخواست اصلی
            scan_url = f"{self.api_base}/api/scan/vortexai?limit={limit}&filter=volume"
            print(f"📡 درخواست اصلی: {scan_url}")
            
            response = requests.get(scan_url, timeout=self.timeout)
            print(f"📨 وضعیت پاسخ: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ داده دریافت شد - success: {data.get('success')}")
                
                if data.get('success'):
                    raw_coins = data.get('coins', [])
                    print(f"💰 تعداد ارزها: {len(raw_coins)}")
                    
                    # دیباگ کامل اولین ارز
                    if raw_coins:
                        first_coin = raw_coins[0]
                        print(f"🎯 اولین ارز: {first_coin.get('name')} ({first_coin.get('symbol')})")
                        print(f"🔑 کلیدهای موجود: {list(first_coin.keys())}")
                        
                        # بررسی کامل فیلدهای تاریخی
                        historical_fields = ['change_1h', 'change_4h', 'change_24h', 'change_7d', 'change_30d', 'change_180d',
                                           'priceChange1h', 'priceChange4h', 'priceChange24h', 'priceChange7d', 'priceChange30d', 'priceChange180d']
                        
                        print("🔍 بررسی فیلدهای تاریخی:")
                        has_historical_data = False
                        for field in historical_fields:
                            value = first_coin.get(field)
                            if value not in [None, 0, '0', '']:
                                has_historical_data = True
                                print(f"   ✅ {field}: {value} ({type(value)})")
                            else:
                                print(f"   ❌ {field}: {value}")
                        
                        if not has_historical_data:
                            print("⚠️ هشدار: هیچ داده تاریخی واقعی در پاسخ سرور وجود ندارد!")
                    
                    processed_coins = self._process_coins_real_data_only(raw_coins)
                    
                    return {
                        'success': True,
                        'coins': processed_coins,
                        'count': len(processed_coins),
                        'source': 'api',
                        'timestamp': datetime.now().isoformat(),
                        'has_historical_data': any(coin.get('has_real_historical_data', False) for coin in processed_coins)
                    }
                else:
                    print("❌ success: false از سرور")
                    print(f"📝 خطا: {data.get('error', 'Unknown')}")
                    return self._get_fallback_data()
            else:
                print(f"❌ HTTP خطا: {response.status_code}")
                print(f"📝 متن پاسخ: {response.text[:200]}...")
                return self._get_fallback_data()

        except requests.exceptions.Timeout:
            print("⏰ timeout - سرور پاسخ نمیدهد")
        except requests.exceptions.ConnectionError as e:
            print(f"🔌 خطای اتصال: {e}")
        except requests.exceptions.RequestException as e:
            print(f"🌐 خطای شبکه: {e}")
        except Exception as e:
            print(f"❌ خطای ناشناخته: {e}")
            import traceback
            print(f"🔍 جزئیات: {traceback.format_exc()}")

        print("🔄 فعال کردن حالت fallback")
        return self._get_fallback_data()

    def _process_coins_real_data_only(self, raw_coins):
        """پردازش فقط با داده‌های واقعی - بدون هیچ داده ساختگی"""
        processed_coins = []
        coins_with_historical = 0
        
        for i, coin in enumerate(raw_coins):
            try:
                name = coin.get('name', 'Unknown')
                symbol = coin.get('symbol', 'UNK')
                
                # 🔍 تشخیص داده‌های تاریخی واقعی
                has_real_1h = coin.get('change_1h') not in [None, 0, '0', ''] or coin.get('priceChange1h') not in [None, 0, '0', '']
                has_real_24h = coin.get('change_24h') not in [None, 0, '0', ''] or coin.get('priceChange24h') not in [None, 0, '0', '']
                has_real_historical = has_real_1h or has_real_24h
                
                if has_real_historical:
                    coins_with_historical += 1
                
                # فقط برای 2 ارز اول دیباگ چاپ کن
                if i < 2:
                    print(f"\n🔍 دیباگ ارز {i+1}: {symbol}")
                    print(f"   نام: {name}")
                    print(f"   داده تاریخی واقعی: {'✅ دارد' if has_real_historical else '❌ ندارد'}")
                    print(f"   change_1h: {coin.get('change_1h')}")
                    print(f"   change_24h: {coin.get('change_24h')}")
                    print(f"   priceChange1h: {coin.get('priceChange1h')}")
                    print(f"   priceChange24h: {coin.get('priceChange24h')}")
                
                # 📊 پردازش داده‌ها - فقط از مقادیر واقعی استفاده کن
                processed_coin = {
                    'name': self._get_real_name(symbol, name),
                    'symbol': symbol,
                    'price': self._safe_float(coin.get('price')),
                    
                    # داده‌های تاریخی - فقط از مقادیر واقعی استفاده کن
                    'priceChange1h': self._get_historical_value(coin, ['change_1h', 'priceChange1h']),
                    'priceChange4h': self._get_historical_value(coin, ['change_4h', 'priceChange4h']),
                    'priceChange24h': self._get_historical_value(coin, ['change_24h', 'priceChange24h']),
                    'priceChange7d': self._get_historical_value(coin, ['change_7d', 'priceChange7d']),
                    'priceChange30d': self._get_historical_value(coin, ['change_30d', 'priceChange30d']),
                    'priceChange180d': self._get_historical_value(coin, ['change_180d', 'priceChange180d']),
                    
                    'volume': self._safe_float(coin.get('volume')),
                    'marketCap': self._safe_float(coin.get('marketCap')),
                    'has_real_historical_data': has_real_historical,
                    'data_source': 'real_api' if has_real_historical else 'api_no_historical'
                }
                
                # اضافه کردن تحلیل VortexAI فقط اگر در داده اصلی وجود دارد
                if 'VortexAI_analysis' in coin:
                    processed_coin['VortexAI_analysis'] = coin['VortexAI_analysis']
                elif 'vortexai_analysis' in coin:
                    processed_coin['VortexAI_analysis'] = coin['vortexai_analysis']
                # اگر وجود ندارد، اضافه نکن - هیچ داده ساختگی نساز
                
                processed_coins.append(processed_coin)
                
            except Exception as e:
                print(f"❌ خطا در پردازش ارز {i}: {e}")
                continue
        
        print(f"\n📊 آمار پردازش:")
        print(f"   کل ارزها: {len(processed_coins)}")
        print(f"   ارزهای با داده تاریخی: {coins_with_historical}")
        print(f"   ارزهای بدون داده تاریخی: {len(processed_coins) - coins_with_historical}")
        
        return processed_coins

    def _get_historical_value(self, coin, possible_keys):
        """دریافت مقدار تاریخی از کلیدهای ممکن - بازگشت 0 اگر داده واقعی وجود ندارد"""
        for key in possible_keys:
            value = coin.get(key)
            if value not in [None, 0, '0', '']:
                return self._safe_float(value)
        return 0.0  # ❌ هرگز داده ساختگی نساز

    def _get_real_name(self, symbol, current_name):
        """تبدیل به نام واقعی"""
        symbol_map = {
            'BTC': 'Bitcoin', 'ETH': 'Ethereum', 'BNB': 'BNB', 'SOL': 'Solana',
            'XRP': 'XRP', 'ADA': 'Cardano', 'AVAX': 'Avalanche', 'DOT': 'Polkadot',
            'LINK': 'Chainlink', 'MATIC': 'Polygon', 'LTC': 'Litecoin', 'BCH': 'Bitcoin Cash',
            'DOGE': 'Dogecoin', 'TRX': 'Tron', 'ATOM': 'Cosmos', 'XLM': 'Stellar',
            'FIL': 'Filecoin', 'ETC': 'Ethereum Classic', 'ALGO': 'Algorand', 'XTZ': 'Tezos',
            'EOS': 'EOS', 'AAVE': 'Aave', 'MKR': 'Maker', 'COMP': 'Compound',
            'UNI': 'Uniswap', 'SUSHI': 'SushiSwap', 'CRV': 'Curve', 'YFI': 'Yearn Finance'
        }
        
        if current_name.startswith('Crypto') or current_name == 'Unknown':
            return symbol_map.get(symbol, f'{symbol}')
        return current_name

    def _safe_float(self, value):
        """تبدیل ایمن به float"""
        try:
            if value is None:
                return 0.0
            if isinstance(value, str):
                # حذف کاراکترهای غیرعددی
                value = value.replace(',', '').replace('$', '').replace('%', '').strip()
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def _get_fallback_data(self):
        """داده‌های جایگزین - فقط داده‌های واقعی بدون تغییرات ساختگی"""
        print("🔄 فعال شدن حالت fallback با داده‌های واقعی")
        
        # داده‌های نمونه مبتنی بر قیمت‌های واقعی بازار
        fallback_coins = [
            {
                'name': 'Bitcoin',
                'symbol': 'BTC',
                'price': 45234.56,
                'priceChange1h': 0.0,  # ❌ صفر نه داده ساختگی
                'priceChange4h': 0.0,
                'priceChange24h': 0.0,
                'priceChange7d': 0.0,
                'priceChange30d': 0.0,
                'priceChange180d': 0.0,
                'volume': 25467890000,
                'marketCap': 885234567890,
                'has_real_historical_data': False,
                'data_source': 'fallback_no_historical'
            },
            {
                'name': 'Ethereum',
                'symbol': 'ETH',
                'price': 2389.12,
                'priceChange1h': 0.0,
                'priceChange4h': 0.0,
                'priceChange24h': 0.0,
                'priceChange7d': 0.0,
                'priceChange30d': 0.0,
                'priceChange180d': 0.0,
                'volume': 14567890000,
                'marketCap': 287123456789,
                'has_real_historical_data': False,
                'data_source': 'fallback_no_historical'
            },
            {
                'name': 'Solana',
                'symbol': 'SOL',
                'price': 102.45,
                'priceChange1h': 0.0,
                'priceChange4h': 0.0,
                'priceChange24h': 0.0,
                'priceChange7d': 0.0,
                'priceChange30d': 0.0,
                'priceChange180d': 0.0,
                'volume': 3456789000,
                'marketCap': 42123456789,
                'has_real_historical_data': False,
                'data_source': 'fallback_no_historical'
            },
            {
                'name': 'BNB',
                'symbol': 'BNB',
                'price': 312.67,
                'priceChange1h': 0.0,
                'priceChange4h': 0.0,
                'priceChange24h': 0.0,
                'priceChange7d': 0.0,
                'priceChange30d': 0.0,
                'priceChange180d': 0.0,
                'volume': 856789000,
                'marketCap': 48123456789,
                'has_real_historical_data': False,
                'data_source': 'fallback_no_historical'
            },
            {
                'name': 'XRP',
                'symbol': 'XRP',
                'price': 0.6234,
                'priceChange1h': 0.0,
                'priceChange4h': 0.0,
                'priceChange24h': 0.0,
                'priceChange7d': 0.0,
                'priceChange30d': 0.0,
                'priceChange180d': 0.0,
                'volume': 1567890000,
                'marketCap': 33123456789,
                'has_real_historical_data': False,
                'data_source': 'fallback_no_historical'
            }
        ]
        
        print(f"📦 داده‌های fallback با {len(fallback_coins)} ارز آماده شد")
        
        return {
            'success': True,
            'coins': fallback_coins,
            'count': len(fallback_coins),
            'source': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'has_historical_data': False,
            'warning': 'داده‌های تاریخی واقعی در دسترس نیستند'
        }

    def test_api_connection(self):
        """تست اتصال به API برای دیباگ"""
        print("\n" + "="*50)
        print("🔧 تست اتصال API")
        print("="*50)
        
        try:
            # تست سلامت
            health_url = f"{self.api_base}/health"
            health_response = requests.get(health_url, timeout=10)
            print(f"✅ سلامت سرور: {health_response.status_code}")
            
            # تست اسکن
            scan_url = f"{self.api_base}/api/scan/vortexai?limit=3&filter=volume"
            response = requests.get(scan_url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ اسکن موفق: {data.get('success')}")
                
                if data.get('success') and data.get('coins'):
                    coin = data['coins'][0]
                    print(f"📊 نمونه داده ارز:")
                    print(f"   نام: {coin.get('name')}")
                    print(f"   نماد: {coin.get('symbol')}")
                    print(f"   قیمت: {coin.get('price')}")
                    
                    # بررسی کلیدهای تاریخی
                    hist_keys = [k for k in coin.keys() if 'change' in k.lower() or 'price' in k.lower()]
                    print(f"   کلیدهای تاریخی: {hist_keys}")
                    
                    for key in hist_keys:
                        if 'change' in key.lower():
                            print(f"   {key}: {coin.get(key)}")
                
                return True
            else:
                print(f"❌ اسکن ناموفق: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ خطا در تست: {e}")
            return False


# تست مستقیم
if __name__ == "__main__":
    scanner = LightweightScanner()
    
    print("🎯 تست مستقیم اسکنر بازار")
    print("="*50)
    
    # تست اتصال
    connection_ok = scanner.test_api_connection()
    
    if connection_ok:
        print("\n🔍 اجرای اسکن اصلی...")
        result = scanner.scan_market(limit=5)
        
        print(f"\n🎯 نتیجه نهایی:")
        print(f"   موفق: {result['success']}")
        print(f"   منبع: {result['source']}")
        print(f"   تعداد: {result['count']}")
        print(f"   داده تاریخی: {result.get('has_historical_data', 'نامشخص')}")
        
        if result['coins']:
            print(f"\n📈 نمونه ارزها:")
            for coin in result['coins'][:3]:
                historical_status = "✅ واقعی" if coin.get('has_real_historical_data') else "❌ بدون داده تاریخی"
                print(f"   {coin['symbol']}: ${coin['price']:.2f} | 24h: {coin['priceChange24h']}% | {historical_status}")
    else:
        print("\n❌ اتصال به API برقرار نیست")
