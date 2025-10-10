import streamlit as st
import pandas as pd
from datetime import datetime

# import constants
from constants import API_BASE_URL, LIGHT_THEME, DARK_THEME

# import api_client
try:
    from api_client import VortexAPIClient
except ImportError:
    # اگر import نشد، از فایل اصلی استفاده می‌کنیم
    import requests
    # محتوای کلاس VortexAPIClient رو اینجا کپی کنید
    pass

class VortexAIApp:
    def __init__(self):
        self.api_client = VortexAPIClient(API_BASE_URL)
        self.current_theme = LIGHT_THEME
        
    def initialize_session_state(self):
        """مقداردهی اولیه session state"""
        if 'scan_data' not in st.session_state:
            st.session_state.scan_data = None
        if 'selected_coin' not in st.session_state:
            st.session_state.selected_coin = None
        if 'last_scan_time' not in st.session_state:
            st.session_state.last_scan_time = None
    
    def render_header(self):
        """هدر اصلی"""
        st.title("🚀 VortexAI Crypto Scanner")
        st.subheader("v6.0 - Real-time Market Intelligence")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            health = self.api_client.get_health_status()
            status = "🟢 Online" if health.get('status') == 'healthy' else "🔴 Offline"
            st.info(f"**System Status:** {status}")
        
        with col2:
            last_update = st.session_state.last_scan_time or "Never"
            st.info(f"**Last Scan:** {last_update}")
        
        with col3:
            if st.button("🔄 Scan Market", use_container_width=True, type="primary"):
                self.perform_market_scan()
    
    def perform_market_scan(self):
        """انجام اسکن واقعی مارکت"""
        with st.spinner("🔄 Scanning market..."):
            scan_result = self.api_client.scan_market(limit=100, filter_type="volume")
            
            if scan_result and scan_result.get("success"):
                st.session_state.scan_data = scan_result
                st.session_state.last_scan_time = datetime.now().strftime("%H:%M:%S")
                st.success(f"✅ Scan completed! Found {len(scan_result.get('coins', []))} coins")
            else:
                st.error("❌ Market scan failed!")
    
    def render_sidebar(self):
        """نوار کناری"""
        with st.sidebar:
            st.header("VortexAI")
            st.caption("Crypto Scanner")
            
            page = st.radio(
                "Navigation",
                ["📊 Dashboard", "🔍 Market Scanner", "⚡ Top Movers", "🔔 Alerts", "📈 Technical Data", "⚙️ Settings"],
                index=1  # شروع از صفحه اسکنر
            )
            
            st.divider()
            
            # تنظیمات اسکن
            st.subheader("Scan Settings")
            scan_limit = st.slider("Number of coins", 10, 200, 100)
            filter_type = st.selectbox("Filter by", ["volume", "momentum_1h", "momentum_4h", "ai_signal"])
            
            if st.button("🎯 Start Scan", use_container_width=True):
                self.api_client.scan_market(limit=scan_limit, filter_type=filter_type)
            
            st.divider()
            dark_mode = st.toggle("🌙 Dark Mode", value=False)
            
            return page, scan_limit, filter_type
    
    def render_market_scanner(self, scan_limit, filter_type):
        """اسکنر مارکت با داده‌های واقعی"""
        st.header("🔍 Market Scanner")
        
        # نمایش وضعیت داده‌ها
        if st.session_state.scan_data:
            coins = st.session_state.scan_data.get("coins", [])
            st.success(f"📊 Displaying {len(coins)} coins from real server data")
            
            # نمایش کوین‌ها
            for coin in coins:
                self.render_coin_card(coin)
        else:
            st.warning("⚠️ No market data available. Click 'Scan Market' to get real-time data.")
            
            # نمایش نمونه برای تست
            st.info("💡 For testing, here's sample data structure:")
            sample_coins = [
                {
                    "symbol": "BTC", 
                    "name": "Bitcoin", 
                    "price": 45000, 
                    "change_1h": 2.5, 
                    "change_24h": 5.2,
                    "volume": 25000000000,
                    "VortexAI_analysis": {
                        "signal_strength": 8.5,
                        "volume_anomaly": True,
                        "trend": "up"
                    }
                }
            ]
            for coin in sample_coins:
                self.render_coin_card(coin)
    
    def render_coin_card(self, coin):
        """کارت نمایش کوین با داده‌های واقعی"""
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                # نماد و نام
                st.write(f"🪙 **{coin.get('symbol', 'N/A')}**")
                st.caption(coin.get('name', 'Unknown'))
                
                # آنومالی حجم
                vortex_data = coin.get('VortexAI_analysis', {})
                if vortex_data.get('volume_anomaly'):
                    st.warning("⚠️ Volume Anomaly")
            
            with col2:
                # قیمت و تغییرات
                price = coin.get('price', 0)
                change_24h = coin.get('change_24h', coin.get('change_24h', 0))
                st.metric(
                    label="Price",
                    value=f"${price:,.2f}" if price else "N/A",
                    delta=f"{change_24h:+.2f}%" if change_24h else None
                )
            
            with col3:
                # قدرت سیگنال
                signal_strength = vortex_data.get('signal_strength', 0)
                st.write("**Signal Strength**")
                if signal_strength > 0:
                    progress_value = min(signal_strength / 10, 1.0)
                    st.progress(progress_value)
                    st.write(f"**{signal_strength}/10**")
                else:
                    st.write("N/A")
            
            with col4:
                # حجم
                volume = coin.get('volume', 0)
                st.write("**Volume**")
                if volume > 0:
                    st.write(f"${volume/1000000:.1f}M")
                else:
                    st.write("N/A")
            
            with col5:
                # دکمه مشاهده جزئیات
                if st.button("📊", key=f"view_{coin.get('symbol', 'unknown')}"):
                    st.session_state.selected_coin = coin.get('symbol')
                    st.rerun()
            
            st.markdown("---")
    
    def render_dashboard(self):
        """داشبورد اصلی"""
        st.header("📊 Market Overview")
        
        if st.session_state.scan_data:
            coins = st.session_state.scan_data.get("coins", [])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Coins", len(coins))
            with col2:
                strong_signals = len([c for c in coins if c.get('VortexAI_analysis', {}).get('signal_strength', 0) > 7])
                st.metric("Strong Signals", strong_signals)
            with col3:
                anomalies = len([c for c in coins if c.get('VortexAI_analysis', {}).get('volume_anomaly', False)])
                st.metric("Volume Anomalies", anomalies)
            with col4:
                avg_signal = sum([c.get('VortexAI_analysis', {}).get('signal_strength', 0) for c in coins]) / max(len(coins), 1)
                st.metric("Avg Signal", f"{avg_signal:.1f}/10")
        else:
            st.warning("Scan market first to see dashboard data")
    
    # بقیه توابع (Top Movers, Alerts, Technical Data, Settings) رو می‌تونیم بعداً کامل کنیم
    
    def run(self):
        """اجرای برنامه"""
        self.initialize_session_state()
        self.render_header()
        
        page, scan_limit, filter_type = self.render_sidebar()
        
        if "📊 Dashboard" in page:
            self.render_dashboard()
        elif "🔍 Market Scanner" in page:
            self.render_market_scanner(scan_limit, filter_type)
        elif "⚡ Top Movers" in page:
            st.info("Top Movers page - Coming soon with real data")
        elif "🔔 Alerts" in page:
            st.info("Alerts page - Coming soon with real data")
        elif "📈 Technical Data" in page:
            st.info("Technical Data page - Coming soon with real data")
        elif "⚙️ Settings" in page:
            st.info("Settings page")

if __name__ == "__main__":
    app = VortexAIApp()
    app.run()
