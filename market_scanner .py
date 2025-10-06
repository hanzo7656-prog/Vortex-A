# market_scanner.py
import requests
from datetime import datetime

class LightweightScanner:
    def __init__(self):
        self.api_base = "https://server-test-ovta.onrender.com"
        self.timeout = 15
    
    def scan_market(self, limit=100):
        """اسکن بازار - بدون محدودیت پردازش"""
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
                    
                    # پردازش همه ارزها - بدون محدودیت
                    processed_coins = self._process_all_coins(raw_coins)
                    
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
    
    def _process_all_coins(self, raw_coins):
        """پردازش همه ارزها - بدون سقف محدودیت"""
        processed_coins = []
        
        print(f"🔧 شروع پردازش {len(raw_coins)} ارز...")
        
        for i, coin in enumerate(raw_coins):
            try:
                # پردازش هر ارز
                processed_coin = {
                    'name': str(coin.get('name', f'Coin_{i}')),
                    'symbol': str(coin.get('symbol', f'UNK_{i}')),
                    'price': self._safe_float(coin.get('price')),
                    'priceChange24h': self._safe_float(coin.get('priceChange24h')),
                    'priceChange1h': self._safe_float(coin.get('priceChange1h')),
                    'volume': self._safe_float(coin.get('volume')),
                    'marketCap': self._safe_float(coin.get('marketCap'))
                }
                processed_coins.append(processed_coin)
                
            except Exception as e:
                print(f"   ⚠️ خطا در ارز {i}: {e}")
                continue
        
        print(f"🏁 پردازش شد: {len(processed_coins)}/{len(raw_coins)} ارز")
        return processed_coins
    
    def _safe_float(self, value):
        """تبدیل امن به float"""
        try:
            return float(value) if value is not None else 0.0
        except:
            return 0.0
    
    def _get_fallback_data(self):
        """داده نمونه - ۱۵ ارز برای تست"""
        print("🔄 فعال شدن حالت fallback")
        sample_coins = []
        coins_list = [
            ('Bitcoin', 'BTC', 65432.10, 2.15, 0.32, 39245678901, 1287654321098),
            ('Ethereum', 'ETH', 3456.78, 1.87, -0.15, 18765432987, 415678901234),
            ('BNB', 'BNB', 567.89, 3.21, 0.45, 2987654321, 87654321098),
            ('Solana', 'SOL', 123.45, -1.23, -0.32, 1987654321, 54321098765),
            ('XRP', 'XRP', 0.567, 0.45, 0.12, 987654321, 30456789012),
            ('Cardano', 'ADA', 0.456, 1.23, 0.08, 876543210, 16234567890),
            ('Dogecoin', 'DOGE', 0.123, 4.56, 0.25, 765432109, 17654321098),
            ('Polkadot', 'DOT', 6.78, -0.89, -0.12, 654321098, 8765432109),
            ('Litecoin', 'LTC', 78.90, 0.67, 0.05, 543210987, 5654321098),
            ('Chainlink', 'LINK', 12.34, 2.34, 0.15, 432109876, 6543210987),
            ('Avalanche', 'AVAX', 34.56, 1.45, 0.22, 321098765, 12345678901),
            ('Polygon', 'MATIC', 0.789, 0.98, 0.07, 210987654, 7654321098),
            ('Stellar', 'XLM', 0.123, 0.34, 0.03, 109876543, 3456789012),
            ('Uniswap', 'UNI', 6.45, 1.12, 0.18, 987654321, 4567890123),
            ('Algorand', 'ALGO', 0.234, 0.56, 0.09, 876543210, 2345678901)
        ]
        
        for name, symbol, price, change24h, change1h, volume, market_cap in coins_list:
            sample_coins.append({
                'name': name,
                'symbol': symbol,
                'price': price,
                'priceChange24h': change24h,
                'priceChange1h': change1h,
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
    result = scanner.scan_market(limit=100)
    print(f"نتایج: {result['count']} ارز - منبع: {result['source']}")
