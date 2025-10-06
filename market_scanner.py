# market_scanner.py
import requests
from datetime import datetime

class LightweightScanner:
    def __init__(self):
        self.api_base = "https://server-test-ovta.onrender.com"
        self.timeout = 15
        self.version = "2.3"
    
    def scan_market(self, limit=100):
        """اسکن بازار - با رفع مشکل فیلدها"""
        try:
            print(f"🎯 درخواست {limit} ارز از سرور...")
            
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
                    
                    # پردازش همه ارزها
                    processed_coins = self._process_coins_with_debug(raw_coins)
                    
                    print(f"🎉 پردازش کامل: {len(processed_coins)} ارز")
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
            print(f"💥 خطا در اسکن: {e}")
            return self._get_fallback_data()
    


    
    def _process_coins_with_debug(self, raw_coins):
        """پردازش ارزها با دیباگ کامل"""
        processed_coins = []
    
        print(f"🔧 شروع پردازش {len(raw_coins)} ارز...")
    
        for i, coin in enumerate(raw_coins):
            try:
                # 🔥 گرفتن تمام فیلدهای ممکن
                price_change_1d = coin.get('priceChange1d')
                price_change_1h = coin.get('priceChange1h')
                price_change_24h = coin.get('priceChange24h')
                price_change_1d_alt = coin.get('price_change_1d')
                price_change_24h_alt = coin.get('price_change_24h')
                daily_change = coin.get('daily_change')
                change_24h = coin.get('change_24h')
            
                # 🔥 دیباگ کامل تمام فیلدها
                print(f"🔍 ارز {i} ({coin.get('name', 'Unknown')}):")
                print(f"   - priceChange1d: {price_change_1d} (نوع: {type(price_change_1d)})")
                print(f"   - priceChange1h: {price_change_1h} (نوع: {type(price_change_1h)})")
                print(f"   - priceChange24h: {price_change_24h} (نوع: {type(price_change_24h)})")
                print(f"   - price_change_1d: {price_change_1d_alt} (نوع: {type(price_change_1d_alt)})")
                print(f"   - price_change_24h: {price_change_24h_alt} (نوع: {type(price_change_24h_alt)})")
                print(f"   - daily_change: {daily_change} (نوع: {type(daily_change)})")
                print(f"   - change_24h: {change_24h} (نوع: {type(change_24h)})")
            
                # 🔥 انتخاب بهترین فیلد برای تغییرات 24 ساعته
                final_24h_change = self._safe_float(
                    price_change_1d or          # اولویت 1: priceChange1d
                    price_change_24h or         # اولویت 2: priceChange24h  
                    daily_change or             # اولویت 3: daily_change
                    change_24h or               # اولویت 4: change_24h
                    price_change_1d_alt or      # اولویت 5: price_change_1d
                    price_change_24h_alt or     # اولویت 6: price_change_24h
                    0.0                         # پیش‌فرض
                )
            
                final_1h_change = self._safe_float(price_change_1h)
            
                print(f"   📊 نهایی: 24h={final_24h_change}, 1h={final_1h_change}")
            
                # فقط 3 ارز اول رو دیباگ کن
                if i >= 3:
                    break
                
            except Exception as e:
                print(f"⚠️ خطا در ارز {i}: {e}")
                continue
    
        # 🔥 حالا پردازش واقعی همه ارزها
        for i, coin in enumerate(raw_coins):
            try:
                # استفاده از منطق مشابه برای همه ارزها
                price_change_1d = coin.get('priceChange1d')
                price_change_1h = coin.get('priceChange1h')
            
                final_24h_change = self._safe_float(price_change_1d or 0.0)
                final_1h_change = self._safe_float(price_change_1h)
            
                processed_coin = {
                    'name': str(coin.get('name', f'Coin_{i}')),
                    'symbol': str(coin.get('symbol', f'UNK_{i}')),
                    'price': self._safe_float(coin.get('price')),
                    'priceChange24h': final_24h_change,
                    'priceChange1h': final_1h_change,
                    'volume': self._safe_float(coin.get('volume')),
                    'marketCap': self._safe_float(coin.get('marketCap'))
                }
            
                processed_coins.append(processed_coin)
            
            except Exception as e:
                print(f"⚠️ خطا در پردازش ارز {i}: {e}")
                continue
    
        print(f"🏁 پردازش کامل: {len(processed_coins)} ارز")
        return processed_coins
    
    def _safe_float(self, value):
        """تبدیل امن به float"""
        try:
            if value is None:
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _get_fallback_data(self):
        """داده نمونه با تغییرات واقعی"""
        print("🔄 فعال شدن حالت fallback")
        sample_coins = []
        coins_list = [
            ('Bitcoin', 'BTC', 65432.10, 2.15, 0.32, 39245678901, 1287654321098),
            ('Ethereum', 'ETH', 3456.78, 1.87, -0.15, 18765432987, 415678901234),
            ('BNB', 'BNB', 567.89, 3.21, 0.45, 2987654321, 87654321098),
            ('Solana', 'SOL', 123.45, -1.23, -0.32, 1987654321, 54321098765),
            ('XRP', 'XRP', 0.567, 0.45, 0.12, 987654321, 30456789012),
            ('Cardano', 'ADA', 0.456, -2.34, -0.18, 876543210, 16234567890),
            ('Dogecoin', 'DOGE', 0.123, 4.56, 0.25, 765432109, 17654321098),
            ('Polkadot', 'DOT', 6.78, -0.89, -0.12, 654321098, 8765432109),
            ('Litecoin', 'LTC', 78.90, 1.67, 0.25, 543210987, 5654321098),
            ('Chainlink', 'LINK', 12.34, -3.21, -0.45, 432109876, 6543210987),
        ]
        
        for name, symbol, price, change_24h, change_1h, volume, market_cap in coins_list:
            sample_coins.append({
                'name': name,
                'symbol': symbol,
                'price': price,
                'priceChange24h': change_24h,  # 🔥 تغییرات واقعی
                'priceChange1h': change_1h,
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

# تست مستقل
if __name__ == "__main__":
    scanner = LightweightScanner()
    result = scanner.scan_market(limit=5)
    print(f"نتایج: {result['count']} ارز - منبع: {result['source']}")
    if result['coins']:
        print(f"نمونه ارز: {result['coins'][0]}")
