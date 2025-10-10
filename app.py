import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ==================== CONSTANTS ====================
LIGHT_THEME = {
    "primary": "#2563EB",
    "secondary": "#6366F1", 
    "background": "#FFFFFF",
    "surface": "#F8FAFC",
    "text_primary": "#1E293B",
    "text_secondary": "#64748B",
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "border": "#E2E8F0"
}

DARK_THEME = {
    "primary": "#3B82F6",
    "secondary": "#818CF8",
    "background": "#0F172A",
    "surface": "#1E293B",
    "text_primary": "#F1F5F9", 
    "text_secondary": "#94A3B8",
    "success": "#34D399",
    "warning": "#FBBF24",
    "error": "#F87171",
    "border": "#334155"
}

API_BASE_URL = "http://localhost:3000/api"

# ==================== API CLIENT ====================
class VortexAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.timeout = 30
        self.request_count = 0  # این خط رو اضافه کردم
    
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

# ==================== MAIN APP ====================
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
                index=1
            )
            
            st.divider()
            
            # تنظیمات اسکن
            st.subheader("Scan Settings")
            scan_limit = st.slider("Number of coins", 10, 200, 100)
            filter_type = st.selectbox("Filter by", ["volume", "momentum_1h", "momentum_4h", "ai_signal"])
            
            if st.button("🎯 Start Scan", use_container_width=True):
                self.perform_market_scan()
            
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
                change_24h = coin.get('change_24h', 0)
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
    
    def render_top_movers(self):
        st.header("⚡ Top Movers")
        st.info("Top movers page")
    
    def render_alerts_page(self):
        st.header("🔔 Alert System")
        st.info("Alerts page")
    
    def render_technical_data(self):
        st.header("📈 Technical Data")
        st.info("Technical data page")
    
    def render_settings(self):
        st.header("⚙️ Settings")
        st.info("Settings page")

    def run(self):
        self.initialize_session_state()
        self.render_header()
        
        page, scan_limit, filter_type = self.render_sidebar()
        
        if "📊 Dashboard" in page:
            self.render_dashboard()
        elif "🔍 Market Scanner" in page:
            self.render_market_scanner(scan_limit, filter_type)
        elif "⚡ Top Movers" in page:
            self.render_top_movers()
        elif "🔔 Alerts" in page:
            self.render_alerts_page()
        elif "📈 Technical Data" in page:
            self.render_technical_data()
        elif "⚙️ Settings" in page:
            self.render_settings()

if __name__ == "__main__":
    app = VortexAIApp()
    app.run()
