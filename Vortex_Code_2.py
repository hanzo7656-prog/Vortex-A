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
    COINSTATE_BASE_URL = "https://crypto-scanner-backend.onrender.com/api"
    
    SYMBOLS = [
        "bitcoin", "ethereum", "binancecoin", "cardano", "ripple", "solana",
        "polkadot", "dogecoin", "avalanche", "matic-network", "litecoin", "cosmos"
    ]
    
    PERIODS = {
        "24h": "24 ساعت", "1w": "1 هفته", "1m": "1 ماه", "3m": "3 ماه",
        "6m": "6 ماه", "1y": "1 سال", "all": "همه زمان"
    }
    
    PERIOD_MAPPING = {
        "24h": "24h", "1w": "1w", "1m": "1m", "3m": "3m",
        "6m": "6m", "1y": "1y", "all": "all"
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

# ==================== SECTION 3: API CLIENT ====================
class CoinStateAPIClient:
    """Enhanced API client for CoinState with better error handling"""
    
    def __init__(self, base-url: str):
        self.base_url = base_url
        self.session = requests.session()
        self.is_healthy = True
        self.last_error = None
        self.last_check = None  # اضافه کردن این خطا
        self._check_health()  # بررسی سلامت هنگام راه‌اندازی

    def get_realtime_data(self, coin_id: str) -> Optional[Dict]:
        try:
            # دریافت داده از سرور میانی شما
            url = f"{self.base_url}/coins"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                # پیدا کردن ارز مورد نظر در لیست
                coins = data.get('coins', [])
                for coin in coins:
                    if (coin.get('id') == coin_id or 
                        coin.get('name', '').lower() == coin_id.lower() or
                        coin.get('symbol', '').lower() == coin_id.lower()):
                        return coin
                return None
            return None
        except Exception as e:
            logger.error(f"Error fetching from middleware: {str(e)}")
            return None
            
    def _check_health(self):
        """Check if API is healthy"""
        try:
            test_url = f"{self.base_url}/coins/bitcoin"
            response = self.session.get(test_url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                self.is_healthy = True
                self.last_error = None
                self.last_check = datetime.now()
                logger.info("✅ API health check passed")
            elif response.status_code == 401:
                self.is_healthy = False
                self.last_error = "API Key نامعتبر یا منقضی شده"
                logger.error("❌ API Key authentication failed")
            elif response.status_code == 403:
                self.is_healthy = False
                self.last_error = "دسترسی غیرمجاز - ممکن است IP محدود شده باشد"
                logger.error("❌ API access forbidden")
            elif response.status_code == 429:
                self.is_healthy = False
                self.last_error = "محدودیت تعداد درخواست - لطفا کمی صبر کنید"
                logger.error("❌ API rate limit exceeded")
            else:
                self.is_healthy = False
                self.last_error = f"خطای سرور: کد {response.status_code}"
                logger.error(f"❌ API error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.is_healthy = False
            self.last_error = "اتصال timeout شد - سرور پاسخ نمی‌دهد"
            logger.error("❌ API connection timeout")
        except requests.exceptions.ConnectionError:
            self.is_healthy = False
            self.last_error = "خطای اتصال - اینترنت یا DNS مشکل دارد"
            logger.error("❌ API connection error")
        except Exception as e:
            self.is_healthy = False
            self.last_error = f"خطای ناشناخته: {str(e)}"
            logger.error(f"❌ Unknown API error: {str(e)}")
            
    def _create_session(self) -> requests.Session:
        """Create session with retry strategy"""
        session = requests.Session()
        retry_strategy = requests.packages.urllib3.util.Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session
    
    def _get_headers(self) -> Dict:
        return {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
    
    def get_realtime_data(self, coin_id: str) -> Optional[Dict]:
        """Get real-time data for a specific coin"""
        try:
            url = f"{self.base_url}/coins/{coin_id}"
            response = self.session.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API Error: {response.status_code} for {coin_id}")
                return None
                
        except Exception as e:
            logger.error(f"Connection error for {coin_id}: {str(e)}")
            return None
    
    def get_historical_data(self, coin_id: str, period: str) -> Optional[pd.DataFrame]:
        """Get historical data with improved error handling"""
        try:
            url = f"{self.base_url}/coins/charts"
            api_period = Config.PERIOD_MAPPING.get(period, "24h")
            
            params = {"period": api_period, "coinIds": coin_id}
            response = self.session.get(url, params=params, headers=self._get_headers(), timeout=15)
            
            if response.status_code == 200:
                return self._process_historical_data(response.json(), coin_id, period)
            else:
                logger.warning(f"Using sample data for {coin_id} - API status: {response.status_code}")
                return self._generate_sample_data(period)
                
        except Exception as e:
            logger.error(f"Historical data error for {coin_id}: {str(e)}")
            return self._generate_sample_data(period)
    
    def _process_historical_data(self, data: Dict, coin_id: str, period: str) -> pd.DataFrame:
        """Process historical data from API response"""
        if not data or not isinstance(data, list):
            return self._generate_sample_data(period)
        
        coin_data = data[0]
        if coin_data.get('errorMessage'):
            logger.warning(f"API error for {coin_id}: {coin_data['errorMessage']}")
            return self._generate_sample_data(period)
        
        chart_data = coin_data.get('chart', [])
        processed_data = []
        
        for point in chart_data:
            if isinstance(point, list) and len(point) >= 4:
                processed_data.append({
                    'time': pd.to_datetime(point[0], unit='s'),
                    'price': point[1]
                })
        
        if processed_data:
            df = pd.DataFrame(processed_data)
            df = df.drop_duplicates(subset=['time']).sort_values('time')
            return self._create_ohlc_data(df, period)
        
        return self._generate_sample_data(period)
    
    def _create_ohlc_data(self, price_df: pd.DataFrame, period: str) -> pd.DataFrame:
        """Create OHLC data from price data"""
        if price_df.empty:
            return self._generate_sample_data(period)
        
        # Determine resampling frequency based on period
        freq_map = {
            "24h": '1H', "1w": '4H', "1m": '1D', 
            "3m": '1D', "6m": '1D', "1y": '1D', "all": '1W'
        }
        freq = freq_map.get(period, '1D')
        
        try:
            price_df = price_df.set_index('time')
            resampled = price_df['price'].resample(freq)
            
            ohlc_data = resampled.agg({
                'open': 'first',
                'high': 'max', 
                'low': 'min',
                'close': 'last'
            }).dropna()
            
            # Add realistic volume data
            ohlc_data['volume'] = (ohlc_data['close'] * 
                                 np.random.uniform(1000, 10000, len(ohlc_data)))
            
            return ohlc_data.reset_index()
            
        except Exception as e:
            logger.error(f"OHLC creation error: {str(e)}")
            return self._generate_sample_data(period)
    
    def _generate_sample_data(self, period: str) -> pd.DataFrame:
        """Generate realistic sample data when API fails"""
        period_points = {
            "24h": 24, "1w": 42, "1m": 30, "3m": 90,
            "6m": 180, "1y": 365, "all": 100
        }
        
        count = period_points.get(period, 100)
        base_price = 50000
        times = [datetime.now() - timedelta(hours=i) for i in range(count)][::-1]
        
        data = []
        current_price = base_price
        
        for i in range(count):
            change = current_price * 0.02 * np.random.randn()
            current_price = max(current_price + change, base_price * 0.5)
            
            data.append({
                'time': times[i],
                'open': current_price * (1 + np.random.uniform(-0.01, 0.01)),
                'high': current_price * (1 + np.random.uniform(0, 0.02)),
                'low': current_price * (1 - np.random.uniform(0, 0.02)),
                'close': current_price,
                'volume': np.random.uniform(1000000, 5000000)
            })
        
        return pd.DataFrame(data)

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
    
    def get_portfolio_value(self, api_client: CoinStateAPIClient) -> Dict:
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
                current_data = api_client.get_realtime_data(asset['symbol'])
                current_price = current_data.get('price', 0) if current_data else 0
                
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

# ==================== SECTION 8: MARKET SCANNER ====================
class MarketScanner:
    """Main market scanner application"""
    
    def __init__(self):
        self.config = Config()
        try:
            # ایجاد API Client با مدیریت خطا
            self.api_client = CoinStateAPIClient(self.config.COINSTATE_BASE_URL)
            logger.info("API Client created successfully")
        except Exception as e:
            logger.error(f"Error creating API client: {e}")
            # اگر API client ساخته نشد، یک نمونه خالی ایجاد می‌کنیم
            self.api_client = None
        
        self.data_manager = DataManager()
        self.technical_analyzer = TechnicalAnalyzer()
        self.chart_renderer = ChartRenderer()
        self.portfolio_manager = PortfolioManager(self.data_manager)
    
    def _generate_sample_data(self, period: str) -> pd.DataFrame:
        """Generate sample data when API is not available"""
        period_points = {
            "24h": 24, "1w": 42, "1m": 30, "3m": 90,
            "6m": 180, "1y": 365, "all": 100
        }
        
        count = period_points.get(period, 100)
        base_price = 50000
        times = [datetime.now() - timedelta(hours=i) for i in range(count)][::-1]
        
        data = []
        current_price = base_price
        
        for i in range(count):
            change = current_price * 0.02 * np.random.randn()
            current_price = max(current_price + change, base_price * 0.5)
            
            data.append({
                'time': times[i],
                'open': current_price * (1 + np.random.uniform(-0.01, 0.01)),
                'high': current_price * (1 + np.random.uniform(0, 0.02)),
                'low': current_price * (1 - np.random.uniform(0, 0.02)),
                'close': current_price,
                'volume': np.random.uniform(1000000, 5000000)
            })
        
        return pd.DataFrame(data)
        
    def run_analysis(self, symbol: str, period: str) -> Optional[Dict]:
        """Run complete technical analysis"""
        try:
            # اگر api_client موجود نیست، از تحلیل صرف نظر کن
            if self.api_client is None:
                logger.warning("API client not available, using sample data for analysis")
                historical_data = self._generate_sample_data(period)
            else:
                # Get historical data
                historical_data = self.get_historical_data(symbol, period)
            
            if historical_data is None or historical_data.empty:
                return None
            
            # Calculate indicators
            historical_data = self.technical_analyzer.calculate_indicators(historical_data)
            
            # Get latest values
            last_row = historical_data.iloc[-1]
            indicators = {
                'current_price': last_row.get('close', 0),
                'rsi': last_row.get('RSI', 50),
                'macd': last_row.get('MACD', 0),
                'macd_signal': last_row.get('MACD_Signal', 0),
                'macd_histogram': last_row.get('MACD_Histogram', 0),
                'sma_20': last_row.get('SMA_20', 0),
                'sma_50': last_row.get('SMA_50', 0)
            }
            
            # Generate signals and recommendations
            signals = self.technical_analyzer.generate_signals(indicators)
            recommendations = self.technical_analyzer.generate_recommendations(signals, indicators)
            
            analysis_results = {
                'symbol': symbol,
                'period': period,
                'timestamp': datetime.now(),
                'indicators': indicators,
                'signals': signals,
                'recommendations': recommendations,
                'historical_data': historical_data
            }
            
            # Save to database
            self.data_manager.save_analysis(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Analysis error for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """Get historical data with caching"""
        # Try cache first
        cached_data = self.data_manager.load_price_data(symbol, period)
        if cached_data is not None:
            return cached_data
        
        # Fetch from API
        api_data = self.api_client.get_historical_data(symbol, period)
        if api_data is not None and not api_data.empty:
            self.data_manager.save_price_data(symbol, period, api_data)
        
        return api_data
    
    def scan_all_market(self) -> Dict:
        """Scan entire cryptocurrency market"""
        results = {}
        
        with st.spinner("در حال اسکن تمام بازار..."):
            for symbol in self.config.SYMBOLS[:6]:  # Limit to 6 for performance
                analysis = self.run_analysis(symbol, "24h")
                if analysis:
                    results[symbol] = analysis
                
                time.sleep(0.5)  # Rate limiting
        
        return results
# ==================== SECTION 9: STREAMLIT UI COMPONENTS ====================
class StreamlitUI:
    """Streamlit user interface components"""
    
    @staticmethod
    def setup_sidebar(scanner: MarketScanner, T: Dict) -> Tuple[str, str, bool, bool, bool, bool, Dict]:
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

        st.sidebar.write(f"حالت ذخیره شده: {st.session_state.sidebar_state['symbol']}")
        
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
        
        # API Health Check Section
        st.sidebar.header("🔧 سلامت سرویس")
        
        # API Status Indicator
        if scanner.api_client and scanner.api_client.is_healthy:
            st.sidebar.success("✅ API متصل")
        else:
            st.sidebar.error("❌ API قطع")
            
            if scanner.api_client and scanner.api_client.last_error:
                with st.sidebar.expander("جزئیات خطا"):
                    st.error(scanner.api_client.last_error)
        
        # API Health Check Button
        if st.sidebar.button("🔄 بررسی سلامت API", use_container_width=True):
            with st.sidebar:
                with st.spinner("در حال بررسی..."):
                    if scanner.api_client:
                        scanner.api_client._check_health()
                        st.rerun()
        
        # Advanced API Troubleshooting
        with st.sidebar.expander("عیب‌یابی پیشرفته"):
            if st.button("🔑 تست API Key"):
                StreamlitUI.test_api_key()
            
            if st.button("🌐 تست اتصال اینترنت"):
                StreamlitUI.test_internet_connection()

            if st.button("پاک کردن حافظه موقت"):
                streamlitUI.clear_cache()
                st.rerun()
                
            st.info("""
            **راهنمای عیب‌یابی:**
            - اگر API Key نامعتبر است، از پنل کاربری جدید دریافت کنید
            - اگر اتصال اینترنت مشکل دارد، VPN روشن کنید
            - برای مشکلات فنی با پشتیبانی تماس بگیرید
            """)
        
        scan_all = st.sidebar.button(T["scan_all"], use_container_width=True)
        
        return symbol, period, show_charts, show_analysis, show_portfolio, scan_all, T
    
    @staticmethod
    def test_api_key():
        """Test the current API key"""
        import requests
        
        try:
            url = "https://openapiv1.coinstats.app/coins/bitcoin"
            headers = {"X-API-KEY": Config.COINSTATE_API_KEY}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                st.success("✅ API Key معتبر است")
                data = response.json()
                st.json({
                    "name": data.get('name', 'N/A'),
                    "price": f"${data.get('price', 'N/A'):,.2f}" if data.get('price') else 'N/A',
                    "symbol": data.get('symbol', 'N/A'),
                    "change_24h": f"{data.get('priceChange1h', 'N/A')}%"
                })
            elif response.status_code == 401:
                st.error("❌ API Key نامعتبر است - لطفا کلید جدید دریافت کنید")
            elif response.status_code == 403:
                st.error("❌ دسترسی غیرمجاز - ممکن است IP محدود شده باشد")
            elif response.status_code == 429: 
                st.error("محدودیت تعداد درخواست - لطفا چند دقیقه صبر کنید")
            else:
                st.warning(f"⚠️ پاسخ غیرمنتظره: کد {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ خطای اتصال: {str(e)}")
    
    @staticmethod
    def test_internet_connection():
        """Test internet connection"""
        import requests
        
        try:
            # Test connection to a reliable server
            response = requests.get("https://www.google.com", timeout=5)
            if response.status_code == 200:
                st.success("✅ اتصال اینترنت برقرار است")
            else:
                st.warning("⚠️ اتصال اینترنت مشکل دارد")
        except:
            st.error("❌ اتصال اینترنت قطع است")
            
        try:
            # Test DNS resolution
            import socket
            socket.gethostbyname("openapiv1.coinstats.app")
            st.success("✅ DNS درست کار می‌کند")
        except:
            st.error("❌ مشکل در DNS - سعی کنید از VPN استفاده کنید")

    @staticmethod
    def clear_cache():
        """Clear session cache"""
        keys = list(st.session_state.keys())
        for key in keys:
            if key !='sidebar_state':
                del st.session_state[key]
        st.success("✅️ حافظه موقت پاک شد")
            
    @staticmethod
    def display_market_overview(market_data: Dict, T: Dict):
        """Display market overview cards"""
        if not market_data:
            st.warning(T["no_data"])
            return
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            price = market_data.get('price', 0)
            st.metric(T["price"], f"${price:,.2f}")
        
        with col2:
            change_24h = market_data.get('priceChange24h', 0)
            change_color = "normal" if change_24h >= 0 else "inverse"
            st.metric(T["change"], f"{change_24h:+.2f}%", delta_color=change_color)
        
        with col3:
            high_24h = market_data.get('high24h', price)
            st.metric(T["high"], f"${high_24h:,.2f}")
        
        with col4:
            low_24h = market_data.get('low24h', price)
            st.metric(T["low"], f"${low_24h:,.2f}")
        
        with col5:
            volume = market_data.get('volume', 0)
            st.metric(T["volume"], f"${volume:,.0f}")
    
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
            if rsi < 30:
                st.error(f"RSI: {rsi:.1f} (اشباع فروش)")
            elif rsi > 70:
                st.warning(f"RSI: {rsi:.1f} (اشباع خرید)")
            else:
                st.success(f"RSI: {rsi:.1f} (نرمال)")
        
        with col2:
                trend = analysis['signals'].get('trend', 'neutral')
                trend_icons = {
                    'strong_bullish': '🚀', 'weak_bullish': '📈',
                    'weak_bearish': '📉', 'strong_bearish': '⚠️'
                }
                trend_text = {
                    'strong_bullish': 'صعودی قوی',
                    'weak_bullish': 'صعودی ضعیف',
                    'weak_bearish': 'نزولی ضعیف',
                    'strong_bearish': 'نزولی قوی',
                    'neutral': 'خنثی'
                }
                st.metric("روند بازار", f"{trend_icons.get(trend, '⚪')} {trend}")
        
        with col3:
            macd_signal = analysis['signals'].get('macd', 'neutral')
            if macd_signal == 'bullish':
                st.success("MACD: صعودی")
            elif macd_signal == 'bearish':
                st.error("MACD: نزولی")
            else:
                st.info("MACD: خنثی")
        
        with col4:
            price = analysis['indicators'].get('current_price', 0)
            sma50 = analysis['indicators'].get('sma_50', price)
            status = "بالاتر از SMA50" if price > sma50 else "پایین‌تر از SMA50"
            color = "normal" if price > sma50 else "inverse"
            st.metric("موقعیت قیمت", status, delta_color=color)
        
        # Recommendations
        st.subheader("💡 توصیه‌های معاملاتی")
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                if any(word in rec for word in ['صعودی', 'خرید', 'طلا']):
                    st.success(f"{i}. {rec}")
                elif any(word in rec for word in ['نزولی', 'فروش', 'مرگ', 'احتیاط']):
                    st.error(f"{i}. {rec}")
                else:
                    st.info(f"{i}. {rec}")
        else:
            st.info("توصیه‌ای برای نمایش وجود ندارد")

    @staticmethod
    def display_portfolio(scanner: MarketScanner, T: Dict):
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
                buy_price = st.number_input("قیمت خرید (USD)", min_value=0.0, step=0.01, values=1000.0)
            
            notes = st.text_input("یادداشت (اختیاری)", placeholder="مانند: خرید در کف قیمت")
            
            if st.form_submit_button("➕ افزودن به پرتفوی"):
                if quantity > 0 and buy_price > 0:
                    if scanner.portfolio_manager.add_to_portfolio(symbol, quantity, buy_price, notes):
                        st.success("✅ دارایی به پرتفوی اضافه شد")
                        st.rerun()
                    else:
                        st.error("❌ خطا در افزودن دارایی")
                else:
                    st.warning("مقدار و قیمت باید بزرگترا صفر باشند")
        
        # Portfolio summary
        portfolio_value = scanner.portfolio_manager.get_portfolio_value(scanner.api_client)
        
        if portfolio_value['assets']:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 سرمایه‌گذاری شده", f"${portfolio_value['total_invested']:,.2f}")
            with col2:
                st.metric("💵 ارزش فعلی", f"${portfolio_value['total_current']:,.2f}")
            with col3:
                pnl = portfolio_value['total_pnl']
                pnl_percent = portfolio_value['total_pnl_percent']
                pnl_color = "normal" if portfolio_value['total_pnl'] >= 0 else "inverse"
                st.metric("📊 سود/زیان", f"${pnl:,.2f}", 
                         delta=f"{pnl_percent:+.2f}%",
                         delta_color=pnl_color)
            with clo4:
                if st.button("بروزرسانی قیمت‌ها"):
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
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="portfolio.xlsx">دانلود فایل Excel</a>'
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
            
            fig = go.Figure(data=[go.Pie(labels=symbols, values=values, hole=.3)])
            fig.update_layout(title="توزیع دارایی‌های پرتفوی")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"❌ خطا در ایجاد نمودار: {e}")
            
# ==================== SECTION 10: MAIN APPLICATION ====================
def main():
    """Main application entry point"""
    logger.info("Starting Enhanced CoinState Scanner")
    
    try:
        # Initialize scanner
        scanner = MarketScanner()
        ui = StreamlitUI()
    
        # Setup UI with persistent sidebar
        st.title("📊 اسکنر بازار CoinState Pro")
        
        # Add automatic API status check on startup - با بررسی ایمن
        if hasattr(scanner, 'api_client') and scanner.api_client:
            if hasattr(scanner.api_client, 'last_check'):
                if not scanner.api_client.last_check:
                    scanner.api_client._check_health()
            else:
                # اگر last_check وجود ندارد، باز هم سلامت را بررسی کن
                scanner.api_client._check_health()
        
        # Sidebar controls with persistence
        (symbol, period, show_charts, 
         show_analysis, show_portfolio, scan_all, T) = ui.setup_sidebar(scanner, TranslationManager.get_text("فارسی"))
        
        # نمایش وضعیت API در صفحه اصلی با بررسی ایمن
        if hasattr(scanner, 'api_client') and scanner.api_client:
            if hasattr(scanner.api_client, 'is_healthy'):
                if scanner.api_client.is_healthy:
                    st.success("✅ اتصال به API برقرار است - داده‌های زنده استفاده می‌شوند")
                    
                    # نمایش اطلاعات اضافی درباره API
                    with st.expander("📊 اطلاعات API"):
                        if hasattr(scanner.api_client, 'last_check'):
                            st.write(f"آخرین بررسی: {scanner.api_client.last_check.strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"کلید API: {scanner.api_client.api_key[:10]}...")
                        st.write(f"آدرس سرور: {scanner.api_client.base_url}")
                else:
                    st.warning("⚠️ اتصال به API قطع است - از داده‌های نمونه استفاده می‌شود")
                    
                    if hasattr(scanner.api_client, 'last_error') and scanner.api_client.last_error:
                        st.info(f"علت قطعی: {scanner.api_client.last_error}")
                    
                    # پیشنهادات برای رفع مشکل
                    with st.expander("🛠️ راه‌حل‌های پیشنهادی"):
                        st.markdown("""
                        1. بررسی اتصال اینترنت - از بخش عیب‌یابی سایدبار استفاده کنید
                        2. تست API Key - مطمئن شوید کلید معتبر است
                        3. استفاده از VPN - ممکن است IP شما محدود شده باشد
                        4. بروزرسانی کلید - از پنل کاربری کلید جدید دریافت کنید
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
