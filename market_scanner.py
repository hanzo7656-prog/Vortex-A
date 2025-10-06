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
        """پردازش ارزها با فیلدهای واقعی CoinGecko API"""
        processed_coins = []
    
        print(f"🔧 شروع پردازش {len(raw_coins)} ارز از CoinGecko API...")
    
        for i, coin in enumerate(raw_coins):
            try:
                # 🔥 گرفتن فیلدهای واقعی CoinGecko
                current_price = coin.get('current_price')
                price_change_24h = coin.get('price_change_percentage_24h')
                price_change_1h = coin.get('price_change_percentage_1h_in_currency')
                total_volume = coin.get('total_volume')
                market_cap = coin.get('market_cap')
                name = coin.get('name')
                symbol = coin.get('symbol', '').upper()
            
                # 🔥 دیباگ کامل برای ۳ ارز اول
                if i < 3:
                    print(f"🔍 ارز {i} ({name}):")
                    print(f"   - current_price: {current_price}")
                    print(f"   - price_change_percentage_24h: {price_change_24h}")
                    print(f"   - price_change_percentage_1h_in_currency: {price_change_1h}")
                    print(f"   - total_volume: {total_volume}")
                    print(f"   - market_cap: {market_cap}")
                    print(f"   - symbol: {symbol}")
            
                # تبدیل به مقادیر عددی
                processed_coin = {
                    'name': str(name) if name else f'Coin_{i}',
                    'symbol': str(symbol) if symbol else f'UNK_{i}',
                    'price': self._safe_float(current_price),
                    # 🔥 استفاده از فیلدهای واقعی CoinGecko
                    'priceChange24h': self._safe_float(price_change_24h),
                    'priceChange1h': self._safe_float(price_change_1h),
                    'volume': self._safe_float(total_volume),
                    'marketCap': self._safe_float(market_cap),
                    # اضافه کردن فیلدهای اضافی برای تحلیل بهتر
                    'rank': coin.get('market_cap_rank', 0),
                    'high_24h': self._safe_float(coin.get('high_24h')),
                    'low_24h': self._safe_float(coin.get('low_24h'))
                }
            
                # 🔥 دیباگ مقادیر نهایی
                if i < 3:
                    print(f"   📊 پردازش شده:")
                    print(f"      - قیمت: ${processed_coin['price']:,.2f}")
                    print(f"      - تغییر 24h: {processed_coin['priceChange24h']:+.2f}%")
                    print(f"      - تغییر 1h: {processed_coin['priceChange1h']:+.2f}%")
                    print(f"      - حجم: ${processed_coin['volume']:,.0f}")
                    print(f"      - بازار: ${processed_coin['marketCap']:,.0f}")
            
                processed_coins.append(processed_coin)
            
            except Exception as e:
                print(f"⚠️ خطا در پردازش ارز {i}: {e}")
                print(f"   🗂️ داده ارز: {coin}")
                continue
    
        print(f"🏁 پردازش کامل: {len(processed_coins)}/{len(raw_coins)} ارز")
    
        # 🔥 خلاصه آماری
        if processed_coins:
            changes_24h = [c['priceChange24h'] for c in processed_coins if c['priceChange24h'] != 0]
            changes_1h = [c['priceChange1h'] for c in processed_coins if c['priceChange1h'] != 0]
        
            if changes_24h:
                print(f"📈 آمار تغییرات 24h:")
                print(f"   - میانگین: {sum(changes_24h)/len(changes_24h):.2f}%")
                print(f"   - بیشترین: {max(changes_24h):.2f}%")
                print(f"   - کمترین: {min(changes_24h):.2f}%")
                print(f"   - صعودی: {sum(1 for c in changes_24h if c > 0)} ارز")
                print(f"   - نزولی: {sum(1 for c in changes_24h if c < 0)} ارز")
    
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
