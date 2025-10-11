# technical_analysis.py (بدون plotly)
import streamlit as st

class TechnicalAnalysisUI:
    def __init__(self, api_client):
        self.api_client = api_client
    
    
    def get_coin_technical(self, symbol):
        """دریافت تحلیل تکنیکال از سرور با اندپوینت صحیح"""
        try:
            st.write(f"🔍 Fetching technical data for {symbol}...")
            technical_data = self.api_client.get_coin_technical(symbol)
        
            if technical_data:
                st.write("✅ Technical data received from server")
                # نمایش دیباگ اطلاعات
                st.json(technical_data)
                return technical_data
            else:
                st.warning("⚠️ No technical data available from server")
                return None
        except Exception as e:
            st.error(f"🔧 Error getting technical data: {str(e)}")
            return None

    def render_technical_dashboard(self, coin):
         """داشبورد تحلیل تکنیکال برای یک کوین"""
        st.markdown(f"""
        <div class="glass-card">
            <h2 style="color: #FFFFFF; margin: 0;">📈 Technical Analysis - {coin.get('symbol', 'N/A')}</h2>
        </div>
        """, unsafe_allow_html=True)
    
        # تست مستقیم اندپوینت
        if st.button("🧪 Test Direct API Call"):
            test_symbol = coin['symbol']
            st.write(f"Testing API for: {test_symbol}")
            test_url = f"https://server-test-ovta.onrender.com/analysis?symbol={test_symbol.lower()}_usdt"
            st.write(f"API URL: {test_url}")
    
        # دریافت داده‌های تکنیکال از سرور
        technical_data = self.get_coin_technical(coin['symbol'])
    
        if technical_data and technical_data.get("success"):
            st.success("✅ Technical data loaded successfully!")
            self.render_indicators_grid(technical_data)
            self.render_signals(technical_data, coin)
        else:
            st.warning("⚠️ Technical data not available for this coin")
            # نمایش داده‌های پایه به عنوان fallback
            self.render_basic_analysis(coin)
    
        self.render_price_info(coin)
    
    def render_indicators_grid(self, technical_data):
        """نمایش گرید اندیکاتورها"""
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: #FFFFFF; margin: 0 0 1rem 0;">📊 Technical Indicators</h3>
        </div>
        """, unsafe_allow_html=True)
        
        indicators = technical_data.get('technical_indicators', {})
        
        # ردیف اول اندیکاتورها
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            self.render_metric_glass("RSI", f"{indicators.get('rsi', 0):.1f}")
        with col2:
            self.render_metric_glass("MACD", f"{indicators.get('macd', 0):.2f}")
        with col3:
            self.render_metric_glass("Stochastic %K", f"{indicators.get('stochastic_k', 0):.1f}")
        with col4:
            self.render_metric_glass("Williams %R", f"{indicators.get('williams_r', 0):.1f}")
        
        # ردیف دوم اندیکاتورها
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            self.render_metric_glass("Bollinger Upper", f"{indicators.get('bollinger_upper', 0):.2f}")
        with col2:
            self.render_metric_glass("MA (20)", f"{indicators.get('moving_avg_20', 0):.2f}")
        with col3:
            self.render_metric_glass("MA (50)", f"{indicators.get('moving_avg_50', 0):.2f}")
        with col4:
            self.render_metric_glass("MA (200)", f"{indicators.get('moving_avg_200', 0):.2f}")
    
    def render_metric_glass(self, title, value):
        """نمایش متریک با طراحی شیشه‌ای"""
        st.markdown(f"""
        <div class="glass-metric">
            <div class="text-secondary" style="font-size: 0.8rem;">{title}</div>
            <div class="text-primary" style="font-size: 1.2rem; margin: 0.5rem 0;">{value}</div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_signals(self, technical_data, coin):
        """نمایش سیگنال‌های خرید/فروش"""
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: #FFFFFF; margin: 0 0 1rem 0;">🎯 Trading Signals</h3>
        </div>
        """, unsafe_allow_html=True)
        
        vortex_analysis = technical_data.get('vortexai_analysis', {})
        support_resistance = technical_data.get('support_resistance', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="glass-card">
                <div class="text-secondary">Market Sentiment</div>
                <div class="text-primary" style="font-size: 1.3rem; font-weight: bold;">
                    {vortex_analysis.get('market_sentiment', 'NEUTRAL')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="glass-card">
                <div class="text-secondary">Risk Level</div>
                <div class="text-primary" style="font-size: 1.3rem; font-weight: bold;">
                    {vortex_analysis.get('risk_level', 'MEDIUM')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            support_levels = support_resistance.get('support', [0, 0])
            resistance_levels = support_resistance.get('resistance', [0, 0])
            
            st.markdown(f"""
            <div class="glass-card">
                <div class="text-success">Support Level</div>
                <div class="text-primary" style="font-size: 1.3rem; font-weight: bold;">
                    ${support_levels[0]:.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="glass-card">
                <div class="text-error">Resistance Level</div>
                <div class="text-primary" style="font-size: 1.3rem; font-weight: bold;">
                    ${resistance_levels[0]:.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_price_info(self, coin):
        """نمایش اطلاعات قیمت"""
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: #FFFFFF; margin: 0 0 1rem 0;">💰 Price Information</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            price = coin.get('price') or coin.get('realtime_price') or 0
            self.render_metric_glass("Current Price", f"${price:.4f}")
        
        with col2:
            change_24h = coin.get('priceChange1d', 0)
            change_color = "text-success" if change_24h >= 0 else "text-error"
            st.markdown(f"""
            <div class="glass-metric">
                <div class="text-secondary" style="font-size: 0.8rem;">24h Change</div>
                <div class="{change_color}" style="font-size: 1.2rem; margin: 0.5rem 0; font-weight: bold;">
                    {change_24h:+.2f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            volume = coin.get('volume') or 0
            self.render_metric_glass("24h Volume", f"${volume/1000000:.1f}M")
