import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests 
import numpy as np
from datetime import datetime, timedelta
import json
import time
import logging
import sqlite3
from typing import Dict, List, Optional, Tuple

# ==================== SECTION 1: CONFIGURATION & SETUP ====================
st.set_page_config(
    page_title="CoinState Market Scanner Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('market_scanner.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Config:
    """Configuration class for all constants"""
    MIDDLEWARE_BASE_URL = "https://crypto-scanner-backend.onrender.com"
    
    SYMBOLS = [
        "bitcoin", "ethereum", "binancecoin", "cardano", "ripple", "solana",
        "polkadot", "dogecoin", "avalanche", "matic-network", "litecoin", "cosmos"
    ]
    
    PERIODS = {
        "24h": "24 ساعت", "1w": "1 هفته", "1m": "1 ماه", "3m": "3 ماه",
        "6m": "6 ماه", "1y": "1 سال", "all": "همه زمان"
    }

# ==================== SECTION 2: MULTILINGUAL SUPPORT ====================
class TranslationManager:
    """Manager for multilingual text support"""
    
    TEXTS = {
        "فارسی": {
            "title": "📊 اسکنر بازار CoinState Pro",
            "select_symbol": "انتخاب نماد:",
            "select_interval": "انتخاب تایم‌فریم:",
            "loading": "در حال دریافت داده‌ها...",
            "price_chart": "نمودار قیمت",
            "indicators": "اندیکاتورها",
            "price": "قیمت",
            "high": "بالاترین",
            "low": "پایین‌ترین",
            "change": "تغییرات",
            "volume": "حجم معاملات",
            "rsi": "RSI",
            "macd": "MACD",
            "sma": "میانگین متحرک",
            "no_data": "داده‌ای دریافت نشد",
            "technical_analysis": "تحلیل تکنیکال",
            "market_data": "داده‌های بازار",
            "settings": "تنظیمات",
            "language": "🌐 زبان",
            "retry": "تلاش مجدد",
            "connection_error": "خطا در اتصال به سرور",
            "last_update": "آخرین بروزرسانی",
            "symbol_info": "اطلاعات نماد",
            "api_health": "بررسی سلامت API",
            "global_market": "داده‌های جهانی بازار",
            "portfolio_tracker": "ردیابی پرتفوی",
            "alerts": "هشدارها",
            "scan_all": "اسکن تمام بازار"
        },
        "English": {
            "title": "📊 CoinState Market Scanner Pro",
            "select_symbol": "Select symbol:",
            "select_interval": "Select interval:",
            "loading": "Loading data...",
            "price_chart": "Price Chart",
            "indicators": "Indicators",
            "price": "Price",
            "high": "High",
            "low": "Low",
            "change": "Change",
            "volume": "Volume",
            "rsi": "RSI",
            "macd": "MACD",
            "sma": "Moving Average",
            "no_data": "No data received",
            "technical_analysis": "Technical Analysis",
            "market_data": "Market Data",
            "settings": "Settings",
            "language": "🌐 Language",
            "retry": "Retry",
            "connection_error": "Connection error",
            "last_update": "Last update",
            "symbol_info": "Symbol Info",
            "api_health": "Check API Health",
            "global_market": "Global Market Data",
            "portfolio_tracker": "Portfolio Tracker",
            "alerts": "Price Alerts",
            "scan_all": "Scan All Market"
        }
    }
    
    @staticmethod
    def get_text(language: str) -> Dict:
        return TranslationManager.TEXTS.get(language, TranslationManager.TEXTS["English"])

# ===================== SECTION 3: MIDDLESERVER CLIENT ===============================
class MiddlewareAPIClient:
    """API Client ساده‌شده برای ارتباط با سرور میانی شما"""
    
    def init(self, base_url: str):
        self.base_url = base_url
        self.session = self._create_session()
        self.is_healthy = False
        self.last_error = None
        self.last_check = None
        self._check_health()  # بررسی سلامت سرور میانی هنگام راه‌اندازی
    
    def _create_session(self) -> requests.Session:
        """Create session with retry strategy"""
        session = requests.Session()
        retry_strategy = requests.packages.urllib3.util.Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session
    
    def _check_health(self):
        """بررسی سلامت سرور میانی"""
        try:
            # تست endpoint سلامت سرور میانی
            health_url = f"{self.base_url}/health"
            response = self.session.get(health_url, timeout=10)
            
            if response.status_code == 200:
                self.is_healthy = True
                self.last_error = None
                self.last_check = datetime.now()
                logger.info("✅ سرور میانی سالم است")
            else:
                self.is_healthy = False
                self.last_error = f"سرور میانی خطا داد: کد {response.status_code}"
                logger.error(f"❌ خطای سرور میانی: {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.is_healthy = False
            self.last_error = "اتصال به سرور میانی timeout شد"
            logger.error("❌ timeout اتصال به سرور میانی")
        except requests.exceptions.ConnectionError:
            self.is_healthy = False
            self.last_error = "خطای اتصال به سرور میانی"
            logger.error("❌ خطای اتصال به سرور میانی")
        except Exception as e:
            self.is_healthy = False
            self.last_error = f"خطای ناشناخته: {str(e)}"
            logger.error(f"❌ خطای ناشناخته در بررسی سلامت: {str(e)}")
    
    def get_all_coins(self, limit: int = 100) -> Optional[Dict]:
        """دریافت تمام ارزها از سرور میانی"""
        try:
            url = f"{self.base_url}/coins"
            params = {"limit": limit} if limit else {}
            
            logger.info(f"🌐 دریافت داده از سرور میانی: {url}")
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ داده دریافت شد: {len(data.get('coins', []))} ارز")
                return data
            else:
                logger.error(f"❌ خطای سرور میانی: کد {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ خطا در دریافت داده از سرور میانی: {str(e)}")
            return None
    
    def get_coin_data(self, coin_id: str) -> Optional[Dict]:
        """دریافت داده‌های یک ارز خاص"""
        try:
            # اول تمام ارزها را بگیریم
            all_data = self.get_all_coins()
            if not all_data:
                return None
            
            # پیدا کردن ارز مورد نظر
            coins = all_data.get('coins', [])
            
            # جستجو با انواع نام‌های ممکن
            coin_id_lower = coin_id.lower()
            for coin in coins:
                # بررسی با id، name، symbol
                if (coin.get('id', '').lower() == coin_id_lower or 
                    coin.get('name', '').lower() == coin_id_lower or
                    coin.get('symbol', '').lower() == coin_id_lower):

                    logger.info(f"✅ ارز {coin_id} پیدا شد")
                    return coin
            
            logger.warning(f"⚠️ ارز {coin_id} پیدا نشد")
            return None
            
        except Exception as e:
            logger.error(f"❌ خطا در یافتن ارز {coin_id}: {str(e)}")
            return None
    
    def get_realtime_data(self, coin_id: str) -> Optional[Dict]:
        """متد سازگار با کد موجود - دریافت داده real-time"""
        return self.get_coin_data(coin_id)
    
    def get_historical_data(self, coin_id: str, period: str) -> Optional[pd.DataFrame]:
        """دریافت داده‌های تاریخی - فعلاً از نمونه داده استفاده می‌کنیم"""
        logger.info(f"📊 استفاده از داده‌های نمونه برای {coin_id} - دوره {period}")
        return self._generate_sample_data(period)
    
    def _generate_sample_data(self, period: str) -> pd.DataFrame:
        """ایجاد داده‌های نمونه واقع‌گرایانه"""
        try:
            period_points = {
                "24h": 24, "1w": 42, "1m": 30, "3m": 90,
                "6m": 180, "1y": 365, "all": 100
            }
            
            count = period_points.get(period, 100)
            base_price = 45000  # قیمت پایه بیت‌کوین
            
            # ایجاد timeline بر اساس دوره
            if period == "24h":
                times = [datetime.now() - timedelta(hours=i) for i in range(count)][::-1]
            else:
                times = [datetime.now() - timedelta(days=i) for i in range(count)][::-1]
            
            data = []
            current_price = base_price
            
            for i, time_point in enumerate(times):
                # تغییرات قیمت واقع‌گرایانه
                volatility = 0.02  # 2% نوسان
                if period in ["1y", "all"]:
                    volatility = 0.04  # نوسان بیشتر برای دوره‌های طولانی
                
                change = current_price * volatility * np.random.randn()
                current_price = max(current_price + change, base_price * 0.3)  # حداقل 30% قیمت پایه
                
                # ایجاد داده OHLC واقع‌گرایانه
                open_price = current_price * (1 + np.random.uniform(-0.005, 0.005))
                high_price = max(open_price, current_price) * (1 + np.random.uniform(0, 0.015))
                low_price = min(open_price, current_price) * (1 - np.random.uniform(0, 0.015))
                close_price = current_price
                
                data.append({
                    'time': time_point,
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': np.random.uniform(1000000, 50000000)  # حجم معاملات واقع‌گرایانه
                })
            
            df = pd.DataFrame(data)
            logger.info(f"✅ داده‌های نمونه برای دوره {period} ایجاد شد: {len(df)} نقطه داده")
            return df
            
        except Exception as e:
            logger.error(f"❌ خطا در ایجاد داده‌های نمونه: {str(e)}")
            # بازگشت داده‌های ساده در صورت خطا
            return pd.DataFrame({
                'time': [datetime.now()],
                'open': [50000], 'high': [51000], 'low': [49000], 
                'close': [50500], 'volume': [1000000]
            })
    
    def scan_multiple_coins(self, coin_ids: List[str]) -> Dict[str, Optional[Dict]]:
        """اسکن چندین ارز به صورت بهینه"""
        results = {}
        
        try:
            # دریافت تمام داده‌ها در یک درخواست
            all_data = self.get_all_coins(limit=100)
            if not all_data:
                return {coin_id: None for coin_id in coin_ids}
            
            coins_map = {}
            for coin in all_data.get('coins', []):
                # ایجاد map برای جستجوی سریع

                id_key = coin.get('id', '').lower()
                name_key = coin.get('name', '').lower()
                symbol_key = coin.get('symbol', '').lower()
                
                coins_map[id_key] = coin
                coins_map[name_key] = coin
                coins_map[symbol_key] = coin
            
            # جستجوی هر ارز
            for coin_id in coin_ids:
                coin_id_lower = coin_id.lower()
                results[coin_id] = coins_map.get(coin_id_lower)
            
            logger.info(f"✅ اسکن {len(coin_ids)} ارز تکمیل شد")
            return results
            
        except Exception as e:
            logger.error(f"❌ خطا در اسکن چندین ارز: {str(e)}")
            return {coin_id: None for coin_id in coin_ids}
# ==================== SECTION 4: DATA MANAGER & CACHING ====================
class DataManager:
    """Enhanced data management with SQLite caching"""
    
    def init(self, db_path: str = 'market_data.db'):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        
        # Price data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_data (
                symbol TEXT, period TEXT, timestamp DATETIME,
                open REAL, high REAL, low REAL, close REAL, volume REAL,
                UNIQUE(symbol, period, timestamp)
            )
        ''')
        
        # Analysis results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                symbol TEXT, period TEXT, timestamp DATETIME,
                rsi REAL, macd REAL, signal REAL, histogram REAL,
                sma20 REAL, sma50 REAL, price REAL,
                signals TEXT, recommendations TEXT,
                UNIQUE(symbol, period, timestamp)
            )
        ''')
        
        # Portfolio table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT, quantity REAL, buy_price REAL,
                timestamp DATETIME, notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_price_data(self, symbol: str, period: str, df: pd.DataFrame):
        """Save price data to cache"""
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            for _, row in df.iterrows():
                conn.execute('''
                    INSERT OR REPLACE INTO price_data 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (symbol, period, row['time'], row['open'], row['high'], 
                      row['low'], row['close'], row['volume']))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Cache save error: {e}")
    
    def load_price_data(self, symbol: str, period: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """Load price data from cache"""
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            df = pd.read_sql_query('''
                SELECT * FROM price_data 
                WHERE symbol = ? AND period = ? 
                ORDER BY timestamp DESC LIMIT ?
            ''', conn, params=(symbol, period, limit))
            conn.close()
            
            if not df.empty:
                df['time'] = pd.to_datetime(df['timestamp'])
                return df.drop('timestamp', axis=1)
            return None
        except Exception as e:
            logger.error(f"Cache load error: {e}")
            return None
    
    def save_analysis(self, analysis_data: Dict):
        """Save technical analysis results"""
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute('''
                INSERT OR REPLACE INTO analysis_results 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_data['symbol'], analysis_data['period'],
                analysis_data['timestamp'], analysis_data['indicators']['rsi'],
                analysis_data['indicators']['macd'], analysis_data['indicators']['macd_signal'],
                analysis_data['indicators']['macd_histogram'], analysis_data['indicators']['sma_20'],
                analysis_data['indicators']['sma_50'], analysis_data['indicators']['current_price'],
                json.dumps(analysis_data['signals']), json.dumps(analysis_data['recommendations'])
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Analysis save error: {e}")

# ==================== SECTION 5: TECHNICAL ANALYSIS ENGINE ====================
class TechnicalAnalyzer:
    """Advanced technical analysis engine"""
    
    # Technical constants
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    RSI_NEUTRAL = 50
    
    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        if df.empty or 'close' not in df.columns:
            return df
        
        try:
            df = df.copy()
            
            # RSI Calculation
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD Calculation
            exp12 = df['close'].ewm(span=12, adjust=False).mean()
            exp26 = df['close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp12 - exp26
            df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
            
            # Moving Averages
            df['SMA_20'] = df['close'].rolling(window=20, min_periods=1).mean()
            df['SMA_50'] = df['close'].rolling(window=50, min_periods=1).mean()
            df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
            
            # Bollinger Bands
            df['BB_Middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
            
            return df
            
        except Exception as e:
            logger.error(f"Indicator calculation error: {e}")
            return df
    
    @staticmethod
    def generate_signals(indicators: Dict) -> Dict:
        """Generate trading signals from indicators"""
        signals = {}
        
        # RSI Signals
        rsi = indicators.get('rsi', 50)
        if rsi < TechnicalAnalyzer.RSI_OVERSOLD:
            signals['rsi'] = 'oversold'
        elif rsi > TechnicalAnalyzer.RSI_OVERBOUGHT:
            signals['rsi'] = 'overbought'
        else:
            signals['rsi'] = 'neutral'
        
        # MACD Signals
        macd = indicators.get('macd', 0)
        signal = indicators.get('macd_signal', 0)
        histogram = indicators.get('macd_histogram', 0)
        
        if macd > signal and histogram > 0:
            signals['macd'] = 'bullish'
        elif macd < signal and histogram < 0:
            signals['macd'] = 'bearish'
        else:
            signals['macd'] = 'neutral'
        
        # Price vs Moving Averages
        price = indicators.get('current_price', 0)
        sma20 = indicators.get('sma_20', price)
        sma50 = indicators.get('sma_50', price)
        
        signals['price_vs_sma20'] = 'above' if price > sma20 else 'below'
        signals['price_vs_sma50'] = 'above' if price > sma50 else 'below'
        signals['sma_crossover'] = 'golden_cross' if sma20 > sma50 else 'death_cross'
        
        # Trend Analysis
        signals['trend'] = TechnicalAnalyzer._analyze_trend(indicators)
        
        return signals
    
    @staticmethod
    def _analyze_trend(indicators: Dict) -> str:
        """Analyze market trend"""
        bullish_signals = 0
        total_signals = 4
        
        price = indicators.get('current_price', 0)
        sma20 = indicators.get('sma_20', price)
        sma50 = indicators.get('sma_50', price)
        macd = indicators.get('macd', 0)
        signal = indicators.get('macd_signal', 0)
        
        if price > sma20: bullish_signals += 1
        if price > sma50: bullish_signals += 1
        if sma20 > sma50: bullish_signals += 1
        if macd > signal: bullish_signals += 1
        
        if bullish_signals >= 3:
            return 'strong_bullish'
        elif bullish_signals >= 2:
            return 'weak_bullish'
        elif bullish_signals >= 1:
            return 'weak_bearish'
        else:
            return 'strong_bearish'
    
    @staticmethod
    def generate_recommendations(signals: Dict, indicators: Dict) -> List[str]:
        """Generate trading recommendations"""
        recommendations = []
        
        # RSI-based recommendations
        rsi_signal = signals.get('rsi', 'neutral')
        if rsi_signal == 'oversold':
            recommendations.append("📈 RSI در ناحیه اشباع فروش - فرصت خرید")
        elif rsi_signal == 'overbought':
            recommendations.append("📉 RSI در ناحیه اشباع خرید - احتیاط در خرید")
        
        # MACD-based recommendations
        macd_signal = signals.get('macd', 'neutral')
        if macd_signal == 'bullish':
            recommendations.append("🟢 سیگنال MACD صعودی - احتمال رشد قیمت")
        elif macd_signal == 'bearish':
            recommendations.append("🔴 سیگنال MACD نزولی - احتمال کاهش قیمت")
        
        # Trend-based recommendations
        trend = signals.get('trend', 'neutral')
        if trend == 'strong_bullish':
            recommendations.append("🚀 روند صعودی قوی - مناسب برای خرید")
        elif trend == 'strong_bearish':
            recommendations.append("⚠️ روند نزولی قوی - مناسب برای فروش")
        
        # Risk management recommendations
        volatility = abs(indicators.get('macd_histogram', 0))
        if volatility > 0.5:
            recommendations.append("🌊 نوسان بالا - مدیریت ریسک ضروری")
        
        if not recommendations:
            recommendations.append("⚪ بازار در حالت تعادل - منتظر سیگنال واضح‌تر")
        
        return recommendations

# ==================== SECTION 6: ENHANCED VISUALIZATION ====================
class ChartRenderer:
    """Advanced chart rendering with Plotly"""
    
    @staticmethod
    def render_price_chart(df: pd.DataFrame, symbol: str, period: str, title: str) -> go.Figure:
        """Render enhanced price chart"""
        fig = go.Figure()
        
        if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            fig.add_trace(go.Candlestick(
                x=df['time'], open=df['open'], high=df['high'],
                low=df['low'], close=df['close'], name='Price'
            ))
        else:
            price_col = 'close' if 'close' in df.columns else 'price'
            fig.add_trace(go.Scatter(
                x=df['time'], y=df[price_col], mode='lines',
                name='Price', line=dict(color='#2962FF', width=2)
            ))
        
        # Add moving averages if available
        if 'SMA_20' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['time'], y=df['SMA_20'], mode='lines',
                name='SMA 20', line=dict(color='#FF6D00', width=1, dash='dash')
            ))
        
        if 'SMA_50' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['time'], y=df['SMA_50'], mode='lines',
                name='SMA 50', line=dict(color='#00C853', width=1, dash='dash')
            ))
        
        fig.update_layout(
            title=f"{symbol} - {title}",
            xaxis_title="زمان",
            yaxis_title="قیمت (USD)",
            xaxis_rangeslider_visible=False,
            height=500,
            template="plotly_white",
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def render_technical_indicators(df: pd.DataFrame) -> Tuple[go.Figure, go.Figure]:
        """Render RSI and MACD indicators"""
        # RSI Chart
        fig_rsi = go.Figure()
        if 'RSI' in df.columns:
            fig_rsi.add_trace(go.Scatter(
                x=df['time'], y=df['RSI'], mode='lines',
                name='RSI', line=dict(color='#7B1FA2', width=2)
            ))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
            fig_rsi.add_hline(y=50, line_dash="dot", line_color="gray")
        
        fig_rsi.update_layout(
            title="RSI (14)", height=300,
            xaxis_title="زمان", yaxis_title="RSI",
            template="plotly_white"
        )
        
        # MACD Chart
        fig_macd = go.Figure()
        if all(col in df.columns for col in ['MACD', 'MACD_Signal']):
            fig_macd.add_trace(go.Scatter(
                x=df['time'], y=df['MACD'], mode='lines',
                name='MACD', line=dict(color='#2962FF', width=2)
            ))
            fig_macd.add_trace(go.Scatter(
                x=df['time'], y=df['MACD_Signal'], mode='lines',
                name='Signal', line=dict(color='#FF6D00', width=2)
            ))
            
            if 'MACD_Histogram' in df.columns:
                colors = ['green' if x >= 0 else 'red' for x in df['MACD_Histogram']]
                fig_macd.add_trace(go.Bar(
                    x=df['time'], y=df['MACD_Histogram'],
                    name='Histogram', marker_color=colors, opacity=0.6
                ))
        
        fig_macd.update_layout(
            title="MACD", height=300,
            xaxis_title="زمان", yaxis_title="MACD",
            template="plotly_white"
        )
        
        return fig_rsi, fig_macd
# ==================== SECTION 7: PORTFOLIO TRACKER ====================
class PortfolioManager:
    """Portfolio tracking and management"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def add_to_portfolio(self, symbol: str, quantity: float, buy_price: float, notes: str = ""):
        """Add asset to portfolio"""
        try:
            conn = sqlite3.connect(self.data_manager.db_path, check_same_thread=False)
            conn.execute('''
                INSERT INTO portfolio (symbol, quantity, buy_price, timestamp, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (symbol, quantity, buy_price, datetime.now(), notes))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Portfolio add error: {e}")
            return False
    
    def get_portfolio_value(self, api_client) -> Dict:  # ✅ نوع ساده‌شده
        """Calculate current portfolio value"""
        try:
            conn = sqlite3.connect(self.data_manager.db_path, check_same_thread=False)
            portfolio = pd.read_sql_query('SELECT * FROM portfolio', conn)
            conn.close()
            
            if portfolio.empty:
                return {"total_value": 0, "assets": []}
            
            total_invested = 0
            total_current = 0
            assets = []
            
            for _, asset in portfolio.iterrows():
                # ✅ دریافت قیمت فعلی از API Client جدید
                if api_client and hasattr(api_client, 'get_coin_data'):
                    current_data = api_client.get_coin_data(asset['symbol'])
                    current_price = current_data.get('price', 0) if current_data else 0
                else:
                    # ✅ fallback در صورت عدم دسترسی
                    current_price = asset['buy_price'] * (1 + np.random.uniform(-0.2, 0.2))
                
                invested = asset['quantity'] * asset['buy_price']
                current_val = asset['quantity'] * current_price
                pnl = current_val - invested
                pnl_percent = (pnl / invested) * 100 if invested > 0 else 0
                
                assets.append({
                    'symbol': asset['symbol'],
                    'quantity': asset['quantity'],
                    'buy_price': asset['buy_price'],
                    'current_price': current_price,
                    'invested': invested,
                    'current_value': current_val,
                    'pnl': pnl,
                    'pnl_percent': pnl_percent
                })
                
                total_invested += invested
                total_current += current_val
            
            return {
                'total_invested': total_invested,
                'total_current': total_current,
                'total_pnl': total_current - total_invested,
                'total_pnl_percent': ((total_current - total_invested) / total_invested * 100) if total_invested > 0 else 0,
                'assets': assets
            }
            
        except Exception as e:
            logger.error(f"Portfolio calculation error: {e}")
            return {"total_value": 0, "assets": []}

    def remove_from_portfolio(self, asset_id: int) -> bool:
        """Remove asset from portfolio"""
        try:
            conn = sqlite3.connect(self.data_manager.db_path, check_same_thread=False)
            conn.execute('DELETE FROM portfolio WHERE id = ?', (asset_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Portfolio remove error: {e}")
            return False

    def get_portfolio_history(self, days: int = 30) -> pd.DataFrame:
        """Get portfolio history"""
        try:
            conn = sqlite3.connect(self.data_manager.db_path, check_same_thread=False)
            query = '''
                SELECT timestamp, SUM(quantity * buy_price) as daily_value 
                FROM portfolio 
                WHERE timestamp >= DATE('now', ?) 
                GROUP BY DATE(timestamp) 
                ORDER BY timestamp
            '''
            df = pd.read_sql_query(query, conn, params=(f'-{days} days',))
            conn.close()
            return df
        except Exception as e:
            logger.error(f"Portfolio history error: {e}")
            return pd.DataFrame()
# ==================== SECTION 8: MARKET SCANNER (کامل و اصلاح شده) ====================
class MarketScanner:
    """اپلیکیشن اصلی اسکنر بازار با پشتیبانی کامل از سرور میانی"""
    
    def init(self):
        self.config = Config()
        
        try:
            # ✅ ایجاد API Client برای سرور میانی شما
            self.api_client = MiddlewareAPIClient(self.config.MIDDLEWARE_BASE_URL)
            logger.info("✅ API Client برای سرور میانی ایجاد شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در ایجاد API Client: {e}")
            # ایجاد یک نمونه پایه برای جلوگیری از crash
            self.api_client = self._create_fallback_client()
        
        self.data_manager = DataManager()
        self.technical_analyzer = TechnicalAnalyzer()
        self.chart_renderer = ChartRenderer()
        self.portfolio_manager = PortfolioManager(self.data_manager)
        self.last_scan_time = None
        self.scan_cache = {}  # کش برای بهبود عملکرد
    
    def _create_fallback_client(self):
        """ایجاد client جایگزین در صورت خطا"""
        class FallbackClient:
            def init(self):
                self.is_healthy = False
                self.last_error = "Client ایجاد نشد"
            
            def get_coin_data(self, coin_id):
                return None
            
            def get_historical_data(self, coin_id, period):
                return self._generate_sample_data(period)
            
            def _generate_sample_data(self, period):
                # داده‌های نمونه پایه
                return pd.DataFrame({
                    'time': [datetime.now() - timedelta(hours=i) for i in range(100)][::-1],
                    'open': np.random.normal(50000, 5000, 100),
                    'high': np.random.normal(52000, 5000, 100),
                    'low': np.random.normal(48000, 5000, 100),
                    'close': np.random.normal(50000, 5000, 100),
                    'volume': np.random.uniform(1000000, 5000000, 100)
                })
        
        return FallbackClient()
    
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """دریافت داده‌های بازار با کشینگ"""
        cache_key = f"market_{symbol}"
        
        # بررسی کش (5 دقیقه اعتبار)
        if (cache_key in self.scan_cache and 
            datetime.now() - self.scan_cache[cache_key]['timestamp'] < timedelta(minutes=5)):
            logger.info(f"📦 استفاده از داده‌های کش شده برای {symbol}")
            return self.scan_cache[cache_key]['data']
        
        try:
            if self.api_client and self.api_client.is_healthy:
                market_data = self.api_client.get_coin_data(symbol)
                
                # ذخیره در کش
                if market_data:
                    self.scan_cache[cache_key] = {
                        'data': market_data,
                        'timestamp': datetime.now()
                    }
                
                return market_data
            else:
                logger.warning(f"⚠️ سرور میانی در دسترس نیست - داده‌های نمونه برای {symbol}")
                return self._generate_sample_market_data(symbol)
                
        except Exception as e:
            logger.error(f"❌ خطا در دریافت داده‌های بازار برای {symbol}: {e}")
            return self._generate_sample_market_data(symbol)
    
    def _generate_sample_market_data(self, symbol: str) -> Dict:
        """ایجاد داده‌های نمونه برای بازار"""
        base_prices = {
            "bitcoin": 45000, "ethereum": 3000, "binancecoin": 600,
            "cardano": 0.5, "ripple": 0.6, "solana": 100,
            "polkadot": 7, "dogecoin": 0.1, "avalanche": 40,
            "matic-network": 1, "litecoin": 70, "cosmos": 10
        }
        
        base_price = base_prices.get(symbol, 100)
        change_24h = np.random.uniform(-10, 10)
        
        return {
            'id': symbol,
            'name': symbol.capitalize(),
            'symbol': symbol.upper()[:4],
            'price': base_price * (1 + np.random.uniform(-0.1, 0.1)),
            'priceChange24h': change_24h,
            'priceChange1h': np.random.uniform(-2, 2),
            'high24h': base_price * (1 + np.random.uniform(0.05, 0.15)),
            'low24h': base_price * (1 - np.random.uniform(0.05, 0.15)),
            'volume': np.random.uniform(10000000, 500000000),
            'marketCap': np.random.uniform(100000000, 100000000000),
            'lastUpdated': datetime.now().isoformat()
        }
    
    def get_historical_data(self, symbol: str, period: str) -> pd.DataFrame:
        """دریافت داده‌های تاریخی با کشینگ"""
        cache_key = f"historical_{symbol}_{period}"
        
        # بررسی کش (10 دقیقه اعتبار برای داده‌های تاریخی)
        if (cache_key in self.scan_cache and 
            datetime.now() - self.scan_cache[cache_key]['timestamp'] < timedelta(minutes=10)):
            logger.info(f"📦 استفاده از داده‌های تاریخی کش شده برای {symbol} - {period}")
            return self.scan_cache[cache_key]['data']
        
        try:
            if self.api_client:
                historical_data = self.api_client.get_historical_data(symbol, period)
                
                # ذخیره در کش
                if historical_data is not None and not historical_data.empty:
                    self.scan_cache[cache_key] = {
                        'data': historical_data,
                        'timestamp': datetime.now()
                    }
                
                return historical_data
            else:
                return self.api_client._generate_sample_data(period)
                
        except Exception as e:
            logger.error(f"❌ خطا در دریافت داده‌های تاریخی برای {symbol}: {e}")
            return self._generate_fallback_historical_data(period)
    
    def _generate_fallback_historical_data(self, period: str) -> pd.DataFrame:
        """داده‌های تاریخی جایگزین در صورت خطا"""
        return pd.DataFrame({
            'time': [datetime.now() - timedelta(hours=i) for i in range(24)][::-1],
            'open': [50000] * 24, 'high': [51000] * 24, 
            'low': [49000] * 24, 'close': [50500] * 24,
            'volume': [1000000] * 24
        })
    
    def run_technical_analysis(self, historical_data: pd.DataFrame) -> pd.DataFrame:
        """اجرای تحلیل تکنیکال روی داده‌های تاریخی"""
        try:
            if historical_data is None or historical_data.empty:
                logger.warning("⚠️ داده‌های تاریخی برای تحلیل خالی هستند")
                return pd.DataFrame()
            
            # محاسبه اندیکاتورها
            analyzed_data = self.technical_analyzer.calculate_indicators(historical_data.copy())
            logger.info(f"✅ تحلیل تکنیکال انجام شد: {len(analyzed_data)} نقطه داده")
            
            return analyzed_data
            
        except Exception as e:
            logger.error(f"❌ خطا در تحلیل تکنیکال: {e}")
            return historical_data  # بازگشت داده‌های اصلی در صورت خطا
    
    def generate_trading_signals(self, analyzed_data: pd.DataFrame, current_price: float) -> Dict:
        """تولید سیگنال‌های معاملاتی"""
        try:
            if analyzed_data.empty:
                return {
                    'signals': {'error': 'داده‌ای برای تحلیل وجود ندارد'},
                    'recommendations': ['داده کافی نیست']
                }
            
            # دریافت آخرین مقادیر اندیکاتورها
            last_row = analyzed_data.iloc[-1]
            
            indicators = {
                'current_price': current_price,
                'rsi': last_row.get('RSI', 50),
                'macd': last_row.get('MACD', 0),
                'macd_signal': last_row.get('MACD_Signal', 0),
                'macd_histogram': last_row.get('MACD_Histogram', 0),
                'sma_20': last_row.get('SMA_20', current_price),
                'sma_50': last_row.get('SMA_50', current_price)
            }
            
            # تولید سیگنال‌ها
            signals = self.technical_analyzer.generate_signals(indicators)
            recommendations = self.technical_analyzer.generate_recommendations(signals, indicators)
            
            return {
                'indicators': indicators,
                'signals': signals,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"❌ خطا در تولید سیگنال‌ها: {e}")
            return {
                'signals': {'error': str(e)},
                'recommendations': ['خطا در تحلیل سیگنال‌ها']
            }
    
    def run_complete_analysis(self, symbol: str, period: str) -> Optional[Dict]:
        """اجرای تحلیل کامل برای یک نماد"""
        try:
            logger.info(f"🔍 شروع تحلیل برای {symbol} - دوره {period}")
            
            # دریافت داده‌های بازار
            market_data = self.get_market_data(symbol)
            current_price = market_data.get('price', 0) if market_data else 0
            
            # دریافت داده‌های تاریخی
            historical_data = self.get_historical_data(symbol, period)
            if historical_data is None or historical_data.empty:
                logger.warning(f"⚠️ داده‌های تاریخی برای {symbol} دریافت نشد")
                return None
            
            # تحلیل تکنیکال
            analyzed_data = self.run_technical_analysis(historical_data)
            
            # تولید سیگنال‌ها
            trading_signals = self.generate_trading_signals(analyzed_data, current_price)
            
            # ایجاد نتیجه نهایی
            analysis_result = {
                'symbol': symbol,
                'period': period,
                'timestamp': datetime.now(),
                'market_data': market_data,
                'historical_data': analyzed_data,
                **trading_signals
            }
            
            # ذخیره در دیتابیس
            self.data_manager.save_analysis(analysis_result)
            logger.info(f"✅ تحلیل کامل {symbol} تکمیل شد")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ خطا در تحلیل کامل {symbol}: {e}")
            return None
    
    def scan_single_symbol(self, symbol: str, period: str = "24h") -> Optional[Dict]:
        """اسکن یک نماد خاص"""
        return self.run_complete_analysis(symbol, period)
    
    def scan_multiple_symbols(self, symbols: List[str], period: str = "24h") -> Dict[str, Optional[Dict]]:
        """اسکن چندین نماد به صورت بهینه"""
        results = {}
        total_symbols = len(symbols)
        
        logger.info(f"🌐 شروع اسکن {total_symbols} نماد")
        
        for i, symbol in enumerate(symbols):
            try:
                # نمایش پیشرفت
                progress = (i + 1) / total_symbols * 100
                logger.info(f"📊 اسکن {symbol} ({i+1}/{total_symbols}) - {progress:.1f}%")
                
                # اجرای تحلیل
                analysis = self.run_complete_analysis(symbol, period)
                results[symbol] = analysis
                
                # تاخیر برای جلوگیری از overload
                if i < total_symbols - 1:  # برای آخرین مورد نیاز نیست
                    time.sleep(0.3)
                    
            except Exception as e:
                logger.error(f"❌ خطا در اسکن {symbol}: {e}")
                results[symbol] = None
        
        # به‌روزرسانی زمان آخرین اسکن
        self.last_scan_time = datetime.now()
        logger.info(f"✅ اسکن {len(results)} نماد تکمیل شد")
        
        return results
    
    def scan_all_market(self, period: str = "24h") -> Dict[str, Optional[Dict]]:
        """اسکن تمام بازار"""
        return self.scan_multiple_symbols(self.config.SYMBOLS[:6], period)
    
    def get_scanner_status(self) -> Dict:
        """دریافت وضعیت فعلی اسکنر"""
        status = {
            'api_healthy': self.api_client.is_healthy if self.api_client else False,
            'last_scan_time': self.last_scan_time,
            'cache_size': len(self.scan_cache),
            'symbols_available': len(self.config.SYMBOLS),
            'last_error': self.api_client.last_error if self.api_client else 'API Client موجود نیست'
        }
        
        if self.api_client and hasattr(self.api_client, 'last_check'):
            status['last_health_check'] = self.api_client.last_check
        
        return status
    
    def clear_cache(self):
        """پاک کردن کش"""
        self.scan_cache.clear()
        logger.info("✅ کش اسکنر پاک شد")
    
    def health_check(self) -> bool:
        """بررسی سلامت اسکنر"""
        try:
            if not self.api_client:
                logger.error("❌ API Client موجود نیست")
                return False
            
            # بررسی سلامت سرور میانی
            if hasattr(self.api_client, '_check_health'):
                self.api_client._check_health()
            
            status = self.get_scanner_status()
            logger.info(f"🔧 وضعیت اسکنر: {status}")
            
            return status['api_healthy']
            
        except Exception as e:
            logger.error(f"❌ خطا در بررسی سلامت اسکنر: {e}")
            return False
    
    def get_symbol_performance_report(self, symbol: str) -> Optional[Dict]:
        """گزارش عملکرد برای یک نماد خاص"""
        try:
            analysis = self.run_complete_analysis(symbol, "24h")
            if not analysis:
                return None
            
            market_data = analysis.get('market_data', {})
            signals = analysis.get('signals', {})
            indicators = analysis.get('indicators', {})
            
            # محاسبه امتیاز عملکرد
            performance_score = self._calculate_performance_score(signals, indicators)
            
            return {
                'symbol': symbol,
                'performance_score': performance_score,
                'current_price': market_data.get('price', 0),
                '24h_change': market_data.get('priceChange24h', 0),
                'trend': signals.get('trend', 'unknown'),
                'rsi_status': signals.get('rsi', 'neutral'),
                'macd_status': signals.get('macd', 'neutral'),
                'recommendations': analysis.get('recommendations', []),
                'timestamp': analysis.get('timestamp')
            }
            
        except Exception as e:
            logger.error(f"❌ خطا در ایجاد گزارش عملکرد برای {symbol}: {e}")
            return None
    
    def _calculate_performance_score(self, signals: Dict, indicators: Dict) -> float:
        """محاسبه امتیاز عملکرد بر اساس سیگنال‌ها"""
        score = 50.0  # امتیاز پایه
        
        # امتیاز بر اساس RSI
        rsi = indicators.get('rsi', 50)
        if 30 <= rsi <= 70:
            score += 10
        elif rsi < 30 or rsi > 70:
            score -= 5
        
        # امتیاز بر اساس روند
        trend = signals.get('trend', 'neutral')
        if trend == 'strong_bullish':
            score += 20
        elif trend == 'weak_bullish':
            score += 10
        elif trend == 'weak_bearish':
            score -= 10
        elif trend == 'strong_bearish':
            score -= 20
        
        # امتیاز بر اساس MACD
        macd_signal = signals.get('macd', 'neutral')
        if macd_signal == 'bullish':
            score += 15
        elif macd_signal == 'bearish':
            score -= 15
        
        return max(0, min(100, score))  # محدود کردن بین 0-100
        
# ==================== SECTION 9: STREAMLIT UI COMPONENTS (کامل و اصلاح شده) ====================
class StreamlitUI:
    """کامپوننت‌های رابط کاربری Streamlit با پشتیبانی از سرور میانی"""
    
    @staticmethod
    def setup_sidebar(scanner, T: Dict) -> Tuple[str, str, bool, bool, bool, bool, Dict]:
        """Setup sidebar controls with enhanced persistence"""
    
        # Initialize session state for persistence
        if 'sidebar_state' not in st.session_state:
            st.session_state.sidebar_state = {
                'language': "فارسی",
                'symbol': Config.SYMBOLS[0],
                'period': list(Config.PERIODS.keys())[0],
                'show_charts': True,
                'show_analysis': True,
                'show_portfolio': False,
                'scan_filter': 'all',
                'max_symbols': 20,
                'notifications_seen': {}
            }

        st.sidebar.header(T["settings"])
    
        # Language selection with persistence
        language = st.sidebar.selectbox(
            T["language"], 
            ["فارسی", "English"],
            index=0 if st.session_state.sidebar_state['language'] == "فارسی" else 1
        )
        st.session_state.sidebar_state['language'] = language
        T = TranslationManager.get_text(language)
    
        # Symbol selection with persistence
        symbol = st.sidebar.selectbox(
            T["select_symbol"],
            options=Config.SYMBOLS,
            index=Config.SYMBOLS.index(st.session_state.sidebar_state['symbol']),
            format_func=lambda x: x.capitalize().replace('-', ' ')
        )
        st.session_state.sidebar_state['symbol'] = symbol
    
        # Period selection with persistence
        period_options = list(Config.PERIODS.keys())
        period_index = period_options.index(st.session_state.sidebar_state['period'])
        period = st.sidebar.selectbox(
            T["select_interval"],
            options=period_options,
            index=period_index,
            format_func=lambda x: Config.PERIODS[x] if language == "فارسی" else x
        )
        st.session_state.sidebar_state['period'] = period
    
        # Display options with persistence
        show_charts = st.sidebar.checkbox(
            "📊 نمایش نمودارها", 
            value=st.session_state.sidebar_state['show_charts']
        )
        st.session_state.sidebar_state['show_charts'] = show_charts
    
        show_analysis = st.sidebar.checkbox(
             "🔍 نمایش تحلیل پیشرفته", 
             value=st.session_state.sidebar_state['show_analysis']
        )
        st.session_state.sidebar_state['show_analysis'] = show_analysis

        # Additional features with persistence
        show_portfolio = st.sidebar.checkbox(
            "💼 نمایش پرتفوی", 
            value=st.session_state.sidebar_state['show_portfolio']
        )
        st.session_state.sidebar_state['show_portfolio'] = show_portfolio
    
        # API Health Check Section - ✅ اصلاح شده با بررسی وجود api_client
        st.sidebar.header("🔧 سلامت سرویس")
    
        # ✅ بررسی ایمن وجود api_client و attributeهایش
        api_healthy = False
        last_error = None
        last_check = None
    
        if scanner and hasattr(scanner, 'api_client') and scanner.api_client is not None:
            if hasattr(scanner.api_client, 'is_healthy'):
                api_healthy = scanner.api_client.is_healthy
            if hasattr(scanner.api_client, 'last_error'):
                last_error = scanner.api_client.last_error
            if hasattr(scanner.api_client, 'last_check'):
                last_check = scanner.api_client.last_check
    
        # API Status Indicator
        if api_healthy:
            st.sidebar.success("✅ سرور میانی متصل")
            # نمایش اطلاعات اضافی فقط اگر api_client سالم است
            with st.sidebar.expander("📊 اطلاعات سرور"):
                st.write("✅ وضعیت: فعال")
                if last_check:
                    st.write(f"⏰ آخرین بررسی: {last_check.strftime('%H:%M:%S')}")
                st.write("🌐 منبع داده: سرور میانی شما")
        else:
            st.sidebar.error("❌ سرور میانی قطع")
        
            if last_error:
                with st.sidebar.expander("جزئیات خطا"):
                     st.error(last_error)
            else:
                with st.sidebar.expander("جزئیات خطا"):
                    st.error("API Client ایجاد نشده یا خطای ناشناخته")
    
        # API Health Check Button - ✅ اصلاح شده
        if st.sidebar.button("🔄 بررسی سلامت سرور", use_container_width=True):
            with st.sidebar:
                with st.spinner("در حال بررسی..."):
                    if scanner and hasattr(scanner, 'api_client') and scanner.api_client is not None:
                        if hasattr(scanner.api_client, '_check_health'):
                            scanner.api_client._check_health()
                    st.rerun()
    
        # بقیه کد بدون تغییر...
        scan_all = st.sidebar.button(T["scan_all"], use_container_width=True)
    
        return symbol, period, show_charts, show_analysis, show_portfolio, scan_all, T
    
    @staticmethod
    def test_middleware_connection(api_client):
        """Test connection to middleware server"""
        import requests
        
        try:
            if not api_client:
                st.error("❌ API Client موجود نیست")
                return
            
            # تست endpoint سلامت
            health_url = f"{api_client.base_url}/health"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                st.success("✅ اتصال به سرور میانی برقرار است")
                health_data = response.json()
                st.json(health_data)
            else:
                st.error(f"❌ خطای سرور: کد {response.status_code}")
                
            # تست endpoint داده‌ها
            data_url = f"{api_client.base_url}/coins"
            response = requests.get(data_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                coin_count = len(data.get('coins', []))
                st.success(f"✅ داده‌ها قابل دسترسی هستند ({coin_count} ارز)")
            else:
                st.warning(f"⚠️ داده‌ها در دسترس نیستند: کد {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ خطای اتصال: {str(e)}")
    
    @staticmethod
    def test_sample_data():
        """Test sample data generation"""
        try:
            # ایجاد داده‌های نمونه
            sample_data = pd.DataFrame({
                'time': [datetime.now() - timedelta(hours=i) for i in range(24)][::-1],
                'open': np.random.normal(50000, 1000, 24),
                'high': np.random.normal(51000, 1000, 24),
                'low': np.random.normal(49000, 1000, 24),
                'close': np.random.normal(50500, 1000, 24),
                'volume': np.random.uniform(1000000, 5000000, 24)
            })
            
            # تحلیل تکنیکال نمونه
            analyzer = TechnicalAnalyzer()
            analyzed_data = analyzer.calculate_indicators(sample_data)
            
            st.success("✅ داده‌های نمونه با موفقیت ایجاد شدند")
            st.dataframe(analyzed_data.tail(5))
            
            # نمایش اندیکاتورها
            last_row = analyzed_data.iloc[-1]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("RSI", f"{last_row.get('RSI', 50):.1f}")
            with col2:
                st.metric("MACD", f"{last_row.get('MACD', 0):.4f}")
            with col3:
                st.metric("SMA 20", f"{last_row.get('SMA_20', 0):.0f}")
                
        except Exception as e:
            st.error(f"❌ خطا در ایجاد داده‌های نمونه: {str(e)}")

    @staticmethod
    def clear_cache(scanner):
        """Clear all caches"""
        try:
            # پاک کردن کش session state
            keys = list(st.session_state.keys())
            for key in keys:
                if key != 'sidebar_state':
                    del st.session_state[key]
            
            # پاک کردن کش اسکنر
            if hasattr(scanner, 'clear_cache'):
                scanner.clear_cache()
            
            st.success("✅ حافظه موقت پاک شد")
        except Exception as e:
            st.error(f"❌ خطا در پاک کردن حافظه: {str(e)}")
    
    @staticmethod
    def display_market_overview(market_data: Dict, T: Dict):
        """Display market overview cards"""
        if not market_data:
            st.warning(T["no_data"])
            return
        
        # ایجاد کارت‌های متریک
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            price = market_data.get('price', 0)
            st.metric(T["price"], f"${price:,.2f}" if price >= 1 else f"${price:.4f}")
        
        with col2:
            change_24h = market_data.get('priceChange24h', 0)
            change_color = "normal" if change_24h >= 0 else "inverse"
            st.metric(T["change"], f"{change_24h:+.2f}%", delta_color=change_color)
        
        with col3:
            high_24h = market_data.get('high24h', market_data.get('price', 0))
            st.metric(T["high"], f"${high_24h:,.2f}" if high_24h >= 1 else f"${high_24h:.4f}")
        
        with col4:
            low_24h = market_data.get('low24h', market_data.get('price', 0))
            st.metric(T["low"], f"${low_24h:,.2f}" if low_24h >= 1 else f"${low_24h:.4f}")
        
        with col5:
            volume = market_data.get('volume', 0)
            if volume > 1000000:
                st.metric(T["volume"], f"${volume/1000000:.1f}M")
            else:
                st.metric(T["volume"], f"${volume:,.0f}")
        
        # اطلاعات اضافی در صورت موجود بودن
        if any(key in market_data for key in ['marketCap', 'priceChange1h']):
            with st.expander("📈 اطلاعات تکمیلی"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    market_cap = market_data.get('marketCap', 0)
                    if market_cap > 0:
                        st.metric("مارکت کپ", f"${market_cap/1000000000:.1f}B")
                with col2:
                    change_1h = market_data.get('priceChange1h', 0)
                    if change_1h != 0:
                        st.metric("تغییر 1h", f"{change_1h:+.2f}%")
                with col3:
                    last_updated = market_data.get('lastUpdated', '')
                    if last_updated:
                        st.metric("آخرین بروزرسانی", last_updated.split('T')[0])
    
    @staticmethod
    def display_analysis_dashboard(analysis: Dict, T: Dict):
        """Display technical analysis dashboard"""
        if not analysis:
            st.warning("تحلیل تکنیکال در دسترس نیست")
            return
        
        st.header("📊 دیشبورد تحلیل تکنیکال")
        
        # Summary cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            rsi = analysis['indicators'].get('rsi', 50)
            rsi_color = "🟢" if 30 <= rsi <= 70 else "🟡" if rsi > 70 else "🔴"
            if rsi < 30:
                st.error(f"{rsi_color} RSI: {rsi:.1f} (اشباع فروش)")
            elif rsi > 70:
                st.warning(f"{rsi_color} RSI: {rsi:.1f} (اشباع خرید)")
            else:
                st.success(f"{rsi_color} RSI: {rsi:.1f} (نرمال)")
        
        with col2:
            trend = analysis['signals'].get('trend', 'neutral')
            trend_config = {
                'strong_bullish': ('🚀', 'صعودی قوی', 'success'),
                'weak_bullish': ('📈', 'صعودی ضعیف', 'info'),
                'weak_bearish': ('📉', 'نزولی ضعیف', 'warning'),
                'strong_bearish': ('⚠️', 'نزولی قوی', 'error'),
                'neutral': ('⚪', 'خنثی', 'info')
            }
            icon, text, color = trend_config.get(trend, ('⚪', 'نامشخص', 'info'))
            
            if color == 'success':
                st.success(f"{icon} {text}")
            elif color == 'error':
                st.error(f"{icon} {text}")
            elif color == 'warning':
                st.warning(f"{icon} {text}")
            else:
                st.info(f"{icon} {text}")
        
        with col3:
            macd_signal = analysis['signals'].get('macd', 'neutral')
            macd_value = analysis['indicators'].get('macd', 0)
            if macd_signal == 'bullish':
                st.success(f"🟢 MACD: {macd_value:.4f} (صعودی)")
            elif macd_signal == 'bearish':
                st.error(f"🔴 MACD: {macd_value:.4f} (نزولی)")
            else:
                st.info(f"⚪ MACD: {macd_value:.4f} (خنثی)")
        
        with col4:
            price = analysis['indicators'].get('current_price', 0)
            sma50 = analysis['indicators'].get('sma_50', price)
            status = "بالاتر از SMA50" if price > sma50 else "پایین‌تر از SMA50"
            difference = ((price - sma50) / sma50 * 100) if sma50 > 0 else 0
            color = "normal" if price > sma50 else "inverse"
            st.metric("موقعیت قیمت", status, delta=f"{difference:+.1f}%", delta_color=color)
        
        # نمایش اندیکاتورهای عددی
        with st.expander("📊 مقادیر اندیکاتورها"):
            indicators = analysis['indicators']
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("قیمت فعلی", f"${indicators.get('current_price', 0):,.2f}")
                st.metric("SMA 20", f"${indicators.get('sma_20', 0):,.2f}")
                
            with col2:
                st.metric("RSI", f"{indicators.get('rsi', 50):.1f}")
                st.metric("SMA 50", f"${indicators.get('sma_50', 0):,.2f}")
                
            with col3:
                st.metric("MACD", f"{indicators.get('macd', 0):.4f}")
                st.metric("MACD Signal", f"{indicators.get('macd_signal', 0):.4f}")
                
            with col4:
                st.metric("MACD Histogram", f"{indicators.get('macd_histogram', 0):.4f}")
                st.metric("تاریخ تحلیل", analysis.get('timestamp', '').split(' ')[0])
        
        # Recommendations
        st.subheader("💡 توصیه‌های معاملاتی")
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                if any(word in rec for word in ['صعودی', 'خرید', 'طلا', 'مناسب', 'فرصت']):
                    st.success(f"✅ {i}. {rec}")
                elif any(word in rec for word in ['نزولی', 'فروش', 'مرگ', 'احتیاط', 'خطر']):
                    st.error(f"❌ {i}. {rec}")
                else:
                    st.info(f"ℹ️ {i}. {rec}")
        else:
            st.info("⚪ در حال حاضر توصیه‌ای برای نمایش وجود ندارد")

    @staticmethod
    def display_portfolio(scanner, T: Dict):
        """Display portfolio tracker"""
        st.header("💼 ردیابی پرتفوی")
    
        # Add asset form
        with st.form("add_asset"):
            col1, col2, col3 = st.columns(3)
            with col1:
                symbol = st.selectbox("نماد", Config.SYMBOLS)
            with col2:
                quantity = st.number_input("مقدار", min_value=0.0, step=0.1, value=1.0)
            with col3:
                buy_price = st.number_input("قیمت خرید (USD)", min_value=0.0, step=0.01, value=1000.0)
        
            notes = st.text_input("یادداشت (اختیاری)", placeholder="مانند: خرید در کف قیمت")
        
            if st.form_submit_button("➕ افزودن به پرتفوی"):
                if quantity > 0 and buy_price > 0:
                    if scanner.portfolio_manager.add_to_portfolio(symbol, quantity, buy_price, notes):
                        st.success("✅ دارایی به پرتفوی اضافه شد")
                        st.rerun()
                    else:
                        st.error("❌ خطا در افزودن دارایی")
                else:
                    st.warning("⚠️ مقدار و قیمت باید بزرگتر از صفر باشند")
    
         # ✅ Portfolio summary با بررسی ایمن
        api_client = scanner.api_client if (scanner and hasattr(scanner, 'api_client')) else None
        portfolio_value = scanner.portfolio_manager.get_portfolio_value(api_client)
        
        if portfolio_value['assets']:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 سرمایه‌گذاری شده", f"${portfolio_value['total_invested']:,.2f}")
            with col2:
                st.metric("💵 ارزش فعلی", f"${portfolio_value['total_current']:,.2f}")
            with col3:
                pnl = portfolio_value['total_pnl']
                pnl_percent = portfolio_value['total_pnl_percent']
                pnl_color = "normal" if pnl >= 0 else "inverse"
                st.metric("📊 سود/زیان", f"${pnl:,.2f}", 
                         delta=f"{pnl_percent:+.2f}%",
                         delta_color=pnl_color)
            with col4:
                if st.button("🔄 بروزرسانی قیمت‌ها"):
                    st.rerun()
        
            # Assets table
            st.subheader("📋 دارایی‌های پرتفوی")
            assets_df = pd.DataFrame(portfolio_value['assets'])

            # Format the dataframe for better display
            display_df = assets_df.copy()
            display_df['buy_price'] = display_df['buy_price'].apply(lambda x: f"${x:,.2f}")
            display_df['current_price'] = display_df['current_price'].apply(lambda x: f"${x:,.2f}")
            display_df['invested'] = display_df['invested'].apply(lambda x: f"${x:,.2f}")
            display_df['current_value'] = display_df['current_value'].apply(lambda x: f"${x:,.2f}")
            display_df['pnl'] = display_df['pnl'].apply(lambda x: f"${x:,.2f}")
            display_df['pnl_percent'] = display_df['pnl_percent'].apply(lambda x: f"{x:+.2f}%")

            st.dataframe(display_df, use_container_width=True)

            # Export portfolio data
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 خروجی Excel"):
                    StreamlitUI.export_to_excel(assets_df)
            with col2:
                if st.button("📊 نمودار پرتفوی"):
                    StreamlitUI.show_portfolio_chart(portfolio_value)
                    
        else:
            st.info("🔄 پرتفوی شما خالی است. اولین دارایی خود را اضافه کنید.")
            
    @staticmethod
    def export_to_excel(df: pd.DataFrame):
        """Export portfolio to Excel"""
        try:
            from io import BytesIO
            import base64
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                 df.to_excel(writer, sheet_name='Portfolio', index=False)
                
            excel_data = output.getvalue()
            b64 = base64.b64encode(excel_data).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="portfolio.xlsx">📥 دانلود فایل Excel</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("✅ فایل Excel آماده دانلود است")
        except Exception as e:
            st.error(f"❌ خطا در ایجاد فایل Excel: {e}")
            
    @staticmethod
    def show_portfolio_chart(portfolio_value: Dict):
        """Show portfolio distribution chart"""
        try:
            assets = portfolio_value['assets']
            if not assets:
                st.warning("هیچ دارایی برای نمایش وجود ندارد")
                return
                
            symbols = [asset['symbol'] for asset in assets]
            values = [asset['current_value'] for asset in assets]
            
            fig = go.Figure(data=[go.Pie(
                labels=symbols, 
                values=values, 
                hole=.3,
                textinfo='label+percent',
                insidetextorientation='radial'
            )])
            fig.update_layout(
                title="توزیع دارایی‌های پرتفوی",
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # نمایش اطلاعات تکمیلی
            total_value = portfolio_value['total_current']
            st.info(f"💰 ارزش کل پرتفوی: ${total_value:,.2f}")
            
        except Exception as e:
            st.error(f"❌ خطا در ایجاد نمودار: {e}")
            
    @staticmethod
    def display_scanner_status(scanner):
        """Display scanner status information"""
        with st.expander("🔧 وضعیت سیستم"):
            if hasattr(scanner, 'get_scanner_status'):
                status = scanner.get_scanner_status()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("وضعیت سرور", "✅ متصل" if status['api_healthy'] else "❌ قطع")
                    st.metric("تعداد نمادها", status['symbols_available'])
                    
                with col2:
                    if status['last_scan_time']:
                        st.metric("آخرین اسکن", status['last_scan_time'].strftime('%H:%M:%S'))
                    st.metric("اندازه کش", status['cache_size'])
                
                if status['last_error'] and status['last_error'] != 'API Client موجود نیست':
                    st.warning(f"آخرین خطا: {status['last_error']}")
            else:
                st.info("اطلاعات وضعیت در دسترس نیست")

    @staticmethod
    def display_performance_report(scanner, symbol: str):
        """Display performance report for a symbol"""
        try:
            if hasattr(scanner, 'get_symbol_performance_report'):
                report = scanner.get_symbol_performance_report(symbol)
                if report:
                    st.subheader(f"📈 گزارش عملکرد {symbol.upper()}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        # نمایش امتیاز عملکرد
                        score = report['performance_score']
                        if score >= 70:
                            st.success(f"🏆 امتیاز: {score:.1f}/100 (عالی)")
                        elif score >= 50:
                            st.info(f"📊 امتیاز: {score:.1f}/100 (متوسط)")
                        else:
                            st.warning(f"⚠️ امتیاز: {score:.1f}/100 (ضعیف)")
                    
                    with col2:
                        st.metric("روند", report['trend'])
                    
                    with col3:
                        st.metric("تغییر 24h", f"{report['24h_change']:+.2f}%")
                    
                    # نمایش توصیه‌ها
                    if report['recommendations']:
                        st.info("💡 توصیه‌ها:")
                        for rec in report['recommendations']:
                            st.write(f"• {rec}")
        except Exception as e:
            st.error(f"❌ خطا در نمایش گزارش عملکرد: {e}")

            
# ==================== SECTION 10: MAIN APPLICATION ==========================
def main():
    """Main application entry point"""
    logger.info("Starting Enhanced CoinState Scanner")
    
    try:
        # Initialize scanner
        scanner = MarketScanner()
        ui = StreamlitUI()
    
        # Setup UI with persistent sidebar
        st.title("📊 اسکنر بازار CoinState Pro")
        
        # ✅ بررسی ایمن سلامت سرور میانی
        if (scanner and hasattr(scanner, 'api_client') and 
            scanner.api_client is not None and 
            hasattr(scanner.api_client, 'is_healthy')):
            
            if not scanner.api_client.is_healthy:
                if hasattr(scanner.api_client, '_check_health'):
                    scanner.api_client._check_health()
        
        # Sidebar controls with persistence
        (symbol, period, show_charts, 
         show_analysis, show_portfolio, scan_all, T) = ui.setup_sidebar(scanner, TranslationManager.get_text("فارسی"))
        
        # ✅ نمایش وضعیت API با بررسی ایمن
        api_healthy = False
        if scanner and hasattr(scanner, 'api_client') and scanner.api_client is not None:
            if hasattr(scanner.api_client, 'is_healthy'):
                api_healthy = scanner.api_client.is_healthy
        
        if api_healthy:
            st.success("✅ اتصال به سرور میانی برقرار است - داده‌های زنده استفاده می‌شوند")
        else:
            st.warning("⚠️ اتصال به سرور میانی قطع است - از داده‌های نمونه استفاده می‌شود")
            
            with st.expander("🛠️ راه‌حل‌های پیشنهادی"):
                st.markdown("""
                1. بررسی اتصال اینترنت
                2. چند دقیقه صبر کنید و صفحه را رفرش کنید
                3. از بخش 'بررسی سلامت سرور' در سایدبار استفاده کنید
                4. در صورت مشکل مداوم، از داده‌های نمونه استفاده می‌شود
                """)
        
        # Get market data با مدیریت خطای پیشرفته
        with st.spinner(T["loading"]):
            try:
                if (hasattr(scanner, 'api_client') and scanner.api_client and 
                    hasattr(scanner.api_client, 'is_healthy') and scanner.api_client.is_healthy):
                    market_data = scanner.api_client.get_realtime_data(symbol)
                    if market_data:
                        st.success("✅ داده‌های بازار با موفقیت دریافت شد")
                    else:
                        st.warning("⚠️ داده‌های بازار دریافت نشد - از داده‌های نمونه استفاده می‌شود")
                        market_data = None
                else:
                    market_data = None
                    st.info("🔁 استفاده از داده‌های نمونه به دلیل قطعی API")
                
                # انجام تحلیل تکنیکال
                analysis = scanner.run_analysis(symbol, period)
                if analysis:
                    st.success("✅ تحلیل تکنیکال با موفقیت انجام شد")
                else:
                    st.warning("⚠️ تحلیل تکنیکال انجام نشد")

            except Exception as e:
                logger.error(f"Error in data fetching: {e}")
                st.error(f"❌ خطا در دریافت داده‌ها: {str(e)}")
                market_data = None
                analysis = None
        
        # Display market overview
        if market_data:
            ui.display_market_overview(market_data, T)
        else:
            st.warning("⚠️ داده‌های بازار در دسترس نیست. از داده‌های نمونه استفاده می‌شود.")
            # Generate sample market data
            sample_market_data = {
                'price': 45000 + np.random.uniform(-5000, 5000),
                'priceChange24h': np.random.uniform(-10, 10),
                'high24h': 50000 + np.random.uniform(0, 5000),
                'low24h': 40000 + np.random.uniform(0, 5000),
                'volume': np.random.uniform(10000000, 50000000)
            }
            ui.display_market_overview(sample_market_data, T)
            
            # اطلاعات درباره داده‌های نمونه
            st.info(""" توجه: در حال حاضر از داده‌های نمونه استفاده می‌شود. برای دسترسی به داده‌های زنده بازار. لطفا اتصال API را بررسی کنید.""")

        # Display analysis dashboard
        if show_analysis:
            if analysis:
                ui.display_analysis_dashboard(analysis, T)
                
                # اطلاعات تکمیلی تحلیل
                with st.expander("📈 جزئیات تحلیل تکنیکال"):
                    if 'indicators' in analysis:
                        indicators = analysis['indicators']
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("قیمت فعلی", f"${indicators.get('current_price', 0):,.2f}")
                            st.metric("SMA 20", f"${indicators.get('sma_20', 0):,.2f}")
                            
                        with col2:
                            st.metric("RSI", f"{indicators.get('rsi', 50):.1f}")
                            st.metric("SMA 50", f"${indicators.get('sma_50', 0):,.2f}")
                            
                        with col3:
                            macd = indicators.get('macd', 0)
                            st.metric("MACD", f"{macd:.4f}")
                            st.metric("MACD Signal", f"{indicators.get('macd_signal', 0):.4f}")
            else:
                st.warning("تحلیل تکنیکال در دسترس نیست")
                
                # ایجاد تحلیل نمونه در صورت عدم دسترسی
                if st.button("🧪 ایجاد تحلیل نمونه"):
                    sample_analysis = create_sample_analysis(symbol, period)
                    if sample_analysis:
                        ui.display_analysis_dashboard(sample_analysis, T)
        
        # Display charts
        if show_charts:
            if analysis and analysis.get('historical_data') is not None:
                historical_data = analysis.get('historical_data')
                
                # Price chart
                st.subheader("📊 نمودار قیمت")
                fig_price = ChartRenderer.render_price_chart(
                    historical_data, symbol, period, T["price_chart"]
                )
                st.plotly_chart(fig_price, use_container_width=True)
                
                # Technical indicators
                st.subheader(" اندیکاتورهای تکنیکال")
                fig_rsi, fig_macd = ChartRenderer.render_technical_indicators(historical_data)
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig_rsi, use_container_width=True)
                with col2:
                    st.plotly_chart(fig_macd, use_container_width=True)
                    
                # اطلاعات تکمیلی نمودار
                with st.expander("ℹ️ راهنمای نمودارها"):
                    st.markdown("""
                    نمودار کندل‌استیک (Candlestick):
                    -  سبز: قیمت بسته شدن بالاتر از باز شدن (صعود)
                    -  قرمز: قیمت بسته شدن پایین‌تر از باز شدن (نزول)
                    - خطوط بالا/پایین:نوسان
                    
                    اندیکاتور RSI:
                    -  بالای 70: اشباع خرید (احتمال correction)
                    -  زیر 30: اشباع فروش (فرصت خرید)
                    -  بین 30-70: منطقه نرمال
                    
                    اندیکاتور MACD:
                    -  خط MACD بالای Signal: سیگنال خرید
                    -  خط MACD زیر Signal: سیگنال فروش
                    -  هیستوگرام: قدرت روند
                    """)
            else:
                st.warning("نمودارها در دسترس نیستند")
                
                # ایجاد نمودارهای نمونه
                if st.button(" نمایش نمودارهای نمونه"):
                    sample_data = create_sample_chart_data(period)
                    if sample_data is not None:
                        fig_price = ChartRenderer.render_price_chart(sample_data, symbol, period, "نمودار نمونه")
                        st.plotly_chart(fig_price, use_container_width=True)
        
        # Display portfolio
        if show_portfolio:
            ui.display_portfolio(scanner, T)
        
        # Market scan feature
        if scan_all:
            st.info("🌐 اسکن تمام بازار در حال اجرا... این عملیات ممکن است چند دقیقه طول بکشد.")
            
            # نوار پیشرفت
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            market_scan_results = {}
            symbols_to_scan = Config.SYMBOLS[:6]  # Limit to 6 for performance
            
            for i, sym in enumerate(symbols_to_scan):
                status_text.text(f"در حال اسکن {sym}... ({i+1}/{len(symbols_to_scan)})")
                progress_bar.progress((i + 1) / len(symbols_to_scan))
                
                analysis = scanner.run_analysis(sym, "24h")
                if analysis:
                    market_scan_results[sym] = analysis
                
                time.sleep(0.5)  # Rate limiting
            
            progress_bar.empty()
            status_text.empty()
            
            # نمایش نتایج اسکن
            st.header("🌐 نتایج اسکن کامل بازار")
            
            if market_scan_results:
                # خلاصه نتایج
                total_symbols = len(market_scan_results)
                bullish_count = sum(1 for r in market_scan_results.values() 
                                  if r['signals'].get('trend') in ['strong_bullish', 'weak_bullish'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("تعداد نمادها", total_symbols)
                with col2:
                    st.metric("نمادهای صعودی", bullish_count)
                with col3:
                    st.metric("نمادهای نزولی", total_symbols - bullish_count)
                
                # نمایش جزئیات هر نماد
                for sym, result in market_scan_results.items():
                    trend = result['signals'].get('trend', 'neutral')
                    trend_color = {
                        'strong_bullish': '🟢',
                        'weak_bullish': '🟡', 
                        'weak_bearish': '🟠',
                        'strong_bearish': '🔴',
                        'neutral': '⚪'
                    }.get(trend, '⚪')
                    
                    with st.expander(f"{trend_color} {sym.upper()} - {trend}"):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            price = result['indicators'].get('current_price', 0)
                            st.metric("قیمت", f"${price:.2f}")
                        
                        with col2:
                            rsi = result['indicators'].get('rsi', 50)
                            rsi_color = "normal" if 30 <= rsi <= 70 else "inverse"
                            st.metric("RSI", f"{rsi:.1f}", delta_color=rsi_color)
                        
                        with col3:
                            macd_signal = result['signals'].get('macd', 'neutral')
                            signal_icon = "🟢" if macd_signal == 'bullish' else "🔴" if macd_signal == 'bearish' else "⚪"
                            st.metric("MACD", signal_icon)
                        
                        with col4:
                            if result['recommendations']:
                                st.info(result['recommendations'][0])
            else:
                st.warning("هیچ داده‌ای از اسکن بازار دریافت نشد.")
        
        # پاورقی و اطلاعات برنامه
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(" توسعه داده شده توسط:")
            st.markdown("CoinState Scanner Pro v2.0")
            
        with col2:
            st.markdown("📊 داده‌ها:")
            if market_data and hasattr(scanner, 'api_client') and scanner.api_client and scanner.api_client.is_healthy:
                st.markdown("✅ داده‌های زنده")
            else:
                st.markdown(" داده‌های نمونه")
                
        with col3:
            st.markdown("آخرین بروزرسانی:")
            st.markdown(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        
        st.error(" خطای غیرمنتظره در اجرای برنامه")
        
        import traceback
        error_details = traceback.format_exc()
        
        with st.expander(" جزئیات فنی خطا (برای توسعه‌دهنده)"):
            st.code(error_details, language='python')
        
        st.markdown("""
        راه‌حل‌های فوری:
        
        1. صفحه را رفرش کنید یا F5 را بزنید.
        2. بررسی سلامت API - از بخش سایدبار استفاده کنید
        3. پاک کردن حافظه - از بخش عیب‌یابی پیشرفته
        4. گزارش خطا - اطلاعات بالا را برای پشتیبانی ارسال کنید
        
         پشتیبانی فنی:
        - گزارش خطاها را به توسعه‌دهنده ارسال کنید
        - در صورت تکرار خطا برنامه را restart کنید
        """)
        
        # دکمه رفرش خودکار
        if st.button(" تلاش مجدد (رفرش صفحه)"):
            st.rerun()

def create_sample_analysis(symbol: str, period: str) -> Dict:
    """Create sample analysis for demonstration"""
    try:
        # ایجاد داده‌های نمونه برای تحلیل
        sample_data = pd.DataFrame({
            'time': [datetime.now() - timedelta(hours=i) for i in range(100)][::-1],
            'open': np.random.normal(50000, 5000, 100),
            'high': np.random.normal(52000, 5000, 100),
            'low': np.random.normal(48000, 5000, 100),
            'close': np.random.normal(50000, 5000, 100),
            'volume': np.random.uniform(1000000, 5000000, 100)
        })
        
        # محاسبه اندیکاتورها
        sample_data = TechnicalAnalyzer.calculate_indicators(sample_data)
        
        # آخرین مقادیر
        last_row = sample_data.iloc[-1]
        indicators = {
            'current_price': last_row.get('close', 50000),
            'rsi': min(max(last_row.get('RSI', 50), 0), 100),
            'macd': last_row.get('MACD', 0),
            'macd_signal': last_row.get('MACD_Signal', 0),
            'macd_histogram': last_row.get('MACD_Histogram', 0),
            'sma_20': last_row.get('SMA_20', 50000),
            'sma_50': last_row.get('SMA_50', 50000)
        }
        
        # تولید سیگنال‌ها
        signals = TechnicalAnalyzer.generate_signals(indicators)
        recommendations = TechnicalAnalyzer.generate_recommendations(signals, indicators)
        
        return {
            'symbol': symbol,
            'period': period,
            'timestamp': datetime.now(),
            'indicators': indicators,
            'signals': signals,
            'recommendations': recommendations,
            'historical_data': sample_data
        }
    except Exception as e:
        logger.error(f"Error creating sample analysis: {e}")
        return None

def create_sample_chart_data(period: str) -> pd.DataFrame:
    """Create sample data for charts"""
    try:
        period_points = {
            "24h": 24, "1w": 42, "1m": 30, "3m": 90,
            "6m": 180, "1y": 365, "all": 100
        }
        
        count = period_points.get(period, 100)
        times = [datetime.now() - timedelta(hours=i) for i in range(count)][::-1]
        
        data = []
        current_price = 50000
        
        for i in range(count):
            change = current_price * 0.02 * np.random.randn()
            current_price = max(current_price + change, 1000)
            
            data.append({
                'time': times[i],
                'open': current_price * (1 + np.random.uniform(-0.01, 0.01)),
                'high': current_price * (1 + np.random.uniform(0, 0.02)),
                'low': current_price * (1 - np.random.uniform(0, 0.02)),
                'close': current_price,
                'volume': np.random.uniform(1000000, 5000000)
            })
        
        df = pd.DataFrame(data)
        return TechnicalAnalyzer.calculate_indicators(df)
    except Exception as e:
        logger.error(f"Error creating sample chart data: {e}")
        return None

if __name__ == "__main__":
    main()
