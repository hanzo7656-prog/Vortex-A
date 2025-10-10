import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import asyncio

# ایمپورت ماژول‌های سفارشی
from config.constants import API_BASE_URL, TIMEFRAMES, ALL_TRADING_PAIRS
from modules.api_client import VortexAPIClient
from modules.technical_analysis import TechnicalAnalyzer
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.scanner import render_scanner, render_technical_analysis
from components.charts import (
    render_price_chart, 
    render_technical_indicators,
    render_volume_chart,
    render_market_sentiment
)

# تنظیمات صفحه
st.set_page_config(
    page_title="VortexAI Crypto Scanner - v6.0",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# استایل سفارشی
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1E88E5;
    }
    .positive-change {
        color: #00C853;
        font-weight: bold;
    }
    .negative-change {
        color: #FF1744;
        font-weight: bold;
    }
    .anomaly-alert {
        background-color: #FFF3E0;
        border: 1px solid #FF9800;
        border-radius: 5px;
        padding: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class VortexAIApp:
    def __init__(self):
        self.api_client = VortexAPIClient(API_BASE_URL)
        self.technical_analyzer = TechnicalAnalyzer()
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """مقداردهی اولیه session state"""
        if 'scan_data' not in st.session_state:
            st.session_state.scan_data = None
        if 'selected_coin' not in st.session_state:
            st.session_state.selected_coin = None
        if 'timeframe' not in st.session_state:
            st.session_state.timeframe = "24h"
        if 'last_update' not in st.session_state:
            st.session_state.last_update = None
    
    def render_header(self):
        """هدر اصلی برنامه"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<h1 class="main-header">🚀 VortexAI Crypto Scanner</h1>', 
                       unsafe_allow_html=True)
            st.markdown("**v6.0 - 6-Layer Analysis System**")
            
        # وضعیت سیستم
        with col3:
            if st.button('🔄 Refresh Data'):
                st.session_state.scan_data = None
                st.rerun()
            
            # نمایش وضعیت اتصال
            try:
                health_status = self.api_client.get_health_status()
                status_color = "🟢" if health_status.get('status') == 'healthy' else "🔴"
                st.write(f"{status_color} System Status: {health_status.get('status', 'unknown')}")
            except:
                st.write("🔴 System Status: Offline")
    
    def run(self):
        """اجرای اصلی برنامه"""
        # رندر هدر
        self.render_header()
        
        # نوار کناری
        selected_page = render_sidebar()
        
        # محتوای اصلی بر اساس صفحه انتخاب شده
        if selected_page == "dashboard":
            render_dashboard(self.api_client)
            
        elif selected_page == "market_scanner":
            render_scanner(self.api_client, self.technical_analyzer)
            
        elif selected_page == "technical_analysis":
            if st.session_state.selected_coin:
                render_technical_analysis(
                    self.api_client, 
                    self.technical_analyzer,
                    st.session_state.selected_coin,
                    st.session_state.timeframe
                )
            else:
                st.warning("⚠️ Please select a coin from Market Scanner first")
                
        elif selected_page == "system_health":
            self.render_system_health()
    
    def render_system_health(self):
        """صفحه سلامت سیستم"""
        st.header("🔧 System Health & Monitoring")
        
        try:
            health_data = self.api_client.get_health_combined()
            
            # کارت‌های وضعیت
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                ws_status = health_data.get('websocket_status', {})
                status = "Connected" if ws_status.get('connected') else "Disconnected"
                color = "green" if ws_status.get('connected') else "red"
                st.metric(
                    label="WebSocket", 
                    value=status,
                    delta=f"{ws_status.get('active_coins', 0)} coins"
                )
            
            with col2:
                gist_status = health_data.get('gist_status', {})
                st.metric(
                    label="Data Storage", 
                    value=f"{gist_status.get('total_coins', 0)} coins",
                    delta="Gist Sync"
                )
            
            with col3:
                api_status = health_data.get('api_status', {})
                st.metric(
                    label="API Requests", 
                    value=api_status.get('requests_count', 0),
                    delta="Active"
                )
            
            with col4:
                ai_status = health_data.get('ai_status', {})
                st.metric(
                    label="AI Engine", 
                    value="Ready",
                    delta=f"{ai_status.get('indicators_available', 0)} indicators"
                )
            
            # جزئیات فنی
            st.subheader("Technical Details")
            st.json(health_data)
            
        except Exception as e:
            st.error(f"Error fetching system health: {str(e)}")

# اجرای برنامه
if __name__ == "__main__":
    app = VortexAIApp()
    app.run()
