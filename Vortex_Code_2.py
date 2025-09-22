import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests 
import numpy as np
from datetime import datetime, timedelta
import json
import time
import logging
import random
import sqlite3
import base64

# ==================== تنظیمات اولیه ====================
st.set_page_config(
    page_title="CoinState Market Scanner Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== دیکشنری دو زبانه ====================
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
        "api_health": "بررسی سلامت API"
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
        "api_health": "Check API Health"
    }
}

# ==================== تنظیمات CoinState API ====================
COINSTATE_API_KEY = "7qmXYUHlF+DWnF9fYml4Klz+/leL7EBRH+mA2WrpsEc="
COINSTATE_BASE_URL = "https://openapiv1.coinstats.app"

# ==================== نمادهای معاملاتی ====================
SYMBOLS = [
    "bitcoin", "ethereum", "binancecoin", 
    "cardano", "ripple", "solana",
    "polkadot", "dogecoin", "avalanche",
    "matic-network", "litecoin", "cosmos"
]

# ==================== تایم‌فریم‌ها (Periods) ====================
PERIODS = {
    "24h": "24 ساعت",
    "1w": "1 هفته", 
    "1m": "1 ماه",
    "3m": "3 ماه",
    "6m": "6 ماه",
    "1y": "1 سال",
    "all": "همه زمان"
}

# دوره‌های معادل برای API (بر اساس مستندات)
PERIOD_MAPPING = {
    "24h": "24h",
    "1w": "1w", 
    "1m": "1m",
    "3m": "3m",
    "6m": "6m",
    "1y": "1y",
    "all": "all"
}

# ==================== توابع کمکی ====================
def create_session():
    """ایجاد یک session با قابلیت retry برای درخواست‌های API"""
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

def format_number(num):
    """فرمت اعداد به صورت خوانا"""
    if num is None or pd.isna(num):
        return "N/A"
    try:
        num = float(num)
        if num >= 1_000_000:
            return f"{num/1_000_000:.2f}M"
        elif num >= 1_000:
            return f"{num/1_000:.2f}K"
        else:
            return f"{num:.2f}"
    except (ValueError, TypeError):
        return "N/A"

def format_currency(num):
    """فرمت ارز"""
    if num is None or pd.isna(num):
        return "N/A"
    try:
        return f"${float(num):,.2f}"
    except (ValueError, TypeError):
        return "N/A"

def format_percentage(num):
    """فرمت درصد"""
    if num is None or pd.isna(num):
        return "N/A"
    try:
        return f"{float(num):+.2f}%"
    except (ValueError, TypeError):
        return "N/A"

def get_coinstate_headers():
    """تهیه هدرهای مورد نیاز برای درخواست‌های CoinState"""
    return {
        "X-API-KEY": COINSTATE_API_KEY,
        "Content-Type": "application/json"
    }

def check_api_health():
    """بررسی سلامت CoinState API"""
    try:
        url = f"{COINSTATE_BASE_URL}/coins/bitcoin"
        headers = get_coinstate_headers()
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return True, "CoinState API در دسترس است"
        else:
            return False, f"CoinState API پاسخ نمی‌دهد. کد وضعیت: {response.status_code}"
    except Exception as e:
        return False, f"خطای اتصال به CoinState API: {str(e)}"

# ==================== توابع CoinState API ====================
@st.cache_data(ttl=30, show_spinner=False)
def get_coinstate_realtime_data(coin_id="bitcoin"):
    """دریافت داده‌های لحظه‌ای از CoinState API"""
    try:
        url = f"{COINSTATE_BASE_URL}/coins/{coin_id}"
        headers = get_coinstate_headers()
        
        session = create_session()
        response = session.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            st.error(f"خطا در دریافت داده از CoinState: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"خطا در اتصال به CoinState API: {str(e)}")
        return None

@st.cache_data(ttl=300, show_spinner=False)
def get_coinstate_historical_data(coin_id="bitcoin", period="24h"):
    """دریافت داده‌های تاریخی از CoinState API بر اساس مستندات واقعی"""
    try:
        url = f"{COINSTATE_BASE_URL}/coins/charts"
        
        # استفاده از period mapping بر اساس مستندات
        api_period = PERIOD_MAPPING.get(period, "24h")
        
        params = {
            "period": api_period,
            "coinIds": coin_id
        }
        
        headers = get_coinstate_headers()
        
        session = create_session()
        response = session.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # پردازش داده‌های دریافتی بر اساس فرمت واقعی CoinState API
            if isinstance(data, list) and len(data) > 0:
                coin_data = data[0]  # اولین کوین در لیست
                
                # بررسی خطا برای این کوین
                if coin_data.get('errorMessage'):
                    st.warning(f"خطا برای {coin_id}: {coin_data['errorMessage']}")
                    return generate_sample_ohlc_data(period)  # استفاده از داده‌های OHLC نمونه بهبود یافته
                
                chart_data = coin_data.get('chart', [])
                df_data = []
                
                for point in chart_data:
                    if isinstance(point, list) and len(point) >= 2:
                        timestamp = point[0]  # تایم‌استمپ به ثانیه
                        price_usd = point[1]  # قیمت به USD

                        df_data.append({
                            'time': pd.to_datetime(timestamp, unit='s'),
                            'price': price_usd
                        })
                
                if df_data:
                    df = pd.DataFrame(df_data)
                    df = df.drop_duplicates(subset=['time']).sort_values('time')
                    
                    # ایجاد داده‌های OHLC واقعی‌تر از داده‌های قیمت
                    return create_ohlc_from_price_data(df, period)
        
        # اگر داده‌ای دریافت نشد
        st.warning(f"داده‌های تاریخی برای {coin_id} دریافت نشد (کد: {response.status_code})")
        return generate_sample_ohlc_data(period)
        
    except Exception as e:
        st.error(f"خطا در دریافت داده تاریخی از CoinState: {str(e)}")
        return generate_sample_ohlc_data(period)

def create_ohlc_from_price_data(price_df, period):
    """ایجاد داده‌های OHLC واقعی‌تر از داده‌های قیمت پایانی"""
    if price_df.empty:
        return price_df
    
    # تعیین بازه زمانی بر اساس period برای گروه‌بندی
    if period == "24h":
        freq = '1H'
    elif period == "1w":
        freq = '4H'
    elif period == "1m":
        freq = '1D'
    else:
        freq = '1D'
    
    # تنظیم ایندکس زمانی
    price_df = price_df.set_index('time')
    
    # نمونه‌برداری مجدد بر اساس فرکانس
    resampled = price_df['price'].resample(freq)
    
    # ایجاد داده‌های OHLC
    ohlc_data = resampled.agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    })
    
    # محاسبه حجم معاملات تقریبی
    ohlc_data['volume'] = ohlc_data['close'] * np.random.uniform(1000, 10000, len(ohlc_data))
    
    # بازگرداندن به حالت عادی
    ohlc_data = ohlc_data.reset_index()
    ohlc_data = ohlc_data.dropna()
    
    return ohlc_data

def generate_sample_ohlc_data(period="24h"):
    """ایجاد داده‌های OHLC نمونه واقعی‌تر"""
    # تعیین تعداد داده‌ها بر اساس دوره
    period_points = {
        "24h": 24,    # 24 کندل برای 24 ساعت
        "1w": 42,     # 42 کندل برای 1 هفته (6 کندل در روز)
        "1m": 30,     # 30 کندل برای 30 روز
        "3m": 90,     # 90 کندل برای 90 روز
        "6m": 180,    # 180 کندل برای 180 روز
        "1y": 365,    # 365 کندل برای 365 روز
        "all": 100    # 100 کندل
    }
    
    count = period_points.get(period, 100)
    now = datetime.now()
    
    # تعیین فاصله زمانی بر اساس period
    if period == "24h":
        delta = timedelta(hours=1)
    elif period == "1w":
        delta = timedelta(hours=4)
    else:
        delta = timedelta(days=1)
    
    # ایجاد زمان‌ها
    times = [now - i * delta for i in range(count)][::-1]
    
    # ایجاد داده‌های OHLC واقعی‌تر
    base_price = 50000
    prices = []
    current_price = base_price
    
    for i in range(count):
        # نوسان واقعی‌تر با در نظر گرفتن روند
        volatility = 0.02  # 2% نوسان
        trend = 0.001 * np.sin(i/10)  # روند سینوسی کوچک
        
        # ایجاد تغییرات واقعی‌تر
        change = current_price * (volatility * np.random.randn() + trend)
        current_price = max(current_price + change, base_price * 0.5)
        
        # ایجاد OHLC از قیمت پایانی
        open_price = current_price * (1 + np.random.uniform(-0.01, 0.01))
        high_price = max(open_price, current_price) * (1 + np.random.uniform(0, 0.02))
        low_price = min(open_price, current_price) * (1 - np.random.uniform(0, 0.02))
        close_price = current_price
        
        prices.append({
            'time': times[i],
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': np.random.uniform(1000000, 5000000)
        })
    
    df = pd.DataFrame(prices)
    return df

# ==================== کش محلی ====================

def init_db():
    """ایجاد دیتابیس برای کش داده‌ها"""
    conn = sqlite3.connect('market_data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS price_data
                 (symbol TEXT, period TEXT, timestamp DATETIME, 
                  open REAL, high REAL, low REAL, close REAL, volume REAL,
                  UNIQUE(symbol, period, timestamp))''')
    conn.commit()
    conn.close()

def save_to_cache(symbol, period, df):
    """ذخیره داده‌ها در کش محلی"""
    try:
        conn = sqlite3.connect('market_data.db', check_same_thread=False)
        for _, row in df.iterrows():
            conn.execute('''INSERT OR REPLACE INTO price_data 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                         (symbol, period, row['time'], 
                          row['open'], row['high'], row['low'], 
                          row['close'], row['volume']))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"خطا در ذخیره کش: {e}")

def load_from_cache(symbol, period, count):
    """بارگذاری داده‌ها از کش محلی"""
    try:
        conn = sqlite3.connect('market_data.db', check_same_thread=False)
        df = pd.read_sql_query('''SELECT * FROM price_data 
                                WHERE symbol = ? AND period = ? 
                                ORDER BY timestamp DESC LIMIT ?''', 
                             conn, params=(symbol, period, count))
        conn.close()
        
        if not df.empty:
            df['time'] = pd.to_datetime(df['timestamp'])
            df = df.drop('timestamp', axis=1)
            return df
        return None
    except Exception as e:
        logger.error(f"خطا در خواندن کش: {e}")
        return None
#================================ذخیره داده‌های تحلیل ==========================
def save_analysis_results(analysis_results):
    """ذخیره نتایج تحلیل برای استفاده‌های بعدی"""
    try:
        conn = sqlite3.connect('market_data.db', check_same_thread=False)
        c = conn.cursor()
        
        # ایجاد جدول برای نتایج تحلیل
        c.execute('''CREATE TABLE IF NOT EXISTS analysis_results
                     (symbol TEXT, period TEXT, timestamp DATETIME,
                      rsi REAL, macd REAL, signal REAL, histogram REAL,
                      sma20 REAL, sma50 REAL, price REAL,
                      signals TEXT, recommendations TEXT)''')
        
        # ذخیره نتایج
        c.execute('''INSERT INTO analysis_results 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (analysis_results['symbol'],
                  analysis_results['period'],
                  analysis_results['timestamp'],
                  analysis_results['indicators']['rsi'],
                  analysis_results['indicators']['macd'],
                  analysis_results['indicators']['macd_signal'],
                  analysis_results['indicators']['macd_histogram'],
                  analysis_results['indicators']['sma_20'],
                  analysis_results['indicators']['sma_50'],
                  analysis_results['indicators']['current_price'],
                  json.dumps(analysis_results['signals']),
                  json.dumps(analysis_results['recommendations'])))
        
        conn.commit()
        conn.close()
        logger.info("نتایج تحلیل ذخیره شد")
    except Exception as e:
        logger.error(f"خطا در ذخیره نتایج تحلیل: {e}")

def load_previous_analysis(symbol, period, hours=24):
    """بارگذاری تحلیل‌های قبلی"""
    try:
        conn = sqlite3.connect('market_data.db', check_same_thread=False)
        since = datetime.now() - timedelta(hours=hours)
        
        df = pd.read_sql_query('''SELECT * FROM analysis_results 
                                WHERE symbol = ? AND period = ? AND timestamp > ?
                                ORDER BY timestamp DESC''', 
                             conn, params=(symbol, period, since))
        conn.close()
        
        return df
    except Exception as e:
        logger.error(f"خطا در بارگذاری تحلیل‌های قبلی: {e}")
        return None
# ==================== توابع تحلیل مستقل ====================
def perform_technical_analysis(historical_data):
    """انجام تحلیل تکنیکال بدون وابستگی به نمایش نمودار"""
    if historical_data is None or historical_data.empty:
        return None
    
    analysis_results = {
        'timestamp': datetime.now(),
        'symbol': '',
        'period': '',
        'indicators': {},
        'signals': {},
        'recommendations': []
    }
    
    try:
        # محاسبه اندیکاتورها
        historical_data = calculate_indicators(historical_data)
        
        # آخرین مقادیر
        last_row = historical_data.iloc[-1]
        
        # ذخیره مقادیر اندیکاتورها
        analysis_results['indicators'] = {
            'current_price': last_row.get('close', last_row.get('price', 0)),
            'rsi': last_row.get('RSI', 0),
            'macd': last_row.get('MACD', 0),
            'macd_signal': last_row.get('MACD_Signal', 0),
            'macd_histogram': last_row.get('MACD_Histogram', 0),
            'sma_20': last_row.get('SMA_20', 0),
            'sma_50': last_row.get('SMA_50', 0)
        }
        
        # تولید سیگنال‌ها
        analysis_results['signals'] = generate_trading_signals(analysis_results['indicators'])
        
        # تولید توصیه‌ها
        analysis_results['recommendations'] = generate_recommendations(analysis_results['signals'])
        
        return analysis_results
        
    except Exception as e:
        logger.error(f"خطا در تحلیل تکنیکال: {e}")
        return None

# ==================== ثابت‌های تحلیل تکنیکال ====================
# سیگنال‌های RSI
RSI_OVERSOLD = 'oversold'
RSI_OVERBOUGHT = 'overbought' 
RSI_NEUTRAL = 'neutral'

# سیگنال‌های MACD
MACD_BULLISH = 'bullish'
MACD_BEARISH = 'bearish'
MACD_NEUTRAL = 'neutral'

# سیگنال‌های میانگین متحرک
GOLDEN_CROSS = 'golden_cross'
DEATH_CROSS = 'death_cross'
PRICE_ABOVE = 'above'
PRICE_BELOW = 'below'

# کلیدهای دیکشنری
KEY_RSI_SIGNAL = 'rsi_signal'
KEY_MACD_SIGNAL = 'macd_signal'
KEY_PRICE_VS_SMA20 = 'price_vs_sma20'
KEY_PRICE_VS_SMA50 = 'price_vs_sma50'
KEY_SMA_CROSSOVER = 'sma_crossover'

# ==================== توابع تحلیل مستقل ====================
def generate_trading_signals(indicators):
    """تولید سیگنال‌های معاملاتی"""
    signals = {}
    
    # سیگنال RSI
    rsi = indicators.get('rsi', 50)
    if rsi < 30:
        signals[KEY_RSI_SIGNAL] = RSI_OVERSOLD
    elif rsi > 70:
        signals[KEY_RSI_SIGNAL] = RSI_OVERBOUGHT
    else:
        signals[KEY_RSI_SIGNAL] = RSI_NEUTRAL
    
    # سیگنال MACD
    macd = indicators.get('macd', 0)
    signal_line = indicators.get('macd_signal', 0)
    histogram = indicators.get('macd_histogram', 0)
    
    if macd > signal_line and histogram > 0:
        signals[KEY_MACD_SIGNAL] = MACD_BULLISH
    elif macd < signal_line and histogram < 0:
        signals[KEY_MACD_SIGNAL] = MACD_BEARISH
    else:
        signals[KEY_MACD_SIGNAL] = MACD_NEUTRAL
    
    # سیگنال میانگین متحرک
    price = indicators.get('current_price', 0)
    sma20 = indicators.get('sma_20', price)
    sma50 = indicators.get('sma_50', price)
    
    signals[KEY_PRICE_VS_SMA20] = PRICE_ABOVE if price > sma20 else PRICE_BELOW
    signals[KEY_PRICE_VS_SMA50] = PRICE_ABOVE if price > sma50 else PRICE_BELOW
    signals[KEY_SMA_CROSSOVER] = GOLDEN_CROSS if sma20 > sma50 else DEATH_CROSS
    
    return signals

def generate_recommendations(signals):
    """تولید توصیه‌های معاملاتی"""
    recommendations = []
    
    # تحلیل RSI
    rsi_signal = signals.get(KEY_RSI_SIGNAL, RSI_NEUTRAL)
    if rsi_signal == RSI_OVERSOLD:
        recommendations.append("📈 RSI در ناحیه اشباع فروش - احتمال بازگشت قیمت")
    elif rsi_signal == RSI_OVERBOUGHT:
        recommendations.append("📉 RSI در ناحیه اشباع خرید - احتمال اصلاح قیمت")
    
    # تحلیل MACD
    macd_signal = signals.get(KEY_MACD_SIGNAL, MACD_NEUTRAL)
    if macd_signal == MACD_BULLISH:
        recommendations.append("🟢 سیگنال MACD صعودی")
    elif macd_signal == MACD_BEARISH:
        recommendations.append("🔴 سیگنال MACD نزولی")
    
    # تحلیل میانگین متحرک
    price_vs_sma20 = signals.get(KEY_PRICE_VS_SMA20, PRICE_ABOVE)
    price_vs_sma50 = signals.get(KEY_PRICE_VS_SMA50, PRICE_ABOVE)
    crossover = signals.get(KEY_SMA_CROSSOVER, GOLDEN_CROSS)
    
    if price_vs_sma20 == PRICE_ABOVE and price_vs_sma50 == PRICE_ABOVE:
        recommendations.append("✅ قیمت بالاتر از میانگین‌های متحرک - روند صعودی")
    elif price_vs_sma20 == PRICE_BELOW and price_vs_sma50 == PRICE_BELOW:
        recommendations.append("❌ قیمت پایین‌تر از میانگین‌های متحرک - روند نزولی")
    
    if crossover == GOLDEN_CROSS:
        recommendations.append("🌟 تقاطع طلایی میانگین‌ها - سیگنال خرید")
    elif crossover == DEATH_CROSS:
        recommendations.append("💀 تقاطع مرگ میانگین‌ها - سیگنال فروش")
    
    if not recommendations:
        recommendations.append("⚪ وضعیت خنثی - منتظر سیگنال واضح‌تر بمانید")
    
    return recommendations

# ==================== توابع پردازش داده ====================
@st.cache_data(ttl=600, show_spinner=False)
def get_historical_data(symbol="bitcoin", period="24h"):
    """دریافت داده‌های تاریخی از CoinState"""
    # ابتدا بررسی کش محلی
    cached_data = load_from_cache(symbol, period, 100)
    if cached_data is not None:
        st.info("استفاده از داده‌های کش شده")
        return cached_data
    
    # دریافت داده از CoinState API
    data = get_coinstate_historical_data(symbol, period)
    if data is not None and not data.empty:
        save_to_cache(symbol, period, data)
        return data
    
    st.error("هیچ داده‌ای دریافت نشد.")
    return None

def calculate_indicators(df):
    """محاسبه اندیکاتورهای تکنیکال با داده‌های OHLC بهبود یافته"""
    if df is None or df.empty:
        return df
    try:
        # اطمینان از وجود ستون close
        if 'close' not in df.columns:
            if 'price' in df.columns:
                df['close'] = df['price']
            else:
                st.error("ستون قیمت برای محاسبه اندیکاتورها وجود ندارد")
                return df
        
        # محاسبه RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # محاسبه MACD
        exp12 = df['close'].ewm(span=12, adjust=False).mean()
        exp26 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp12 - exp26
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # محاسبه میانگین متحرک
        df['SMA_20'] = df['close'].rolling(window=20, min_periods=1).mean()
        df['SMA_50'] = df['close'].rolling(window=50, min_periods=1).mean()
        
        return df
    except Exception as e:
        st.error(f"خطای محاسبه اندیکاتورها: {str(e)}")
        return df

# ==================== توابع نمایش ====================
def display_market_data(coin_data, T, symbol):
    """نمایش اطلاعات بازار"""
    if coin_data and isinstance(coin_data, dict):
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            price = coin_data.get('price', coin_data.get('current_price', 0))
            st.metric(T["price"], format_currency(price))
        
        with col2:
            price_change = coin_data.get('priceChange24h', coin_data.get('price_change_percentage_24h', 0))
            st.metric(T["change"], format_percentage(price_change), delta_color="inverse")
        
        with col3:
            high = coin_data.get('high24h', coin_data.get('high_24h', price))
            st.metric(T["high"], format_currency(high))
        
        with col4:
            low = coin_data.get('low24h', coin_data.get('low_24h', price))
            st.metric(T["low"], format_currency(low))
        
        with col5:
            volume = coin_data.get('volume', coin_data.get('total_volume', 0))
            st.metric(T["volume"], format_number(volume))
        
        return True
    else:
        st.warning(T["no_data"])
        return False

def display_price_chart(historical_data, symbol, period, T):
    """نمایش نمودار قیمت با کندل‌های بهبود یافته"""
    if historical_data is not None and not historical_data.empty:
        st.subheader(f"{T['price_chart']} - {symbol}")
        
        fig = go.Figure()
        
        # استفاده از نمودار شمعی اگر داده OHLC داریم
        if all(col in historical_data.columns for col in ['open', 'high', 'low', 'close']):
            # ایجاد کندل‌های واقعی‌تر
            fig.add_trace(go.Candlestick(
                x=historical_data['time'],
                open=historical_data['open'],
                high=historical_data['high'],
                low=historical_data['low'],
                close=historical_data['close'],
                name='Price',
                increasing_line_color='#2E8B57',  # سبز برای افزایش
                decreasing_line_color='#DC143C',  # قرمز برای کاهش
                increasing_fillcolor='#2E8B57',
                decreasing_fillcolor='#DC143C',
                line=dict(width=1)
            ))
            
            # اضافه کردن حجم معاملات در نمودار جداگانه
            if 'volume' in historical_data.columns:
                # ایجاد نمودار دوم برای حجم
                fig.add_trace(go.Bar(
                    x=historical_data['time'],
                    y=historical_data['volume'],
                    name='Volume',
                    marker_color='rgba(100, 100, 100, 0.3)',
                    yaxis='y2'
                ))
                
                # تنظیمات layout برای نمودار دو محوری
                fig.update_layout(
                    yaxis2=dict(
                        title='Volume',
                        titlefont=dict(color='gray'),
                        tickfont=dict(color='gray'),
                        overlaying='y',
                        side='right',
                        showgrid=False
                    )
                )
        else:
            # نمودار خطی ساده اگر داده OHLC نداریم
            fig.add_trace(go.Scatter(
                x=historical_data['time'],
                y=historical_data['close'] if 'close' in historical_data.columns else historical_data['price'],
                mode='lines',
                name='Price',
                line=dict(color='blue', width=2)
            ))
        
        # میانگین متحرک
        if 'SMA_20' in historical_data.columns:
            fig.add_trace(go.Scatter(
                x=historical_data['time'],
                y=historical_data['SMA_20'],
                mode='lines',
                name='SMA 20',
                line=dict(color='orange', width=1.5),

opacity=0.7
            ))
        
        if 'SMA_50' in historical_data.columns:
            fig.add_trace(go.Scatter(
                x=historical_data['time'],
                y=historical_data['SMA_50'],
                mode='lines',
                name='SMA 50',
                line=dict(color='purple', width=1.5),
                opacity=0.7
            ))
        
        # تنظیمات layout
        fig.update_layout(
            title=f"{symbol} {T['price_chart']} ({PERIODS.get(period, period)})",
            xaxis_title="زمان",
            yaxis_title="قیمت (USD)",
            xaxis_rangeslider_visible=False,
            height=600,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                gridcolor='lightgray',
                showgrid=True
            ),
            yaxis=dict(
                gridcolor='lightgray',
                showgrid=True
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        return True
    else:
        st.warning(T["no_data"])
        return False

def display_indicators(historical_data, T):
    """نمایش اندیکاتورها"""
    if historical_data is not None and not historical_data.empty:
        st.subheader(T["indicators"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'RSI' in historical_data.columns:
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(
                    x=historical_data['time'],
                    y=historical_data['RSI'],
                    mode='lines',
                    name='RSI',
                    line=dict(color='blue', width=2)
                ))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                fig_rsi.update_layout(
                    title="RSI (14)", 
                    height=300,
                    xaxis_title="زمان",
                    yaxis_title="RSI"
                )
                st.plotly_chart(fig_rsi, use_container_width=True)

        with col2:
            if 'MACD' in historical_data.columns and 'MACD_Signal' in historical_data.columns:
                fig_macd = go.Figure()
                fig_macd.add_trace(go.Scatter(
                    x=historical_data['time'],
                    y=historical_data['MACD'],
                    mode='lines',
                    name='MACD',
                    line=dict(color='blue', width=2)
                ))
                fig_macd.add_trace(go.Scatter(
                    x=historical_data['time'],
                    y=historical_data['MACD_Signal'],
                    mode='lines',
                    name='Signal',
                    line=dict(color='red', width=2)
                ))
                if 'MACD_Histogram' in historical_data.columns:
                    colors = ['green' if x >= 0 else 'red' for x in historical_data['MACD_Histogram']]
                    fig_macd.add_trace(go.Bar(
                        x=historical_data['time'],
                        y=historical_data['MACD_Histogram'],
                        name='Histogram',
                        marker_color=colors
                    ))
                fig_macd.update_layout(
                    title="MACD", 
                    height=300,
                    xaxis_title="زمان",
                    yaxis_title="MACD"
                )
                st.plotly_chart(fig_macd, use_container_width=True)
        
        return True
    
    return False

def display_technical_analysis(historical_data, T):
    """نمایش تحلیل تکنیکال"""
    if historical_data is not None and not historical_data.empty:
        with st.expander(T["technical_analysis"]):
            st.write("آخرین مقادیر اندیکاتورها:")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if 'RSI' in historical_data.columns:
                    rsi_value = historical_data['RSI'].iloc[-1]
                    st.metric("RSI", f"{rsi_value:.2f}")
                    if rsi_value < 30:
                        st.success("اشباع فروش")
                    elif rsi_value > 70:
                        st.warning("اشباع خرید")
                    else:
                        st.info("نرمال")
            
            with col2:
                if 'MACD' in historical_data.columns:
                    macd_value = historical_data['MACD'].iloc[-1]
                    st.metric("MACD", f"{macd_value:.4f}")
            
            with col3:
                if 'MACD_Signal' in historical_data.columns:
                    signal_value = historical_data['MACD_Signal'].iloc[-1]
                    st.metric("سیگنال MACD", f"{signal_value:.4f}")

            with col4:
                if 'MACD_Histogram' in historical_data.columns:
                    hist_value = historical_data['MACD_Histogram'].iloc[-1]
                    st.metric("هیستوگرام MACD", f"{hist_value:.4f}")
                    if hist_value > 0:
                        st.success("صعودی")
                    else:
                        st.warning("نزولی")
            
            st.write("میانگین‌های متحرک:")
            col1, col2 = st.columns(2)
            
            with col1:
                if 'SMA_20' in historical_data.columns:
                    sma20 = historical_data['SMA_20'].iloc[-1]
                    price = historical_data['close'].iloc[-1]
                    st.metric("SMA 20", format_currency(sma20))
                    if price > sma20:
                        st.success("قیمت بالاتر از SMA20")
                    else:
                        st.warning("قیمت پایین‌تر از SMA20")
            
            with col2:
                if 'SMA_50' in historical_data.columns:
                    sma50 = historical_data['SMA_50'].iloc[-1]
                    price = historical_data['close'].iloc[-1]
                    st.metric("SMA 50", format_currency(sma50))
                    if price > sma50:
                        st.success("قیمت بالاتر از SMA50")
                    else:
                        st.warning("قیمت پایین‌تر از SMA50")

#===============================دیشبورد=============================

def save_analysis_results(analysis_results):
    """ذخیره نتایج تحلیل برای استفاده‌های بعدی"""
    try:
        conn = sqlite3.connect('market_data.db', check_same_thread=False)
        c = conn.cursor()
        
        # ایجاد جدول برای نتایج تحلیل
        c.execute('''CREATE TABLE IF NOT EXISTS analysis_results
                     (symbol TEXT, period TEXT, timestamp DATETIME,
                      rsi REAL, macd REAL, signal REAL, histogram REAL,
                      sma20 REAL, sma50 REAL, price REAL,
                      signals TEXT, recommendations TEXT)''')
        
        # ذخیره نتایج
        c.execute('''INSERT INTO analysis_results 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (analysis_results['symbol'],
                  analysis_results['period'],
                  analysis_results['timestamp'],
                  analysis_results['indicators']['rsi'],
                  analysis_results['indicators']['macd'],
                  analysis_results['indicators']['macd_signal'],
                  analysis_results['indicators']['macd_histogram'],
                  analysis_results['indicators']['sma_20'],
                  analysis_results['indicators']['sma_50'],
                  analysis_results['indicators']['current_price'],
                  json.dumps(analysis_results['signals']),
                  json.dumps(analysis_results['recommendations'])))
        
        conn.commit()
        conn.close()
        logger.info("نتایج تحلیل ذخیره شد")
    except Exception as e:
        logger.error(f"خطا در ذخیره نتایج تحلیل: {e}")

def load_previous_analysis(symbol, period, hours=24):
    """بارگذاری تحلیل‌های قبلی"""
    try:
        conn = sqlite3.connect('market_data.db', check_same_thread=False)
        since = datetime.now() - timedelta(hours=hours)
        
        df = pd.read_sql_query('''SELECT * FROM analysis_results 
                                WHERE symbol = ? AND period = ? AND timestamp > ?
                                ORDER BY timestamp DESC''', 
                             conn, params=(symbol, period, since))
        conn.close()
        
        return df
    except Exception as e:
        logger.error(f"خطا در بارگذاری تحلیل‌های قبلی: {e}")
        return None

# ==================== رابط کاربری اصلی ====================
def main():
    # مقداردهی اولیه دیتابیس
    init_db()
    
    # انتخاب زبان
    language = st.sidebar.selectbox("🌐 زبان / Language:", ["فارسی", "English"])
    T = TEXTS[language]
    
    st.title(T["title"])
    
    # تنظیمات سایدبار
    st.sidebar.header(T["settings"])
    
    # انتخاب نماد
    symbol = st.sidebar.selectbox(
        T["select_symbol"],
        options=SYMBOLS,
        index=0,
        format_func=lambda x: x.capitalize().replace('-', ' ')
    )
    
    # انتخاب تایم‌فریم (اصلاح شده: index=0 برای 24h)
    period = st.sidebar.selectbox(
        T["select_interval"],
        options=list(PERIODS.keys()),
        format_func=lambda x: PERIODS[x] if language == "فارسی" else x,
        index=0  # 24h به عنوان پیش‌فرض
    )
    
    # دکمه بروزرسانی داده‌ها
    if st.sidebar.button("🔄 بروزرسانی داده‌ها"):
        st.cache_data.clear()
        # حذف داده‌های کش شده برای این نماد و دوره
        try:
            conn = sqlite3.connect('market_data.db', check_same_thread=False)
            conn.execute('DELETE FROM price_data WHERE symbol = ? AND period = ?', (symbol, period))
            conn.commit()
            conn.close()
            st.sidebar.success("داده‌های کش حذف شدند")
        except Exception as e:
            logger.error(f"خطا در حذف کش: {e}")
            st.sidebar.error("خطا در حذف داده‌های کش")
        st.rerun()
    
    # بررسی سلامت API
    if st.sidebar.button(T["api_health"]):
        with st.spinner("در حال بررسی API..."):
            status, message = check_api_health()
            if status:
                st.sidebar.success(message)
            else:
                st.sidebar.error(message)
    
    # نمایش اطلاعات آخرین بروزرسانی
    st.sidebar.markdown("---")
    st.sidebar.caption(f"{T['last_update']}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # نمایش اطلاعات نماد
    st.sidebar.subheader(T["symbol_info"])
    st.sidebar.write(f"نماد: {symbol.capitalize().replace('-', ' ')}")
    st.sidebar.write(f"دوره: {PERIODS.get(period, period)}")
      
    # دریافت داده‌های بازار
    with st.spinner(T["loading"]):
        # دریافت داده‌های لحظه‌ای
        market_data = get_coinstate_realtime_data(symbol)
        
        # دریافت داده‌های تاریخی
        historical_data = get_historical_data(symbol=symbol, period=period)
        
        # انجام تحلیل تکنیکال مستقل
        analysis_results = None
        if historical_data is not None:
            analysis_results = perform_technical_analysis(historical_data)
    
    # ==================== بخش‌های مختلف نمایش ====================
    
    # ۱. نمایش اطلاعات بازار (همیشه)
    if not display_market_data(market_data, T, symbol):
        st.error(T["connection_error"])
        if st.button(T["retry"]):
            st.cache_data.clear()
            st.rerun()
        return
    
    # ۲. دیشبورد تحلیل تکنیکال (همیشه - مستقل از نمودار)
    if analysis_results:
        analysis_results['symbol'] = symbol
        analysis_results['period'] = period
        display_analysis_dashboard(analysis_results, T, symbol, period)
    else:
        st.warning("تحلیل تکنیکال در دسترس نیست")
    
    # ۳. نمایش نمودار قیمت (اختیاری - می‌تواند غیرفعال شود)
    show_charts = st.sidebar.checkbox("📊 نمایش نمودارها", value=True)
    if show_charts:
        display_price_chart(historical_data, symbol, period, T)
        display_indicators(historical_data, T)
    else:
        st.info("نمایش نمودارها غیرفعال شده است. تحلیل‌ها در دیشبورد بالا قابل مشاهده هستند.")
    
    # ۴. نمایش جزئیات فنی (اختیاری)
    show_details = st.sidebar.checkbox("🔍 نمایش جزئیات فنی", value=False)
    if show_details and historical_data is not None:
        display_technical_analysis(historical_data, T)
        
    # نمایش اندیکاتورها
    display_indicators(historical_data, T)
    
    # نمایش تحلیل تکنیکال
    display_technical_analysis(historical_data, T)
    
    # نمایش نمونه داده‌ها
    with st.expander("نمایش داده‌های خام"):
        if historical_data is not None:
            st.dataframe(historical_data.tail(10))
        if market_data is not None:
            st.json(market_data)

# ==================== اجرای برنامه ====================
if __name__ == "__main__":
    main()
