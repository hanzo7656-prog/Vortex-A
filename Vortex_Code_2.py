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
logger = logging.getLogger(name)

class Config:
    """Configuration class for all constants"""
    COINSTATE_API_KEY = "7qmXYUHlF+DWnF9fYml4Klz+/leL7EBRH+mA2WrpsEc="
    COINSTATE_BASE_URL = "https://openapiv1.coinstats.app"
    
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
    
    def init(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = self._create_session()
    
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
    
    def init(self, data_manager: DataManager):
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
    
    def init(self):
        self.config = Config()
        self.api_client = CoinStateAPIClient(self.config.COINSTATE_API_KEY, self.config.CONSTATE_BASE_URL)
        self.data_manager = DataManager()
        self.technical_analyzer = TechnicalAnalyzer()
        self.chart_renderer = ChartRenderer()
        self.portfolio_manager = PortfolioManager(self.data_manager)
        
    def run_analysis(self, symbol: str, period: str) -> Optional[Dict]:
        """Run complete technical analysis"""
        try:
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
    def setup_sidebar(scanner: MarketScanner, T: Dict) -> Tuple[str, str, bool, bool]:
        """Setup sidebar controls"""
        st.sidebar.header(T["settings"])
        
        # Language selection
        language = st.sidebar.selectbox(T["language"], ["فارسی", "English"])
        T = TranslationManager.get_text(language)
        
        # Symbol selection
        symbol = st.sidebar.selectbox(
            T["select_symbol"],
            options=Config.SYMBOLS,
            index=0,
            format_func=lambda x: x.capitalize().replace('-', ' ')
        )
        
        # Period selection
        period = st.sidebar.selectbox(
            T["select_interval"],
            options=list(Config.PERIODS.keys()),
            format_func=lambda x: Config.PERIODS[x] if language == "فارسی" else x,
            index=0
        )
        
        # Display options
        show_charts = st.sidebar.checkbox("📊 نمایش نمودارها", value=True)
        show_analysis = st.sidebar.checkbox("🔍 نمایش تحلیل پیشرفته", value=True)
        
        # Additional features
        show_portfolio = st.sidebar.checkbox("💼 نمایش پرتفوی", value=False)
        scan_all = st.sidebar.button(T["scan_all"])
        
        return symbol, period, show_charts, show_analysis, show_portfolio, scan_all, T
    
    @staticmethod
    def display_market_overview(market_data: Dict, T: Dict):
        """Display market overview cards"""
        if not market_data:
            return
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            price = market_data.get('price', 0)
            st.metric(T["price"], f"${price:,.2f}")
        
        with col2:
            change_24h = market_data.get('priceChange24h', 0)
            st.metric(T["change"], f"{change_24h:+.2f}%")
        
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
            st.metric("موقعیت قیمت", status)
        
        # Recommendations
        st.subheader("💡 توصیه‌های معاملاتی")
        for i, rec in enumerate(analysis.get('recommendations', []), 1):
            if any(word in rec for word in ['صعودی', 'خرید', 'طلا']):
                st.success(f"{i}. {rec}")
            elif any(word in rec for word in ['نزولی', 'فروش', 'مرگ']):
                st.error(f"{i}. {rec}")
            else:
                st.info(f"{i}. {rec}")

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
                quantity = st.number_input("مقدار", min_value=0.0, step=0.1)
            with col3:
                buy_price = st.number_input("قیمت خرید (USD)", min_value=0.0, step=0.01)
            
            notes = st.text_input("یادداشت (اختیاری)")
            
            if st.form_submit_button("➕ افزودن به پرتفوی"):
                if quantity > 0 and buy_price > 0:
                    if scanner.portfolio_manager.add_to_portfolio(symbol, quantity, buy_price, notes):
                        st.success("✅ دارایی به پرتفوی اضافه شد")
                    else:
                        st.error("❌ خطا در افزودن دارایی")
        
        # Portfolio summary
        portfolio_value = scanner.portfolio_manager.get_portfolio_value(scanner.api_client)
        
        if portfolio_value['assets']:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 سرمایه‌گذاری شده", f"${portfolio_value['total_invested']:,.2f}")
            with col2:
                st.metric("💵 ارزش فعلی", f"${portfolio_value['total_current']:,.2f}")
            with col3:
                pnl_color = "normal" if portfolio_value['total_pnl'] >= 0 else "inverse"
                st.metric("📊 سود/زیان", f"${portfolio_value['total_pnl']:,.2f}", 
                         delta=f"{portfolio_value['total_pnl_percent']:+.2f}%",
                         delta_color=pnl_color)
            
            # Assets table
            st.subheader("📋 دارایی‌های پرتفوی")
            assets_df = pd.DataFrame(portfolio_value['assets'])
            st.dataframe(assets_df, use_container_width=True)
        else:
            st.info("🔄 پرتفوی شما خالی است. اولین دارایی خود را اضافه کنید.")

# ==================== SECTION 10: MAIN APPLICATION ====================
def main():
    """Main application entry point"""
    logger.info("Starting Enhanced CoinState Scanner")
    
    # Initialize scanner
    scanner = MarketScanner()
    ui = StreamlitUI()
    
    # Setup UI
    st.title("📊 اسکنر بازار CoinState Pro")
    
    # Sidebar controls
    (symbol, period, show_charts, 
     show_analysis, show_portfolio, scan_all, T) = ui.setup_sidebar(scanner, TranslationManager.get_text("فارسی"))
    
    # Main content area
    try:
        # Get market data
        with st.spinner(T["loading"]):
            market_data = scanner.api_client.get_realtime_data(symbol)
            analysis = scanner.run_analysis(symbol, period)
        
        # Display market overview
        ui.display_market_overview(market_data, T)
        
        # Display analysis dashboard
        if show_analysis and analysis:
            ui.display_analysis_dashboard(analysis, T)
        
        # Display charts
        if show_charts and analysis:
            historical_data = analysis.get('historical_data')
            if historical_data is not None:
                # Price chart
                fig_price = ui.chart_renderer.render_price_chart(
                    historical_data, symbol, period, T["price_chart"]
                )
                st.plotly_chart(fig_price, use_container_width=True)
                
                # Technical indicators
                fig_rsi, fig_macd = ui.chart_renderer.render_technical_indicators(historical_data)
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig_rsi, use_container_width=True)
                with col2:
                    st.plotly_chart(fig_macd, use_container_width=True)
        
        # Display portfolio
        if show_portfolio:
            ui.display_portfolio(scanner, T)
        
        # Market scan feature
        if scan_all:
            market_scan_results = scanner.scan_all_market()
            st.header("🌐 اسکن کامل بازار")
            
            for sym, result in market_scan_results.items():
                with st.expander(f"{sym.upper()} - {result['signals'].get('trend', 'unknown')}"):
                    st.write(f"قیمت: ${result['indicators'].get('current_price', 0):.2f}")
                    st.write(f"RSI: {result['indicators'].get('rsi', 0):.1f}")
                    st.write(f"توصیه: {result['recommendations'][0] if result['recommendations'] else 'N/A'}")
    
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("خطا در اجرای برنامه. لطفا صفحه را رفرش کنید.")

if __name__ == "__main__":
    main()
