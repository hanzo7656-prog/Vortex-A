import streamlit as st

class TechnicalAnalysisUI:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def render_technical_dashboard(self, coin):
        """داشبورد تحلیل تکنیکال با داده‌های واقعی"""
        st.markdown(f"""
        <div class="glass-card">
            <h2 style="color: #FFFFFF; margin: 0;">📈 Technical Analysis - {coin.get('symbol', 'N/A')}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # دریافت داده‌های تکنیکال از سرور
        technical_data = self.get_coin_technical(coin['symbol'])
        
        if technical_data and technical_data.get("success"):
            st.success("✅ Advanced technical data loaded!")
            self.render_advanced_technical(technical_data, coin)
        else:
            st.warning("⚠️ Using basic analysis data")
            self.render_basic_technical(coin)
    
    def get_coin_technical(self, symbol):
        """دریافت تحلیل تکنیکال از سرور"""
        try:
            return self.api_client.get_coin_technical(symbol)
        except Exception as e:
            st.error(f"🔧 Error: {str(e)}")
            return None
    
    def render_advanced_technical(self, technical_data, coin):
        """نمایش تحلیل تکنیکال پیشرفته"""
        indicators = technical_data.get('technical_indicators', {})
        support_resistance = technical_data.get('support_resistance', {})
        vortex_analysis = technical_data.get('vortexai_analysis', {})
        
        # نمایش اطلاعات قیمت
        self.render_price_info(coin, technical_data.get('current_price'))
        
        # نمایش اندیکاتورهای اصلی
        self.render_main_indicators(indicators)
        
        # نمایش سطوح حمایت/مقاومت
        self.render_support_resistance(support_resistance)
        
        # نمایش سیگنال‌های VortexAI
        self.render_vortex_signals(vortex_analysis)
        
        # نمایش اندیکاتورهای تکمیلی
        self.render_additional_indicators(indicators)
    
    def render_price_info(self, coin, current_price):
        """نمایش اطلاعات قیمت"""
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: #FFFFFF; margin: 0 0 1rem 0;">💰 Current Price</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            price = current_price or coin.get('price') or coin.get('realtime_price') or 0
            self.render_metric_glass("Current Price", f"${price:,.2f}")
        
        with col2:
            change_24h = coin.get('priceChange1d', 0)
            change_color = "text-success" if change_24h >= 0 else "text-error"
            st.markdown(f"""
            <div class="glass-metric">
                <div class="text-secondary" style="font-size: 0.8rem;">24H Change</div>
                <div class="{change_color}" style="font-size: 1.2rem; margin: 0.5rem 0; font-weight: bold;">
                    {change_24h:+.2f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            volume = coin.get('volume') or 0
            self.render_metric_glass("24H Volume", f"${volume/1000000:,.1f}M")
    
    def render_main_indicators(self, indicators):
        """نمایش اندیکاتورهای اصلی"""
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: #FFFFFF; margin: 0 0 1rem 0;">📊 Main Technical Indicators</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            rsi = indicators.get('rsi', 0)
            rsi_color = "text-error" if rsi > 70 else "text-success" if rsi < 30 else "text-primary"
            st.markdown(f"""
            <div class="glass-metric">
                <div class="text-secondary">RSI</div>
                <div class="{rsi_color}" style="font-size: 1.3rem; font-weight: bold;">
                    {rsi:.1f}
                </div>
                <div class="text-secondary" style="font-size: 0.7rem;">
                    {"Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            macd = indicators.get('macd', 0)
            macd_color = "text-success" if macd > 0 else "text-error"
            st.markdown(f"""
            <div class="glass-metric">
                <div class="text-secondary">MACD</div>
                <div class="{macd_color}" style="font-size: 1.3rem; font-weight: bold;">
                    {macd:.3f}
                </div>
                <div class="text-secondary" style="font-size: 0.7rem;">
                    {"Bullish" if macd > 0 else "Bearish"}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            stoch_k = indicators.get('stochastic_k', 0)
            stoch_color = "text-error" if stoch_k > 80 else "text-success" if stoch_k < 20 else "text-primary"
            st.markdown(f"""
            <div class="glass-metric">
                <div class="text-secondary">Stochastic %K</div>
                <div class="{stoch_color}" style="font-size: 1.3rem; font-weight: bold;">
                    {stoch_k:.1f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            williams_r = indicators.get('williams_r', 0)
            williams_color = "text-error" if williams_r > -20 else "text-success" if williams_r < -80 else "text-primary"
            st.markdown(f"""
            <div class="glass-metric">
                <div class="text-secondary">Williams %R</div>
                <div class="{williams_color}" style="font-size: 1.3rem; font-weight: bold;">
                    {williams_r:.1f}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_support_resistance(self, support_resistance):
        """نمایش سطوح حمایت و مقاومت"""
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: #FFFFFF; margin: 0 0 1rem 0;">🎯 Support & Resistance</h3>
        </div>
        """, unsafe_allow_html=True)
        
        support_levels = support_resistance.get('support', [0, 0])
        resistance_levels = support_resistance.get('resistance', [0, 0])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="glass-card">
                <div class="text-success" style="font-size: 1.1rem; font-weight: bold;">Support Levels</div>
                <div class="text-primary" style="font-size: 1.3rem; margin: 0.5rem 0;">
                    ${support_levels[0]:,.2f}
                </div>
                <div class="text-secondary" style="font-size: 0.9rem;">
                    Secondary: ${support_levels[1]:,.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="glass-card">
                <div class="text-error" style="font-size: 1.1rem; font-weight: bold;">Resistance Levels</div>
                <div class="text-primary" style="font-size: 1.3rem; margin: 0.5rem 0;">
                    ${resistance_levels[0]:,.2f}
                </div>
                <div class="text-secondary" style="font-size: 0.9rem;">
                    Secondary: ${resistance_levels[1]:,.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_vortex_signals(self, vortex_analysis):
        """نمایش سیگنال‌های VortexAI"""
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: #FFFFFF; margin: 0 0 1rem 0;">🧠 VortexAI Trading Signals</h3>
        </div>
        """, unsafe_allow_html=True)
        
        market_sentiment = vortex_analysis.get('market_sentiment', 'NEUTRAL')
        risk_level = vortex_analysis.get('risk_level', 'MEDIUM')
        prediction_confidence = vortex_analysis.get('prediction_confidence', 0) * 100
        top_opportunities = vortex_analysis.get('top_opportunities', [])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sentiment_color = "text-success" if market_sentiment == "BULLISH" else "text-error" if market_sentiment == "BEARISH" else "text-primary"
            st.markdown(f"""
            <div class="glass-metric">
                <div class="text-secondary">Market Sentiment</div>
                <div class="{sentiment_color}" style="font-size: 1.3rem; font-weight: bold;">
                    {market_sentiment}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            risk_color = "text-error" if risk_level == "HIGH" else "text-warning" if risk_level == "MEDIUM" else "text-success"
            st.markdown(f"""
            <div class="glass-metric">
                <div class="text-secondary">Risk Level</div>
                <div class="{risk_color}" style="font-size: 1.3rem; font-weight: bold;">
                    {risk_level}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="glass-metric">
                <div class="text-secondary">Prediction Confidence</div>
                <div class="text-primary" style="font-size: 1.3rem; font-weight: bold;">
                    {prediction_confidence:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # نمایش سیگنال‌های معاملاتی
        if top_opportunities:
            st.markdown("""
            <div class="glass-card">
                <h4 style="color: #FFFFFF; margin: 0 0 1rem 0;">💎 Top Trading Opportunities</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for opportunity in top_opportunities[:3]:  # فقط ۳ تا اول
                signal_color = "text-success" if opportunity.get('signal') == "BUY" else "text-error"
                confidence = opportunity.get('confidence', 0) * 100
                
                st.markdown(f"""
                <div class="glass-card" style="margin: 0.5rem 0; padding: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div class="text-primary" style="font-weight: bold; font-size: 1.1rem;">
                                {opportunity.get('symbol', 'N/A')}
                            </div>
                            <div class="text-secondary" style="font-size: 0.9rem;">
                                Change: {opportunity.get('change', 0):+.2f}%
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div class="{signal_color}" style="font-weight: bold; font-size: 1.1rem;">
                                {opportunity.get('signal', 'HOLD')}
                            </div>
                            <div class="text-secondary" style="font-size: 0.9rem;">
                                Confidence: {confidence:.1f}%
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def render_additional_indicators(self, indicators):
        """نمایش اندیکاتورهای تکمیلی"""
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: #FFFFFF; margin: 0 0 1rem 0;">📈 Additional Indicators</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.render_metric_glass("Bollinger Upper", f"${indicators.get('bollinger_upper', 0):,.2f}")
        
        with col2:
            self.render_metric_glass("Bollinger Lower", f"${indicators.get('bollinger_lower', 0):,.2f}")
        
        with col3:
            self.render_metric_glass("MA (20)", f"${indicators.get('moving_avg_20', 0):,.2f}")
        
        with col4:
            self.render_metric_glass("MA (50)", f"${indicators.get('moving_avg_50', 0):,.2f}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.render_metric_glass("ATR", f"{indicators.get('atr', 0):.3f}")
        
        with col2:
            self.render_metric_glass("ADX", f"{indicators.get('adx', 0):.1f}")
        
        with col3:
            self.render_metric_glass("OBV", f"{indicators.get('obv', 0):,.0f}")
        
        with col4:
            self.render_metric_glass("CCI", f"{indicators.get('cci', 0):.1f}")
    
    def render_basic_technical(self, coin):
        """نمایش تحلیل تکنیکال پایه (fallback)"""
        vortex_data = coin.get('VortexAI_analysis', {})
        
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: #FFFFFF; margin: 0 0 1rem 0;">🧠 Basic VortexAI Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.render_metric_glass("Signal Strength", f"{vortex_data.get('signal_strength', 0):.1f}/10")
        
        with col2:
            trend = vortex_data.get('trend', 'neutral')
            trend_color = "text-success" if trend == "up" else "text-error" if trend == "down" else "text-primary"
            st.markdown(f"""
            <div class="glass-metric">
                <div class="text-secondary">Trend</div>
                <div class="{trend_color}" style="font-size: 1.2rem; font-weight: bold;">
                    {trend.upper()}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            self.render_metric_glass("Volatility", f"{vortex_data.get('volatility_score', 0):.3f}")
        
        with col4:
            anomaly = vortex_data.get('volume_anomaly', False)
            anomaly_color = "text-error" if anomaly else "text-success"
            anomaly_text = "DETECTED" if anomaly else "NORMAL"
            st.markdown(f"""
            <div class="glass-metric">
                <div class="text-secondary">Volume Anomaly</div>
                <div class="{anomaly_color}" style="font-size: 1.1rem; font-weight: bold;">
                    {anomaly_text}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_metric_glass(self, title, value):
        """نمایش متریک با طراحی شیشه‌ای"""
        st.markdown(f"""
        <div class="glass-metric">
            <div class="text-secondary" style="font-size: 0.8rem;">{title}</div>
            <div class="text-primary" style="font-size: 1.1rem; margin: 0.5rem 0; font-weight: bold;">{value}</div>
        </div>
        """, unsafe_allow_html=True)
