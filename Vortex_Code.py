import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import numpy as np
from datetime import datetime, timedelta
import json
import time
import logging
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

# ==================== تنظیمات اولیه ====================
st.set_page_config(
    page_title="TradingView Market Scanner Pro",
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
        "title": "📊 اسکنر بازار TradingView Pro",
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
        "title": "📊 TradingView Market Scanner Pro",
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

# ==================== تنظیمات TradingView API ====================
TRADINGVIEW_API_URL = "https://scanner.tradingview.com/global/scan"
RAPIDAPI_KEY = "19f9fc8235msh7baef879e868351p1fe3dejsnaa49178c32ef"
RAPIDAPI_HOST = "tradingview.p.rapidapi.com"

# ==================== نمادهای معاملاتی ====================
SYMBOLS = [
    "BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:BNBUSDT",
    "BINANCE:ADAUSDT", "BINANCE:XRPUSDT", "BINANCE:SOLUSDT",
    "BINANCE:DOTUSDT", "BINANCE:DOGEUSDT", "BINANCE:AVAXUSDT",
    "BINANCE:MATICUSDT", "BINANCE:LTCUSDT", "BINANCE:ATOMUSDT"
]

# ==================== تایم‌فریم‌ها ====================
INTERVALS = {
    "1": "1 دقیقه",
    "5": "5 دقیقه", 
    "15": "15 دقیقه",
    "30": "30 دقیقه",
    "60": "1 ساعت",
    "240": "4 ساعت",
    "D": "1 روز",
    "W": "1 هفته",
    "M": "1 ماه"
}

# ==================== توابع کمکی ====================
def create_session():
    """ایجاد یک session با قابلیت retry برای درخواست‌های API"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
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

def check_api_health():
    """بررسی سلامت API"""
    try:
        # تست یک درخواست ساده
        response = requests.get("https://api.coingecko.com/api/v3/ping", timeout=10)
        if response.status_code == 200:
            return True, "API در دسترس است"
        else:
            return False, f"API پاسخ نمی‌دهد. کد وضعیت: {response.status_code}"
    except Exception as e:
        return False, f"خطای اتصال به API: {str(e)}"

def get_historical_data_fallback(symbol="BINANCE:BTCUSDT", interval="60", count=100):
    """دریافت داده‌های تاریخی از Binance Public API به عنوان جایگزین"""
    try:
        # تبدیل نماد: BINANCE:BTCUSDT -> BTCUSDT
        binance_symbol = symbol.replace("BINANCE:", "")
        
        # تعیین interval برای Binance
        interval_mapping = {
            "1": "1m", "5": "5m", "15": "15m", "30": "30m",
            "60": "1h", "240": "4h", "D": "1d", "W": "1w", "M": "1M"
        }
        
        binance_interval = interval_mapping.get(interval, "1h")
        
        # دریافت داده از Binance
        url = f"https://api.binance.com/api/v3/klines"
        params = {
            "symbol": binance_symbol,
            "interval": binance_interval,
            "limit": count
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        # پردازش داده‌های Binance
        df = pd.DataFrame(data, columns=[
            'time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        
        # تبدیل به نوع داده مناسب
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        return df[['time', 'open', 'high', 'low', 'close', 'volume']]
        
    except Exception as e:
        st.error(f"خطای دریافت داده از Binance: {str(e)}")
        return None
    
    
# ==================== دریافت داده از TradingView API ====================
@st.cache_data(ttl=30, show_spinner=False)
def get_tradingview_data(symbols, columns=["close", "volume", "change"]):
    """دریافت داده از TradingView API"""
    try:
        payload = {
            "symbols": {"tickers": symbols, "query": {"types": []}},
            "columns": columns
        }
        
        headers = {
            "x-rapidapi-host": RAPIDAPI_HOST,
            "x-rapidapi-key": RAPIDAPI_KEY,
            "Content-Type": "application/json"
        }
        
        session = create_session()
        response = session.post(TRADINGVIEW_API_URL, json=payload, headers=headers, timeout=10)
        
        # مدیریت خطاهای HTTP
        if response.status_code == 400:
            st.error("خطای 400: درخواست نامعتبر. پارامترهای ارسالی را بررسی کنید.")
            return None
        elif response.status_code == 403:
            st.error("خطای 403: دسترسی غیرمجاز. ممکن است API Key نامعتبر باشد یا محدودیت دسترسی وجود داشته باشد.")
            return None
        elif response.status_code == 429:
            st.error("خطای 429: تعداد درخواست‌ها بیش از حد مجاز. لطفاً چند دقیقه صبر کنید.")
            return None
        elif response.status_code != 200:
            st.error(f"خطای HTTP: {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        return data
        
    except requests.exceptions.Timeout:
        st.error("خطای timeout: اتصال به سرور زمان‌بر شد.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("خطای اتصال: مشکل در ارتباط با سرور.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"خطای درخواست: {str(e)}")
        return None
    except Exception as e:
        st.error(f"خطای غیرمنتظره: {str(e)}")
        return None

@st.cache_data(ttl=300, show_spinner=False)
def get_historical_data(symbol="BINANCE:BTCUSDT", interval="60", count=100):
    """دریافت داده‌های تاریخی از CoinGecko API"""
    try:
        # تبدیل نماد به فرمت CoinGecko
        symbol_mapping = {
            "BINANCE:BTCUSDT": "bitcoin",
            "BINANCE:ETHUSDT": "ethereum",
            "BINANCE:BNBUSDT": "binancecoin",
            "BINANCE:ADAUSDT": "cardano",
            "BINANCE:XRPUSDT": "ripple",
            "BINANCE:SOLUSDT": "solana",
            "BINANCE:DOTUSDT": "polkadot",
            "BINANCE:DOGEUSDT": "dogecoin",
            "BINANCE:AVAXUSDT": "avalanche-2",
            "BINANCE:MATICUSDT": "matic-network",
            "BINANCE:LTCUSDT": "litecoin",
            "BINANCE:ATOMUSDT": "cosmos"
        }
        
        coin_id = symbol_mapping.get(symbol)
        if not coin_id:
            st.error(f"نماد {symbol} پشتیبانی نمی‌شود")
            return None
        
        # محاسبه بازه زمانی

        
        # تعیین days بر اساس interval و count
        interval_days = {
            "1": max(1, count // 1440),
            "5": max(1, count // 288),
            "15": max(1, count // 96),
            "30": max(1, count // 48),
            "60": max(1, count // 24),
            "240": max(1, count // 6),
            "D": count,
            "W": count * 7,
            "M": count * 30
        }
        
        days = interval_days.get(interval, 30)
        
        # دریافت داده از CoinGecko API
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": str(days),
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        # مدیریت خطاهای HTTP
        if response.status_code == 400:
            st.error("خطای 400: درخواست نامعتبر. پارامترهای ارسالی را بررسی کنید.")
            st.error(f"پارامترهای ارسالی: {params}")
            return None
        elif response.status_code == 401:
            st.error("خطای 401: دسترسی غیر مجاز. لطفا از پلن رایگان استفاده‌ کنید و پارامتر interval را حذف کنید.")
            return get_historical_data_fallback(symbol, interval, count)
        elif response.status_code == 403:
            st.error("خطای 403: دسترسی غیرمجاز. ممکن است API Key نامعتبر باشد یا محدودیت دسترسی وجود داشته باشد.")
            return None
        elif response.status_code == 404:
            st.error("خطای 404: منبع یافت نشد. endpoint یا نماد مورد نظر وجود ندارد.")
            return None
        elif response.status_code == 429:
            st.error("خطای 429: تعداد درخواست‌ها بیش از حد مجاز. لطفاً چند دقیقه صبر کنید.")
            return None
        elif response.status_code == 500:
            st.error("خطای 500: مشکل سرور داخلی. لطفاً بعداً تلاش کنید.")
            return None
        elif response.status_code != 200:
            st.error(f"خطای HTTP ناشناخته: {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        
        # پردازش داده‌های دریافتی
        if 'prices' in data:
            prices = data['prices']
            volumes = data.get('total_volumes', [])
            
            # ایجاد DataFrame
            df = pd.DataFrame(prices, columns=['time', 'close'])
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            
            # اضافه کردن حجم معاملات
            if volumes:
                df_vol = pd.DataFrame(volumes, columns=['time', 'volume'])
                df_vol['time'] = pd.to_datetime(df_vol['time'], unit='ms')
                df = pd.merge(df, df_vol, on='time', how='left')
            
            # محاسبه open, high, low (با تقریب)
            df['open'] = df['close'].shift(1)
            df['high'] = df[['open', 'close']].max(axis=1)
            df['low'] = df[['open', 'close']].min(axis=1)
            
            # حذف مقادیر NaN
            df = df.dropna()
            
            return df
        
        return None
    
    except Exception as e:
        st.error(f"خطای دریافت داده‌های تاریخی: {str(e)}")
        return get_historical_data_fallback(symbol, interval, count)
        
    except requests.exceptions.Timeout:
        st.error("خطای timeout: اتصال به سرور زمان‌بر شد.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("خطای اتصال: مشکل در ارتباط با سرور.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"خطای درخواست: {str(e)}")
        return None
    except ValueError as e:
        st.error(f"خطای پردازش JSON: {str(e)}")
        return None
    except Exception as e:
        st.error(f"خطای غیرمنتظره: {str(e)}")
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

def display_market_data(data, T, symbol):
    """نمایش اطلاعات بازار"""
    if data and 'data' in data and data['data']:
        symbol_data = None
        for item in data['data']:
            if item.get('s') == symbol:
                symbol_data = item
                break
        
        if symbol_data is None:
            st.warning(T["no_data"])
            return False
        
        values = symbol_data.get('d', [])
        
        if len(values) < 3:
            st.warning("داده‌های ناقص از API دریافت شده")
            return False
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            price = values[0] if len(values) > 0 else None
            st.metric(T["price"], format_currency(price))
        
        with col2:
            change = values[2] if len(values) > 2 else None
            st.metric(T["change"], format_percentage(change), delta_color="inverse")
        
        with col3:
            # داده high از TradingView ممکن است موجود نباشد
            st.metric(T["high"], "N/A")
        
        with col4:
            # داده low از TradingView ممکن است موجود نباشد
            st.metric(T["low"], "N/A")
            
        with col5:
            volume = values[1] if len(values) > 1 else None
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
        
        # نمودار شمعی
        fig.add_trace(go.Candlestick(
            x=historical_data['time'],
            open=historical_data['open'],
            high=historical_data['high'],
            low=historical_data['low'],
            close=historical_data['close'],
            name='OHLC'
        ))
        
        # میانگین متحرک
        fig.add_trace(go.Scatter(
            x=historical_data['time'],
            y=historical_data['SMA_20'],
            mode='lines',
            name='SMA 20',
            line=dict(color='orange', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=historical_data['time'],
            y=historical_data['SMA_50'],
            mode='lines',
            name='SMA 50',
            line=dict(color='purple', width=2)
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
            # نمودار RSI
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
            # نمودار MACD
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
                st.metric("RSI", f"{historical_data['RSI'].iloc[-1]:.2f}")
                
            with col2:
                st.metric("MACD", f"{historical_data['MACD'].iloc[-1]:.4f}")
                
            with col3:
                st.metric("سیگنال MACD", f"{historical_data['MACD_Signal'].iloc[-1]:.4f}")
                
            with col4:
                st.metric("هیستوگرام MACD", f"{historical_data['MACD_Histogram'].iloc[-1]:.4f}")
            
            st.write("میانگین‌های متحرک:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("SMA 20", format_currency(historical_data['SMA_20'].iloc[-1]))
                
            with col2:
                st.metric("SMA 50", format_currency(historical_data['SMA_50'].iloc[-1]))
                
            # تحلیل ساده بر اساس اندیکاتورها
            st.write("تحلیل لحظه‌ای:")
            
            last_rsi = historical_data['RSI'].iloc[-1]
            last_macd = historical_data['MACD'].iloc[-1]
            last_signal = historical_data['MACD_Signal'].iloc[-1]
            
            if last_rsi < 30:
                st.success("RSI در ناحیه اشباع فروش - احتمال بازگشت قیمت")
            elif last_rsi > 70:
                st.warning("RSI در ناحیه اشباع خرید - احتمال کاهش قیمت")
            else:
                st.info("RSI در ناحیه طبیعی")
                
            if last_macd > last_signal:
                st.success("MACD بالاتر از خط سیگنال - روند صعودی")
            else:
                st.warning("MACD پایین‌تر از خط سیگنال - روند نزولی")

# ==================== رابط کاربری ====================
def main():
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
        index=4  # 1h به عنوان پیش‌فرض
    )
    
    # دکمه بروزرسانی داده‌ها
    if st.sidebar.button("🔄 بروزرسانی داده‌ها"):
        st.cache_data.clear()
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
        market_data = get_tradingview_data([symbol])
    
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
if __name__ == "__main__":
    main()
