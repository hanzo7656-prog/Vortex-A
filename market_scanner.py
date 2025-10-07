# market_scanner.py - تست ساده

import requests
from datetime import datetime

class LightweightScanner:
    def __init__(self):
        self.api_base = "https://server-test-ovta.onrender.com"
        self.timeout = 15

    def scan_market(self, limit=5):  # فقط ۵ ارز برای تست
        try:
            print("🧪 تست سرور - بررسی فیلدهای تاریخی...")
            
            response = requests.get(
                f"{self.api_base}/api/scan/vortexai?limit={limit}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    raw_coins = data.get('coins', [])
                    
                    # 🔥 لاگ کامل اولین ارز
                    if raw_coins:
                        first_coin = raw_coins[0]
                        print(f"\n✅ فیلدهای دریافتی از سرور:")
                        for key, value in sorted(first_coin.items()):
                            if 'change' in key.lower():
                                print(f"   - {key}: {value}")
                        
                        # بررسی وجود فیلدهای جدید
                        new_fields = ['change_4h', 'change_7d', 'change_30d', 'change_180d']
                        existing_fields = [f for f in new_fields if f in first_coin and first_coin[f] not in [None, 0]]
                        
                        if existing_fields:
                            print(f"🎉 فیلدهای جدید پر شده: {existing_fields}")
                        else:
                            print("❌ فیلدهای جدید هنوز پر نشدن")
                    
                    return data
                    
        except Exception as e:
            print(f"❌ خطا: {e}")
        
        return None

# تست
if __name__ == "__main__":
    scanner = LightweightScanner()
    result = scanner.scan_market(limit=3)
