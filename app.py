# app.py - نسخه بهینه‌شده
import streamlit as st
import time
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
    
    # سایدبار
    with st.sidebar:
        st.header(lang.t('sidebar_title'))
        
        # انتخاب زبان
        selected_lang = st.selectbox(
            lang.t('language_label'),
            ['fa', 'en'],
            format_func=lambda x: 'فارسی' if x == 'fa' else 'English'
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
    
    # تب‌های اصلی - عناوین همیشه فارسی
    tab1, tab2, tab3 = st.tabs(["💰 اسکن بازار", "📊 مانیتورینگ", "❓ راهنما"])
    
    with tab1:
        display_market_tab(lang)
    
    with tab2:
        display_monitoring_tab(lang)
    
    with tab3:
        display_help_tab(lang)

def display_market_tab(lang):
    """نمایش تب بازار"""
    st.header("اسکن بازار")  # همیشه فارسی
    
    if st.session_state.get('normal_scan'):
        with st.spinner(lang.t('scanning')):
            time.sleep(2)
            st.session_state.scan_results = get_sample_data()
            st.rerun()
    
    if st.session_state.get('ai_scan'):
        with st.spinner(lang.t('analyzing')):
            time.sleep(3)
            st.session_state.scan_results = get_sample_data()
            st.session_state.ai_results = {
                "ai_confidence": 75,
                "strong_signals": [
                    {"coin": "Bitcoin", "signal_strength": 85},
                    {"coin": "Ethereum", "signal_strength": 78}
                ]
            }
            st.rerun()
    
    # نمایش نتایج
    if st.session_state.scan_results:
        st.success("✅ " + lang.t('success'))
        display_simple_results(st.session_state.scan_results, lang)
        
        if st.session_state.ai_results:
            st.info(f"🤖 {lang.t('ai_analysis')}: {st.session_state.ai_results['ai_confidence']}%")
            
            # نمایش سیگنال‌های قوی
            if 'strong_signals' in st.session_state.ai_results:
                st.subheader(lang.t('strong_signals'))
                for signal in st.session_state.ai_results['strong_signals']:
                    st.write(f"• {signal['coin']} - قدرت: {signal['signal_strength']}%")
    else:
        # مطالب راهنما - همیشه فارسی
        st.info("""
        **برای شروع:**
        - از دکمه **اسکن بازار** برای دریافت داده‌های بازار استفاده کنید
        - از دکمه **اسکن با VortexAI** برای تحلیل پیشرفته استفاده کنید
        """)

def display_monitoring_tab(lang):
    """نمایش تب مانیتورینگ"""
    st.header("مانیتورینگ سیستم")  # همیشه فارسی
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("وضعیت سیستم", "🟢 فعال")  # همیشه فارسی
    
    with col2:
        st.metric("زبان界面", "فارسی" if lang.current_lang == 'fa' else "English")
    
    with col3:
        st.metric("سرعت اجرا", "⏱️ سریع")  # همیشه فارسی
    
    st.markdown("---")
    st.info("سیستم در حالت سبک اجرا می‌شود.")  # همیشه فارسی

def display_help_tab(lang):
    """نمایش تب راهنما"""
    st.header("راهنمای استفاده")  # همیشه فارسی
    
    # مطالب راهنما - همیشه فارسی
    st.write("""
    **مراحل شروع کار:**
    
    1. **اسکن بازار** - از سایدبار دکمه اسکن بازار را بزنید
    2. **دریافت داده** - منتظر دریافت داده‌های بازار بمانید  
    3. **تحلیل پیشرفته** - برای تحلیل AI از دکمه اسکن با VortexAI استفاده کنید
    4. **مانیتورینگ** - از تب مانیتورینگ وضعیت سیستم را مشاهده کنید
    
    ---
    
    **قابلیت‌های اصلی:**
    - 🔄 اسکن بازار و دریافت داده‌های زنده
    - 🤖 تحلیل پیشرفته با هوش مصنوعی
    - 📊 مانیتورینگ وضعیت سیستم
    - ⚠️ هشدارهای ریسک و مدیریت
    """)

def display_simple_results(results, lang):
    """نمایش ساده نتایج"""
    if results and 'coins' in results:
        coins = results['coins']
        st.subheader(f"{lang.t('results_title')} - {len(coins)} ارز")  # "ارز" همیشه فارسی
        
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
        ]
    }

if __name__ == "__main__":
    main()
