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

#سکشن 5
def scan_market(self, limit: int = 100) -> Optional[Dict]:
    try:
        url = f"https://server-test-ovta.onrender.com/api/scan/vortexai?limit={limit}"
        print(f"🔍 Calling: {url}")
        
        response = requests.get(url, timeout=30)
        print(f"📡 Status: {response.status_code}")
        print(f"📦 Headers: {response.headers}")
        
        # اگر وضعیت 200 نبود، خطا رو ببین
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"❌ Response text: {response.text}")
            return self._get_fallback_data()
        
        data = response.json()
        print(f"✅ Data keys: {data.keys()}")
        print(f"✅ Success: {data.get('success')}")
        print(f"✅ Coins count: {len(data.get('coins', []))}")
        
        coins = data.get('coins', [])
        
        if not coins:
            print("⚠️ No coins in response, using fallback")
            return self._get_fallback_data()
            
        self.db_manager.save_market_data(coins)
        
        return {
            'success': True,
            'coins': coins,
            'count': len(coins),
            'timestamp': datetime.now().isoformat()
        }
        
    except requests.exceptions.RequestException as e:
        print(f"🌐 Network Error: {e}")
        return self._get_fallback_data()
    except json.JSONDecodeError as e:
        print(f"📄 JSON Parse Error: {e}")
        print(f"📄 Response text: {response.text}")
        return self._get_fallback_data()
    except Exception as e:
        print(f"💥 Unexpected Error: {e}")
        return self._get_fallback_data()

def _get_fallback_data(self):
    """داده نمونه موقت"""
    sample_coins = [
        {
            'name': 'Bitcoin', 'symbol': 'BTC', 'price': 45000.50, 'priceChange24h': 2.34,
            'priceChange1h': 0.56, 'volume': 25467890000, 'marketCap': 882456123000
        },
        {
            'name': 'Ethereum', 'symbol': 'ETH', 'price': 2345.67, 'priceChange24h': 1.23,
            'priceChange1h': -0.34, 'volume': 14567890000, 'marketCap': 282456123000
        }
    ]
    return {
        'success': True,
        'coins': sample_coins,
        'count': len(sample_coins),
        'timestamp': datetime.now().isoformat()
    }

# --- SECTION 6: UI COMPONENTS ---

def display_market_results(results: Dict):
    """Display market scan results"""
    if not results or not results.get('success'):
        st.error(lang.t('error'))
        return
        
    coins_data = results.get('coins', [])
    st.header(lang.t('results_title'))
    
    # Create DataFrame for display
    df_data = []
    for coin in coins_data[:50]:  # Show top 50 coins
        df_data.append((
            coin.get('name', ''),
            coin.get('symbol', ''),
            f"${coin.get('price', 0):.2f}",
            f"{coin.get('priceChange24h', 0):.2f}%",
            f"{coin.get('priceChange1h', 0):.2f}%",
            f"{coin.get('volume', 0):.0f}",
            f"{coin.get('marketCap', 0):.0f}"
        ))
    
    if df_data:
        df = pd.DataFrame(df_data, columns=[
            lang.t('coin_name'),
            'Symbol',
            lang.t('price'),
            lang.t('change_24h'),
            lang.t('change_1h'),
            lang.t('volume'),
            lang.t('market_cap')
        ])
        st.dataframe(df, use_container_width=True, height=400)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("تعداد ارزها" if lang.current_lang == 'fa' else "Total Coins", len(coins_data))
    with col2:
        avg_change = np.mean([c.get('priceChange24h', 0) for c in coins_data])
        st.metric("میانگین تغییر" if lang.current_lang == 'fa' else "Average Change", f"{avg_change:.2f}%")
    with col3:
        total_volume = sum(c.get('volume', 0) for c in coins_data)
        st.metric("حجم کل" if lang.current_lang == 'fa' else "Total Volume", f"{total_volume:.0f}")
    with col4:
        st.metric("وضعیت" if lang.current_lang == 'fa' else "Status", lang.t('completed'))

def display_ai_analysis(ai_analysis: Dict):
    """Display AI analysis results"""
    if not ai_analysis:
        return
        
    st.markdown("---")
    st.header(lang.t('ai_analysis'))
    
    # AI Confidence
    ai_confidence = ai_analysis.get('ai_confidence', 0)
    st.metric(lang.t('ai_confidence'), f'{ai_confidence:.1f}%')
    
    # Strong Signals
    strong_signals = ai_analysis.get('strong_signals', [])
    if strong_signals:
        st.subheader(lang.t('strong_signals'))
        for signal in strong_signals[:5]:
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(f"**{signal['coin']}** ({signal['symbol']})")
            with col2:
                st.write(f"قدرت سیگنال: {signal['signal_strength']}%" if lang.current_lang == 'fa' else f"Signal: {signal['signal_strength']}%")
            with col3:
                st.write(signal['recommendation'])
    
    # Risk Warnings
    risk_warnings = ai_analysis.get('risk_warnings', [])
    if risk_warnings:
        st.subheader(lang.t('risk_warnings'))
        for warning in risk_warnings[:3]:
            st.error(f"**{warning['coin']}**: سطح ریسک {warning['risk_level']}%" if lang.current_lang == 'fa' else f"**{warning['coin']}**: Risk level {warning['risk_level']}%")
    
    # Market Insights
    market_insights = ai_analysis.get('market_insights', [])
    if market_insights:
        st.subheader(lang.t('market_insights'))
        for insight in market_insights:
            st.info(insight)

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
