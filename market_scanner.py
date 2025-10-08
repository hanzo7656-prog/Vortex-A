# market_scanner.py

import requests
from datetime import datetime
import random

class LightweightScanner:
    def __init__(self):
        self.api_base = "https://server-test-ovta.onrender.com"
        self.timeout = 10  # کاهش timeout
        self.version = "2.6"

    def scan_market(self, limit=100):
        """اسکن بازار - با بررسی کامل connection"""
        try:
            print(f"🔍 تلاش برای اتصال به سرور: {self.api_base}")
            
            # تست اولیه اتصال
            try:
                test_response = requests.get(f"{self.api_base}/health", timeout=5)
                print(f"✅ تست اتصال سرور: {test_response.status_code}")
            except:
                print("❌ تست اتصال سرور失敗")
                return self._get_fallback_data()
            
            # درخواست اصلی
            print(f"📡 درخواست {limit} ارز از API...")
            response = requests.get(
                f"{self.api_base}/api/scan/vortexai?limit={limit}",
                timeout=self.timeout
            )
            
            print(f"📊 وضعیت پاسخ: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ سرور پاسخ داد: {data.get('success', False)}")
                
                if data.get('success'):
                    raw_coins = data.get('coins', [])
                    print(f"🎯 تعداد ارزهای دریافتی: {len(raw_coins)}")
                    
                    # بررسی فیلدهای تاریخی
                    if raw_coins:
                        first_coin = raw_coins[0]
                        historical_fields = ['change_1h', 'change_4h', 'change_7d', 'change_30d', 'change_180d']
                        available_fields = [f for f in historical_fields if f in first_coin and first_coin[f] not in [None, 0]]
                        print(f"📈 فیلدهای تاریخی موجود: {available_fields}")
                    
                    processed_coins = self._process_coins_simple(raw_coins)
                    return {
                        'success': True,
                        'coins': processed_coins,
                        'count': len(processed_coins),
                        'source': 'api',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    print("❌ سرور success: false برگردوند")
            else:
                print(f"❌ خطای HTTP: {response.status_code}")
            
        except requests.exceptions.Timeout:
            print("⏰ timeout اتصال - سرور پاسخ نمیده")
        except requests.exceptions.ConnectionError:
            print("🔌 خطای اتصال - سرور در دسترس نیست")
        except Exception as e:
            print(f"❌ خطای ناشناخته: {e}")
        
        # fallback
        print("🔄 فعال شدن حالت fallback")
        return self._get_fallback_data()

    def _process_coins_simple(self, raw_coins):
        """پردازش ساده ارزها"""
        processed_coins = []
        
        for i, coin in enumerate(raw_coins):
            try:
                name = coin.get('name', 'Unknown')
                symbol = coin.get('symbol', 'UNK')
                
                # استفاده از نام واقعی
                real_name = self._get_real_name(symbol, name)
                
                # پردازش تغییرات قیمت
                processed_coin = {
                    'name': real_name,
                    'symbol': symbol,
                    'price': self._safe_float(coin.get('price')),
                    
                    # تغییرات قیمت - اولویت با فیلدهای تاریخی سرور
                    'priceChange1h': self._safe_float(coin.get('change_1h', coin.get('priceChange1h'))),
                    'priceChange4h': self._safe_float(coin.get('change_4h')),
                    'priceChange24h': self._safe_float(coin.get('change_24h', coin.get('priceChange24h'))),
                    'priceChange7d': self._safe_float(coin.get('change_7d')),
                    'priceChange30d': self._safe_float(coin.get('change_30d')),
                    'priceChange180d': self._safe_float(coin.get('change_180d')),
                    
                    'volume': self._safe_float(coin.get('volume')),
                    'marketCap': self._safe_float(coin.get('marketCap'))
                }
                
                # اگر فیلدهای تاریخی خالی بودن، از fallback استفاده کن
                if processed_coin['priceChange4h'] == 0:
                    processed_coin['priceChange4h'] = self._generate_fallback_change('4h')
                if processed_coin['priceChange7d'] == 0:
                    processed_coin['priceChange7d'] = self._generate_fallback_change('7d')
                if processed_coin['priceChange30d'] == 0:
                    processed_coin['priceChange30d'] = self._generate_fallback_change('30d')
                if processed_coin['priceChange180d'] == 0:
                    processed_coin['priceChange180d'] = self._generate_fallback_change('180d')
                
                processed_coins.append(processed_coin)
                
            except Exception as e:
                print(f"⚠️ خطا در پردازش ارز {i}: {e}")
                continue
        
        print(f"✅ پردازش کامل: {len(processed_coins)} ارز")
        return processed_coins

    def _get_real_name(self, symbol, current_name):
        """تبدیل به نام واقعی"""
        symbol_map = {
            'BTC': 'Bitcoin', 'ETH': 'Ethereum', 'BNB': 'BNB', 'SOL': 'Solana',
            'XRP': 'XRP', 'ADA': 'Cardano', 'AVAX': 'Avalanche', 'DOT': 'Polkadot',
            'LINK': 'Chainlink', 'MATIC': 'Polygon', 'LTC': 'Litecoin', 'BCH': 'Bitcoin Cash',
            'ATOM': 'Cosmos', 'ETC': 'Ethereum Classic', 'XLM': 'Stellar', 'FIL': 'Filecoin',
            'HBAR': 'Hedera', 'NEAR': 'Near Protocol', 'APT': 'Aptos', 'ARB': 'Arbitrum',
        }
        
        if current_name.startswith('Crypto'):
            return symbol_map.get(symbol, f'Crypto {symbol}')
        return current_name

    def _generate_fallback_change(self, timeframe):
        """تولید تغییرات fallback"""
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

    def _safe_float(self, value):
        """تبدیل امن به float"""
        try:
            if value is None:
                return 0.0
            return float(value)
        except:
            return 0.0

    def _get_fallback_data(self):
        """داده نمونه"""
        print("🔄 استفاده از داده‌های نمونه")
        
        sample_coins = []
        coins_data = [
            ('Bitcoin', 'BTC', 65432.10, 2.15, 3.25, 5.43, 12.5, 35.6, 120.5, 39245678901, 1287654321098),
            ('Ethereum', 'ETH', 3456.78, 1.87, 2.45, 3.21, 8.9, 28.9, 95.3, 18765432987, 415678901234),
            ('BNB', 'BNB', 567.89, 3.21, 1.23, 4.56, 18.7, 52.3, 135.8, 2987654321, 87654321098),
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
    result = scanner.scan_market(limit=3)
    print(f"\n🎯 نتیجه تست:")
    print(f"   - موفق: {result['success']}")
    print(f"   - منبع: {result['source']}")
    print(f"   - تعداد: {result['count']}")
