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
    MIDDLEWARE_BASE_URL = "https://server-test-ovta.onrender.com"
    
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

# ==================== SECTION 3: NOTIFICATION MANAGER ====================
class NotificationManager:
    """مدیریت نوتیفیکیشن‌های هوشمند"""
    
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
            if notification_id in self.notification_timers:
                self.notification_timers[notification_id].cancel()
                del self.notification_timers[notification_id]
            
            self.notifications = [n for n in self.notifications if n["id"] != notification_id]
    
    def get_visible_notifications(self):
        """دریافت نوتیفیکیشن‌های قابل نمایش"""
        with self.lock:
            return [n for n in self.notifications if n["visible"]]
    
    def clear_all_notifications(self):
        """پاک کردن تمام نوتیفیکیشن‌ها"""
        with self.lock:
            for timer in self.notification_timers.values():
                timer.cancel()
            self.notification_timers.clear()
            self.notifications.clear()
    
    def should_show_notification(self, message: str, level: str) -> bool:
        """بررسی آیا باید نوتیفیکیشن نمایش داده شود"""
        with self.lock:
            if level in ["error", "warning"]:
                return True
            
            recent_threshold = datetime.now() - timedelta(minutes=5)
            recent_notifications = [
                n for n in self.notification_history[level] 
                if n["timestamp"] > recent_threshold and n["message"] == message
            ]
            
            return len(recent_notifications) == 0

# ==================== SECTION 4: MIDDLEWARE CLIENT ====================
class MiddlewareAPIClient:
    """API Client برای ارتباط با سرور میانی"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
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
    
    def get_scan_data(self, limit: int = 100, filter_type: str = "volume") -> Optional[Dict]:
        """دریافت داده‌های اسکن از سرور میانی"""
        try:
            url = f"{self.base_url}/scan-all"
            params = {
                "limit": limit,
                "filter": filter_type
            }
            
            logger.info(f"🌐 دریافت داده از: {url}")
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ داده دریافت شد: {len(data.get('scan_results', []))} ارز")
                return data
            else:
                logger.error(f"❌ خطا: کد {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ خطا در دریافت داده: {str(e)}")
            return None
    
    def get_coin_data(self, coin_id: str) -> Optional[Dict]:
        """دریافت داده‌های یک ارز خاص"""
        try:
            scan_data = self.get_scan_data(limit=50)
            if not scan_data or 'scan_results' not in scan_data:
                return None
            
            coins = scan_data.get('scan_results', [])
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

    @staticmethod
    def generate_sample_market_data(symbol: str) -> Dict:
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
            'name': symbol.capitalize().replace('-', ' '),
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
    
    @staticmethod
    def generate_sample_historical_data(period: str = "24h") -> pd.DataFrame:
        """ایجاد داده‌های تاریخی نمونه"""
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
            
            data.append({
                'time': time_point,
                'open': current_price * (1 + np.random.uniform(-0.005, 0.005)),
                'high': current_price * (1 + np.random.uniform(0, 0.015)),
                'low': current_price * (1 - np.random.uniform(0, 0.015)),
                'close': current_price,
                'volume': np.random.uniform(1000000, 50000000)
            })
        
        return pd.DataFrame(data)

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

# ==================== SECTION 9: MARKET SCANNER (کامل) ====================
class MarketScanner:
    """اپلیکیشن اصلی اسکنر بازار"""
    
    def __init__(self):
        self.config = Config()
        self.notification_manager = NotificationManager()
        self.api_client = MiddlewareAPIClient(self.config.MIDDLEWARE_BASE_URL)
        self.data_manager = DataManager()
        self.technical_analyzer = TechnicalAnalyzer()
        self.chart_renderer = ChartRenderer()
        self.portfolio_manager = PortfolioManager(self.data_manager)
        self.last_scan_time = None
        self.scan_cache = {}
    
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
            logger.info(f"🌐 ارسال درخواست اسکن پیشرفته: {url}")
            
            response = requests.get(url, params=params, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ اسکن با فیلتر {filter_type} تکمیل شد")
                
                self.notification_manager.add_notification(
                    f"اسکن {data.get('total_coins', 0)} ارز با موفقیت انجام شد",
                    "success",
                    auto_hide=True,
                    duration=5
                )
                
                return data
            else:
                error_msg = f"خطای سرور: کد {response.status_code}"
                logger.error(error_msg)
                
                self.notification_manager.add_notification(
                    error_msg,
                    "error",
                    auto_hide=False
                )
                
                return None
                
        except Exception as e:
            error_msg = f"خطا در اسکن: {str(e)}"
            logger.error(error_msg)
            
            self.notification_manager.add_notification(
                error_msg,
                "error",
                auto_hide=False
            )
            
            return None
    
    def get_market_data(self, symbol: str) -> Dict:
        """دریافت داده‌های بازار"""
        try:
            if self.api_client.is_healthy:
                coin_data = self.api_client.get_coin_data(symbol)
                if coin_data:
                    return coin_data
            
            return self.data_manager.generate_sample_market_data(symbol)
            
        except Exception as e:
            logger.error(f"خطا در دریافت داده بازار: {e}")
            return self.data_manager.generate_sample_market_data(symbol)
    
    def get_historical_data(self, symbol: str, period: str) -> pd.DataFrame:
        """دریافت داده‌های تاریخی"""
        try:
            # اول از کش بخوان
            cached_data = self.data_manager.load_price_data(symbol, period)
            if cached_data is not None:
                return cached_data
            
            # اگر کش نبود، نمونه ایجاد کن
            df = self.data_manager.generate_sample_historical_data(period)
            df = self.technical_analyzer.calculate_indicators(df)
            
            # در کش ذخیره کن
            self.data_manager.save_price_data(symbol, period, df)
            
            return df
        except Exception as e:
            logger.error(f"خطا در ایجاد داده تاریخی: {e}")
            return pd.DataFrame()
    
    def run_analysis(self, symbol: str, period: str) -> Optional[Dict]:
        """اجرای تحلیل کامل"""
        try:
            # دریافت داده‌های بازار
            market_data = self.get_market_data(symbol)
            current_price = market_data.get('price', 0)
            
            # دریافت داده‌های تاریخی
            historical_data = self.get_historical_data(symbol, period)
            if historical_data.empty:
                return None
            
            # تولید سیگنال‌ها
            signals = self.technical_analyzer.generate_signals({
                'rsi': historical_data['RSI'].iloc[-1] if 'RSI' in historical_data.columns else 50,
                'macd': historical_data['MACD'].iloc[-1] if 'MACD' in historical_data.columns else 0,
                'macd_signal': historical_data['MACD_Signal'].iloc[-1] if 'MACD_Signal' in historical_data.columns else 0,
                'macd_histogram': historical_data['MACD_Histogram'].iloc[-1] if 'MACD_Histogram' in historical_data.columns else 0,
                'sma_20': historical_data['SMA_20'].iloc[-1] if 'SMA_20' in historical_data.columns else current_price,
                'sma_50': historical_data['SMA_50'].iloc[-1] if 'SMA_50' in historical_data.columns else current_price,
                'current_price': current_price
            })
            
            return {
                'symbol': symbol,
                'period': period,
                'market_data': market_data,
                'historical_data': historical_data,
                'signals': signals,
                'recommendations': self.technical_analyzer.generate_recommendations(signals, {
                    'current_price': current_price,
                    'rsi': historical_data['RSI'].iloc[-1] if 'RSI' in historical_data.columns else 50,
                    'macd_histogram': historical_data['MACD_Histogram'].iloc[-1] if 'MACD_Histogram' in historical_data.columns else 0
                })
            }
            
        except Exception as e:
            logger.error(f"خطا در تحلیل {symbol}: {e}")
            return None

# ==================== SECTION 10: STREAMLIT UI COMPONENTS (کامل) ====================
class StreamlitUI:
    """کامپوننت‌های رابط کاربری Streamlit"""
    
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
    
    @staticmethod
    def setup_sidebar(scanner, T: Dict) -> Tuple[str, str, bool, bool, bool, bool, Dict]:
        """Setup sidebar controls with enhanced persistence"""
    
        if 'sidebar_state' not in st.session_state:
            st.session_state.sidebar_state = {
                'language': "فارسی",
                'symbol': Config.SYMBOLS[0],
                'period': list(Config.PERIODS.keys())[0],
                'show_charts': True,
                'show_analysis': True,
                'show_portfolio': False
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
    
        if scanner and hasattr(scanner, 'api_client') and scanner.api_client is not None:
            if hasattr(scanner.api_client, 'is_healthy'):
                api_healthy = scanner.api_client.is_healthy
            if hasattr(scanner.api_client, 'last_error'):
                last_error = scanner.api_client.last_error
    
        if api_healthy:
            st.sidebar.success("✅ سرور میانی متصل")
        else:
            st.sidebar.error("❌ سرور میانی قطع")
            if last_error:
                with st.sidebar.expander("جزئیات خطا"):
                    st.error(last_error)
    
        if st.sidebar.button("🔄 بررسی سلامت سرور", use_container_width=True):
            if scanner and hasattr(scanner, 'api_client') and scanner.api_client is not None:
                scanner.api_client._check_health()
                st.rerun()
    
        scan_all = st.sidebar.button(T["scan_all"], use_container_width=True)
    
        return symbol, period, show_charts, show_analysis, show_portfolio, scan_all, T

    @staticmethod
    def setup_advanced_scan_controls(scanner, T: Dict) -> Dict:
        """کنترل‌های پیشرفته اسکن"""
        st.sidebar.header("🎛️ کنترل‌های پیشرفته اسکن")
        
        scan_limit = st.sidebar.selectbox(
            "تعداد ارزها برای اسکن",
            options=[100, 500, 1000],
            index=0
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
            }.get(x, x)
        )
        
        custom_filters = {}
        with st.sidebar.expander("⚙️ فیلترهای سفارشی (اختیاری)"):
            min_volume = st.number_input("حداقل حجم (USD)", min_value=0, value=1000000)
            max_volume = st.number_input("حداکثر حجم (USD)", min_value=0, value=1000000000)
            
            if min_volume > 0:
                custom_filters["min_volume"] = min_volume
            if max_volume > 0:
                custom_filters["max_volume"] = max_volume
        
        advanced_scan = st.sidebar.button("🚀 اجرای اسکن پیشرفته", use_container_width=True)
        
        return {
            "scan_limit": scan_limit,
            "filter_type": filter_type,
            "custom_filters": custom_filters if custom_filters else None,
            "advanced_scan": advanced_scan
        }

    @staticmethod
    def display_market_overview(market_data: Dict, T: Dict):
        """Display market overview cards"""
        if not market_data:
            st.warning(T["no_data"])
            return
        
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

    @staticmethod
    def display_technical_analysis(analysis: Dict, T: Dict):
        """Display technical analysis dashboard"""
        if not analysis:
            st.warning("تحلیل تکنیکال در دسترس نیست")
            return
        
        st.header("📊 دیشبورد تحلیل تکنیکال")
        
        indicators = analysis.get('indicators', {})
        signals = analysis.get('signals', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            rsi = indicators.get('rsi', 50)
            if rsi < 30:
                st.error(f"RSI: {rsi:.1f} (اشباع فروش)")
            elif rsi > 70:
                st.warning(f"RSI: {rsi:.1f} (اشباع خرید)")
            else:
                st.success(f"RSI: {rsi:.1f} (نرمال)")
        
        with col2:
            trend = signals.get('trend', 'neutral')
            if 'bullish' in trend:
                st.success(f"روند: {trend}")
            else:
                st.error(f"روند: {trend}")
        
        with col3:
            price = indicators.get('current_price', 0)
            st.metric("قیمت فعلی", f"${price:,.2f}")
        
        with col4:
            sma_20 = indicators.get('sma_20', price)
            status = "بالاتر از SMA20" if price > sma_20 else "پایین‌تر از SMA20"
            st.metric("موقعیت قیمت", status)
        
        # توصیه‌ها
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            st.subheader("💡 توصیه‌های معاملاتی")
            for rec in recommendations:
                st.write(f"• {rec}")

    @staticmethod
    def display_charts(analysis: Dict, T: Dict):
        """Display price and indicator charts"""
        if not analysis or 'historical_data' not in analysis:
            st.warning("نمودارها در دسترس نیستند")
            return
        
        historical_data = analysis['historical_data']
        symbol = analysis.get('symbol', '')
        period = analysis.get('period', '')
        
        # Price chart
        st.subheader(T["price_chart"])
        fig_price = ChartRenderer.render_price_chart(historical_data, symbol, period, T["price_chart"])
        st.plotly_chart(fig_price, use_container_width=True)
        
        # Technical indicators
        st.subheader(T["indicators"])
        fig_rsi, fig_macd = ChartRenderer.render_technical_indicators(historical_data)
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_rsi, use_container_width=True)
        with col2:
            st.plotly_chart(fig_macd, use_container_width=True)

    @staticmethod
    def display_portfolio(scanner, T: Dict):
        """Display portfolio tracker"""
        st.header("💼 ردیابی پرتفوی")
        
        # فرم افزودن دارایی
        with st.form("add_asset"):
            col1, col2, col3 = st.columns(3)
            with col1:
                symbol = st.selectbox("نماد", Config.SYMBOLS)
            with col2:
                quantity = st.number_input("مقدار", min_value=0.0, value=1.0)
            with col3:
                buy_price = st.number_input("قیمت خرید (USD)", min_value=0.0, value=1000.0)
            
            notes = st.text_input("یادداشت (اختیاری)")
            
            if st.form_submit_button("➕ افزودن به پرتفوی"):
                if scanner.portfolio_manager.add_to_portfolio(symbol, quantity, buy_price, notes):
                    st.success("✅ دارایی به پرتفوی اضافه شد")
        
        # نمایش پرتفوی
        portfolio_value = scanner.portfolio_manager.get_portfolio_value(scanner.api_client)
        if portfolio_value['assets']:
            st.subheader("📋 دارایی‌های شما")
            for asset in portfolio_value['assets']:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"**{asset['symbol']}**")
                with col2:
                    st.write(f"مقدار: {asset['quantity']}")
                with col3:
                    st.write(f"سود/زیان: {asset['pnl_percent']:+.2f}%")
                with col4:
                    st.write(f"ارزش فعلی: ${asset['current_value']:,.2f}")

# ==================== MAIN APPLICATION ====================
def main():
    """تابع اصلی برنامه"""
    logger.info("Starting CoinState Market Scanner Pro")
    
    try:
        # ایجاد اسکنر
        scanner = MarketScanner()
        ui = StreamlitUI()
        
        # عنوان برنامه
        st.title("📊 اسکنر بازار CoinState Pro")
        
        # نمایش نوتیفیکیشن‌ها
        ui.display_notifications(scanner.notification_manager)
        
        # تنظیمات سایدبار
        symbol, period, show_charts, show_analysis, show_portfolio, scan_all, T = ui.setup_sidebar(scanner, TranslationManager.get_text("فارسی"))
        
        # کنترل‌های پیشرفته
        scan_controls = ui.setup_advanced_scan_controls(scanner, T)
        
        # اسکن پیشرفته
        if scan_controls["advanced_scan"]:
            st.info(f"🌐 اسکن پیشرفته در حال اجرا...")
            with st.spinner("در حال اسکن بازار با فیلترهای پیشرفته..."):
                scan_results = scanner.scan_with_filters(
                    limit=scan_controls["scan_limit"],
                    filter_type=scan_controls["filter_type"],
                    custom_filters=scan_controls["custom_filters"]
                )
            
            if scan_results:
                st.success("✅ اسکن پیشرفته تکمیل شد")
        
        # دریافت و نمایش داده‌ها
        with st.spinner(T["loading"]):
            analysis = scanner.run_analysis(symbol, period)
        
        if analysis:
            # نمایش خلاصه بازار
            ui.display_market_overview(analysis['market_data'], T)
            
            st.markdown("---")
            
            # نمایش تحلیل تکنیکال
            if show_analysis:
                ui.display_technical_analysis(analysis, T)
                st.markdown("---")
            
            # نمایش نمودارها
            if show_charts:
                ui.display_charts(analysis, T)
                st.markdown("---")
        
        # نمایش پرتفوی
        if show_portfolio:
            ui.display_portfolio(scanner, T)
        
        # پاورقی
        st.markdown("---")
        st.markdown("**CoinState Scanner Pro** • توسعه داده شده با Streamlit")
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("خطای غیرمنتظره در اجرای برنامه")

if __name__ == "__main__":
    main()
