import requests
import streamlit as st
from datetime import datetime

class VortexAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.timeout = 30
        self.request_count = 0

    

    # 🔥 این تابع رو اضافه کن:
    def get_coin_technical(self, symbol):
        """دریافت تحلیل تکنیکال برای یک کوین"""
        try:
            response = self.session.get(
                f"{self.base_url}/coin/{symbol}/technical",
                timeout=self.timeout
            )
            self.request_count += 1
            data = response.json()
            return data if data.get("success") else None
        except Exception as e:
            st.error(f"🔧 Technical analysis error: {str(e)}")
            return None

   
    
    def get_health_status(self):
        """دریافت وضعیت سلامت سرور"""
        try:
            response = self.session.get(f"{self.base_url}/health-combined", timeout=self.timeout)
            self.request_count += 1
            return response.json()
        except Exception as e:
            return {
                "status": "offline",
                "error": str(e),
                "websocket_status": {"connected": False, "active_coins": 0},
                "api_status": {"requests_count": self.request_count},
                "gist_status": {"total_coins": 0}
            }
    
    def scan_market(self, limit=100, filter_type="volume"):
        """
        اسکن واقعی مارکت - مشابه endpoint اسکن شما
        /api/scan/vortexai
        """
        try:
            params = {
                "limit": limit,
                "filter": filter_type
            }
            
            st.info(f"🔄 Scanning market with {limit} coins...")
            response = self.session.get(
                f"{self.base_url}/scan/vortexai", 
                params=params, 
                timeout=self.timeout
            )
            self.request_count += 1
            
            data = response.json()
            
            if data.get("success"):
                st.success(f"✅ Received {len(data.get('coins', []))} coins from server")
                return data
            else:
                st.error(f"❌ Scan failed: {data.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            st.error(f"🚨 API Error: {str(e)}")
            return None
    
    def get_coin_technical(self, symbol):
        """دریافت تحلیل تکنیکال برای یک کوین - با اندپوینت صحیح"""
        try:
            # تبدیل symbol به فرمت مورد نیاز سرور (مثلاً BTC -> btc_usdt)
            formatted_symbol = f"{symbol.lower()}_usdt"
        
            response = self.session.get(
                f"{self.base_url}/analysis",  # 🔥 اندپوینت صحیح
                params={"symbol": formatted_symbol},  # 🔥 پارامتر صحیح
                timeout=self.timeout
            )
            self.request_count += 1
            data = response.json()
            return data if data.get("success") else None
        except Exception as e:
            st.error(f"🔧 Technical analysis error: {str(e)}")
            return None
    
    def get_coin_history(self, symbol, timeframe="24h"):
        """
        دریافت تاریخچه قیمت واقعی
        /api/coin/{symbol}/history/{timeframe}
        """
        try:
            response = self.session.get(
                f"{self.base_url}/coin/{symbol}/history/{timeframe}",
                timeout=self.timeout
            )
            self.request_count += 1
            
            data = response.json()
            return data if data.get("success") else None
            
        except Exception as e:
            st.error(f"History data error: {str(e)}")
            return None
    
    def get_exchange_price(self, exchange="Binance", from_coin="BTC", to_coin="USDT"):
        """دریافت قیمت از صرافی"""
        try:
            response = self.session.get(
                f"{self.base_url}/exchange/price",
                params={
                    "exchange": exchange,
                    "from": from_coin,
                    "to": to_coin,
                    "timestamp": int(datetime.now().timestamp())
                },
                timeout=self.timeout
            )
            self.request_count += 1
            return response.json()
        except Exception as e:
            st.error(f"Exchange price error: {str(e)}")
            return None
    
    def get_system_health(self):
        """سلامت کامل سیستم"""
        return self.get_health_status()

    
    def get_coin_technical(self, symbol):
        """دریافت تحلیل تکنیکال برای یک کوین"""
        try:
            response = self.session.get(
                f"{self.base_url}/coin/{symbol}/technical",
                timeout=self.timeout
            )
            self.request_count += 1
            data = response.json()
            return data if data.get("success") else None
        except Exception as e:
            st.error(f"🔧 Technical analysis error: {str(e)}")
            return None
