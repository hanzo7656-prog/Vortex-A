# technical_analysis.py
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class TechnicalAnalysisUI:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def render_technical_dashboard(self, coin):
        """داشبورد تحلیل تکنیکال برای یک کوین"""
        st.markdown(f"## 📈 Technical Analysis - {coin.get('symbol', 'N/A')}")
        
        # دریافت داده‌های تکنیکال از سرور
        technical_data = self.get_coin_technical(coin['symbol'])
        
        if technical_data and technical_data.get('success'):
            self.render_indicators_grid(technical_data)
            self.render_charts(technical_data, coin)
            self.render_signals(technical_data)
        else:
            st.warning("⚠️ Technical data not available")
    
    def get_coin_technical(self, symbol):
        """دریافت تحلیل تکنیکال از سرور"""
        try:
            response = self.api_client.session.get(
                f"{self.api_client.base_url}/coin/{symbol}/technical"
            )
            return response.json()
        except:
            return None
    
    def render_indicators_grid(self, technical_data):
        """نمایش گرید اندیکاتورها"""
        st.subheader("📊 Technical Indicators")
        
        indicators = technical_data.get('technical_indicators', {})
        
        cols = st.columns(4)
        with cols[0]:
            st.metric("RSI", f"{indicators.get('rsi', 0):.1f}")
        with cols[1]:
            st.metric("MACD", f"{indicators.get('macd', 0):.2f}")
        with cols[2]:
            st.metric("Stochastic %K", f"{indicators.get('stochastic_k', 0):.1f}")
        with cols[3]:
            st.metric("Williams %R", f"{indicators.get('williams_r', 0):.1f}")
        
        cols = st.columns(3)
        with cols[0]:
            st.metric("Bollinger Upper", f"{indicators.get('bollinger_upper', 0):.2f}")
        with cols[1]:
            st.metric("Moving Avg (20)", f"{indicators.get('moving_avg_20', 0):.2f}")
        with cols[2]:
            st.metric("Moving Avg (50)", f"{indicators.get('moving_avg_50', 0):.2f}")

    def render_charts(self, technical_data, coin):
        """رسم نمودارهای تکنیکال"""
        # اینجا میتونی از Plotly برای رسم نمودار استفاده کنی
        pass
    
    def render_signals(self, technical_data):
        """نمایش سیگنال‌های خرید/فروش"""
        st.subheader("🎯 Trading Signals")
        
        vortex_analysis = technical_data.get('vortexai_analysis', {})
        support_resistance = technical_data.get('support_resistance', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Market Sentiment**: {vortex_analysis.get('market_sentiment', 'NEUTRAL')}")
            st.info(f"**Risk Level**: {vortex_analysis.get('risk_level', 'MEDIUM')}")
        
        with col2:
            st.success(f"**Support**: ${support_resistance.get('support', [0])[0]:.2f}")
            st.error(f"**Resistance**: ${support_resistance.get('resistance', [0])[0]:.2f}")
