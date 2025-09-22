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
    "bitcoin", "ethereum", "binance-coin", 
    "cardano", "ripple", "solana",
    "polkadot", "dogecoin", "avalanche",
    "matic-network", "litecoin", "cosmos"
]

# ==================== تایم‌فریم‌ها ====================
INTERVALS = {
    "1h": "1 ساعت",
    "4h": "4 ساعت", 
    "1d": "1 روز",
    "7d": "7 روز",
    "1m": "1 ماه",
    "3m": "3 ماه",
    "1y": "1 سال",
    "all": "همه زمان"
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
def get_coinstate_historical_data(coin_id="bitcoin", period="1d", limit=100):
    """دریافت داده‌های تاریخی از CoinState API"""
    try:
        url = f"{COINSTATE_BASE_URL}/coins/{coin_id}/charts"
        params = {
            "period": period,
            "limit": limit
        }
        
        headers = get_coinstate_headers()
        
        session = create_session()
        response = session.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # پردازش داده‌های دریافتی
            if isinstance(data, list) and len(data) > 0:
                df_data = []
                for item in data:
                    # فرض بر این که داده‌ها به صورت [timestamp, price, volume] هستند
                    if len(item) >= 2:
                        df_data.append({
                            'time': pd.to_datetime(item[0], unit='ms'),
                            'price': item[1],
                            'volume': item[2] if len(item) > 2 else 0
                        })
                
                df = pd.DataFrame(df_data)
                
                # برای OHLC، از قیمت به عنوان open, high, low, close استفاده می‌کنیم
                df['open'] = df['price']
                df['high'] = df['price']
                df['low'] = df['price']
                df['close'] = df['price']
                
                return df[['time', 'open', 'high', 'low', 'close', 'volume']]
        
        return None
        
    except Exception as e:
        st.error(f"خطا در دریافت داده تاریخی از CoinState: {str(e)}")
        return None

# ==================== کش محلی ====================
def init_db():
    """ایجاد دیتابیس برای کش داده‌ها"""
    conn = sqlite3.connect('market_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS price_data
                 (symbol TEXT, interval TEXT, timestamp DATETIME, 
                  open REAL, high REAL, low REAL, close REAL, volume REAL,
                  UNIQUE(symbol, interval, timestamp))''')
    conn.commit()
    conn.close()

def save_to_cache(symbol, interval, df):
    """ذخیره داده‌ها در کش محلی"""
    try:
        conn = sqlite3.connect('market_data.db')
        for _, row in df.iterrows():
            conn.execute('''INSERT OR REPLACE INTO price_data 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                         (symbol, interval, row['time'], 
                          row['open'], row['high'], row['low'], 
                          row['close'], row['volume']))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"خطا در ذخیره کش: {e}")

def load_from_cache(symbol, interval, count):
    """بارگذاری داده‌ها از کش محلی"""
    try:
        conn = sqlite3.connect('market_data.db')
        df = pd.read_sql_query('''SELECT * FROM price_data 
                                WHERE symbol = ? AND interval = ? 
                                ORDER BY timestamp DESC LIMIT ?''', 
                             conn, params=(symbol, interval, count))
        conn.close()
        
        if not df.empty:
            df['time'] = pd.to_datetime(df['timestamp'])
            df = df.drop('timestamp', axis=1)
            return df
        return None
    except Exception as e:
        logger.error(f"خطا در خواندن کش: {e}")
        return None

# ==================== توابع پردازش داده ====================
@st.cache_data(ttl=600, show_spinner=False)
def get_historical_data(symbol="bitcoin", interval="1d", count=100):
    """دریافت داده‌های تاریخی از CoinState"""
    # ابتدا بررسی کش محلی
    cached_data = load_from_cache(symbol, interval, count)
    if cached_data is not None:
        st.info("استفاده از داده‌های کش شده")
        return cached_data
    
    # دریافت داده از CoinState API
    data = get_coinstate_historical_data(symbol, interval, count)
    if data is not None and not data.empty:
        save_to_cache(symbol, interval, data)
        return data
    
    st.error("هیچ داده‌ای دریافت نشد.")
    return None

def calculate_indicators(df):
    """محاسبه اندیکاتورهای تکنیکال"""
    if df is None or df.empty:
        return df
    try:
        # محاسبه RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # محاسبه MACD
        exp12 = df['close'].ewm(span=12, adjust=False).mean()
        exp26 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp12 - exp26
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # محاسبه میانگین متحرک
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        
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

def display_price_chart(historical_data, symbol, interval, T):
    """نمایش نمودار قیمت"""
    if historical_data is not None and not historical_data.empty:
        st.subheader(f"{T['price_chart']} - {symbol}")
        
        fig = go.Figure()
        
        # نمودار خطی
        fig.add_trace(go.Scatter(
            x=historical_data['time'],
            y=historical_data['close'],
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
                line=dict(color='orange', width=1)
            ))
        
        if 'SMA_50' in historical_data.columns:
            fig.add_trace(go.Scatter(
                x=historical_data['time'],
                y=historical_data['SMA_50'],
                mode='lines',
                name='SMA 50',
                line=dict(color='purple', width=1)
            ))
        
        fig.update_layout(
            title=f"{symbol} {T['price_chart']} ({INTERVALS.get(interval, interval)})",
            xaxis_rangeslider_visible=False,
            height=600,
            showlegend=True,
            xaxis_title="زمان",
            yaxis_title="قیمت (USD)"
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
                    fig_macd.add_trace(go.Bar(
                        x=historical_data['time'],
                        y=historical_data['MACD_Histogram'],
                        name='Histogram',
                        marker_color='gray'
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
                    st.metric("RSI", f"{historical_data['RSI'].iloc[-1]:.2f}")
            
            with col2:
                if 'MACD' in historical_data.columns:
                    st.metric("MACD", f"{historical_data['MACD'].iloc[-1]:.4f}")
            
            with col3:
                if 'MACD_Signal' in historical_data.columns:
                    st.metric("سیگنال MACD", f"{historical_data['MACD_Signal'].iloc[-1]:.4f}")

            with col4:
                if 'MACD_Histogram' in historical_data.columns:
                    st.metric("هیستوگرام MACD", f"{historical_data['MACD_Histogram'].iloc[-1]:.4f}")
            
            st.write("میانگین‌های متحرک:")
            col1, col2 = st.columns(2)
            
            with col1:
                if 'SMA_20' in historical_data.columns:
                    st.metric("SMA 20", format_currency(historical_data['SMA_20'].iloc[-1]))
            
            with col2:
                if 'SMA_50' in historical_data.columns:
                    st.metric("SMA 50", format_currency(historical_data['SMA_50'].iloc[-1]))
            
            # تحلیل ساده بر اساس اندیکاتورها
            st.write("تحلیل لحظه‌ای:")
            if 'RSI' in historical_data.columns:
                last_rsi = historical_data['RSI'].iloc[-1]
                if last_rsi < 30:
                    st.success("RSI در ناحیه اشباع فروش - احتمال بازگشت قیمت")
                elif last_rsi > 70:
                    st.warning("RSI در ناحیه اشباع خرید - احتمال کاهش قیمت")
                else:
                    st.info("RSI در ناحیه طبیعی")
            
            if 'MACD' in historical_data.columns and 'MACD_Signal' in historical_data.columns:
                last_macd = historical_data['MACD'].iloc[-1]
                last_signal = historical_data['MACD_Signal'].iloc[-1]
                if last_macd > last_signal:
                    st.success("MACD بالاتر از خط سیگنال - روند صعودی")
                else:
                    st.warning("MACD پایین‌تر از خط سیگنال - روند نزولی")

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
        index=0
    )
    
    # انتخاب تایم‌فریم
    interval = st.sidebar.selectbox(
        T["select_interval"],
        options=list(INTERVALS.keys()),
        format_func=lambda x: INTERVALS[x] if language == "فارسی" else x,
        index=2  # 1d به عنوان پیش‌فرض
    )
    
    # دکمه بروزرسانی داده‌ها
    if st.sidebar.button("🔄 بروزرسانی داده‌ها"):
        st.cache_data.clear()
        # حذف داده‌های کش شده برای این نماد و تایم‌فریم
        try:
            conn = sqlite3.connect('market_data.db')
            conn.execute('DELETE FROM price_data WHERE symbol = ? AND interval = ?', (symbol, interval))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"خطا در حذف کش: {e}")
        st.rerun()
    
    # بررسی سلامت API
    if st.sidebar.button(T["api_health"]):
        status, message = check_api_health()
        if status:
            st.sidebar.success(message)
        else:
            st.sidebar.error(message)
    
    # نمایش اطلاعات آخرین بروزرسانی
    st.sidebar.markdown("---")
    st.sidebar.caption(f"{T['last_update']}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # دریافت داده‌های بازار
    with st.spinner(T["loading"]):
        # دریافت داده‌های لحظه‌ای
        market_data = get_coinstate_realtime_data(symbol)
        
        # دریافت داده‌های تاریخی
        historical_data = get_historical_data(symbol=symbol, interval=interval, count=100)
        
        if historical_data is not None:
            historical_data = calculate_indicators(historical_data)
    
    # نمایش اطلاعات بازار
    if not display_market_data(market_data, T, symbol):
        st.error(T["connection_error"])
        if st.button(T["retry"]):
            st.cache_data.clear()
            st.rerun()
        return
    
    # نمایش نمودار قیمت
    display_price_chart(historical_data, symbol, interval, T)
    
    # نمایش اندیکاتورها
    display_indicators(historical_data, T)
    
    # نمایش تحلیل تکنیکال
    display_technical_analysis(historical_data, T)

# ==================== اجرای برنامه ====================
if __name__ == "main":
    main()
