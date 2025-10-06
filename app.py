# app.py - نسخه کامل با رفع مشکل تغییرات قیمت
import streamlit as st
import time
import pandas as pd
import requests
from datetime import datetime
from market_scanner import LightweightScanner
from advanced_ai import AdvancedAI
from multilingual import Multilanguage

def initialize_session_state():
    """Initialize تمام session state ها"""
    if 'scanner' not in st.session_state:
        st.session_state.scanner = LightweightScanner()
        print("درحال راه اندازی سیستم 2.3")
    
    if 'advanced_ai' not in st.session_state:
        st.session_state.advanced_ai = AdvancedAI()
        print("✅ هوش مصنوعی پیشرفته Initialize شد")
    
    if 'scan_results' not in st.session_state:
        st.session_state.scan_results = None
    
    if 'ai_results' not in st.session_state:
        st.session_state.ai_results = None
    
    if 'normal_scan' not in st.session_state:
        st.session_state.normal_scan = False
    
    if 'ai_scan' not in st.session_state:
        st.session_state.ai_scan = False

def main():
    """تابع اصلی"""
    # 🔥 اول session state ها رو initialize کن
    initialize_session_state()
    
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
    
    # سایدبار
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
            if st.button(lang.t('scan_button'), use_container_width=True, key='normal_scan_btn'):
                st.session_state.normal_scan = True
                st.rerun()
        with col2:
            if st.button(lang.t('ai_scan_button'), use_container_width=True, type="secondary", key='ai_scan_btn'):
                st.session_state.ai_scan = True
                st.rerun()
        
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
    
    # 🔥 هندل کردن اسکن
    if st.session_state.normal_scan:
        handle_normal_scan(lang)
    
    if st.session_state.ai_scan:
        handle_ai_scan(lang)
    
    # نمایش نتایج
    if st.session_state.scan_results:
        display_advanced_results(st.session_state.scan_results, lang)
        
        if st.session_state.ai_results:
            display_advanced_ai_analysis(st.session_state.ai_results, lang)
    else:
        display_welcome_message(lang)

def handle_normal_scan(lang):
    """مدیریت اسکن معمولی"""
    st.session_state.normal_scan = False
    
    with st.spinner(lang.t('scanning')):
        try:
            if not st.session_state.scanner:
                st.session_state.scanner = LightweightScanner()
            
            results = st.session_state.scanner.scan_market(limit=100)
            
            if results and results.get('success'):
                st.session_state.scan_results = results
                st.session_state.ai_results = None
                st.success(f"✅ اسکن موفق! {len(results.get('coins', []))} ارز دریافت شد")
                st.rerun()
            else:
                st.error("❌ خطا در دریافت داده از سرور")
                
        except Exception as e:
            st.error(f"❌ خطا در اسکن: {str(e)}")

def handle_ai_scan(lang):
    """مدیریت اسکن AI"""
    st.session_state.ai_scan = False
    
    with st.spinner(lang.t('analyzing')):
        print("🤖 شروع تحلیل AI پیشرفته...")
        
        try:
            if not st.session_state.scanner:
                st.session_state.scanner = LightweightScanner()
            
            if not st.session_state.advanced_ai:
                st.session_state.advanced_ai = AdvancedAI()
                print("✅ AI پیشرفته Initialize شد")
            
            market_results = st.session_state.scanner.scan_market(limit=100)
            
            if market_results and market_results.get('success'):
                coins = market_results['coins']
                print(f"📊 داده‌های بازار دریافت شد: {len(coins)} ارز")
                
                # تحلیل AI پیشرفته
                ai_analysis = st.session_state.advanced_ai.analyze_market_trend(coins)
                print(f"✅ تحلیل AI کامل شد")
                
                st.session_state.scan_results = market_results
                st.session_state.ai_results = ai_analysis
                
                st.success(f"✅ تحلیل AI موفق! {len(coins)} ارز تحلیل شد")
                st.rerun()
            else:
                st.error("❌ خطا در دریافت داده برای تحلیل AI")
                
        except Exception as e:
            print(f"❌ خطا در تحلیل AI: {str(e)}")
            st.error(f"❌ خطا در تحلیل AI: {str(e)}")

def display_advanced_results(results, lang):
    """نمایش پیشرفته نتایج"""
    if results and 'coins' in results:
        coins = results['coins']
        
        # 🔥 دیباگ مقادیر تغییرات قیمت
        with st.expander("🔍 دیباگ تغییرات قیمت", expanded=False):
            if coins:
                st.write("نمونه مقادیر تغییرات 24h (5 ارز اول):")
                sample_data = []
                for i, coin in enumerate(coins[:5]):
                    sample_data.append({
                        'ارز': coin.get('name', 'Unknown'),
                        'priceChange24h': coin.get('priceChange24h', 'NOT_FOUND'),
                        'priceChange1h': coin.get('priceChange1h', 'NOT_FOUND'),
                        'قیمت': coin.get('price', 0)
                    })
                st.dataframe(sample_data)
        
        # هدر با اطلاعات
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("تعداد ارزها", len(coins))
        with col2:
            source = "🚀 سرور" if results.get('source') == 'api' else "📁 نمونه"
            st.metric("منبع داده", source)
        with col3:
            # 🔥 محاسبه ارزهای صعودی
            bullish = sum(1 for c in coins if c.get('priceChange24h', 0) > 0)
            st.metric("ارزهای صعودی", f"📈 {bullish}")
        with col4:
            # 🔥 محاسبه ارزهای نزولی
            bearish = sum(1 for c in coins if c.get('priceChange24h', 0) < 0)
            st.metric("ارزهای نزولی", f"📉 {bearish}")
        
        st.markdown("---")
        
        # نمایش جدول زیبا - همه ارزها
        st.subheader(f"{lang.t('results_title')} - {len(coins)} ارز")
        
        # ایجاد دیتافریم برای همه ارزها
        df_data = []
        for coin in coins:
            price_change_24h = coin.get('priceChange24h', 0)
            price_change_1h = coin.get('priceChange1h', 0)
            
            df_data.append({
                'نام ارز': f"{coin.get('name', 'Unknown')} ({coin.get('symbol', 'UNK')})",
                'قیمت': f"${coin.get('price', 0):,.2f}",
                'تغییر ۲۴h': f"{price_change_24h:+.2f}%",
                'تغییر ۱h': f"{price_change_1h:+.2f}%", 
                'حجم': f"${coin.get('volume', 0):,.0f}",
                'ارزش بازار': f"${coin.get('marketCap', 0):,.0f}"
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True, height=600)
        
        # اطلاعات اضافی
        st.success(f"📊 نمایش تمام {len(coins)} ارز دریافت شده")
        
        # دکمه اسکن مجدد
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 اسکن مجدد", use_container_width=True, key='rescan_btn'):
                st.session_state.normal_scan = True
                st.rerun()
        with col2:
            if st.button("🤖 تحلیل پیشرفته AI", use_container_width=True, type="secondary", key='advanced_ai_btn'):
                st.session_state.ai_scan = True
                st.rerun()

def display_advanced_ai_analysis(ai_results, lang):
    """نمایش تحلیل AI پیشرفته"""
    st.markdown("---")
    st.header("🧠 تحلیل پیشرفته هوش مصنوعی")
    
    # خلاصه بازار
    if 'market_summary' in ai_results:
        display_market_summary(ai_results['market_summary'])
    
    # سیگنال‌های معاملاتی
    if 'trading_signals' in ai_results:
        display_trading_signals(ai_results['trading_signals'])
    
    # ارزیابی ریسک
    if 'risk_assessment' in ai_results:
        display_risk_assessment(ai_results['risk_assessment'])
    
    # احساسات بازار و پیشنهادات
    if 'market_sentiment' in ai_results and 'recommended_actions' in ai_results:
        display_market_sentiment(ai_results['market_sentiment'], ai_results['recommended_actions'])

def display_market_summary(market_summary):
    """نمایش خلاصه بازار"""
    st.subheader("📊 خلاصه بازار")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("روند غالب", market_summary.get('dominant_trend', 'نامشخص'))
    
    with col2:
        st.metric("صعودی", market_summary.get('bullish_percentage', '0%'))
    
    with col3:
        st.metric("نزولی", market_summary.get('bearish_percentage', '0%'))
    
    with col4:
        st.metric("قدرت بازار", market_summary.get('market_strength', 'نامشخص'))

def display_trading_signals(trading_signals):
    """نمایش سیگنال‌های معاملاتی"""
    st.subheader("💡 سیگنال‌های معاملاتی")
    
    if not any(trading_signals.values()):
        st.info("📊 هیچ سیگنال معاملاتی قوی‌ای شناسایی نشد")
        return
    
    # ایجاد تب برای انواع سیگنال‌ها
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        f"🟢 خرید قوی ({len(trading_signals.get('strong_buy', []))})",
        f"🟡 خرید ({len(trading_signals.get('buy', []))})", 
        f"📊 نظارت ({len(trading_signals.get('hold', []))})",
        f"🟠 فروش ({len(trading_signals.get('sell', []))})",
        f"🔴 فروش قوی ({len(trading_signals.get('strong_sell', []))})"
    ])
    
    with tab1:
        display_signal_list(trading_signals.get('strong_buy', []), "خرید قوی")
    
    with tab2:
        display_signal_list(trading_signals.get('buy', []), "خرید")
    
    with tab3:
        display_signal_list(trading_signals.get('hold', []), "نظارت")
    
    with tab4:
        display_signal_list(trading_signals.get('sell', []), "فروش")
    
    with tab5:
        display_signal_list(trading_signals.get('strong_sell', []), "فروش قوی")

def display_signal_list(signals, signal_type):
    """نمایش لیست سیگنال‌ها"""
    if not signals:
        st.info(f"هیچ سیگنال {signal_type}ی شناسایی نشد")
        return
    
    for signal in signals[:10]:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
            
            with col1:
                st.write(f"**{signal.get('coin', 'Unknown')}** ({signal.get('symbol', 'UNK')})")
            
            with col2:
                st.write(f"${signal.get('price', 0):,.2f}")
            
            with col3:
                change = signal.get('change_24h', 0)
                color = "green" if change > 0 else "red"
                st.write(f":{color}[{change:+.1f}%]")
            
            with col4:
                confidence = signal.get('confidence', 0)
                st.write(f"{confidence:.0f}%")
            
            with col5:
                recommendation = signal.get('recommendation', '📊 نظارت')
                st.write(recommendation)
            
            st.markdown("---")

def display_risk_assessment(risk_assessment):
    """نمایش ارزیابی ریسک"""
    st.subheader("⚠️ ارزیابی ریسک بازار")
    
    col1, col2 = st.columns(2)
    
    with col1:
        risk_score = risk_assessment.get('score', 50)
        risk_level = risk_assessment.get('overall_risk', 'medium')
        risk_color = risk_assessment.get('risk_color', '🟡')
        
        st.metric("سطح ریسک کلی", f"{risk_color} {risk_level}")
        st.metric("امتیاز ریسک", f"{risk_score:.1f}/100")
    
    with col2:
        warnings = risk_assessment.get('warnings', [])
        if warnings:
            st.write("**هشدارها:**")
            for warning in warnings:
                st.error(warning)
        else:
            st.success("✅ هیچ هشدار مهمی شناسایی نشد")

def display_market_sentiment(sentiment, recommended_actions):
    """نمایش احساسات بازار و پیشنهادات"""
    st.subheader("🎯 احساسات بازار")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("احساسات بازار", sentiment)
    
    with col2:
        st.write("**پیشنهادات اقدام:**")
        for action in recommended_actions:
            st.info(action)

def display_sidebar_status(lang):
    """نمایش وضعیت در سایدبار"""
    st.subheader("وضعیت سیستم")
    
    scanner_status = "🟢 فعال" if st.session_state.get('scanner') else "🔴 غیرفعال"
    st.metric("وضعیت اسکنر", scanner_status)
    
    ai_status = "🟢 فعال" if st.session_state.get('advanced_ai') else "🔴 غیرفعال"
    st.metric("وضعیت AI", ai_status)
    
    if st.session_state.scan_results:
        coins_count = len(st.session_state.scan_results.get('coins', []))
        source = "سرور" if st.session_state.scan_results.get('source') == 'api' else "نمونه"
        st.success(f"✅ {coins_count} ارز ({source})")
    else:
        st.info("⚡ آماده اسکن")
    
    if st.session_state.ai_results:
        st.info(f"🧠 AI پیشرفته فعال")

def display_monitoring_tab(lang):
    """نمایش تب مانیتورینگ"""
    st.header("مانیتورینگ سیستم")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        scanner_status = "🟢 فعال" if st.session_state.get('scanner') else "🔴 غیرفعال"
        st.metric("وضعیت اسکنر", scanner_status)
    
    with col2:
        ai_status = "🟢 فعال" if st.session_state.get('advanced_ai') else "🔴 غیرفعال"
        st.metric("وضعیت AI", ai_status)
    
    with col3:
        results_count = len(st.session_state.scan_results.get('coins', [])) if st.session_state.scan_results else 0
        st.metric("داده‌های ذخیره شده", results_count)
    
    with col4:
        ai_analyses = len(st.session_state.advanced_ai.analysis_history) if st.session_state.get('advanced_ai') else 0
        st.metric("تحلیل‌های AI", ai_analyses)
    
    st.markdown("---")
    
    # اطلاعات فنی
    st.subheader("اطلاعات فنی")
    
    tech_info = {
        "نسخه سیستم": "۲.۲ (رفع مشکل تغییرات قیمت)",
        "حالت اجرا": "بهینه‌شده برای وب", 
        "مدیریت حافظه": "فعال",
        "پشتیبانی API": "فعال با fallback",
        "محدودیت اسکن": "❌ بدون محدودیت",
        "تحلیل AI": "✅ پیشرفته فعال"
    }
    
    for key, value in tech_info.items():
        st.write(f"**{key}:** {value}")

def display_help_tab(lang):
    """نمایش تب راهنما"""
    st.header("راهنمای استفاده")
    
    st.write("""
    **🎯 مراحل شروع کار:**
    
    ۱. **اسکن بازار** - دریافت داده‌های کامل بازار
    ۲. **تحلیل پیشرفته AI** - تحلیل حرفه‌ای با هوش مصنوعی
    ۳. **مدیریت پرتفو** - بر اساس سیگنال‌های AI اقدام کنید
    
    **🔧 قابلیت‌های جدید:**
    - نمایش تمام ارزها بدون محدودیت
    - تحلیل پیشرفته بازار
    - دیباگ تغییرات قیمت
    - مدیریت ریسک خودکار
    """)

def display_welcome_message(lang):
    """نمایش پیام خوشامد"""
    st.info("""
    **🌟 به VortexAI خوش آمدید!**
    
    برای شروع از دکمه‌های سایدبار استفاده کنید.
    
    **قابلیت‌های سیستم:**
    - 🔄 اسکن کامل بازار (بدون محدودیت)
    - 🧠 تحلیل پیشرفته هوش مصنوعی
    - 💡 سیگنال‌های معاملاتی دقیق
    - ⚠️ ارزیابی ریسک حرفه‌ای
    """)

if __name__ == "__main__":
    main()
