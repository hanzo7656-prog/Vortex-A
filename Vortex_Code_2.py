import streamlit as st
import pandas as pd
import requests 
import numpy as np
from datetime import datetime, timedelta
import json
import time
import logging
from typing import Dict, List, Optional
import threading
from collections import defaultdict

# ==================== SECTION 1: CONFIGURATION & SETUP ====================
st.set_page_config(
    page_title="CryptoScanner Pro v2.5",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Config:
    MIDDLEWARE_BASE_URL = "https://server-test-ovta.onrender.com"
    
    SCAN_LIMITS = [100, 200, 300]
    
    FILTERS = {
        "volume": "📊 حجم معاملات بالا",
        "momentum": "🚀 حرکت قیمت قوی",
        "breakout": "🎯 شکست سطوح",
        "oversold": "📈 اشباع فروش",
        "overbought": "📉 اشباع خرید"
    }
    
    PERIODS = {
        "24h": "24 ساعت", "1w": "1 هفته", "1m": "1 ماه", 
        "3m": "3 ماه", "6m": "6 ماه", "1y": "1 سال"
    }

# ==================== SECTION 2: MULTILINGUAL SUPPORT ====================
class TranslationManager:
    TEXTS = {
        "فارسی": {
            "title": "📊 CryptoScanner Pro v2.5",
            "select_interval": "انتخاب تایم‌فریم:",
            "loading": "در حال اسکن بازار...",
            "no_data": "داده‌ای دریافت نشد",
            "settings": "تنظیمات",
            "language": "🌐 زبان",
            "scan_all": "اسکن بازار",
            "total_coins": "تعداد ارزها",
            "bullish_coins": "ارزهای صعودی",
            "bearish_coins": "ارزهای نزولی",
            "avg_change": "میانگین تغییرات",
            "strongest_signal": "قوی‌ترین سیگنال",
            "coin": "ارز",
            "symbol": "نماد",
            "price": "قیمت",
            "change_24h": "تغییر 24h",
            "volume": "حجم",
            "signal_power": "قدرت سیگنال",
            "filter": "فیلتر",
            "scan_limit": "تعداد ارز برای اسکن",
            "connection_error": "خطا در اتصال به سرور",
            "try_again": "تلاش مجدد",
            "scan_results": "نتایج اسکن",
            "last_update": "آخرین بروزرسانی"
        },
        "English": {
            "title": "📊 CryptoScanner Pro v2.5",
            "select_interval": "Select interval:",
            "loading": "Scanning market...",
            "no_data": "No data received",
            "settings": "Settings",
            "language": "🌐 Language",
            "scan_all": "Scan Market",
            "total_coins": "Total Coins",
            "bullish_coins": "Bullish Coins",
            "bearish_coins": "Bearish Coins",
            "avg_change": "Average Change",
            "strongest_signal": "Strongest Signal",
            "coin": "Coin",
            "symbol": "Symbol",
            "price": "Price",
            "change_24h": "24h Change",
            "volume": "Volume",
            "signal_power": "Signal Power",
            "filter": "Filter",
            "scan_limit": "Scan Limit",
            "connection_error": "Connection error",
            "try_again": "Try again",
            "scan_results": "Scan Results",
            "last_update": "Last update"
        }
    }
    
    @staticmethod
    def get_text(language: str) -> Dict:
        return TranslationManager.TEXTS.get(language, TranslationManager.TEXTS["English"])

# ==================== SECTION 3: NOTIFICATION MANAGER ====================
class NotificationManager:
    def __init__(self):
        self.notifications = []
        self.lock = threading.Lock()
    
    def add_notification(self, message: str, level: str = "info"):
        with self.lock:
            self.notifications.append({
                "message": message,
                "level": level,
                "timestamp": datetime.now()
            })
    
    def get_notifications(self):
        with self.lock:
            return self.notifications.copy()

# ==================== SECTION 4: ENHANCED MIDDLEWARE CLIENT ====================
class MiddlewareAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.is_healthy = False
        self.last_error = None
        self._check_health()
    
    def _check_health(self):
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            self.is_healthy = response.status_code == 200
            self.last_error = None if self.is_healthy else f"HTTP {response.status_code}"
            logger.info(f"Server health: {self.is_healthy}")
        except Exception as e:
            self.is_healthy = False
            self.last_error = str(e)
            logger.error(f"Health check failed: {e}")
    
    def get_scan_data(self, limit: int = 100, filter_type: str = "volume") -> Optional[Dict]:
        try:
            url = f"{self.base_url}/scan-all"
            params = {"limit": limit, "filter": filter_type}
            logger.info(f"Fetching data from: {url} with params: {params}")
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully received {len(data.get('scan_results', []))} coins")
                return data
            else:
                logger.error(f"HTTP Error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Scan error: {e}")
            return None

# ==================== SECTION 5: SMART SIGNAL ENGINE ====================
class SignalEngine:
    @staticmethod
    def calculate_signal_power(coin_data: Dict) -> float:
        """محاسبه قدرت سیگنال برای هر ارز"""
        try:
            power = 0.0
            
            # تغییرات قیمت (وزن بالا)
            change_24h = abs(coin_data.get('priceChange24h', 0))
            power += min(change_24h * 2, 40)
            
            # حجم معاملات (وزن متوسط)
            volume = coin_data.get('volume', 0)
            if volume > 100000000:
                power += 25
            elif volume > 50000000:
                power += 15
            elif volume > 10000000:
                power += 5
            
            # رتبه بازار (وزن پایین)
            rank = coin_data.get('rank', 999)
            if rank <= 10:
                power += 20
            elif rank <= 50:
                power += 10
            elif rank <= 100:
                power += 5
            
            return min(power, 100)
            
        except Exception as e:
            logger.error(f"Signal calculation error: {e}")
            return 0.0

    @staticmethod
    def filter_coins_by_signal(coins: List[Dict], min_power: float = 10) -> List[Dict]:
        """فیلتر کردن ارزها بر اساس قدرت سیگنال"""
        filtered_coins = []
        for coin in coins:
            try:
                signal_power = SignalEngine.calculate_signal_power(coin)
                if signal_power >= min_power:
                    coin['signal_power'] = signal_power
                    filtered_coins.append(coin)
            except Exception as e:
                logger.error(f"Error filtering coin {coin.get('id', 'unknown')}: {e}")
                continue
                
        return filtered_coins

    @staticmethod
    def rank_coins(coins: List[Dict]) -> List[Dict]:
        """رتبه‌بندی ارزها بر اساس قدرت سیگنال"""
        return sorted(coins, key=lambda x: x.get('signal_power', 0), reverse=True)

# ==================== SECTION 6: MARKET ANALYZER ====================
class MarketAnalyzer:
    @staticmethod
    def calculate_market_stats(coins: List[Dict]) -> Dict:
        """محاسبه آمار کلی بازار"""
        if not coins:
            return {
                'total_coins': 0,
                'bullish_coins': 0,
                'bearish_coins': 0,
                'avg_change': 0,
                'strongest_signal': 'None',
                'strongest_power': 0
            }
        
        try:
            total_coins = len(coins)
            bullish_coins = sum(1 for coin in coins if coin.get('priceChange24h', 0) > 0)
            bearish_coins = total_coins - bullish_coins
            
            changes = [coin.get('priceChange24h', 0) for coin in coins if coin.get('priceChange24h') is not None]
            avg_change = np.mean(changes) if changes else 0
            
            strongest_coin = max(coins, key=lambda x: x.get('signal_power', 0), default={})
            strongest_signal = strongest_coin.get('name', 'None')
            
            return {
                'total_coins': total_coins,
                'bullish_coins': bullish_coins,
                'bearish_coins': bearish_coins,
                'avg_change': avg_change,
                'strongest_signal': strongest_signal,
                'strongest_power': strongest_coin.get('signal_power', 0)
            }
        except Exception as e:
            logger.error(f"Market stats error: {e}")
            return {}

# ==================== SECTION 7: MAIN SCANNER CLASS ====================
class CryptoScanner:
    def __init__(self):
        self.config = Config()
        self.notification_manager = NotificationManager()
        self.api_client = MiddlewareAPIClient(self.config.MIDDLEWARE_BASE_URL)
        self.signal_engine = SignalEngine()
        self.market_analyzer = MarketAnalyzer()
        self.last_scan_data = None
        self.last_scan_time = None

    def scan_market(self, limit: int = 100, filter_type: str = "volume") -> Optional[Dict]:
        """اسکن کامل بازار"""
        try:
            logger.info(f"Scanning market with limit {limit}, filter {filter_type}")
            
            # دریافت داده از سرور میانی
            scan_data = self.api_client.get_scan_data(limit, filter_type)
            if not scan_data:
                self.notification_manager.add_notification("خطا در دریافت داده از سرور", "error")
                return None

            coins = scan_data.get('scan_results', [])
            if not coins:
                self.notification_manager.add_notification("هیچ داده‌ای از سرور دریافت نشد", "warning")
                return None

            logger.info(f"Received {len(coins)} coins from server")
            
            # اعمال فیلتر سیگنال
            filtered_coins = self.signal_engine.filter_coins_by_signal(coins)
            logger.info(f"After signal filtering: {len(filtered_coins)} coins")
            
            # رتبه‌بندی ارزها
            ranked_coins = self.signal_engine.rank_coins(filtered_coins)
            
            # محاسبه آمار بازار
            market_stats = self.market_analyzer.calculate_market_stats(ranked_coins)
            
            result = {
                'coins': ranked_coins,
                'market_stats': market_stats,
                'scan_time': datetime.now(),
                'total_scanned': len(coins),
                'total_signals': len(ranked_coins),
                'success': True
            }
            
            self.last_scan_data = result
            self.last_scan_time = datetime.now()
            
            success_msg = f"اسکن موفق: {len(ranked_coins)} ارز سیگنال‌دهنده از {len(coins)} ارز"
            self.notification_manager.add_notification(success_msg, "success")
            
            return result
            
        except Exception as e:
            error_msg = f"خطا در اسکن بازار: {str(e)}"
            logger.error(error_msg)
            self.notification_manager.add_notification(error_msg, "error")
            return None

# ==================== SECTION 8: STREAMLIT UI COMPONENTS ====================
class StreamlitUI:
    @staticmethod
    def display_notifications(notification_manager: NotificationManager):
        notifications = notification_manager.get_notifications()
        for notification in notifications[-5:]:  # نمایش 5 نوتیفیکیشن آخر
            if notification["level"] == "error":
                st.error(notification["message"])
            elif notification["level"] == "warning":
                st.warning(notification["message"])
            elif notification["level"] == "success":
                st.success(notification["message"])
            else:
                st.info(notification["message"])

    @staticmethod
    def setup_sidebar(T: Dict) -> tuple:
        st.sidebar.header(T["settings"])
        
        language = st.sidebar.selectbox(
            T["language"], 
            ["فارسی", "English"],
            index=0
        )
        T = TranslationManager.get_text(language)
        
        period = st.sidebar.selectbox(
            T["select_interval"],
            options=list(Config.PERIODS.keys()),
            index=0,
            format_func=lambda x: Config.PERIODS[x] if language == "فارسی" else x
        )
        
        scan_limit = st.sidebar.selectbox(
            T["scan_limit"],
            options=Config.SCAN_LIMITS,
            index=0
        )
        
        filter_type = st.sidebar.selectbox(
            T["filter"],
            options=list(Config.FILTERS.keys()),
            index=0,
            format_func=lambda x: Config.FILTERS[x]
        )
        
        # نمایش وضعیت سرور
        st.sidebar.markdown("---")
        st.sidebar.header("🔧 وضعیت سرویس")
        
        # اینجا بعداً وضعیت واقعی رو نشون میدیم
        st.sidebar.info("آماده برای اسکن...")
        
        scan_clicked = st.sidebar.button(T["scan_all"], use_container_width=True, type="primary")
        
        return language, period, scan_limit, filter_type, scan_clicked, T

    @staticmethod
    def display_market_stats(market_stats: Dict, T: Dict):
        """نمایش آمار کلی بازار"""
        if not market_stats or market_stats['total_coins'] == 0:
            st.info("هنوز اسکنی انجام نشده است. دکمه اسکن را فشار دهید.")
            return
        
        st.subheader("📈 آمار کلی بازار")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(T["total_coins"], f"{market_stats['total_coins']:,}")
        
        with col2:
            st.metric(T["bullish_coins"], f"{market_stats['bullish_coins']:,}")
        
        with col3:
            st.metric(T["bearish_coins"], f"{market_stats['bearish_coins']:,}")
        
        with col4:
            avg_change = market_stats['avg_change']
            delta_color = "normal" if avg_change >= 0 else "inverse"
            st.metric(T["avg_change"], f"{avg_change:+.2f}%", delta_color=delta_color)
        
        with col5:
            st.metric(T["strongest_signal"], market_stats['strongest_signal'])

    @staticmethod
    def display_coins_table(coins: List[Dict], T: Dict):
        """نمایش جدول ارزهای سیگنال‌دهنده"""
        if not coins:
            st.warning("هیچ ارز سیگنال‌دهنده‌ای یافت نشد")
            return
        
        # ایجاد دیتافریم برای نمایش
        table_data = []
        for i, coin in enumerate(coins, 1):  # شروع از 1
            table_data.append({
                'ردیف': i,
                T['coin']: coin.get('name', 'N/A'),
                T['symbol']: coin.get('symbol', 'N/A'),
                T['price']: f"${coin.get('price', 0):,.2f}" if coin.get('price') else 'N/A',
                T['change_24h']: f"{coin.get('priceChange24h', 0):+.2f}%" if coin.get('priceChange24h') is not None else 'N/A',
                T['volume']: f"${coin.get('volume', 0)/1000000:.1f}M" if coin.get('volume') else 'N/A',
                T['signal_power']: f"{coin.get('signal_power', 0):.1f}"
            })
        
        df = pd.DataFrame(table_data)
        
        # نمایش جدول با استایل بهتر
        st.dataframe(
            df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                'ردیف': st.column_config.NumberColumn(width='small'),
                T['coin']: st.column_config.TextColumn(width='medium'),
                T['symbol']: st.column_config.TextColumn(width='small'),
                T['price']: st.column_config.TextColumn(width='medium'),
                T['change_24h']: st.column_config.TextColumn(width='medium'),
                T['volume']: st.column_config.TextColumn(width='medium'),
                T['signal_power']: st.column_config.ProgressColumn(
                    width='medium',
                    min_value=0,
                    max_value=100,
                    format="%.1f"
                )
            }
        )

# ==================== MAIN APPLICATION ====================
def main():
    st.title("📊 CryptoScanner Pro v2.5.1")
    
    # Initialize scanner and UI
    scanner = CryptoScanner()
    ui = StreamlitUI()
    
    # Display notifications
    ui.display_notifications(scanner.notification_manager)
    
    # Setup sidebar
    language, period, scan_limit, filter_type, scan_clicked, T = ui.setup_sidebar(
        TranslationManager.get_text("فارسی")
    )
    
    # Initialize session state for scan results
    if 'scan_result' not in st.session_state:
        st.session_state.scan_result = None
    
    # Perform scan when button clicked
    if scan_clicked:
        with st.spinner(T["loading"]):
            scan_result = scanner.scan_market(scan_limit, filter_type)
            st.session_state.scan_result = scan_result
            st.rerun()  # برای بروزرسانی صفحه
    else:
        scan_result = st.session_state.scan_result
    
    # Display results
    if scan_result and scan_result.get('success'):
        # Display market statistics
        ui.display_market_stats(scan_result['market_stats'], T)
        
        st.markdown("---")
        
        # Display coins table
        st.subheader(f"🎯 ارزهای سیگنال‌دهنده ({len(scan_result['coins'])} ارز)")
        ui.display_coins_table(scan_result['coins'], T)
        
        # Display scan info
        st.caption(f"🕒 {T['last_update']}: {scan_result['scan_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        st.caption(f"📊 از {scan_result['total_scanned']} ارز اسکن شده، {scan_result['total_signals']} ارز سیگنال‌دهنده شناسایی شد")
    
    elif scan_clicked and not scan_result:
        st.error("❌ اسکن ناموفق بود. لطفاً دوباره تلاش کنید.")
    
    # Footer
    st.markdown("---")
    st.markdown("**CryptoScanner Pro v2.5.1** • توسعه داده شده با Streamlit")

if __name__ == "__main__":
    main()
