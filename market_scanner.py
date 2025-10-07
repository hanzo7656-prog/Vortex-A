# market_scanner.py

import requests
from datetime import datetime
import random

class LightweightScanner:
    def __init__(self):
        self.api_base = "https://server-test-ovta.onrender.com"
        self.timeout = 15
        self.version = "2.3"

    def scan_market(self, limit=100):
        """اسکن بازار - نسخه دیباگ"""
        try:
            print(f"🔍 درخواست {limit} ارز از سرور...")
            
            response = requests.get(
                f"{self.api_base}/api/scan/vortexai?limit={limit}",
                timeout=self.timeout
            )
            
            print(f"📡 وضعیت پاسخ: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 کلیدهای داده: {list(data.keys())}")
                
                if data.get('success'):
                    raw_coins = data.get('coins', [])
                    print(f"✅ سرور {len(raw_coins)} ارز برگردوند")
                    
                    # 🔥 لاگ کامل اولین ارز
                    if raw_coins:
                        first_coin = raw_coins[0]
                        print(f"\n🔥 لاگ کامل اولین ارز:")
                        for key, value in first_coin.items():
                            if any(time_word in key.lower() for time_word in ['change', 'price', 'time']):
                                print(f"   - {key}: {value} (نوع: {type(value)})")
                    
                    processed_coins = self._process_coins_simple(raw_coins)
                    print(f"✅ پردازش کامل {len(processed_coins)} ارز")
                    
                    return {
                        'success': True,
                        'coins': processed_coins,
                        'count': len(processed_coins),
                        'source': 'api',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    print(f"❌ سرور success: false")
            else:
                print(f"❌ خطای HTTP: {response.status_code}")
            
            # fallback
            print("🔄 استفاده از داده نمونه")
            return self._get_fallback_data()
            
        except Exception as e:
            print(f"❌ خطا در اسکن: {e}")
            return self._get_fallback_data()

    def _process_coins_simple(self, raw_coins):
        """پردازش ساده و مستقیم"""
        processed_coins = []
        
        print(f"🔍 شروع پردازش {len(raw_coins)} ارز...")
        
        for i, coin in enumerate(raw_coins):
            try:
                # نام و نماد
                name = coin.get('name', 'Unknown')
                symbol = coin.get('symbol', 'UNK')
                
                # 🔥 مستقیماً از coin همه فیلدها رو بگیر
                processed_coin = {
                    'name': name,
                    'symbol': symbol,
                    'price': self._safe_float(coin.get('price')),
                    
                    # 🔥 مستقیماً از فیلدهای coin بردار
                    'priceChange1h': self._safe_float(coin.get('priceChange1h')),
                    'priceChange4h': self._safe_float(coin.get('change_4h')),  # اینو تست کن
                    'priceChange24h': self._safe_float(coin.get('priceChange24h')),
                    'priceChange7d': self._safe_float(coin.get('change_7d')),  # اینو تست کن  
                    'priceChange30d': self._safe_float(coin.get('change_30d')), # اینو تست کن
                    'priceChange180d': self._safe_float(coin.get('change_180d')), # اینو تست کن
                    
                    'volume': self._safe_float(coin.get('volume')),
                    'marketCap': self._safe_float(coin.get('marketCap'))
                }
                
                # 🔥 لاگ برای ۲ ارز اول
                if i < 2:
                    print(f"\n🔍 پردازش ارز {i}: {name} ({symbol})")
                    print(f"   - قیمت: {processed_coin['price']}")
                    print(f"   - 1h: {processed_coin['priceChange1h']} (از: priceChange1h)")
                    print(f"   - 4h: {processed_coin['priceChange4h']} (از: change_4h)")
                    print(f"   - 24h: {processed_coin['priceChange24h']} (از: priceChange24h)")
                    print(f"   - 7d: {processed_coin['priceChange7d']} (از: change_7d)")
                    print(f"   - 30d: {processed_coin['priceChange30d']} (از: change_30d)")
                    print(f"   - 180d: {processed_coin['priceChange180d']} (از: change_180d)")
                
                processed_coins.append(processed_coin)
                
            except Exception as e:
                print(f"❌ خطا در پردازش ارز {i}: {e}")
                continue
        
        return processed_coins

    def _safe_float(self, value):
        """تبدیل امن به float"""
        try:
            if value is None:
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                cleaned = ''.join(c for c in value if c.isdigit() or c in '.-')
                return float(cleaned) if cleaned else 0.0
            return float(value)
        except:
            return 0.0

    def _get_fallback_data(self):
        """داده نمونه"""
        print("🔄 فعال شدن حالت fallback")
        
        sample_coins = []
        coins_data = [
            ('Bitcoin', 'BTC', 65432.10, 2.15, 1.32, 5.43, 15.2, 45.6, 120.5, 39245678901, 1287654321098),
            ('Ethereum', 'ETH', 3456.78, 1.87, 0.89, 3.21, 12.5, 38.9, 95.3, 18765432987, 415678901234),
        ]
        
        for name, symbol, price, change_1h, change_4h, change_24h, change_7d, change_30d, change_180d, volume, market_cap in coins_data:
            sample_coins.append({
                'name': name,
                'symbol': symbol,
                'price': price,
                'priceChange1h': change_1h,
                'priceChange4h': change_4h,
                'priceChange24h': change_24h,
                'priceChange7d': change_7d,
                'priceChange30d': change_30d,
                'priceChange180d': change_180d,
                'volume': volume,
                'marketCap': market_cap
            })
        
        return {
            'success': True,
            'coins': sample_coins,
            'count': len(sample_coins),
            'source': 'fallback',
            'timestamp': datetime.now().isoformat()
        }

# تست
if __name__ == "__main__":
    scanner = LightweightScanner()
    result = scanner.scan_market(limit=5)
