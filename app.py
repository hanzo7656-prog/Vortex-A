# app.py - با اسکنر واقعی
import streamlit as st
import time
import pandas as pd
from multilingual import Multilanguage

# ایمپورت سبک - فقط وقتی نیاز شد لود می‌شه
def load_scanner():
    from market_scanner import LightweightScanner
    return LightweightScanner()

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
    if 'scanner' not in st.session_state:
        st.session_state.scanner = None
    
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
        display_sidebar_status(lang)
    
    # تب‌های اصلی
    tab1, tab2, tab3 = st.tabs(["💰 اسکن بازار", "📊 مانیتورینگ", "❓ راهنما"])
    
    with tab1:
        display_market_tab(lang)
    
    with tab2:
        display_monitoring_tab(lang)
    
    with tab3:
        display_help_tab(lang)

def display_market_tab(lang):
    """نمایش تب بازار"""
    st.header("اسکن بازار")
    
    # هندل کردن اسکن
    if st.session_state.get('normal_scan'):
        handle_normal_scan(lang)
    
    if st.session_state.get('ai_scan'):
        handle_ai_scan(lang)
    
    # نمایش نتایج
    if st.session_state.scan_results:
        display_advanced_results(st.session_state.scan_results, lang)
        
        if st.session_state.ai_results:
            display_ai_analysis(st.session_state.ai_results, lang)
    else:
        display_welcome_message(lang)

def handle_normal_scan(lang):
    """مدیریت اسکن معمولی"""
    with st.spinner(lang.t('scanning')):
        # لود اسکنر فقط وقتی نیاز شد
        if st.session_state.scanner is None:
            st.session_state.scanner = load_scanner()
        
        results = st.session_state.scanner.scan_market(limit=20)
        
        if results and results.get('success'):
            st.session_state.scan_results = results
            st.session_state.ai_results = None
            st.rerun()
        else:
            st.error("خطا در دریافت داده از سرور")

def handle_ai_scan(lang):
    """مدیریت اسکن AI"""
    with st.spinner(lang.t('analyzing')):
        if st.session_state.scanner is None:
            st.session_state.scanner = load_scanner()
        
        # اول داده بازار رو بگیر
        market_results = st.session_state.scanner.scan_market(limit=15)
        
        if market_results and market_results.get('success'):
            # تحلیل AI ساده
            ai_analysis = analyze_with_simple_ai(market_results['coins'])
            
            st.session_state.scan_results = market_results
            st.session_state.ai_results = ai_analysis
            st.rerun()
        else:
            st.error("خطا در تحلیل AI")

def display_advanced_results(results, lang):
    """نمایش پیشرفته نتایج"""
    if results and 'coins' in results:
        coins = results['coins']
        
        # هدر با اطلاعات
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("تعداد ارزها", len(coins))
        with col2:
            source = "🚀 سرور" if results.get('source') == 'api' else "📁 نمونه"
            st.metric("منبع داده", source)
        with col3:
            bullish = sum(1 for c in coins if c['priceChange24h'] > 0)
            st.metric("روند بازار", f"📈 {bullish}/{len(coins)}")
        
        st.markdown("---")
        
        # نمایش جدول زیبا
        st.subheader(f"{lang.t('results_title')} - {len(coins)} ارز")
        
        # ایجاد دیتافریم
        df_data = []
        for coin in coins:
            df_data.append({
                'نام ارز': f"{coin['name']} ({coin['symbol']})",
                'قیمت': f"${coin['price']:,.2f}",
                'تغییر ۲۴h': f"{coin['priceChange24h']:+.2f}%",
                'تغییر ۱h': f"{coin['priceChange1h']:+.2f}%", 
                'حجم': f"${coin['volume']:,.0f}"
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

def display_ai_analysis(ai_results, lang):
    """نمایش تحلیل AI"""
    st.markdown("---")
    st.header("🤖 " + lang.t('ai_analysis'))
    
    col1, col2 = st.columns(2)
    
    with col1:
        confidence = ai_results.get('ai_confidence', 0)
        st.metric(lang.t('ai_confidence'), f"{confidence}%")
    
    with col2:
        signals = len(ai_results.get('strong_signals', []))
        st.metric(lang.t('strong_signals'), signals)
    
    # نمایش سیگنال‌های قوی
    if 'strong_signals' in ai_results:
        st.subheader("💪 " + lang.t('strong_signals'))
        for signal in ai_results['strong_signals']:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{signal['coin']}**")
                with col2:
                    st.write(f"قدرت: {signal['signal_strength']}%")
                with col3:
                    recommendation = signal.get('recommendation', '📊 نظارت')
                    st.write(recommendation)
            st.markdown("---")

def analyze_with_simple_ai(coins):
    """تحلیل ساده AI - نسخه سبک"""
    strong_signals = []
    
    for coin in coins[:10]:  # فقط 10 ارز اول
        # منطق ساده تحلیل
        change_24h = coin['priceChange24h']
        volume = coin['volume']
        
        signal_strength = 0
        
        # تحلیل بر اساس تغییرات قیمت و حجم
        if change_24h > 5 and volume > 1000000000:
            signal_strength = 85
            recommendation = "🟢 خرید قوی"
        elif change_24h > 2:
            signal_strength = 70  
            recommendation = "🟡 خرید محتاطانه"
        elif change_24h < -5:
            signal_strength = 80
            recommendation = "🔴 فروش قوی"
        elif change_24h < -2:
            signal_strength = 65
            recommendation = "🟠 فروش محتاطانه"
        else:
            signal_strength = 50
            recommendation = "📊 نظارت"
        
        if signal_strength > 65:
            strong_signals.append({
                'coin': coin['name'],
                'symbol': coin['symbol'],
                'signal_strength': signal_strength,
                'recommendation': recommendation
            })
    
    return {
        'ai_confidence': 75,  # اعتماد ثابت برای نسخه ساده
        'strong_signals': strong_signals,
        'risk_warnings': [],
        'market_insights': ["تحلیل ساده AI انجام شد"]
    }

def display_sidebar_status(lang):
    """نمایش وضعیت در سایدبار"""
    st.subheader("وضعیت سیستم")
    
    if st.session_state.scan_results:
        coins_count = len(st.session_state.scan_results.get('coins', []))
        source = "سرور" if st.session_state.scan_results.get('source') == 'api' else "نمونه"
        st.success(f"✅ {coins_count} ارز ({source})")
    else:
        st.info("⚡ آماده اسکن")
    
    if st.session_state.ai_results:
        st.info(f"🤖 AI فعال")

def display_monitoring_tab(lang):
    """نمایش تب مانیتورینگ"""
    st.header("مانیتورینگ سیستم")
    
    # کارت‌های وضعیت
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = "🟢 فعال" if st.session_state.scanner else "⚪ غیرفعال"
        st.metric("وضعیت اسکنر", status)
    
    with col2:
        lang_status = "فارسی" if lang.current_lang == 'fa' else "English"
        st.metric("زبان سیستم", lang_status)
    
    with col3:
        results_count = len(st.session_state.scan_results.get('coins', [])) if st.session_state.scan_results else 0
        st.metric("داده‌های ذخیره شده", results_count)
    
    with col4:
        ai_status = "فعال" if st.session_state.ai_results else "غیرفعال"
        st.metric("وضعیت AI", ai_status)
    
    st.markdown("---")
    
    # اطلاعات فنی
    st.subheader("اطلاعات فنی")
    st.write("""
    - **نسخه سیستم:** ۱.۰ (سبک)
    - **حالت اجرا:** بهینه‌شده برای وب
    - **مدیریت حافظه:** فعال
    - **پشتیبانی API:** فعال با fallback
    """)

def display_help_tab(lang):
    """نمایش تب راهنما"""
    st.header("راهنمای استفاده")
    
    st.write("""
    **🎯 مراحل شروع کار:**
    
    ۱. **اسکن بازار** - از سایدبار دکمه اسکن بازار را بزنید
    ۲. **دریافت داده** - سیستم به صورت خودکار از سرور دریافت می‌کند
    ۳. **تحلیل پیشرفته** - برای تحلیل AI از دکمه مخصوص استفاده کنید
    ۴. **مانیتورینگ** - وضعیت سیستم را实时 مشاهده کنید
    
    ---
    
    **⚡ قابلیت‌های فعلی:**
    - دریافت داده‌های زنده از سرور
    - تحلیل خودکار بازار با AI سبک
    - نمایش جدولی زیبا و خوانا
    - مدیریت خطا و fallback خودکار
    - سیستم چندزبانه
    
    **🔧 نکات فنی:**
    - در صورت قطعی سرور، از داده‌های نمونه استفاده می‌شود
    - تحلیل AI به صورت سبک انجام می‌شود
    - سیستم بهینه‌شده برای اجرا در فضای ابری
    """)

def display_welcome_message(lang):
    """نمایش پیام خوشامد"""
    st.info("""
    **🌟 به VortexAI خوش آمدید!**
    
    برای شروع کار از دکمه‌های سایدبار استفاده کنید:
    
    - **🔄 اسکن بازار** - دریافت داده‌های زنده بازار
    - **🤖 اسکن با VortexAI** - تحلیل پیشرفته با هوش مصنوعی
    
    *سیستم به صورت خودکار بهترین منبع داده را انتخاب می‌کند.*
    """)

if __name__ == "__main__":
    main()
