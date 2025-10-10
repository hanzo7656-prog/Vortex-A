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
