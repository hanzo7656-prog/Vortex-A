import requests
import pandas as pd
from datetime import datetime
import streamlit as st
from config.constants import API_BASE_URL, TIMEFRAMES

class VortexAPIClient:
    """کلاینت برای ارتباط با سرور VortexAI شما"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.timeout = 30
    
    def get_health_status(self):
        """بررسی سلامت سرور - مشابه endpoint سلامت شما"""
        try:
            response = self.session.get(f"{self.base_url}/health-combined", timeout=self.timeout)
            return response.json()
        except Exception as e:
            return {"status": "offline", "error": str(e)}
    
    def scan_market(self, limit=100, filter_type="volume"):
        """
        اسکن مارکت - دقیقاً مشابه endpoint اسکن شما
        /api/scan/vortexai
        """
        try:
            params = {
                "limit": limit,
                "filter": filter_type
            }
            
            response = self.session.get(
                f"{self.base_url}/scan/vortexai", 
                params=params, 
                timeout=self.timeout
            )
            
            data = response.json()
            
            if data.get("success"):
                return data
            else:
                st.error(f"Scan failed: {data.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None
    
    def get_coin_technical(self, symbol, timeframe="24h"):
        """
        دریافت تحلیل تکنیکال - مشابه endpoint شما
        /api/coin/{symbol}/technical
        """
        try:
            response = self.session.get(
                f"{self.base_url}/coin/{symbol}/technical",
                timeout=self.timeout
            )
            
            data = response.json()
            return data if data.get("success") else None
            
        except Exception as e:
            st.error(f"Technical analysis error: {str(e)}")
            return None
    
    def get_coin_history(self, symbol, timeframe="24h"):
        """
        دریافت تاریخچه قیمت - مشابه endpoint شما  
        /api/coin/{symbol}/history/{timeframe}
        """
        try:
            response = self.session.get(
                f"{self.base_url}/coin/{symbol}/history/{timeframe}",
                timeout=self.timeout
            )
            
            data = response.json()
            return data if data.get("success") else None
            
        except Exception as e:
            st.error(f"History data error: {str(e)}")
            return None
    
    def get_health_combined(self):
        """سلامت ترکیبی سیستم - مشابه endpoint شما"""
        try:
            response = self.session.get(f"{self.base_url}/health-combined", timeout=self.timeout)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_timeframes(self):
        """دریافت تایم‌فریم‌های موجود - مشابه endpoint شما"""
        try:
            response = self.session.get(f"{self.base_url}/timeframes", timeout=self.timeout)
            data = response.json()
            return data.get("timeframes", []) if data.get("success") else []
        except:
            return TIMEFRAMES
