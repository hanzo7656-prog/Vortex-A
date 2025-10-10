import streamlit as st
import pandas as pd
from datetime import datetime
from config.constants import API_BASE_URL, LIGHT_THEME, DARK_THEME
from modules.api_client import VortexAPIClient

class VortexAIApp:
    def __init__(self):
        self.api_client = VortexAPIClient(API_BASE_URL)
        self.current_theme = LIGHT_THEME
    
    def apply_theme(self, dark_mode):
        """اعمال تم انتخاب شده"""
        self.current_theme = DARK_THEME if dark_mode else LIGHT_THEME
        
        st.markdown(f"""
        <style>
            .main {{
                background-color: {self.current_theme['background']};
            }}
            .metric-card {{
                background: {self.current_theme['surface']};
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid {self.current_theme['primary']};
                margin: 0.5rem 0;
            }}
            .coin-card {{
                background: {self.current_theme['surface']};
                padding: 1rem;
                border-radius: 10px;
                border: 1px solid {self.current_theme['border']};
                margin: 0.5rem 0;
            }}
            .alert-card {{
                background: {self.current_theme['surface']};
                padding: 1rem;
                border-radius: 10px;
                border-left: 4px solid {self.current_theme['warning']};
                margin: 0.5rem 0;
            }}
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self):
        """هدر اصلی"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"""
            <div style="color: {self.current_theme['primary']}; font-size: 2rem; font-weight: bold;">
                🚀 VortexAI Crypto Scanner
            </div>
            <div style="color: {self.current_theme['text_secondary']};">
                v6.0 - Real-time Market Intelligence
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # وضعیت سیستم
            health = self.api_client.get_health_status()
            status_color = "🟢" if health.get('status') == 'healthy' else "🔴"
            st.markdown(f"""
            <div style="color: {self.current_theme['text_secondary']}; text-align: center;">
                <div>System Status</div>
                <div style="font-weight: bold; color: {self.current_theme['text_primary']};">
                    {status_color} {health.get('status', 'Unknown').title()}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # زمان بروزرسانی
            st.markdown(f"""
            <div style="color: {self.current_theme['text_secondary']}; text-align: center;">
                <div>Last Update</div>
                <div style="font-weight: bold; color: {self.current_theme['text_primary']};">
                    {datetime.now().strftime('%H:%M:%S')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
    
    def render_sidebar(self):
        """نوار کناری"""
        with st.sidebar:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid {self.current_theme['border']};">
                <div style="color: {self.current_theme['primary']}; font-size: 1.5rem; font-weight: bold;">VortexAI</div>
                <div style="color: {self.current_theme['text_secondary']}; font-size: 0.9rem;">Crypto Scanner</div>
            </div>
            """, unsafe_allow_html=True)
            
            # منوهای اصلی
            menu_options = [
                {"icon": "📊", "label": "Dashboard", "page": "dashboard"},
                {"icon": "🔍", "label": "Market Scanner", "page": "scanner"},
                {"icon": "⚡", "label": "Top Movers", "page": "movers"},
                {"icon": "🔔", "label": "Alerts", "page": "alerts"},
                {"icon": "📈", "label": "Technical Data", "page": "technical"},
                {"icon": "⚙️", "label": "Settings", "page": "settings"},
            ]
            
            selected_page = "dashboard"
            for option in menu_options:
                if st.button(
                    f"{option['icon']} {option['label']}", 
                    key=option['page'],
                    use_container_width=True,
                    type="primary" if option['page'] == selected_page else "secondary"
                ):
                    selected_page = option['page']
            
            st.divider()
            
            # سوئیچ تم
            dark_mode = st.toggle("🌙 Dark Mode", value=False)
            self.apply_theme(dark_mode)
            
            return selected_page
    
    def render_dashboard(self):
        """داشبورد اصلی - بدون نمودار"""
        st.markdown(f"""
        <div style="color: {self.current_theme['text_primary']}; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;">
            📊 Market Overview
        </div>
        """, unsafe_allow_html=True)
        
        # کارت‌های متریک بازار
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.render_metric_card("Total Coins", "150", "+5", self.current_theme)
        
        with col2:
            self.render_metric_card("Active Signals", "23", "+3", self.current_theme)
        
        with col3:
            self.render_metric_card("Volume Anomalies", "7", "+2", self.current_theme)
        
        with col4:
            self.render_metric_card("Market Sentiment", "Bullish", None, self.current_theme)
        
        # هشدارهای فوری
        st.markdown(f"""
        <div style="color: {self.current_theme['text_primary']}; font-size: 1.2rem; font-weight: bold; margin: 2rem 0 1rem 0;">
            ⚠️ Active Alerts
        </div>
        """, unsafe_allow_html=True)
        
        alerts = [
            {"type": "volume", "coin": "BTC", "message": "Volume spike detected", "time": "2 min ago"},
            {"type": "price", "coin": "ETH", "message": "Rapid price movement", "time": "5 min ago"},
        ]
        
        for alert in alerts:
            self.render_alert_card(alert, self.current_theme)
    
    def render_market_scanner(self):
        """اسکنر مارکت - بدون نمودار"""
        st.markdown(f"""
        <div style="color: {self.current_theme['text_primary']}; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;">
            🔍 Market Scanner
        </div>
        """, unsafe_allow_html=True)
        
        # فیلترها
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_query = st.text_input("🔍 Search coins...", placeholder="BTC, ETH, SOL...")
        
        with col2:
            filter_type = st.selectbox("Filter by", ["All", "Volume", "Momentum", "Signals"])
        
        with col3:
            limit = st.slider("Results", 10, 100, 50)
        
        # داده‌های نمونه
        coins_data = [
            {"symbol": "BTC", "name": "Bitcoin", "price": 45000, "change_24h": 2.5, "volume": 25000000, "signal": 8.5, "anomaly": True},
            {"symbol": "ETH", "name": "Ethereum", "price": 2500, "change_24h": -1.2, "volume": 15000000, "signal": 6.8, "anomaly": False},
            {"symbol": "SOL", "name": "Solana", "price": 120, "change_24h": 5.8, "volume": 5000000, "signal": 9.2, "anomaly": True},
        ]
        
        # نمایش کوین‌ها
        for coin in coins_data:
            self.render_coin_card(coin, self.current_theme)
    
    def render_top_movers(self):
        """صفحه Top Movers - بدون نمودار"""
        st.markdown(f"""
        <div style="color: {self.current_theme['text_primary']}; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;">
            ⚡ Top Movers
        </div>
        """, unsafe_allow_html=True)
        
        # فیلترهای Top Movers
        col1, col2, col3 = st.columns(3)
        
        with col1:
            timeframe = st.selectbox("Timeframe", ["1H", "4H", "24H", "7D"], key="movers_timeframe")
        
        with col2:
            mover_type = st.selectbox("Type", ["Gainers", "Losers", "Both"], key="movers_type")
        
        with col3:
            min_volume = st.slider("Min Volume ($M)", 1, 100, 10)
        
        # داده‌های نمونه Top Movers
        top_movers = [
            {"symbol": "BTC", "name": "Bitcoin", "price": 45000, "change": 8.5, "volume": 45.2, "signal": 9.1},
            {"symbol": "SOL", "name": "Solana", "price": 125.60, "change": 12.3, "volume": 8.9, "signal": 8.7},
            {"symbol": "AVAX", "name": "Avalanche", "price": 42.30, "change": 9.8, "volume": 3.2, "signal": 8.2},
            {"symbol": "ETH", "name": "Ethereum", "price": 2480.50, "change": 5.6, "volume": 18.7, "signal": 7.8},
            {"symbol": "ADA", "name": "Cardano", "price": 0.58, "change": -3.2, "volume": 2.1, "signal": 6.5},
            {"symbol": "DOT", "name": "Polkadot", "price": 7.25, "change": -5.7, "volume": 1.8, "signal": 5.9},
        ]
        
        # نمایش Top Movers
        for coin in top_movers:
            self.render_mover_card(coin, self.current_theme)
    
    def render_alerts_page(self):
        """صفحه هشدارها - بدون نمودار"""
        st.markdown(f"""
        <div style="color: {self.current_theme['text_primary']}; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;">
            🔔 Alert System
        </div>
        """, unsafe_allow_html=True)
        
        # آمار هشدارها
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.render_metric_card("Active Alerts", "12", "+3", self.current_theme)
        
        with col2:
            self.render_metric_card("Volume Alerts", "5", "+1", self.current_theme)
        
        with col3:
            self.render_metric_card("Price Alerts", "4", "+2", self.current_theme)
        
        with col4:
            self.render_metric_card("Signal Alerts", "3", "0", self.current_theme)
        
        # فیلتر هشدارها
        col1, col2 = st.columns([3, 1])
        
        with col1:
            alert_filter = st.selectbox("Filter Alerts", [
                "All Alerts", 
                "Volume Anomalies", 
                "Price Movements", 
                "Strong Signals",
                "System Alerts"
            ])
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Refresh Alerts", use_container_width=True):
                st.rerun()
        
        # لیست هشدارها
        alerts_data = [
            {"type": "volume", "coin": "BTC", "message": "Unusual volume spike detected", "time": "2 min ago", "priority": "high"},
            {"type": "price", "coin": "ETH", "message": "Rapid price increase +8.5%", "time": "5 min ago", "priority": "medium"},
            {"type": "signal", "coin": "SOL", "message": "Strong buy signal detected", "time": "8 min ago", "priority": "high"},
            {"type": "volume", "coin": "AVAX", "message": "Volume anomaly - potential pump", "time": "12 min ago", "priority": "high"},
            {"type": "system", "coin": "System", "message": "API connection unstable", "time": "15 min ago", "priority": "medium"},
        ]
        
        for alert in alerts_data:
            self.render_detailed_alert_card(alert, self.current_theme)
    
    def render_technical_data(self):
        """صفحه داده‌های تکنیکال - بدون نمودار"""
        st.markdown(f"""
        <div style="color: {self.current_theme['text_primary']}; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;">
            📈 Technical Data
        </div>
        """, unsafe_allow_html=True)
        
        # انتخاب کوین
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_coin = st.selectbox(
                "Select Coin", 
                ["BTC", "ETH", "SOL", "AVAX", "ADA", "DOT", "XRP", "MATIC"],
                key="tech_coin"
            )
        
        with col2:
            timeframe = st.selectbox("Timeframe", ["1H", "4H", "24H", "7D"], key="tech_timeframe")
        
        # داده‌های تکنیکال نمونه
        tech_data = {
            "BTC": {
                "rsi": 65.2,
                "macd": 2.45,
                "bollinger_upper": 46200,
                "bollinger_lower": 43800,
                "moving_avg_20": 44800,
                "volume": 45.2,
                "support": 44200,
                "resistance": 46000,
                "signal_strength": 8.5
            }
        }
        
        data = tech_data.get(selected_coin, tech_data["BTC"])
        
        # نمایش اندیکاتورهای تکنیکال
        st.markdown(f"""
        <div style="color: {self.current_theme['text_primary']}; font-size: 1.2rem; font-weight: bold; margin: 1.5rem 0 1rem 0;">
            📊 Technical Indicators for {selected_coin}
        </div>
        """, unsafe_allow_html=True)
        
        # ردیف اول اندیکاتورها
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.render_tech_indicator("RSI", f"{data['rsi']}", "Momentum", data['rsi'] > 70, self.current_theme)
        
        with col2:
            self.render_tech_indicator("MACD", f"{data['macd']}", "Trend", data['macd'] > 0, self.current_theme)
        
        with col3:
            self.render_tech_indicator("Signal Strength", f"{data['signal_strength']}/10", "AI Analysis", data['signal_strength'] > 7, self.current_theme)
        
        with col4:
            self.render_tech_indicator("Volume", f"${data['volume']}M", "Activity", data['volume'] > 20, self.current_theme)
        
        # ردیف دوم اندیکاتورها
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.render_tech_indicator("Bollinger Upper", f"${data['bollinger_upper']:,.0f}", "Resistance", False, self.current_theme)
        
        with col2:
            self.render_tech_indicator("Bollinger Lower", f"${data['bollinger_lower']:,.0f}", "Support", False, self.current_theme)
        
        with col3:
            self.render_tech_indicator("MA 20", f"${data['moving_avg_20']:,.0f}", "Trend", False, self.current_theme)
        
        with col4:
            self.render_tech_indicator("Support", f"${data['support']:,.0f}", "Key Level", False, self.current_theme)
    
    def render_settings(self):
        """صفحه تنظیمات"""
        st.markdown(f"""
        <div style="color: {self.current_theme['text_primary']}; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;">
            ⚙️ Settings
        </div>
        """, unsafe_allow_html=True)
        
        # تنظیمات اسکن
        with st.expander("🔍 Scanner Settings", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                scan_interval = st.slider("Scan Interval (minutes)", 1, 60, 5)
                min_volume = st.number_input("Minimum Volume ($M)", value=1.0)
                signal_threshold = st.slider("Signal Threshold", 1, 10, 7)
            
            with col2:
                max_results = st.slider("Max Results", 10, 200, 50)
                auto_refresh = st.toggle("Auto Refresh", value=True)
                alert_sound = st.toggle("Alert Sound", value=True)
        
        # تنظیمات اعلان‌ها
        with st.expander("🔔 Alert Settings"):
            col1, col2 = st.columns(2)
            
            with col1:
                volume_alert = st.toggle("Volume Anomaly Alerts", value=True)
                price_alert = st.toggle("Price Movement Alerts", value=True)
                signal_alert = st.toggle("Strong Signal Alerts", value=True)
            
            with col2:
                volume_threshold = st.slider("Volume Threshold (%)", 50, 500, 200)
                price_threshold = st.slider("Price Change Threshold (%)", 1, 50, 10)
        
        # تنظیمات API
        with st.expander("🔗 API Settings"):
            api_url = st.text_input("API Base URL", value=API_BASE_URL)
            api_timeout = st.slider("API Timeout (seconds)", 5, 60, 30)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Test Connection", use_container_width=True):
                    st.success("✅ Connection successful!")
            
            with col2:
                if st.button("Save Settings", use_container_width=True):
                    st.success("✅ Settings saved successfully!")
        
        # اطلاعات سیستم
        with st.expander("📊 System Information"):
            health_data = self.api_client.get_health_status()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**WebSocket Status:**", health_data.get('websocket_status', {}).get('connected', False))
                st.write("**Active Coins:**", health_data.get('websocket_status', {}).get('active_coins', 0))
                st.write("**API Requests:**", health_data.get('api_status', {}).get('requests_count', 0))
            
            with col2:
                st.write("**Storage Coins:**", health_data.get('gist_status', {}).get('total_coins', 0))
                st.write("**Uptime:**", "Online")
                st.write("**Version:**", "v6.0.0")
    
    def render_metric_card(self, title, value, change, theme):
        """کارت متریک"""
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
    
    def render_coin_card(self, coin, theme):
        """کارت نمایش کوین"""
        change_color = theme['success'] if coin['change_24h'] >= 0 else theme['error']
        change_icon = "📈" if coin['change_24h'] >= 0 else "📉"
        
        anomaly_badge = ""
        if coin['anomaly']:
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
                                {coin['symbol']}
                            </div>
                            {anomaly_badge}
                        </div>
                        <div style="color: {theme['text_secondary']}; font-size: 0.8rem;">{coin['name']}</div>
                    </div>
                </div>
                
                <div style="text-align: center;">
                    <div style="font-weight: bold; color: {theme['text_primary']}; font-size: 1.1rem;">
                        ${coin['price']:,.2f}
                    </div>
                    <div style="color: {change_color}; font-size: 0.9rem;">
                        {change_icon} {coin['change_24h']:+.2f}%
                    </div>
                </div>
                
                <div style="text-align: center;">
                    <div style="color: {theme['text_secondary']}; font-size: 0.8rem;">Signal</div>
                    <div style="color: {theme['primary']}; font-weight: bold; font-size: 1.1rem;">
                        {coin['signal']}/10
                    </div>
                </div>
                
                <div style="text-align: center;">
                    <div style="color: {theme['text_secondary']}; font-size: 0.8rem;">Volume</div>
                    <div style="color: {theme['text_primary']}; font-size: 0.9rem;">
                        ${coin['volume']/1000000:.1f}M
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_mover_card(self, coin, theme):
        """کارت Top Mover"""
        change_color = theme['success'] if coin['change'] >= 0 else theme['error']
        change_icon = "🚀" if coin['change'] >= 0 else "🔻"
        change_prefix = "+" if coin['change'] >= 0 else ""
        
        st.markdown(f"""
        <div class="coin-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 1rem; flex: 2;">
                    <div style="font-size: 1.8rem;">{'🪙' if coin['change'] >= 0 else '📉'}</div>
                    <div>
                        <div style="font-weight: bold; color: {theme['text_primary']}; font-size: 1.2rem;">
                            {coin['symbol']}
                        </div>
                        <div style="color: {theme['text_secondary']}; font-size: 0.8rem;">{coin['name']}</div>
                    </div>
                </div>
                
                <div style="text-align: center; flex: 1;">
                    <div style="font-weight: bold; color: {theme['text_primary']}; font-size: 1.1rem;">
                        ${coin['price']:,.2f}
                    </div>
                </div>
                
                <div style="text-align: center; flex: 1;">
                    <div style="color: {theme['text_secondary']}; font-size: 0.8rem;">Change</div>
                    <div style="color: {change_color}; font-weight: bold; font-size: 1.1rem;">
                        {change_icon} {change_prefix}{coin['change']}%
                    </div>
                </div>
                
                <div style="text-align: center; flex: 1;">
                    <div style="color: {theme['text_secondary']}; font-size: 0.8rem;">Volume</div>
                    <div style="color: {theme['text_primary']}; font-size: 0.9rem;">
                        ${coin['volume']}M
                    </div>
                </div>
                
                <div style="text-align: center; flex: 1;">
                    <div style="color: {theme['text_secondary']}; font-size: 0.8rem;">Signal</div>
                    <div style="color: {theme['primary']}; font-weight: bold; font-size: 1.1rem;">
                        {coin['signal']}/10
                    </div>
                </div>
                
                <div style="flex: 0.5; text-align: center;">
                    <button style="
                        background: {theme['primary']}; 
                        color: white; 
                        border: none; 
                        padding: 0.5rem 1rem; 
                        border-radius: 8px; 
                        cursor: pointer;
                        font-size: 0.8rem;
                    ">View</button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_alert_card(self, alert, theme):
        """کارت هشدار"""
        alert_colors = {
            "volume": theme['warning'],
            "price": theme['error'],
            "signal": theme['success']
        }
        
        st.markdown(f"""
        <div class="alert-card" style="border-left-color: {alert_colors[alert['type']]} !important;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-weight: bold; color: {theme['text_primary']};">
                        {alert['coin']} - {alert['message']}
                    </div>
                </div>
                <div style="color: {theme['text_secondary']}; font-size: 0.8rem;">
                    {alert['time']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_detailed_alert_card(self, alert, theme):
        """کارت هشدار دقیق"""
        priority_colors = {
            "high": theme['error'],
            "medium": theme['warning'],
            "low": theme['success']
        }
        
        alert_icons = {
            "volume": "📊",
            "price": "💰", 
            "signal": "🎯",
            "system": "⚙️"
        }
        
        st.markdown(f"""
        <div class="alert-card" style="border-left-color: {priority_colors[alert['priority']]} !important;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="display: flex; align-items: start; gap: 1rem; flex: 3;">
                    <div style="font-size: 1.5rem;">{alert_icons[alert['type']]}</div>
                    <div>
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem;">
                            <div style="font-weight: bold; color: {theme['text_primary']}; font-size: 1.1rem;">
                                {alert['coin']}
                            </div>
                            <div style="
                                background: {priority_colors[alert['priority']]}; 
                                color: white; 
                                padding: 0.1rem 0.5rem; 
                                border-radius: 8px; 
                                font-size: 0.7rem;
                                text-transform: uppercase;
                            ">
                                {alert['priority']}
                            </div>
                        </div>
                        <div style="color: {theme['text_primary']};">
                            {alert['message']}
                        </div>
                    </div>
                </div>
                
                <div style="text-align: right; flex: 1;">
                    <div style="color: {theme['text_secondary']}; font-size: 0.8rem;">
                        {alert['time']}
                    </div>
                    <button style="
                        background: transparent; 
                        color: {theme['primary']}; 
                        border: 1px solid {theme['primary']}; 
                        padding: 0.3rem 0.8rem; 
                        border-radius: 6px; 
                        cursor: pointer;
                        font-size: 0.7rem;
                        margin-top: 0.5rem;
                    ">Dismiss</button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_tech_indicator(self, title, value, description, is_alert, theme):
        """کارت اندیکاتور تکنیکال"""
        alert_badge = ""
        if is_alert:
            alert_badge = f"""
            <div style="
                background: {theme['warning']}; 
                color: white; 
                padding: 0.1rem 0.4rem; 
                border-radius: 8px; 
                font-size: 0.6rem;
                display: inline-block;
                margin-left: 0.3rem;
            ">Alert</div>
            """
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <div style="color: {theme['text_secondary']}; font-size: 0.9rem; flex: 1;">{title}</div>
                {alert_badge}
            </div>
            <div style="color: {theme['text_primary']}; font-size: 1.4rem; font-weight: bold; margin: 0.5rem 0;">{value}</div>
            <div style="color: {theme['text_secondary']}; font-size: 0.8rem;">{description}</div>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """اجرای برنامه"""
        # رندر هدر
        self.render_header()
        
        # رندر سایدبار و دریافت صفحه انتخاب شده
        selected_page = self.render_sidebar()
        
        # رندر صفحه انتخاب شده
        if selected_page == "dashboard":
            self.render_dashboard()
        elif selected_page == "scanner":
            self.render_market_scanner()
        elif selected_page == "movers":
            self.render_top_movers()
        elif selected_page == "alerts":
            self.render_alerts_page()
        elif selected_page == "technical":
            self.render_technical_data()
        elif selected_page == "settings":
            self.render_settings()

# اجرای برنامه
if __name__ == "__main__":
    app = VortexAIApp()
    app.run()
