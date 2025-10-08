# market_scanner.py

import requests
from datetime import datetime
import random

class LightweightScanner:
    def __init__(self):
        self.api_base = "https://server-test-ovta.onrender.com"
        self.timeout = 20  # افزایش timeout
        self.version = "3.0"

    def scan_market(self, limit=100):
        """اسکن بازار - با دیباگ کامل"""
        try:
            print(f"🚀 شروع اسکن از: {self.api_base}")
            
            # تست اولیه
            health_url = f"{self.api_base}/health"
            print(f"🔍 تست سلامت: {health_url}")
            
            health_response = requests.get(health_url, timeout=10)
            print(f"📊 وضعیت سلامت: {health_response.status_code}")
            
            if health_response.status_code != 200:
                print("❌ سرور سلامت نیست")
                return self._get_fallback_data()
            
            # درخواست اصلی
            scan_url = f"{self.api_base}/api/scan/vortexai?limit={limit}"
            print(f"📡 درخواست اصلی: {scan_url}")
            
            response = requests.get(scan_url, timeout=self.timeout)
            print(f"📨 وضعیت پاسخ: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ داده دریافت شد - success: {data.get('success')}")
                
                if data.get('success'):
                    raw_coins = data.get('coins', [])
                    print(f"🎯 تعداد ارزها: {len(raw_coins)}")
                    
                    # دیباگ اولین ارز
                    if raw_coins:
                        first_coin = raw_coins[0]
                        print(f"🔍 اولین ارز: {first_coin.get('name')} ({first_coin.get('symbol')})")
                        
                        # بررسی فیلدهای تاریخی
                        historical_fields = ['change_1h', 'change_4h', 'change_7d', 'change_30d', 'change_180d']
                        for field in historical_fields:
                            value = first_coin.get(field)
                            print(f"   - {field}: {value} (نوع: {type(value)})")
                    
                    processed_coins = self._process_coins_with_fallback(raw_coins)
                    
                    return {
                        'success': True,
                        'coins': processed_coins,
                        'count': len(processed_coins),
                        'source': 'api',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    print("❌ سرور success: false برگردوند")
                    print(f"📝 پیام خطا: {data.get('error', 'Unknown')}")
            else:
                print(f"❌ خطای HTTP: {response.status_code}")
                print(f"📝 متن پاسخ: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print("⏰ timeout - سرور پاسخ نمیده")
        except requests.exceptions.ConnectionError as e:
            print(f"🔌 خطای اتصال: {e}")
        except requests.exceptions.RequestException as e:
            print(f"🌐 خطای شبکه: {e}")
        except Exception as e:
            print(f"💥 خطای ناشناخته: {e}")
            import traceback
            print(f"📋 جزئیات: {traceback.format_exc()}")
        
        print("🔄 فعال کردن حالت fallback")
        return self._get_fallback_data()
        
    def _process_coins_with_fallback(self, raw_coins):
        """پردازش بدون داده ساختگی"""
        processed_coins = []

        for i, coin in enumerate(raw_coins):
            try:
                name = coin.get('name', 'Unknown')
                symbol = coin.get('symbol', 'UNK')

                # ✅ فقط از داده‌های واقعی استفاده میشه
                price_changes = {
                    '1h': self._safe_float(coin.get('change_1h', coin.get('priceChange1h'))),
                    '4h': self._safe_float(coin.get('change_4h')),
                    '24h': self._safe_float(coin.get('change_24h', coin.get('priceChange24h'))),
                    '7d': self._safe_float(coin.get('change_7d')),
                    '30d': self._safe_float(coin.get('change_30d')),
                    '180d': self._safe_float(coin.get('change_180d'))
                }

                # ❌ هیچ داده ساختگی تولید نمیشه
                processed_coin = {
                    'name': self._get_real_name(symbol, name),
                    'symbol': symbol,
                    'price': self._safe_float(coin.get('price')),
                    'priceChange1h': price_changes['1h'],
                    'priceChange4h': price_changes['4h'],
                    'priceChange24h': price_changes['24h'],
                    'priceChange7d': price_changes['7d'],
                    'priceChange30d': price_changes['30d'],
                    'priceChange180d': price_changes['180d'],
                    'volume': self._safe_float(coin.get('volume')),
                    'marketCap': self._safe_float(coin.get('marketCap'))
                }

                processed_coins.append(processed_coin)

            except Exception as e:
                print(f'خطا در پردازش ارز {i}: {e}')
                continue

        return processed_coins

    def _generate_realistic_change(self, timeframe):
        """تولید تغییرات واقعی"""
        ranges = {
            '1h': (-3, 3),
            '4h': (-6, 6),
            '24h': (-12, 12),
            '7d': (-20, 25),
            '30d': (-35, 40),
            '180d': (-50, 80)
        }
        min_val, max_val = ranges.get(timeframe, (-5, 5))
        return round(random.uniform(min_val, max_val), 2)

    def _get_real_name(self, symbol, current_name):
        """تبدیل به نام واقعی"""
        symbol_map = {
            'BTC': 'Bitcoin', 'ETH': 'Ethereum', 'BNB': 'BNB', 'SOL': 'Solana',
            'XRP': 'XRP', 'ADA': 'Cardano', 'AVAX': 'Avalanche', 'DOT': 'Polkadot',
            'LINK': 'Chainlink', 'MATIC': 'Polygon', 'LTC': 'Litecoin', 'BCH': 'Bitcoin Cash',
        }
        if current_name.startswith('Crypto'):
            return symbol_map.get(symbol, f'Crypto {symbol}')
        return current_name

    def _safe_float(self, value):
        try:
            if value is None:
                return 0.0
            return float(value)
        except:
            return 0.0

    def _get_fallback_data(self):
        """فقط برای مواقع ضروری"""
        print("🔄 فعال شدن حالت fallback کامل")
        # ... کد fallback

# تست
if __name__ == "__main__":
    scanner = LightweightScanner()
    result = scanner.scan_market(limit=3)
    print(f"\n🎯 نتیجه نهایی:")
    print(f"   - موفق: {result['success']}")
    print(f"   - منبع: {result['source']}")
    print(f"   - تعداد: {result['count']}")
