import requests
import streamlit as st
from datetime import datetime

class VortexAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.timeout = 30
    
    def get_health_status(self):
        """دریافت وضعیت سلامت سرور"""
        try:
            response = self.session.get(f"{self.base_url}/health-combined", timeout=self.timeout)
            return response.json()
        except Exception as e:
            return {
                "status": "offline",
                "websocket_status": {"connected": False, "active_coins": 0},
                "api_status": {"requests_count": 0},
                "gist_status": {"total_coins": 0}
            }
    
    def scan_market(self, limit=50, filter_type="volume"):
        """اسکن مارکت"""
        try:
            params = {"limit": limit, "filter": filter_type}
            response = self.session.get(f"{self.base_url}/scan/vortexai", params=params, timeout=self.timeout)
            return response.json()
        except Exception as e:
            st.error(f"Scan error: {str(e)}")
            return None
    
    def get_coin_technical(self, symbol):
        """دریافت داده‌های تکنیکال"""
        try:
            response = self.session.get(f"{self.base_url}/coin/{symbol}/technical", timeout=self.timeout)
            data = response.json()
            return data if data.get("success") else None
        except:
            return None
