import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import random

# ==================== CONSTANTS ====================
LIGHT_THEME = {
    "primary": "#2563EB",
    "secondary": "#6366F1", 
    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "surface": "rgba(255, 255, 255, 0.25)",
    "glass": "rgba(255, 255, 255, 0.2)",
    "glass_border": "rgba(255, 255, 255, 0.3)",
    "text_primary": "#FFFFFF",
    "text_secondary": "rgba(255, 255, 255, 0.8)",
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "shadow": "0 8px 32px rgba(0, 0, 0, 0.1)"
}

DARK_THEME = {
    "primary": "#3B82F6",
    "secondary": "#818CF8",
    "background": "linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)",
    "surface": "rgba(30, 41, 59, 0.7)",
    "glass": "rgba(30, 41, 59, 0.5)",
    "glass_border": "rgba(255, 255, 255, 0.1)",
    "text_primary": "#F1F5F9", 
    "text_secondary": "rgba(241, 245, 249, 0.7)",
    "success": "#34D399",
    "warning": "#FBBF24",
    "error": "#F87171",
    "shadow": "0 8px 32px rgba(0, 0, 0, 0.3)"
}

API_BASE_URL = "https://server-test-ovta.onrender.com/api"

# ==================== API CLIENT ====================
class VortexAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.timeout = 30
        self.request_count = 0
    
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
        """اسکن واقعی مارکت"""
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

# ==================== COMPONENTS ====================
def render_glass_card(theme):
    """استایل شیشه‌ای برای کارت‌ها"""
    st.markdown(f"""
    <style>
        .glass-card {{
            background: {theme['surface']};
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid {theme['glass_border']};
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: {theme['shadow']};
        }}
        .metric-card {{
            background: {theme['glass']};
            backdrop-filter: blur(5px);
            border-radius: 12px;
            padding: 1.5rem;
            border-left: 4px solid {theme['primary']};
            margin: 0.5rem 0;
        }}
        .coin-card {{
            background: {theme['surface']};
            backdrop-filter: blur(8px);
            border: 1px solid {theme['glass_border']};
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            transition: all 0.3s ease;
        }}
        .coin-card:hover {{
            transform: translateY(-2px);
            box-shadow: {theme['shadow']};
        }}
        .main {{
            background: {theme['background']};
            background-attachment: fixed;
        }}
    </style>
    """, unsafe_allow_html=True)

def render_metric_card(title, value, change, theme):
    """کارت متریک شیشه‌ای"""
    change_html = ""
    if change:
        change_color = theme['success'] if change.startswith('+') else theme['error']
        change_html = f"""<div style="color: {change_color}; font-size: 0.9rem; margin-top: 0.5rem;">{change}</div>"""
    
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: {theme['text_secondary']}; font-size: 0.9rem;">{title}</div>
        <div style="color: {theme['text_primary']}; font-size: 1.8rem; font-weight: bold; margin: 0.5rem 0;">{value}</div>
        {change_html}
    </div>
    """, unsafe_allow_html=True)

def render_coin_card(coin, theme):
    """کارت کوین شیشه‌ای"""
    change_color = theme['success'] if coin.get('change_24h', 0) >= 0 else theme['error']
    change_icon = "📈" if coin.get('change_24h', 0) >= 0 else "📉"
    
    vortex_data = coin.get('VortexAI_analysis', {})
    anomaly_badge = ""
    if vortex_data.get('volume_anomaly'):
        anomaly_badge = f"""
        <div style="background: {theme['warning']}; color: white; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.7rem; display: inline-block; margin-left: 0.5rem;">
            ⚠️ Anomaly
        </div>
        """
    
    st.markdown(f"""
    <div class="coin-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="font-size: 1.5rem;">🪙</div>
                <div>
                    <div style="display: flex; align-items: center;">
                        <div style="font-weight: bold; color: {theme['text_primary']}; font-size: 1.1rem;">
                            {coin.get('symbol', 'N/A')}
                        </div>
                        {anomaly_badge}
                    </div>
                    <div style="color: {theme['text_secondary']}; font-size: 0.8rem;">{coin.get('name', 'Unknown')}</div>
                </div>
            </div>
            
            <div style="text-align: center;">
                <div style="font-weight: bold; color: {theme['text_primary']}; font-size: 1.1rem;">
                    ${coin.get('price', 0):,.2f}
                </div>
                <div style="color: {change_color}; font-size: 0.9rem;">
                    {change_icon} {coin.get('change_24h', 0):+.2f}%
                </div>
            </div>
            
            <div style="text-align: center;">
                <div style="color: {theme['text_secondary']}; font-size: 0.8rem;">Signal</div>
                <div style="color: {theme['primary']}; font-weight: bold; font-size: 1.1rem;">
                    {vortex_data.get('signal_strength', 0)}/10
                </div>
            </div>
            
            <div style="text-align: center;">
                <div style="color: {theme['text_secondary']}; font-size: 0.8rem;">Volume</div>
                <div style="color: {theme['text_primary']}; font-size: 0.9rem;">
                    ${coin.get('volume', 0)/1000000:.1f}M
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
    
    def apply_theme(self, dark_mode):
        """اعمال تم"""
        self.current_theme = DARK_THEME if dark_mode else LIGHT_THEME
        render_glass_card(self.current_theme)
    
    def render_header(self):
        """هدر اصلی با طراحی شیشه‌ای"""
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h1 style="color: {self.current_theme['text_primary']}; margin: 0;">🚀 VortexAI Crypto Scanner</h1>
            <p style="color: {self.current_theme['text_secondary']}; margin: 0;">v6.0 - Real-time Market Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            health = self.api_client.get_health_status()
            status_color = "🟢" if health.get('status') == 'healthy' else "🔴"
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <div style="color: {self.current_theme['text_secondary']};">System Status</div>
                <div style="color: {self.current_theme['text_primary']}; font-weight: bold; font-size: 1.2rem;">
                    {status_color} {health.get('status', 'Unknown').title()}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            last_update = st.session_state.last_scan_time or "Never"
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <div style="color: {self.current_theme['text_secondary']};">Last Scan</div>
                <div style="color: {self.current_theme['text_primary']}; font-weight: bold; font-size: 1.2rem;">
                    {last_update}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if st.button("🔄 Scan Market", use_container_width=True, type="primary"):
                self.perform_market_scan()
    
    def perform_market_scan(self):
        """انجام اسکن مارکت"""
        with st.spinner("🔄 Scanning market..."):
            scan_result = self.api_client.scan_market(limit=100, filter_type="volume")
            
            if scan_result and scan_result.get("success"):
                st.session_state.scan_data = scan_result
                st.session_state.last_scan_time = datetime.now().strftime("%H:%M:%S")
                st.success(f"✅ Scan completed! Found {len(scan_result.get('coins', []))} coins")
            else:
                st.error("❌ Market scan failed!")
    
    def render_sidebar(self):
        """نوار کناری شیشه‌ای"""
        with st.sidebar:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h2 style="color: {self.current_theme['primary']}; margin: 0;">VortexAI</h2>
                <p style="color: {self.current_theme['text_secondary']}; margin: 0;">Crypto Scanner</p>
            </div>
            """, unsafe_allow_html=True)
            
            page = st.radio(
                "Navigation",
                ["📊 Dashboard", "🔍 Market Scanner", "⚡ Top Movers", "🔔 Alerts", "📈 Technical Data", "⚙️ Settings"],
                index=1
            )
            
            st.divider()
            
            # تنظیمات اسکن
            st.markdown(f"""
            <div class="glass-card">
                <h4 style="color: {self.current_theme['text_primary']};">Scan Settings</h4>
            </div>
            """, unsafe_allow_html=True)
            
            scan_limit = st.slider("Number of coins", 10, 200, 100)
            filter_type = st.selectbox("Filter by", ["volume", "momentum_1h", "momentum_4h", "ai_signal"])
            
            if st.button("🎯 Start Real Scan", use_container_width=True):
                self.perform_market_scan()
            
            st.divider()
            dark_mode = st.toggle("🌙 Dark Mode", value=False)
            self.apply_theme(dark_mode)
            
            return page, scan_limit, filter_type
    
    def render_market_scanner(self, scan_limit, filter_type):
        """اسکنر مارکت"""
        st.markdown(f"""
        <div class="glass-card">
            <h2 style="color: {self.current_theme['text_primary']}; margin: 0;">🔍 Market Scanner</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # نمایش وضعیت داده‌ها
        if st.session_state.scan_data:
            coins = st.session_state.scan_data.get("coins", [])
            st.success(f"📊 Displaying {len(coins)} coins from real server")
            
            # نمایش کوین‌ها
            for coin in coins:
                render_coin_card(coin, self.current_theme)
        else:
            st.warning("⚠️ No market data available. Click 'Scan Market' to get real-time data.")
    
    def render_dashboard(self):
        """داشبورد اصلی"""
        st.markdown(f"""
        <div class="glass-card">
            <h2 style="color: {self.current_theme['text_primary']}; margin: 0;">📊 Market Overview</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.scan_data:
            coins = st.session_state.scan_data.get("coins", [])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                render_metric_card("Total Coins", len(coins), None, self.current_theme)
            with col2:
                strong_signals = len([c for c in coins if c.get('VortexAI_analysis', {}).get('signal_strength', 0) > 7])
                render_metric_card("Strong Signals", strong_signals, None, self.current_theme)
            with col3:
                anomalies = len([c for c in coins if c.get('VortexAI_analysis', {}).get('volume_anomaly', False)])
                render_metric_card("Volume Anomalies", anomalies, None, self.current_theme)
            with col4:
                avg_signal = sum([c.get('VortexAI_analysis', {}).get('signal_strength', 0) for c in coins]) / max(len(coins), 1)
                render_metric_card("Avg Signal", f"{avg_signal:.1f}/10", None, self.current_theme)
        else:
            st.warning("Scan market first to see dashboard data")
    
    def render_top_movers(self):
        st.markdown(f"""
        <div class="glass-card">
            <h2 style="color: {self.current_theme['text_primary']}; margin: 0;">⚡ Top Movers</h2>
        </div>
        """, unsafe_allow_html=True)
        st.info("Top movers page - Coming soon")
    
    def render_alerts_page(self):
        st.markdown(f"""
        <div class="glass-card">
            <h2 style="color: {self.current_theme['text_primary']}; margin: 0;">🔔 Alert System</h2>
        </div>
        """, unsafe_allow_html=True)
        st.info("Alerts page - Coming soon")
    
    def render_technical_data(self):
        st.markdown(f"""
        <div class="glass-card">
            <h2 style="color: {self.current_theme['text_primary']}; margin: 0;">📈 Technical Data</h2>
        </div>
        """, unsafe_allow_html=True)
        st.info("Technical data page - Coming soon")
    
    def render_settings(self):
        st.markdown(f"""
        <div class="glass-card">
            <h2 style="color: {self.current_theme['text_primary']}; margin: 0;">⚙️ Settings</h2>
        </div>
        """, unsafe_allow_html=True)
        st.info("Settings page")

    def run(self):
        """اجرای برنامه"""
        self.initialize_session_state()
        self.apply_theme(False)
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
