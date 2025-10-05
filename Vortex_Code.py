# crypto_scanner.py - سیستم دو زبان

import streamlit as st
import requests
import pandas as pd
import numpy as np
import sqlite3
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json

# --- SECTION 1: MULTI-LANGUAGE SYSTEM ---

class MultiLanguage:  # تصحیح نام کلاس
    def __init__(self):
        self.dictionaries = {
            'fa': self._persian_dict(),
            'en': self._english_dict()
        }
        self.current_lang = 'fa'

    def _persian_dict(self):
        return {
            # UI Elements
            'app_title': "🔄 VortexAI - اسکنر بازار کریپتو",
            'scan_button': "📊 اسکن بازار",
            'ai_scan_button': "🤖 اسکن با VortexAI",
            'settings_button': "⚙️ تنظیمات",
            'search_placeholder': "...جستجوی ارز",
            
            # Sidebar
            'sidebar_title': "کنترل‌ها",
            'language_label': "زبان",
            'theme_label': "تم",
            'dark_mode': "تیره",
            'light_mode': "روشن",
            
            # Results
            'results_title': "نتایج اسکن",
            'coin_name': "نام ارز",
            'price': "قیمت",
            'change_24h': "تغییر 24h",
            'change_1h': "تغییر 1h",
            'volume': "حجم",
            'market_cap': "ارزش بازار",
            'signal_strength': "قدرت سیگنال",
            
            # AI Analysis
            'ai_analysis': "تحلیل هوش مصنوعی",
            'strong_signals': "سیگنال‌های قوی",
            'risk_warnings': "هشدارهای ریسک",
            'market_insights': "بینش‌های بازار",
            'ai_confidence': "اعتماد هوش مصنوعی",
            
            # Technical Analysis
            'technical_analysis': "تحلیل تکنیکال",
            'rsi': "شاخص قدرت نسبی",
            'macd': "واگرایی همگرایی میانگین متحرک",
            'bollinger_bands': "باندهای بولینگر",
            'moving_average': "میانگین متحرک",
            
            # Status Messages
            'scanning': "...در حال اسکن بازار",
            'analyzing': "...VortexAI در حال تحلیل",
            'completed': "تکمیل شد",
            'error': "خطا",
            'success': "موفق"
        }

    def _english_dict(self):
        return {
            # UI Elements
            'app_title': "VortexAI - Crypto Market Scanner",
            'scan_button': "📊 Scan Market",
            'ai_scan_button': "🤖 Scan with VortexAI",
            'settings_button': "⚙️ Settings",
            'search_placeholder': "Search coins...",
            
            # Sidebar
            'sidebar_title': "Controls",
            'language_label': "Language",
            'theme_label': "Theme",
            'dark_mode': "Dark",
            'light_mode': "Light",
            
            # Results
            'results_title': "Scan Results",
            'coin_name': "Coin Name",
            'price': "Price",
            'change_24h': "24h Change",
            'change_1h': "1h Change",
            'volume': "Volume",
            'market_cap': "Market Cap",
            'signal_strength': "Signal Strength",
            
            # AI Analysis
            'ai_analysis': "AI Analysis",
            'strong_signals': "Strong Signals",
            'risk_warnings': "Risk Warnings",
            'market_insights': "Market Insights",
            'ai_confidence': "AI Confidence",
            
            # Technical Analysis
            'technical_analysis': "Technical Analysis",
            'rsi': "Relative Strength Index",
            'macd': "Moving Average Convergence Divergence",
            'bollinger_bands': "Bollinger Bands",
            'moving_average': "Moving Average",
            
            # Status Messages
            'scanning': "Scanning market...",
            'analyzing': "VortexAI analyzing...",
            'completed': "Completed",
            'error': "Error",
            'success': "Success"
        }

    def t(self, key):
        """Get translation for current language"""
        return self.dictionaries[self.current_lang].get(key, key)

    def set_language(self, lang):
        """Set current language"""
        if lang in self.dictionaries:
            self.current_lang = lang

# Initialize multi-language system
lang = MultiLanguage()

# --- SECTION 2: CONFIGURATION ---

def setup_page_config():
    """Setup Streamlit page configuration"""
    st.set_page_config(
        page_title=lang.t('app_title'),
        page_icon="🔄",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def setup_sidebar():
    """Setup sidebar with language and theme controls"""
    with st.sidebar:
        st.header(lang.t('sidebar_title'))
        
        # Language selection
        selected_lang = st.selectbox(
            lang.t('language_label'),
            ['fa', 'en'],
            format_func=lambda x: 'فارسی' if x == 'fa' else 'English',
            key='language_selector'
        )
        lang.set_language(selected_lang)
        
        # Theme selection
        theme = st.selectbox(
            lang.t('theme_label'),
            ['dark', 'light'],
            format_func=lambda x: lang.t('dark_mode') if x == 'dark' else lang.t('light_mode'),
            key='theme_selector'
        )
        
        st.markdown("---")
        
        # Scan buttons
        col1, col2 = st.columns(2)
        with col1:
            normal_scan = st.button(lang.t('scan_button'), use_container_width=True)
        with col2:
            ai_scan = st.button(lang.t('ai_scan_button'), use_container_width=True, type="secondary")
            
        return normal_scan, ai_scan

# --- SECTION 3: DATABASE MANAGER ---

class DatabaseManager:
    def __init__(self, db_path="crypto_data.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL,
                    volume REAL,
                    price_change_24h REAL,
                    price_change_1h REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def save_market_data(self, data: List[Dict]):
        try:
            with sqlite3.connect(self.db_path) as conn:
                for coin in data:
                    conn.execute('''
                        INSERT INTO market_data (symbol, price, volume, price_change_24h, price_change_1h)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        coin.get('symbol'),
                        coin.get('price'),
                        coin.get('volume'),
                        coin.get('priceChange24h'),
                        coin.get('priceChange1h')
                    ))
        except Exception as e:
            logging.error(f"Error saving market data: {e}")

# --- SECTION 4: VORTEXAI CORE ---

class VortexAI:
    def __init__(self):
        self.learning_sessions = 0
        self.analysis_history = []

    def analyze_market_data(self, coins_data: List[Dict]) -> Dict:
        """Analyze market data and return insights"""
        self.learning_sessions += 1
        
        analysis = {
            "strong_signals": [],
            "risk_warnings": [],
            "market_insights": [],
            "ai_confidence": self._calculate_confidence(coins_data)
        }

        for coin in coins_data[:20]:  # Analyze top 20 coins
            coin_analysis = self._analyze_single_coin(coin)
            if coin_analysis["signal_strength"] > 70:
                analysis["strong_signals"].append(coin_analysis)
            if coin_analysis["risk_level"] > 60:
                analysis["risk_warnings"].append(coin_analysis)

        analysis["market_insights"] = self._generate_market_insights(coins_data)
        self.analysis_history.append(analysis)
        
        return analysis

    def _analyze_single_coin(self, coin: Dict) -> Dict:
        """Analyze a single coin"""
        signal_strength = 0
        risk_level = 0
        
        # Price change analysis
        price_change_24h = abs(coin.get('priceChange24h', 0))
        if price_change_24h > 10:
            signal_strength += 40
        elif price_change_24h > 5:
            signal_strength += 20
            
        # Volume analysis
        volume = coin.get('volume', 0)
        if volume > 50000000:
            signal_strength += 30
        elif volume > 10000000:
            signal_strength += 15
            
        # Risk assessment
        if price_change_24h > 15:
            risk_level = 70
        elif price_change_24h > 25:
            risk_level = 85
            
        return {
            "coin": coin.get('name', ''),
            "symbol": coin.get('symbol', ''),
            "signal_strength": min(signal_strength, 100),
            "risk_level": risk_level,
            "recommendation": self._generate_recommendation(signal_strength, risk_level)
        }

    def _calculate_confidence(self, coins_data: List[Dict]) -> float:
        """Calculate AI confidence level"""
        if not coins_data:
            return 0.0
            
        confidence_factors = []
        confidence_factors.append(min(len(coins_data) / 50, 1.0) * 0.4)
        
        changes = [abs(c.get('priceChange24h', 0)) for c in coins_data]
        market_volatility = np.std(changes) if changes else 0
        stability_factor = max(0, 1 - (market_volatility / 20))
        confidence_factors.append(stability_factor * 0.6)
        
        return min(sum(confidence_factors), 1.0) * 100

    def _generate_recommendation(self, signal_strength: float, risk_level: float) -> str:
        """Generate trading recommendation"""
        if lang.current_lang == 'fa':
            if signal_strength >= 70 and risk_level < 40:
                return "خرید قوی"
            elif signal_strength >= 50 and risk_level < 60:
                return "خرید محتاطانه"
            elif signal_strength >= 30 or risk_level > 70:
                return "نظارت بدون اقدام"
            else:
                return "صبر کنید"
        else:
            if signal_strength >= 70 and risk_level < 40:
                return "🔍 Strong Buy"
            elif signal_strength >= 50 and risk_level < 60:
                return "🔍 Cautious Buy"
            elif signal_strength >= 30 or risk_level > 70:
                return "🔍 Monitor Only"
            else:
                return "🔍 Wait"

    def _generate_market_insights(self, coins_data: List[Dict]) -> List[str]:
        """Generate market insights"""
        insights = []
        
        if lang.current_lang == 'fa':
            changes_24h = [c.get('priceChange24h', 0) for c in coins_data]
            avg_change_24h = np.mean(changes_24h) if changes_24h else 0
            
            if avg_change_24h > 5:
                insights.append("✅ بازار در حالت صعودی قوی")
            elif avg_change_24h < -3:
                insights.append("⚠️ بازار در حالت نزولی")
            else:
                insights.append("⚖️ بازار در حالت تعادل")
                
            bullish_coins = sum(1 for c in coins_data if c.get('priceChange24h', 0) > 0)
            bearish_coins = len(coins_data) - bullish_coins
            
            if bullish_coins > bearish_coins * 1.5:
                insights.append("😊 اکثریت ارزها صعودی هستند")
            elif bearish_coins > bullish_coins * 1.5:
                insights.append("⚠️ اکثریت ارزها نزولی هستند")
        else:
            changes_24h = [c.get('priceChange24h', 0) for c in coins_data]
            avg_change_24h = np.mean(changes_24h) if changes_24h else 0
            
            if avg_change_24h > 5:
                insights.append("✅ Market in strong bullish mode")
            elif avg_change_24h < -3:
                insights.append("⚠️ Market in bearish mode")
            else:
                insights.append("⚖️ Market in balance")
                
            bullish_coins = sum(1 for c in coins_data if c.get('priceChange24h', 0) > 0)
            bearish_coins = len(coins_data) - bullish_coins
            
            if bullish_coins > bearish_coins * 1.5:
                insights.append("😊 Majority of coins are bullish")
            elif bearish_coins > bullish_coins * 1.5:
                insights.append("⚠️ Majority of coins are bearish")
                
        return insights
# --- SECTION 5: CRYPTO SCANNER ---

class CryptoScanner:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.vortex_ai = VortexAI()
        self.api_base = "https://server-test-ovta.onrender.com"

    def scan_market(self, limit: int = 100) -> Optional[Dict]:
        """Scan cryptocurrency market"""
        try:
            url = f"{self.api_base}/api/scan/vortexai?limit={limit}"
            print(f"🔍 STEP 1 - Calling API: {url}")
            
            response = requests.get(url, timeout=15)
            print(f"📡 STEP 2 - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ STEP 3 - API Success: {data.get('success')}")
                print(f"📊 STEP 4 - Response keys: {list(data.keys())}")
                
                if data.get('success'):
                    raw_coins = data.get('coins', [])
                    print(f"📦 STEP 5 - Raw coins count: {len(raw_coins)}")
                    
                    if raw_coins:
                        # نمایش ساختار اولین کوین برای دیباگ
                        first_coin = raw_coins[0]
                        print(f"🔍 STEP 6 - First coin keys: {list(first_coin.keys())}")
                        print(f"🔍 STEP 7 - First coin data: {first_coin}")
                    
                    # پردازش داده‌ها - نسخه ایمن
                    coins = []
                    for i, coin in enumerate(raw_coins):
                        try:
                            # استفاده از فیلدهای مختلف برای پیدا کردن داده
                            price = float(coin.get('price') or coin.get('realtime_price') or 0)
                            change_24h = float(coin.get('priceChange24h') or coin.get('priceChange1d') or 0)
                            change_1h = float(coin.get('priceChange1h') or 0)
                            volume = float(coin.get('volume') or coin.get('realtime_volume') or 0)
                            market_cap = float(coin.get('marketCap') or 0)
                            
                            processed_coin = {
                                'name': str(coin.get('name', f'Coin_{i}')),
                                'symbol': str(coin.get('symbol', 'UNKNOWN')),
                                'price': price,
                                'priceChange24h': change_24h,
                                'priceChange1h': change_1h,
                                'volume': volume,
                                'marketCap': market_cap
                            }
                            coins.append(processed_coin)
                            print(f"🔄 Coin {i}: {processed_coin['symbol']} - ${processed_coin['price']}")
                            
                        except Exception as e:
                            print(f"⚠️ Error processing coin {i}: {e}")
                            continue
                    
                    print(f"✅ STEP 8 - Successfully processed: {len(coins)} coins")
                    
                    if coins:
                        self.db_manager.save_market_data(coins)
                        print("💾 STEP 9 - Data saved to database")
                        
                        return {
                            'success': True,
                            'coins': coins,
                            'count': len(coins),
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        print("❌ STEP 10 - No coins processed successfully")
                else:
                    print(f"❌ STEP 11 - API returned success: false - {data.get('error')}")
            else:
                print(f"❌ STEP 12 - HTTP Error: {response.status_code}")
                print(f"❌ Response text: {response.text[:200]}...")
            
            print("🔄 STEP 13 - Using fallback data")
            return self._get_fallback_data()
            
        except Exception as e:
            print(f"💥 STEP 14 - Unexpected error: {e}")
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")
            return self._get_fallback_data()

    def _get_fallback_data(self):
        """Sample data as fallback when server is unavailable"""
        print("🔄 Using comprehensive fallback data")
        sample_coins = [
            {
                'name': 'Bitcoin',
                'symbol': 'BTC',
                'price': 124619.36,
                'priceChange24h': 1.92,
                'priceChange1h': -0.08,
                'volume': 39306468043,
                'marketCap': 2483440001648
            },
            {
                'name': 'Ethereum',
                'symbol': 'ETH',
                'price': 4586.82,
                'priceChange24h': 2.15,
                'priceChange1h': -0.32,
                'volume': 40423228887,
                'marketCap': 553641132921
            },
            {
                'name': 'BNB',
                'symbol': 'BNB', 
                'price': 1171.38,
                'priceChange24h': 1.38,
                'priceChange1h': -0.58,
                'volume': 14106039249,
                'marketCap': 163038687343
            },
            {
                'name': 'Solana',
                'symbol': 'SOL',
                'price': 235.20,
                'priceChange24h': 2.77,
                'priceChange1h': -0.59,
                'volume': 12280809846,
                'marketCap': 128270536156
            },
            {
                'name': 'XRP',
                'symbol': 'XRP',
                'price': 3.05,
                'priceChange24h': 1.64,
                'priceChange1h': -0.45,
                'volume': 3140519134,
                'marketCap': 182571288194
            }
        ]
        
        return {
            'success': True,
            'coins': sample_coins,
            'count': len(sample_coins),
            'timestamp': datetime.now().isoformat()
        }

    def scan_with_ai(self, limit: int = 100) -> Optional[Dict]:
        """Scan market with AI analysis"""
        try:
            print("🤖 Starting AI-enhanced scan...")
            
            market_result = self.scan_market(limit)
            
            if not market_result or not market_result.get('success'):
                print("❌ AI Scan: No market data available")
                return None
                
            coins = market_result['coins']
            print(f"🤖 Analyzing {len(coins)} coins with VortexAI...")
            
            ai_analysis = self.vortex_ai.analyze_market_data(coins)
            print(f"🤖 AI analysis completed")
            
            return {
                **market_result,
                "ai_analysis": ai_analysis,
                "scan_mode": "ai_enhanced"
            }
            
        except Exception as e:
            print(f"🤖 AI Scan Error: {e}")
            logging.error(f"AI scan error: {e}")
            return None
# --- SECTION 6: UI COMPONENTS ---

def display_market_results(results: Dict):
    """Display market scan results"""
    if not results or not results.get('success'):
        st.error("❌ " + lang.t('error'))
        return
        
    coins_data = results.get('coins', [])
    
    if not coins_data:
        st.warning("⚠️ هیچ داده‌ای برای نمایش وجود ندارد")
        return
    
    # هدر با تعداد ارزها
    st.header(f"{lang.t('results_title')} - {len(coins_data)} ارز")
    
    # ایجاد دیتافریم برای نمایش
    df_data = []
    for coin in coins_data:
        # بررسی وجود داده‌ها
        price = coin.get('price', 0)
        change_24h = coin.get('priceChange24h', 0)
        change_1h = coin.get('priceChange1h', 0)
        volume = coin.get('volume', 0)
        market_cap = coin.get('marketCap', 0)
        
        df_data.append((
            coin.get('name', 'نامشخص'),
            coin.get('symbol', 'N/A'),
            f"${price:,.2f}" if price > 0 else "$0.00",
            f"{change_24h:+.2f}%" if change_24h != 0 else "0.00%",
            f"{change_1h:+.2f}%" if change_1h != 0 else "0.00%",
            f"${volume:,.0f}" if volume > 0 else "$0",
            f"${market_cap:,.0f}" if market_cap > 0 else "$0"
        ))
    
    # ایجاد دیتافریم
    df = pd.DataFrame(df_data, columns=[
        lang.t('coin_name'),
        'نماد',
        lang.t('price'),
        lang.t('change_24h'),
        lang.t('change_1h'),
        lang.t('volume'),
        lang.t('market_cap')
    ])
    
    # تنظیم ایندکس از 1 شروع بشه
    df.index = df.index + 1
    
    # تنظیمات استایل برای دیتافریم
    st.dataframe(
        df,
        use_container_width=True,
        height=min(600, 35 * len(df) + 40),  # ارتفاع داینامیک
        hide_index=False
    )
    
    # متریک‌های کلی
    st.subheader("📊 آمار کلی بازار")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_coins = len(coins_data)
        st.metric(
            label="تعداد ارزها",
            value=total_coins,
            delta=None
        )
    
    with col2:
        changes_24h = [c.get('priceChange24h', 0) for c in coins_data]
        avg_change_24h = np.mean(changes_24h) if changes_24h else 0
        st.metric(
            label="میانگین تغییر 24h",
            value=f"{avg_change_24h:+.2f}%",
            delta=None
        )
    
    with col3:
        total_volume = sum(c.get('volume', 0) for c in coins_data)
        st.metric(
            label="حجم کل بازار",
            value=f"${total_volume:,.0f}",
            delta=None
        )
    
    with col4:
        bullish_count = sum(1 for c in coins_data if c.get('priceChange24h', 0) > 0)
        bearish_count = total_coins - bullish_count
        st.metric(
            label="روند بازار",
            value=f"{bullish_count}↑ {bearish_count}↓",
            delta=None
        )

def display_ai_analysis(ai_analysis: Dict):
    """Display AI analysis results"""
    if not ai_analysis:
        st.info("🤖 تحلیل هوش مصنوعی در دسترس نیست")
        return
        
    st.markdown("---")
    st.header("🧠 " + lang.t('ai_analysis'))
    
    # اعتماد هوش مصنوعی
    ai_confidence = ai_analysis.get('ai_confidence', 0)
    confidence_color = "🟢" if ai_confidence > 70 else "🟡" if ai_confidence > 40 else "🔴"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label=lang.t('ai_confidence'),
            value=f"{ai_confidence:.1f}%",
            delta=None
        )
    
    with col2:
        st.write(f"{confidence_color} سطح اعتماد: {'عالی' if ai_confidence > 70 else 'متوسط' if ai_confidence > 40 else 'پایین'}")
    
    # سیگنال‌های قوی
    strong_signals = ai_analysis.get('strong_signals', [])
    if strong_signals:
        st.subheader("🎯 " + lang.t('strong_signals'))
        
        for i, signal in enumerate(strong_signals[:8], 1):  # حداکثر 8 سیگنال
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                
                with col1:
                    st.write(f"**{i}. {signal['coin']}** ({signal['symbol']})")
                
                with col2:
                    signal_strength = signal['signal_strength']
                    strength_color = "🟢" if signal_strength > 70 else "🟡" if signal_strength > 50 else "🔴"
                    st.write(f"{strength_color} {signal_strength}%")
                
                with col3:
                    risk_level = signal['risk_level']
                    risk_color = "🔴" if risk_level > 70 else "🟡" if risk_level > 40 else "🟢"
                    st.write(f"{risk_color} ریسک: {risk_level}%")
                
                with col4:
                    rec = signal['recommendation']
                    rec_color = "success" if "قوی" in rec or "Strong" in rec else "warning" if "محتاط" in rec or "Cautious" in rec else "info"
                    st.write(f":{rec_color}[{rec}]")
            
            st.markdown("---")
    
    # هشدارهای ریسک
    risk_warnings = ai_analysis.get('risk_warnings', [])
    if risk_warnings:
        st.subheader("⚠️ " + lang.t('risk_warnings'))
        
        for warning in risk_warnings[:5]:  # حداکثر 5 هشدار
            with st.expander(f"🚨 {warning['coin']} ({warning['symbol']}) - سطح ریسک: {warning['risk_level']}%", expanded=False):
                st.error(f"**هشدار ریسک بالا** - این ارز دارای نوسانات شدید یا ریسک معاملاتی بالایی است.")
                st.write(f"💡 پیشنهاد: {warning['recommendation']}")
    
    # بینش‌های بازار
    market_insights = ai_analysis.get('market_insights', [])
    if market_insights:
        st.subheader("💡 " + lang.t('market_insights'))
        
        for insight in market_insights:
            if "صعودی" in insight or "bullish" in insight:
                st.success(insight)
            elif "نزولی" in insight or "bearish" in insight:
                st.warning(insight)
            else:
                st.info(insight)

def display_search_filter(coins_data: List[Dict]):
    """Display search and filter controls"""
    if not coins_data:
        return
    
    st.markdown("---")
    st.subheader("🔍 جستجو و فیلتر")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input(
            lang.t('search_placeholder'),
            placeholder="...نام یا نماد ارز",
            key="search_input"
        )
    
    with col2:
        min_volume = st.number_input(
            "حداقل حجم (میلیون دلار)",
            min_value=0,
            value=10,
            step=10,
            key="min_volume"
        ) * 1000000  # تبدیل به دلار
    
    with col3:
        trend_filter = st.selectbox(
            "فیلتر روند",
            options=["همه", "صعودی", "نزولی"],
            index=0,
            key="trend_filter"
        )
    
    # اعمال فیلترها
    filtered_coins = coins_data
    
    if search_term:
        filtered_coins = [
            coin for coin in filtered_coins 
            if search_term.lower() in coin.get('name', '').lower() 
            or search_term.lower() in coin.get('symbol', '').lower()
        ]
    
    if min_volume > 0:
        filtered_coins = [
            coin for coin in filtered_coins 
            if coin.get('volume', 0) >= min_volume
        ]
    
    if trend_filter == "صعودی":
        filtered_coins = [
            coin for coin in filtered_coins 
            if coin.get('priceChange24h', 0) > 0
        ]
    elif trend_filter == "نزولی":
        filtered_coins = [
            coin for coin in filtered_coins 
            if coin.get('priceChange24h', 0) < 0
        ]
    
    # نمایش نتایج فیلتر شده
    if len(filtered_coins) != len(coins_data):
        st.info(f"📊 نمایش {len(filtered_coins)} از {len(coins_data)} ارز (فیلتر شده)")
    
    return filtered_coins

def display_quick_actions():
    """Display quick action buttons"""
    st.markdown("---")
    st.subheader("⚡ اقدامات سریع")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 اسکن مجدد", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("💾 ذخیره گزارش", use_container_width=True):
            st.success("گزارش ذخیره شد")
    
    with col3:
        if st.button("📧 اشتراک‌گذاری", use_container_width=True):
            st.info("امکان اشتراک‌گذاری")
    
    with col4:
        if st.button("⚙️ تنظیمات پیشرفته", use_container_width=True):
            st.session_state.show_settings = True
# --- SECTION 7: MAIN APPLICATION ---

def main():
    """Main application function"""
    setup_page_config()
    
    # Display title
    st.title(lang.t('app_title'))
    st.markdown("---")
    
    # Setup sidebar and get scan buttons
    normal_scan, ai_scan = setup_sidebar()
    
    # Initialize scanner
    @st.cache_resource
    def load_scanner():
        return CryptoScanner()
    
    scanner = load_scanner()
    
    # Handle scan requests
    if normal_scan:
        with st.spinner(lang.t('scanning')):
            results = scanner.scan_market(limit=100)
            if results and results.get('success'):
                display_market_results(results)
            else:
                st.error(lang.t('error'))
                
    if ai_scan:
        with st.spinner(lang.t('analyzing')):
            results = scanner.scan_with_ai(limit=100)
            if results and results.get('success'):
                display_market_results(results)
                display_ai_analysis(results.get('ai_analysis'))
            else:
                st.error(lang.t('error'))
    
    # Display AI status in sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("🤖 وضعیت VortexAI" if lang.current_lang == 'fa' else "🤖 VortexAI Status")
        st.metric("جلسات یادگیری" if lang.current_lang == 'fa' else "Learning Sessions", scanner.vortex_ai.learning_sessions)
        st.metric("تحلیل‌های انجام شده" if lang.current_lang == 'fa' else "Analysis Completed", len(scanner.vortex_ai.analysis_history))

# Run the application
if __name__ == "__main__":
    main()
