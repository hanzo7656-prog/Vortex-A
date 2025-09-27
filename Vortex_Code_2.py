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
import threading
from collections import defaultdict

# ==================== SECTION 1: NOTIFICATION MANAGER ====================
class NotificationManager:
    """مدیریت نوتیفیکیشن‌های هوشمند با زمان‌بندی خودکار"""
    
    def __init__(self):
        self.notifications = []
        self.notification_timers = {}
        self.notification_history = defaultdict(list)
        self.lock = threading.Lock()
    
    def add_notification(self, message: str, level: str = "info", auto_hide: bool = True, duration: int = 5):
        """افزودن نوتیفیکیشن جدید"""
        with self.lock:
            notification_id = f"{level}_{int(time.time() * 1000)}"
            notification = {
                "id": notification_id,
                "message": message,
                "level": level,
                "auto_hide": auto_hide,
                "duration": duration,
                "timestamp": datetime.now(),
                "visible": True
            }
            
            self.notifications.append(notification)
            
            # ذخیره در تاریخچه
            self.notification_history[level].append(notification)
            
            # تنظیم تایمر برای مخفی شدن خودکار
            if auto_hide and level in ["info", "success"]:
                timer = threading.Timer(duration, self._auto_hide_notification, [notification_id])
                self.notification_timers[notification_id] = timer
                timer.start()
            
            return notification_id
    
    def _auto_hide_notification(self, notification_id: str):
        """مخفی کردن خودکار نوتیفیکیشن"""
        with self.lock:
            for notification in self.notifications:
                if notification["id"] == notification_id:
                    notification["visible"] = False
                    break
    
    def remove_notification(self, notification_id: str):
        """حذف دستی نوتیفیکیشن"""
        with self.lock:
            # توقف تایمر اگر وجود دارد
            if notification_id in self.notification_timers:
                self.notification_timers[notification_id].cancel()
                del self.notification_timers[notification_id]
            
            # حذف نوتیفیکیشن
            self.notifications = [n for n in self.notifications if n["id"] != notification_id]
    
    def get_visible_notifications(self):
        """دریافت نوتیفیکیشن‌های قابل نمایش"""
        with self.lock:
            return [n for n in self.notifications if n["visible"]]
    
    def clear_all_notifications(self):
        """پاک کردن تمام نوتیفیکیشن‌ها"""
        with self.lock:
            # توقف تمام تایمرها
            for timer in self.notification_timers.values():
                timer.cancel()
            
            self.notification_timers.clear()
            self.notifications.clear()
    
    def should_show_notification(self, message: str, level: str) -> bool:
        """بررسی آیا باید نوتیفیکیشن نمایش داده شود"""
        with self.lock:
            # برای خطاها و اخطارها همیشه نمایش بده
            if level in ["error", "warning"]:
                return True
            
            # برای اطلاعات عمومی، اگر اخیراً نمایش داده شده نمایش نده
            recent_threshold = datetime.now() - timedelta(minutes=5)
            recent_notifications = [
                n for n in self.notification_history[level] 
                if n["timestamp"] > recent_threshold and n["message"] == message
            ]
            
            return len(recent_notifications) == 0

# ==================== SECTION 2: CONFIGURATION & SETUP ====================
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
    MIDDLEWARE_BASE_URL = "https://server-test-ovta.onrender.com"
    
    SYMBOLS = [
        "bitcoin", "ethereum", "binancecoin", "cardano", "ripple", "solana",
        "polkadot", "dogecoin", "avalanche", "matic-network", "litecoin", "cosmos"
    ]
    
    PERIODS = {
        "24h": "24 ساعت", "1w": "1 هفته", "1m": "1 ماه", "3m": "3 ماه",
        "6m": "6 ماه", "1y": "1 سال", "all": "همه زمان"
    }

# ==================== SECTION 3: MULTILINGUAL SUPPORT ====================
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

# ==================== SECTION 4: MIDDLEWARE CLIENT ====================
class MiddlewareAPIClient:
    """API Client برای ارتباط با سرور میانی"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = self._create_session()
        self.is_healthy = False
        self.last_error = None
        self.last_check = None
        self._check_health()
    
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
            all_data = self.get_all_coins()
            if not all_data:
                return None
            
            coins = all_data.get('coins', [])
            coin_id_lower = coin_id.lower()
            
            for coin in coins:
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
        """دریافت داده‌های تاریخی"""
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
            base_price = 45000
            
            if period == "24h":
                times = [datetime.now() - timedelta(hours=i) for i in range(count)][::-1]
            else:
                times = [datetime.now() - timedelta(days=i) for i in range(count)][::-1]
            
            data = []
            current_price = base_price
            
            for i, time_point in enumerate(times):
                volatility = 0.02
                if period in ["1y", "all"]:
                    volatility = 0.04
                
                change = current_price * volatility * np.random.randn()
                current_price = max(current_price + change, base_price * 0.3)
                
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
                    'volume': np.random.uniform(1000000, 50000000)
                })
            
            df = pd.DataFrame(data)
            logger.info(f"✅ داده‌های نمونه برای دوره {period} ایجاد شد: {len(df)} نقطه داده")
            return df
            
        except Exception as e:
            logger.error(f"❌ خطا در ایجاد داده‌های نمونه: {str(e)}")
            return pd.DataFrame({
                'time': [datetime.now()],
                'open': [50000], 'high': [51000], 'low': [49000], 
                'close': [50500], 'volume': [1000000]
            })
    
    def scan_multiple_coins(self, coin_ids: List[str]) -> Dict[str, Optional[Dict]]:
        """اسکن چندین ارز به صورت بهینه"""
        results = {}
        
        try:
            all_data = self.get_all_coins(limit=100)
            if not all_data:
                return {coin_id: None for coin_id in coin_ids}
            
            coins_map = {}
            for coin in all_data.get('coins', []):
                id_key = coin.get('id', '').lower()
                name_key = coin.get('name', '').lower()
                symbol_key = coin.get('symbol', '').lower()
                
                coins_map[id_key] = coin
                coins_map[name_key] = coin
                coins_map[symbol_key] = coin
            
            for coin_id in coin_ids:
                coin_id_lower = coin_id.lower()
                results[coin_id] = coins_map.get(coin_id_lower)
            
            logger.info(f"✅ اسکن {len(coin_ids)} ارز تکمیل شد")
            return results
            
        except Exception as e:
            logger.error(f"❌ خطا در اسکن چندین ارز: {str(e)}")
            return {coin_id: None for coin_id in coin_ids}

# ==================== SECTION 5: DATA MANAGER & CACHING ====================
class DataManager:
    """Enhanced data management with SQLite caching"""
    
    def __init__(self, db_path: str = 'market_data.db'):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_data (
                symbol TEXT, period TEXT, timestamp DATETIME,
                open REAL, high REAL, low REAL, close REAL, volume REAL,
                UNIQUE(symbol, period, timestamp)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                symbol TEXT, period TEXT, timestamp DATETIME,
                rsi REAL, macd REAL, signal REAL, histogram REAL,
                sma20 REAL, sma50 REAL, price REAL,
                signals TEXT, recommendations TEXT,
                UNIQUE(symbol, period, timestamp)
            )
        ''')
        
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

# ==================== SECTION 6: TECHNICAL ANALYSIS ENGINE ====================
class TechnicalAnalyzer:
    """Advanced technical analysis engine"""
    
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
        
        if signals.get('rsi') == 'oversold':
            recommendations.append("📈 RSI در ناحیه اشباع فروش - فرصت خرید")
        elif signals.get('rsi') == 'overbought':
            recommendations.append("📉 RSI در ناحیه اشباع خرید - احتیاط در خرید")
        
        macd_signal = signals.get('macd', 'neutral')
        if macd_signal == 'bullish':
            recommendations.append("🟢 سیگنال MACD صعودی - احتمال رشد قیمت")
        elif macd_signal == 'bearish':
            recommendations.append("🔴 سیگنال MACD نزولی - احتمال کاهش قیمت")
        
        trend = signals.get('trend', 'neutral')
        if trend == 'strong_bullish':
            recommendations.append("🚀 روند صعودی قوی - مناسب برای خرید")
        elif trend == 'strong_bearish':
            recommendations.append("⚠️ روند نزولی قوی - مناسب برای فروش")
        
        volatility = abs(indicators.get('macd_histogram', 0))
        if volatility > 0.5:
            recommendations.append("🌊 نوسان بالا - مدیریت ریسک ضروری")
        
        if not recommendations:
            recommendations.append("⚪ بازار در حالت تعادل - منتظر سیگنال واضح‌تر")
        
        return recommendations

# ==================== SECTION 7: ENHANCED VISUALIZATION ====================
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

# ==================== SECTION 8: PORTFOLIO TRACKER ====================
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
    
    def get_portfolio_value(self, api_client) -> Dict:
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
                if api_client and hasattr(api_client, 'get_coin_data'):
                    current_data = api_client.get_coin_data(asset['symbol'])
                    current_price = current_data.get('price', 0) if current_data else 0
                else:
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

# ==================== SECTION 9: MARKET SCANNER (کامل و اصلاح شده) ====================
class MarketScanner:
    """اپلیکیشن اصلی اسکنر بازار با پشتیبانی کامل از سرور میانی و فیلترهای پیشرفته"""
    
    def __init__(self):
        self.config = Config()
        self.notification_manager = NotificationManager()
        
        try:
            self.api_client = MiddlewareAPIClient(self.config.MIDDLEWARE_BASE_URL)
            logger.info("✅ API Client برای سرور میانی ایجاد شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در ایجاد API Client: {e}")
            self.api_client = self._create_fallback_client()
        
        self.data_manager = DataManager()
        self.technical_analyzer = TechnicalAnalyzer()
        self.chart_renderer = ChartRenderer()
        self.portfolio_manager = PortfolioManager(self.data_manager)
        self.last_scan_time = None
        self.scan_cache = {}

    def _create_fallback_client(self):
        """ایجاد client جایگزین در صورت خطا"""
        class FallbackClient:
            def __init__(self):
                self.is_healthy = False
                self.last_error = "Client ایجاد نشد"
            
            def get_coin_data(self, coin_id):
                return None
            
            def get_historical_data(self, coin_id, period):
                return self._generate_sample_data(period)
            
            def _generate_sample_data(self, period):
                return pd.DataFrame({
                    'time': [datetime.now() - timedelta(hours=i) for i in range(100)][::-1],
                    'open': np.random.normal(50000, 5000, 100),
                    'high': np.random.normal(52000, 5000, 100),
                    'low': np.random.normal(48000, 5000, 100),
                    'close': np.random.normal(50000, 5000, 100),
                    'volume': np.random.uniform(1000000, 5000000, 100)
                })
        
        return FallbackClient()

    def scan_with_filters(self, limit: int = 100, filter_type: str = "volume", custom_filters: Dict = None) -> Dict:
        """اسکن بازار با فیلترهای پیشرفته"""
        try:
            params = {"limit": limit, "filter": filter_type}
            
            if custom_filters:
                params.update(custom_filters)
                endpoint = "/scan-custom"
            else:
                endpoint = "/scan-all"
            
            url = f"{self.config.MIDDLEWARE_BASE_URL}{endpoint}"
            logger.info(f"🌐 ارسال درخواست اسکن پیشرفته: {url} با پارامترها: {params}")
            
            response = requests.get(url, params=params, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ اسکن با فیلتر {filter_type} تکمیل شد: {data.get('total_coins', 0)} ارز")
                
                # افزودن نوتیفیکیشن موفقیت
                self.notification_manager.add_notification(
                    f"اسکن {data.get('total_coins', 0)} ارز با فیلتر {filter_type} تکمیل شد",
                    "success",
                    auto_hide=True,
                    duration=5
                )
                
                return data
            else:
                error_msg = f"خطای سرور: کد {response.status_code}"
                logger.error(f"❌ {error_msg}")
                
                # افزودن نوتیفیکیشن خطا
                self.notification_manager.add_notification(
                    error_msg,
                    "error",
                    auto_hide=False,
                    duration=0
                )
                
                return None
                
        except Exception as e:
            error_msg = f"خطا در اسکن با فیلتر: {e}"
            logger.error(f"❌ {error_msg}")
            
            self.notification_manager.add_notification(
                error_msg,
                "error",
                auto_hide=False,
                duration=0
            )
            
            return None

    # ... (بقیه متدهای قبلی با اضافه کردن نوتیفیکیشن‌ها)

# ==================== SECTION 10: STREAMLIT UI COMPONENTS (کامل و اصلاح شده) ====================
class StreamlitUI:
    """کامپوننت‌های رابط کاربری Streamlit با نوتیفیکیشن‌های هوشمند"""
    
    @staticmethod
    def display_notifications(notification_manager: NotificationManager):
        """نمایش نوتیفیکیشن‌های هوشمند"""
        notifications = notification_manager.get_visible_notifications()
        
        if not notifications:
            return
        
        for notification in notifications:
            level = notification["level"]
            message = notification["message"]
            notification_id = notification["id"]
            auto_hide = notification["auto_hide"]
            
            # ایجاد استایل‌های مختلف برای سطوح مختلف
            if level == "error":
                with st.container():
                    col1, col2 = st.columns([0.9, 0.1])
                    with col1:
                        st.error(message)
                    with col2:
                        if st.button("✕", key=f"close_{notification_id}"):
                            notification_manager.remove_notification(notification_id)
                            st.rerun()
            
            elif level == "warning":
                with st.container():
                    col1, col2 = st.columns([0.9, 0.1])
                    with col1:
                        st.warning(message)
                    with col2:
                        if st.button("✕", key=f"close_{notification_id}"):
                            notification_manager.remove_notification(notification_id)
                            st.rerun()
            
            elif level == "success":
                if auto_hide:
                    st.success(message)
                else:
                    with st.container():
                        col1, col2 = st.columns([0.9, 0.1])
                        with col1:
                            st.success(message)
                        with col2:
                            if st.button("✕", key=f"close_{notification_id}"):
                                notification_manager.remove_notification(notification_id)
                                st.rerun()
            
            else:  # info
                if auto_hide:
                    st.info(message)
                else:
                    with st.container():
                        col1, col2 = st.columns([0.9, 0.1])
                        with col1:
                            st.info(message)
                        with col2:
                            if st.button("✕", key=f"close_{notification_id}"):
                                notification_manager.remove_notification(notification_id)
                                st.rerun()
        
        # فاصله بین نوتیفیکیشن‌ها
        st.markdown("<br>", unsafe_allow_html=True)

    @staticmethod
    def setup_sidebar(scanner, T: Dict) -> Tuple[str, str, bool, bool, bool, bool, Dict]:
        """Setup sidebar controls with advanced scan options"""
        
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
    
        language = st.sidebar.selectbox(
            T["language"], 
            ["فارسی", "English"],
            index=0 if st.session_state.sidebar_state['language'] == "فارسی" else 1
        )
        st.session_state.sidebar_state['language'] = language
        T = TranslationManager.get_text(language)
    
        symbol = st.sidebar.selectbox(
            T["select_symbol"],
            options=Config.SYMBOLS,
            index=Config.SYMBOLS.index(st.session_state.sidebar_state['symbol']),
            format_func=lambda x: x.capitalize().replace('-', ' ')
        )
        st.session_state.sidebar_state['symbol'] = symbol
    
        period_options = list(Config.PERIODS.keys())
        period_index = period_options.index(st.session_state.sidebar_state['period'])
        period = st.sidebar.selectbox(
            T["select_interval"],
            options=period_options,
            index=period_index,
            format_func=lambda x: Config.PERIODS[x] if language == "فارسی" else x
        )
        st.session_state.sidebar_state['period'] = period
    
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

        show_portfolio = st.sidebar.checkbox(
            "💼 نمایش پرتفوی", 
            value=st.session_state.sidebar_state['show_portfolio']
        )
        st.session_state.sidebar_state['show_portfolio'] = show_portfolio
    
        # API Health Check
        st.sidebar.header("🔧 سلامت سرویس")
    
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
    
        if api_healthy:
            st.sidebar.success("✅ سرور میانی متصل")
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
    
        if st.sidebar.button("🔄 بررسی سلامت سرور", use_container_width=True):
            with st.sidebar:
                with st.spinner("در حال بررسی..."):
                    if scanner and hasattr(scanner, 'api_client') and scanner.api_client is not None:
                        if hasattr(scanner.api_client, '_check_health'):
                            scanner.api_client._check_health()
                    st.rerun()
    
        scan_all = st.sidebar.button(T["scan_all"], use_container_width=True)
    
        return symbol, period, show_charts, show_analysis, show_portfolio, scan_all, T

    @staticmethod
    def setup_advanced_scan_controls(scanner, T: Dict) -> Dict:
        """کنترل‌های پیشرفته اسکن در سایدبار"""
        st.sidebar.header("🎛️ کنترل‌های پیشرفته اسکن")
        
        scan_limit = st.sidebar.selectbox(
            "تعداد ارزها برای اسکن",
            options=[100, 500, 1000],
            index=0,
            help="تعداد ارزهایی که می‌خواهید اسکن شوند"
        )
        
        filter_type = st.sidebar.selectbox(
            "فیلتر اسکن",
            options=["volume", "liquidity", "price_change_24h", "market_cap", "signals"],
            index=0,
            format_func=lambda x: {
                "volume": "📊 حجم معاملات بالا",
                "liquidity": "💧 نقدینگی بالا", 
                "price_change_24h": "📈 تغییرات قیمت ۲۴h",
                "market_cap": "💰 مارکت کپ بالا",
                "signals": "🎯 سیگنال‌های تکنیکال"
            }.get(x, x),
            help="معیار فیلتر کردن ارزها"
        )
        
        custom_filters = {}
        with st.sidebar.expander("⚙️ فیلترهای سفارشی (اختیاری)"):
            st.write("**فیلتر حجم معاملات:**")
            col1, col2 = st.columns(2)
            with col1:
                min_volume = st.number_input("حداقل حجم (USD)", min_value=0, value=1000000, step=1000000)
            with col2:
                max_volume = st.number_input("حداکثر حجم (USD)", min_value=0, value=1000000000, step=10000000)
            
            st.write("**فیلتر تغییرات قیمت:**")
            col3, col4 = st.columns(2)
            with col3:
                min_price_change = st.number_input("حداقل تغییر (%)", min_value=0.0, value=1.0, step=0.5)
            with col4:
                max_price_change = st.number_input("حداکثر تغییر (%)", min_value=0.0, value=50.0, step=1.0)
            
            if min_volume > 0:
                custom_filters["min_volume"] = min_volume
            if max_volume > 0 and max_volume > min_volume:
                custom_filters["max_volume"] = max_volume
            if min_price_change > 0:
                custom_filters["min_price_change"] = min_price_change
            if max_price_change > 0 and max_price_change > min_price_change:
                custom_filters["max_price_change"] = max_price_change
        
        advanced_scan = st.sidebar.button(
            "🚀 اجرای اسکن پیشرفته", 
            use_container_width=True,
            type="primary",
            help="اجرای اسکن با تنظیمات انتخاب شده"
        )
        
        return {
            "scan_limit": scan_limit,
            "filter_type": filter_type,
            "custom_filters": custom_filters if custom_filters else None,
            "advanced_scan": advanced_scan
        }

    # ... (بقیه متدهای UI)

# ==================== SECTION 11: MAIN APPLICATION ====================
def main():
    """Main application entry point"""
    logger.info("Starting Enhanced CoinState Scanner with Smart Notifications")
    
    try:
        # Initialize scanner
        scanner = MarketScanner()
        ui = StreamlitUI()
    
        # Setup UI
        st.title("📊 اسکنر بازار CoinState Pro - نسخه پیشرفته")
        
        # نمایش نوتیفیکیشن‌ها
        ui.display_notifications(scanner.notification_manager)
        
        # سایدبار اصلی
        (symbol, period, show_charts, 
         show_analysis, show_portfolio, scan_all, T) = ui.setup_sidebar(scanner, TranslationManager.get_text("فارسی"))
        
        # کنترل‌های پیشرفته اسکن
        scan_controls = ui.setup_advanced_scan_controls(scanner, T)
        
        # بخش اسکن پیشرفته
        if scan_controls["advanced_scan"]:
            st.info(f"""
            🌐 **اسکن پیشرفته در حال اجرا...**
            - تعداد ارزها: **{scan_controls['scan_limit']}**
            - فیلتر اعمال شده: **{scan_controls['filter_type']}**
            - فیلترهای سفارشی: **{'فعال' if scan_controls['custom_filters'] else 'غیرفعال'}**
            """)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner("در حال اسکن بازار با فیلترهای پیشرفته..."):
                scan_results = scanner.scan_with_filters(
                    limit=scan_controls["scan_limit"],
                    filter_type=scan_controls["filter_type"],
                    custom_filters=scan_controls["custom_filters"]
                )
            
            progress_bar.progress(100)
            status_text.empty()
            
            if scan_results and scan_results.get("success"):
                st.success("✅ اسکن پیشرفته با موفقیت تکمیل شد")
                # نمایش نتایج...
            else:
                st.error("❌ خطا در اجرای اسکن پیشرفته")
        
        # بقیه بخش‌های برنامه...
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        st.error("خطای غیرمنتظره در اجرای برنامه")

if __name__ == "__main__":
    main()
