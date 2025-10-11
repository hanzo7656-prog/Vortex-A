import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from technical_analysis import TechnicalAnalysisUI

# --- CONSTANTS ---
API_BASE_URL = "https://server-test-ovta.onrender.com/api"

# --- API CLIENT ---
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

    def scan_market(self, limit=100, filter_type="volume", timeframe="24h"):
        """اسکن واقعی مارکت با تایم‌فریم"""
        try:
            params = {
                "limit": limit,
                "filter": filter_type
            }
            st.info(f"🔍 Scanning market with {limit} coins ({timeframe})...")
            response = self.session.get(
                f"{self.base_url}/scan/vortexai",
                params=params,
                timeout=self.timeout
            )
            self.request_count += 1
            data = response.json()
            if data.get("success"):
                st.success(f"✅ Received {len(data.get('coins', []))} coins ({timeframe})")
                return data
            else:
                st.error(f"❌ Scan failed: {data.get('error', 'Unknown error')}")
                return None
        except Exception as e:
            st.error(f"🔍 API Error: {str(e)}")
            return None

# =============================== GLASS DESIGN SYSTEM ==============================

def apply_glass_design():
    """اعمال طراحی شیشه‌ای"""
    st.markdown("""
    <style>
    /* طراحی شیشه‌ای اصلی */
    .glass-header {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        text-align: center;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }

    .glass-metric {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(5px);
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 4px solid #2563EB;
        margin: 0.5rem 0;
        text-align: center;
    }

    .timeframe-selector {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 16px;
        padding: 1.2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    }

    .timeframe-btn {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 10px;
        padding: 0.7rem 0.3rem;
        color: #FFFFFF;
        font-size: 0.9rem;
        font-weight: bold;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        width: 100%;
    }

    .timeframe-btn:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: translateY(-1px);
    }

    .timeframe-btn.selected {
        background: rgba(255, 255, 255, 0.35);
        border: 1px solid #2563EB;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.3);
    }

    .value-badge {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(5px);
        border-radius: 8px;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem 0;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .anomaly-badge {
        background: #F59E0B;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.7rem;
        display: inline-block;
        margin-left: 0.5rem;
    }

    /* پس‌زمینه گرادینت */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }

    /* رنگ‌های متن */
    .text-primary {
        color: #FFFFFF;
        font-weight: bold;
    }

    .text-secondary {
        color: rgba(255, 255, 255, 0.8);
    }

    .text-success {
        color: #10B981;
    }

    .text-error {
        color: #EF4444;
    }

    .text-signal {
        color: #2563EB;
    }
    </style>
    """, unsafe_allow_html=True)

# --- COMPONENTS ---
def render_glass_header():
    """هدر شیشه‌ای"""
    st.markdown("""
    <div class="glass-header">
        <h1 style="color: #FFFFFF; margin: 0; font-size: 2.5rem;">🌀 VortexAI Crypto Scanner</h1>
        <p style="color: rgba(255, 255, 255, 0.8); margin: 0; font-size: 1.2rem;">v6.0 - Real-time Market Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

def render_timeframe_selector():
    """نمایش انتخاب تایم‌فریم محدود شده به 1H, 1D, 1W"""
    
    st.markdown("""
    <style>
    /* حذف کامل استایل رادیو باتون‌ها */
    .stRadio > div {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        gap: 12px !important;
        margin: 1rem 0 !important;
    }
    
    /* حذف دایره‌های رادیو */
    .stRadio > div > label > div:first-child {
        display: none !important;
    }
    
    /* استایل برای لیبل‌ها به صورت دکمه */
    .stRadio > div > label {
        flex: 1 !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 12px 8px !important;
        text-align: center !important;
        color: white !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        margin: 0 !important;
        min-width: 80px !important;
    }
    
    .stRadio > div > label:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-2px) !important;
    }
    
    /* وقتی انتخاب شده */
    .stRadio > div > label[data-testid="stRadio"] {
        background: linear-gradient(135deg, #667ee0 0%, #764ba2 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        box-shadow: 0 4px 15px rgba(102, 126, 224, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: center; margin-bottom: 1rem;'>
        <h3 style='color: #FFFFFF; margin: 0;'>📊 Select Timeframe</h3>
    </div>
    """, unsafe_allow_html=True)

    # فقط 3 تایم‌فریم اصلی
    timeframe_options = {
        "1H": "1h",
        "1D": "24h", 
        "1W": "7d"
    }

    # استفاده از radio button بدون دایره
    selected = st.radio(
        "Timeframe",
        options=list(timeframe_options.keys()),
        horizontal=True,
        label_visibility="collapsed",
        key="timeframe_radio"
    )

    # آپدیت session state
    st.session_state.selected_timeframe = timeframe_options[selected]

    # نمایش تایم‌فریم انتخاب شده
    current_tf = st.session_state.selected_timeframe
    display_map = {"1h": "1H", "24h": "1D", "7d": "1W"}
    
    st.markdown(
        f"""
        <div style='
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 0.7rem;
            color: white;
            text-align: center;
            margin-top: 1rem;
            font-weight: 600;
        '>
            🎯 Selected: <span style='color: #667ee0; font-weight: bold;'>{display_map.get(current_tf, current_tf)}</span>
        </div>
        """, 
        unsafe_allow_html=True
    )

def render_metric_card(title, value, change=None):
    """کارت متریک شیشه‌ای"""
    change_html = ""
    if change is not None:
        change_color = "text-success" if change >= 0 else "text-error"
        change_icon = "📈" if change >= 0 else "📉"
        change_html = f'<div class="{change_color}" style="font-size: 0.9rem; margin-top: 0.5rem;">{change_icon} {change:+.2f}%</div>'

    st.markdown(f"""
    <div class="glass-metric">
        <div class="text-secondary" style="font-size: 0.9rem;">{title}</div>
        <div class="text-primary" style="font-size: 1.8rem; margin: 0.5rem 0;">{value}</div>
        {change_html}
    </div>
    """, unsafe_allow_html=True)

def render_coin_card_clean(coin):
    """کارت کوین با فیلدهای صحیح درصد تغییرات برای 3 تایم‌فریم اصلی"""
    
    # پیدا کردن درصد تغییرات بر اساس تایم‌فریم انتخاب شده
    def get_price_change_by_timeframe(coin_data, timeframe):
        """گرفتن درصد تغییرات بر اساس تایم‌فریم"""
        timeframe_map = {
            "1h": "priceChange1h",   # 1 ساعت
            "24h": "priceChange1d",  # 1 روز
            "7d": "priceChange1w"    # 1 هفته
        }
        
        change_field = timeframe_map.get(timeframe, "priceChange1d")
        change_value = coin_data.get(change_field, 0)
        
        return change_value if change_value is not None else 0
    
    # گرفتن درصد تغییرات بر اساس تایم‌فریم انتخاب شده
    current_timeframe = st.session_state.selected_timeframe
    change_value = get_price_change_by_timeframe(coin, current_timeframe)
    
    change_color = "text-success" if change_value >= 0 else "text-error"
    change_icon = "📈" if change_value >= 0 else "📉"
    
    vortex_data = coin.get('VortexAI_analysis', {})
    
    # استفاده از کامپوننت‌های خالص Streamlit
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        
        with col1:
            # نماد و نام
            st.markdown(f"**{coin.get('symbol', 'N/A')}**")
            st.markdown(f"<div class='text-secondary' style='font-size: 0.8rem;'>{coin.get('name', 'Unknown')}</div>", unsafe_allow_html=True)
            
            # آنومالی حجم
            if vortex_data.get('volume_anomaly'):
                st.markdown("<div class='anomaly-badge'>∆ Anomaly</div>", unsafe_allow_html=True)
        
        with col2:
            # قیمت - اولویت‌بندی شده
            price = (
                coin.get('realtime_price') or 
                coin.get('price') or 
                0
            )
            st.markdown(f"<div class='text-primary' style='font-size: 1.1rem; font-weight: bold; text-align: center;'>${price:,.2f}</div>", unsafe_allow_html=True)
            
            # درصد تغییرات در دکمه سفید - حالا با مقدار واقعی
            st.markdown(f"""
            <div class='value-badge'>
                <div class='{change_color}' style='font-size: 0.9rem;'>
                    {change_icon} {change_value:+.2f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # سیگنال AI در دکمه سفید
            st.markdown("<div class='text-secondary' style='font-size: 0.8rem; text-align: center;'>Signal</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='value-badge'>
                <div class='text-signal' style='font-size: 1rem; font-weight: bold;'>
                    {vortex_data.get('signal_strength', 0):.1f}/10
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # حجم - اولویت‌بندی شده
            volume = (
                coin.get('realtime_volume') or 
                coin.get('volume') or 
                0
            )
            st.markdown("<div class='text-secondary' style='font-size: 0.8rem; text-align: center;'>Volume</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='text-primary' style='font-size: 0.9rem; text-align: center;'>${volume/1000000:,.1f}M</div>", unsafe_allow_html=True)
        
        # جداکننده خط
        st.markdown("---")

# اضافه کردن دکمه دیباگ در جایی از برنامه
def add_debug_button():
    """اضافه کردن دکمه دیباگ برای بررسی داده‌ها"""
    if st.sidebar.button("🐛 Debug Mode"):
        st.session_state.show_debug = not st.session_state.get('show_debug', False)
        st.rerun()
    
    if st.session_state.get('show_debug', False):
        st.sidebar.info("🔍 Debug Mode: ON")
        
        # نمایش ساختار اولین کوین
        if st.session_state.scan_data and st.session_state.scan_data.get('coins'):
            st.sidebar.write("📊 First Coin Structure:")
            st.sidebar.json(st.session_state.scan_data['coins'][0])

# ==================== MAIN APP ====================
class VortexAIApp:
    def __init__(self):
        self.api_client = VortexAPIClient(API_BASE_URL)
        self.technical_ui = TechnicalAnalysisUI(self.api_client)

    def render_technical_analysis(self):
        """صفحه تحلیل تکنیکال پیشرفته"""
        st.markdown("""
        <div class="glass-card">
            <h2 style="color: #FFFFFF; margin: 0;">📈 Technical Analysis</h2>
        </div>
        """, unsafe_allow_html=True)
    
        if st.session_state.scan_data:
            coins = st.session_state.scan_data.get("coins", [])
        
            if not coins:
                st.warning("⚠️ No coins data available")
                return
            
            # انتخاب کوین برای تحلیل
            selected_symbol = st.selectbox(
                "Select Coin for Detailed Analysis",
                options=[coin['symbol'] for coin in coins],
                key="tech_analysis_coin"
            )
        
            # پیدا کردن کوین انتخاب شده
            selected_coin = next((coin for coin in coins if coin['symbol'] == selected_symbol), None)
        
            if selected_coin:
                self.technical_ui.render_technical_dashboard(selected_coin)
            else:
                st.warning("⚠️ Please select a valid coin")
        else:
            st.warning("⚠️ Please scan market first to see technical data")
    def run(self):
        self.initialize_session_state()
        apply_glass_design()
        render_glass_header()
        self.render_status_cards()
        
        page, scan_limit, filter_type = self.render_sidebar()
        
        if "📊 Dashboard" in page:
            self.render_dashboard()
        elif "🔍 Market Scanner" in page:
            self.render_market_scanner(scan_limit, filter_type)
        elif "📈 Technical Data" in page:  # این خط تغییر کرد
            self.render_technical_analysis()  # حالا صفحه واقعی هست
        elif "🚀 Top Movers" in page:
            st.info("🚀 Top movers page - Coming soon")
        elif "⚠️ Alerts" in page:
            st.info("⚠️ Alerts page - Coming soon")
        elif "⚙️ Settings" in page:
            st.info("⚙️ Settings page")
    
    def initialize_session_state(self):
        """مقادیر اولیه session state"""
        if 'scan_data' not in st.session_state:
            st.session_state.scan_data = None
        if 'selected_coin' not in st.session_state:
            st.session_state.selected_coin = None
        if 'last_scan_time' not in st.session_state:
            st.session_state.last_scan_time = None
        if 'selected_timeframe' not in st.session_state:
            st.session_state.selected_timeframe = "24h"
        if 'pending_rescan' not in st.session_state:
            st.session_state.pending_rescan = False

    def perform_market_scan(self, timeframe=None):
        """انجام اسکن مارکت"""
        scan_timeframe = timeframe or st.session_state.selected_timeframe
        with st.spinner(f"🔍 Scanning market ({scan_timeframe})..."):
            scan_result = self.api_client.scan_market(
                limit=100,
                filter_type="volume",
                timeframe=scan_timeframe
            )
            if scan_result and scan_result.get("success"):
                st.session_state.scan_data = scan_result
                st.session_state.last_scan_time = datetime.now().strftime("%H:%M:%S")
                st.session_state.pending_rescan = False
                st.success(f"✅ Scan completed! Found {len(scan_result.get('coins', []))} coins ({scan_timeframe})")
            else:
                st.error("❌ Market scan failed!")

    def render_status_cards(self):
        """کارت های وضعیت"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            health = self.api_client.get_health_status()
            status_color = "🟢" if health.get('status') == 'healthy' else "🔴"
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <div class="text-secondary">System Status</div>
                <div class="text-primary" style="font-size: 1.2rem; font-weight: bold;">
                    {status_color} {health.get('status','Unknown').title()}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            last_update = st.session_state.last_scan_time or "Never"
            current_tf = st.session_state.selected_timeframe
            display_map = {"1h": "1H", "4h": "4H", "24h": "1D", "7d": "1W", "30d": "1M", "90d": "3M"}
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <div class="text-secondary">Last Scan</div>
                <div class="text-primary" style="font-size: 1.1rem; font-weight: bold;">
                    {last_update}
                </div>
                <div class="text-secondary" style="font-size: 0.8rem; margin-top: 0.3rem;">
                    {display_map.get(current_tf, current_tf)}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if st.button("🔄 Scan Market", use_container_width=True, type="primary"):
                self.perform_market_scan()

    def render_sidebar(self):
        """نوار کناری"""
        with st.sidebar:
            st.markdown("""
            <div class="glass-card" style="text-align: center;">
                <h2 style="color: #2563EB; margin: 0;">VortexAI</h2>
                <p style="color: rgba(255, 255, 255, 0.8); margin: 0;">Crypto Scanner</p>
            </div>
            """, unsafe_allow_html=True)
            
            page = st.radio(
                "Navigation",
                ["📊 Dashboard", "🔍 Market Scanner", "📈 Technical Data", "🚀 Top Movers", "⚠️ Alerts", "📈 Technical Data", "⚙️ Settings"],
                index=1
            )
            
            st.divider()
            
            # تنظیمات اسکن
            st.markdown("""
            <div class="glass-card">
                <h4 style="color: #FFFFFF;">Scan Settings</h4>
            </div>
            """, unsafe_allow_html=True)
            
            scan_limit = st.slider("Number of coins", 10, 200, 100)
            filter_type = st.selectbox("Filter by", ["volume", "momentum_1h", "momentum_4h", "ai_signal"])
            
            if st.button("💡 Start Real Scan", use_container_width=True):
                self.perform_market_scan()
            
            return page, scan_limit, filter_type

    def render_market_scanner(self, scan_limit, filter_type):
        """اسکنر مارکت"""
        st.markdown("""
        <div class="glass-card">
            <h2 style="color: #FFFFFF; margin: 0;">🔍 Market Scanner</h2>
        </div>
        """, unsafe_allow_html=True)

        # اگر تایم‌فریم تغییر کرد، اسکن جدید بزن
        if st.session_state.pending_rescan:
            self.perform_market_scan()

        # نمایش وضعیت داده‌ها
        if st.session_state.scan_data:
            coins = st.session_state.scan_data.get("coins", [])
            current_tf = st.session_state.selected_timeframe
            display_map = {"1h": "1H", "4h": "4H", "24h": "1D", "7d": "1W", "30d": "1M", "90d": "3M"}
            st.success(f"📊 Displaying {len(coins)} coins ({display_map.get(current_tf, current_tf)})")

            # نمایش انتخاب تایم‌فریم
            render_timeframe_selector()

            # نمایش کوین‌ها در یک کارت شیشه‌ای
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            for coin in coins:
                render_coin_card_clean(coin)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ No market data available. Click 'Scan Market' to get real-time data.")

    def render_dashboard(self):
        """داشبورد اصلی"""
        st.markdown("""
        <div class="glass-card">
            <h2 style="color: #FFFFFF; margin: 0;">📊 Market Overview</h2>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.scan_data:
            coins = st.session_state.scan_data.get("coins", [])
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                render_metric_card("Total Coins", len(coins))
            
            with col2:
                strong_signals = len([c for c in coins if c.get('VortexAI_analysis', {}).get('signal_strength', 0) > 7])
                render_metric_card("Strong Signals", strong_signals)
            
            with col3:
                anomalies = len([c for c in coins if c.get('VortexAI_analysis', {}).get('volume_anomaly', False)])
                render_metric_card("Volume Anomalies", anomalies)
            
            with col4:
                # محاسبه میانگین تغییرات 24h - اصلاح شده
                total_change = sum([c.get('change_24h', 0) for c in coins])
                avg_change = total_change / max(len(coins), 1)
                render_metric_card("Avg 24h Change", f"{avg_change:+.2f}%", avg_change)
        else:
            st.warning("⚠️ Scan market first to see dashboard data")

    def run(self):
        """اجرای برنامه"""
        self.initialize_session_state()
        apply_glass_design()
        render_glass_header()
        add_debug_button()
        self.render_status_cards()
        
        page, scan_limit, filter_type = self.render_sidebar()
        
        if "📊 Dashboard" in page:
            self.render_dashboard()
        elif "🔍 Market Scanner" in page:
            self.render_market_scanner(scan_limit, filter_type)
        elif "🚀 Top Movers" in page:
            st.info("🚀 Top movers page - Coming soon")
        elif "⚠️ Alerts" in page:
            st.info("⚠️ Alerts page - Coming soon")
        elif "📈 Technical Data" in page:
            st.info("📈 Technical data page - Coming soon")
        elif "⚙️ Settings" in page:
            st.info("⚙️ Settings page")

if __name__ == "__main__":
    app = VortexAIApp()
    app.run()
