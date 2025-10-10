import streamlit as st
import pandas as pd
from datetime import datetime
from constants import API_BASE_URL, LIGHT_THEME, DARK_THEME
from api_client import VortexAPIClient
from components.cards import render_metric_card, render_coin_card, render_alert_card

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
            /* حذف استایل‌های اضافی */
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
            dark_mode = st.toggle("🌙 Dark Mode", value=False)
            self.apply_theme(dark_mode)
            
            return selected_page
    
    def render_dashboard(self):
        """داشبورد اصلی"""
        st.markdown(f"""
        <div style="color: {self.current_theme['text_primary']}; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;">
            📊 Market Overview
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_metric_card("Total Coins", "150", "+5", self.current_theme)
        with col2:
            render_metric_card("Active Signals", "23", "+3", self.current_theme)
        with col3:
            render_metric_card("Volume Anomalies", "7", "+2", self.current_theme)
        with col4:
            render_metric_card("Market Sentiment", "Bullish", None, self.current_theme)
        
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
            render_alert_card(alert, self.current_theme)
    
    def render_market_scanner(self):
        """اسکنر مارکت"""
        st.markdown(f"""
        <div style="color: {self.current_theme['text_primary']}; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;">
            🔍 Market Scanner
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_query = st.text_input("🔍 Search coins...", placeholder="BTC, ETH, SOL...")
        with col2:
            filter_type = st.selectbox("Filter by", ["All", "Volume", "Momentum", "Signals"])
        with col3:
            limit = st.slider("Results", 10, 100, 50)
        
        coins_data = [
            {"symbol": "BTC", "name": "Bitcoin", "price": 45000, "change_24h": 2.5, "volume": 25000000, "signal": 8.5, "anomaly": True},
            {"symbol": "ETH", "name": "Ethereum", "price": 2500, "change_24h": -1.2, "volume": 15000000, "signal": 6.8, "anomaly": False},
            {"symbol": "SOL", "name": "Solana", "price": 120, "change_24h": 5.8, "volume": 5000000, "signal": 9.2, "anomaly": True},
        ]
        
        for coin in coins_data:
            render_coin_card(coin, self.current_theme)
    
    def render_top_movers(self):
        """صفحه Top Movers"""
        st.markdown(f"""
        <div style="color: {self.current_theme['text_primary']}; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;">
            ⚡ Top Movers
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            timeframe = st.selectbox("Timeframe", ["1H", "4H", "24H", "7D"], key="movers_timeframe")
        with col2:
            mover_type = st.selectbox("Type", ["Gainers", "Losers", "Both"], key="movers_type")
        with col3:
            min_volume = st.slider("Min Volume ($M)", 1, 100, 10)
        
        top_movers = [
            {"symbol": "BTC", "name": "Bitcoin", "price": 45000, "change": 8.5, "volume": 45.2, "signal": 9.1},
            {"symbol": "SOL", "name": "Solana", "price": 125.60, "change": 12.3, "volume": 8.9, "signal": 8.7},
        ]
        
        for coin in top_movers:
            render_coin_card({
                "symbol": coin['symbol'],
                "name": coin['name'],
                "price": coin['price'],
                "change_24h": coin['change'],
                "volume": coin['volume'] * 1000000,
                "signal": coin['signal'],
                "anomaly": coin['change'] > 10
            }, self.current_theme)
    
    def render_alerts_page(self):
        """صفحه هشدارها"""
        st.markdown(f"""
        <div style="color: {self.current_theme['text_primary']}; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;">
            🔔 Alert System
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_metric_card("Active Alerts", "12", "+3", self.current_theme)
        with col2:
            render_metric_card("Volume Alerts", "5", "+1", self.current_theme)
        with col3:
            render_metric_card("Price Alerts", "4", "+2", self.current_theme)
        with col4:
            render_metric_card("Signal Alerts", "3", "0", self.current_theme)
        
        alerts_data = [
            {"type": "volume", "coin": "BTC", "message": "Unusual volume spike detected", "time": "2 min ago", "priority": "high"},
            {"type": "price", "coin": "ETH", "message": "Rapid price increase +8.5%", "time": "5 min ago", "priority": "medium"},
        ]
        
        for alert in alerts_data:
            render_alert_card(alert, self.current_theme)
    
    def render_technical_data(self):
        """صفحه داده‌های تکنیکال"""
        st.markdown(f"""
        <div style="color: {self.current_theme['text_primary']}; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;">
            📈 Technical Data
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_coin = st.selectbox("Select Coin", ["BTC", "ETH", "SOL", "AVAX"], key="tech_coin")
        with col2:
            timeframe = st.selectbox("Timeframe", ["1H", "4H", "24H", "7D"], key="tech_timeframe")
        
        st.markdown(f"""
        <div style="color: {self.current_theme['text_primary']}; font-size: 1.2rem; font-weight: bold; margin: 1.5rem 0 1rem 0;">
            📊 Technical Indicators for {selected_coin}
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_metric_card("RSI", "65.2", None, self.current_theme)
        with col2:
            render_metric_card("MACD", "2.45", None, self.current_theme)
        with col3:
            render_metric_card("Signal Strength", "8.5/10", None, self.current_theme)
        with col4:
            render_metric_card("Volume", "$45.2M", None, self.current_theme)
    
    def render_settings(self):
        """صفحه تنظیمات"""
        st.markdown(f"""
        <div style="color: {self.current_theme['text_primary']}; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;">
            ⚙️ Settings
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔍 Scanner Settings", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                scan_interval = st.slider("Scan Interval (minutes)", 1, 60, 5)
                min_volume = st.number_input("Minimum Volume ($M)", value=1.0)
            with col2:
                max_results = st.slider("Max Results", 10, 200, 50)
                auto_refresh = st.toggle("Auto Refresh", value=True)
    
    def run(self):
        """اجرای برنامه"""
        self.render_header()
        selected_page = self.render_sidebar()
        
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

if __name__ == "__main__":
    app = VortexAIApp()
    app.run()
