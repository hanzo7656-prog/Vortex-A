# app.py - نسخه پیشرفته‌تر
import streamlit as st
import time

# ایمپورت سیستم چندزبانه
from multilingual import Multilanguage

def main():
    """تابع اصلی"""
    # سیستم چندزبانه
    lang = Multilanguage()
    
    # تنظیمات صفحه
    st.set_page_config(
        page_title=lang.t('app_title'),
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # نمایش عنوان
    st.title(lang.t('app_title'))
    st.markdown("---")
    
    # وضعیت session state
    if 'scan_results' not in st.session_state:
        st.session_state.scan_results = None
    if 'ai_results' not in st.session_state:
        st.session_state.ai_results = None
    if 'lang' not in st.session_state:
        st.session_state.lang = lang
    
    # سایدبار پیشرفته
    with st.sidebar:
        st.header(lang.t('sidebar_title'))
        
        # انتخاب زبان
        selected_lang = st.selectbox(
            lang.t('language_label'),
            ['fa', 'en'],
            format_func=lambda x: 'فارسی' if x == 'fa' else 'English',
            key='lang_selector'
        )
        lang.set_language(selected_lang)
        
        st.markdown("---")
        
        # دکمه‌های اصلی
        col1, col2 = st.columns(2)
        with col1:
            if st.button(lang.t('scan_button'), use_container_width=True):
                st.session_state.normal_scan = True
        with col2:
            if st.button(lang.t('ai_scan_button'), use_container_width=True, type="secondary"):
                st.session_state.ai_scan = True
        
        st.markdown("---")
        st.subheader("وضعیت سیستم")
        st.info("🟢 " + lang.t('completed'))
    
    # تب‌های اصلی
    tab1, tab2, tab3 = st.tabs(["💰 " + lang.t('results_title'), "📊 مانیتورینگ", "❓ راهنما"])
    
    with tab1:
        display_market_tab(lang)
    
    with tab2:
        display_monitoring_tab(lang)
    
    with tab3:
        display_help_tab(lang)

def display_market_tab(lang):
    """نمایش تب بازار"""
    st.header(lang.t('results_title'))
    
    if st.session_state.get('normal_scan'):
        with st.spinner(lang.t('scanning')):
            time.sleep(2)
            st.session_state.scan_results = get_sample_data()
            st.rerun()
    
    if st.session_state.get('ai_scan'):
        with st.spinner(lang.t('analyzing')):
            time.sleep(3)
            st.session_state.scan_results = get_sample_data()
            st.session_state.ai_results = {"ai_confidence": 75}
            st.rerun()
    
    # نمایش نتایج
    if st.session_state.scan_results:
        st.success("✅ " + lang.t('success'))
        display_simple_results(st.session_state.scan_results, lang)
        
        if st.session_state.ai_results:
            st.info(f"🤖 {lang.t('ai_analysis')}: {st.session_state.ai_results['ai_confidence']}%")
    else:
        st.info(f"""
        **برای شروع:**
        - از دکمه **{lang.t('scan_button')}** برای دریافت داده‌های بازار استفاده کنید
        - از دکمه **{lang.t('ai_scan_button')}** برای تحلیل پیشرفته استفاده کنید
        """)

def display_monitoring_tab(lang):
    """نمایش تب مانیتورینگ"""
    st.header("مانیتورینگ سیستم")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("وضعیت", "🟢 " + lang.t('completed'))
    
    with col2:
        st.metric("زبان", "فارسی" if lang.current_lang == 'fa' else "English")
    
    with col3:
        st.metric("سرعت", "⏱️ سریع")
    
    st.markdown("---")
    st.info("سیستم در حالت سبک اجرا می‌شود.")

def display_help_tab(lang):
    """نمایش تب راهنما"""
    st.header("راهنمای استفاده")
    
    st.write(f"""
    **مراحل شروع:**
    1. از سایدبار **{lang.t('scan_button')}** را بزنید
    2. منتظر دریافت داده‌ها بمانید  
    3. برای تحلیل پیشرفته **{lang.t('ai_scan_button')}** را استفاده کنید
    """)

def display_simple_results(results, lang):
    """نمایش ساده نتایج"""
    if results and 'coins' in results:
        coins = results['coins']
        st.subheader(f"{lang.t('results_title')} - {len(coins)} {lang.t('coin_name')}")
        
        for coin in coins:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            with col1:
                st.write(f"**{coin['name']}** ({coin['symbol']})")
            with col2:
                st.write(f"${coin['price']:,.2f}")
            with col3:
                change = coin['priceChange24h']
                color = "🟢" if change > 0 else "🔴"
                st.write(f"{color} {change:+.2f}%")
            with col4:
                st.write(f"${coin.get('volume', 0):,.0f}")

def get_sample_data():
    """داده نمونه برای تست"""
    return {
        'success': True,
        'coins': [
            {'name': 'Bitcoin', 'symbol': 'BTC', 'price': 65432.10, 'priceChange24h': 2.15, 'volume': 39245678901},
            {'name': 'Ethereum', 'symbol': 'ETH', 'price': 3456.78, 'priceChange24h': 1.87, 'volume': 18765432987},
            {'name': 'BNB', 'symbol': 'BNB', 'price': 567.89, 'priceChange24h': 3.21, 'volume': 2987654321},
            {'name': 'Solana', 'symbol': 'SOL', 'price': 123.45, 'priceChange24h': -1.23, 'volume': 1987654321},
            {'name': 'XRP', 'symbol': 'XRP', 'price': 0.567, 'priceChange24h': 0.45, 'volume': 987654321},
        ]
    }

if __name__ == "__main__":
    main()
