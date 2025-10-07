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
    """نمایش پیشرفته نتایج با جستجوی اصلاح شده"""
    if results and 'coins' in results:
        coins = results['coins']

        st.subheader("🔍 جستجوی پیشرفته")
        
        # ردیف اول: جستجو و فیلترها
        col1, col2, col3 = st.columns([3, 2, 2])
        
        with col1:
            search_query = st.text_input(
                "جستجوی ارز:", 
                placeholder="نام (Bitcoin) یا نماد (BTC) را وارد کنید...",
                key='search_input'
            )
        
        with col2:
            filter_type = st.selectbox(
                "فیلتر بر اساس:",
                ["همه", "صعودی 24h", "نزولی 24h", "حجم بالا"],
                key='filter_select'
            )
        
        with col3:
            sort_by = st.selectbox(
                "مرتب سازی:",
                ["حجم معاملات", "تغییر 24h", "تغییر 7d", "ارزش بازار"],
                key='sort_select'
            )

        # فیلتر کردن داده‌ها
        filtered_coins = coins.copy()
        
        # ۱. اعمال جستجو
        if search_query:
            search_lower = search_query.lower().strip()
            filtered_coins = [
                coin for coin in filtered_coins 
                if (search_lower in coin.get('name', '').lower() or 
                    search_lower in coin.get('symbol', '').lower() or
                    search_lower in coin.get('name', '').lower().replace(' ', '') or
                    search_lower == coin.get('symbol', '').lower())
            ]
        
        # ۲. اعمال فیلتر
        if filter_type == "صعودی 24h":
            filtered_coins = [coin for coin in filtered_coins if coin.get('priceChange24h', 0) > 0]
        elif filter_type == "نزولی 24h":
            filtered_coins = [coin for coin in filtered_coins if coin.get('priceChange24h', 0) < 0]
        elif filter_type == "حجم بالا":
            filtered_coins = [coin for coin in filtered_coins if coin.get('volume', 0) > 1000000]
        
        # ۳. اعمال مرتب‌سازی
        if sort_by == "حجم معاملات":
            filtered_coins.sort(key=lambda x: x.get('volume', 0), reverse=True)
        elif sort_by == "تغییر 24h":
            filtered_coins.sort(key=lambda x: x.get('priceChange24h', 0), reverse=True)
        elif sort_by == "تغییر 7d":
            filtered_coins.sort(key=lambda x: x.get('priceChange7d', 0), reverse=True)
        elif sort_by == "ارزش بازار":
            filtered_coins.sort(key=lambda x: x.get('marketCap', 0), reverse=True)

        # نمایش اطلاعات خلاصه
        st.info(f"""
        **📊 اطلاعات جستجو:** 
        - کل ارزها: {len(coins)} 
        - نمایش: {len(filtered_coins)}
        - جستجو: `{search_query if search_query else 'همه'}`
        - فیلتر: {filter_type}
        - مرتب‌سازی: {sort_by}
        """)

        if filtered_coins:
            # ایجاد دیتافریم
            df_data = []
            for idx, coin in enumerate(filtered_coins, 1):
                df_data.append({
                    '#': idx,
                    'نام ارز': coin.get('name', 'Unknown'),
                    'نماد': coin.get('symbol', 'UNK'),
                    'قیمت': f"${coin.get('price', 0):.2f}",
                    '1h': f"{coin.get('priceChange1h', 0):+.2f}%",
                    '4h': f"{coin.get('priceChange4h', 0):+.2f}%", 
                    '24h': f"{coin.get('priceChange24h', 0):+.2f}%",
                    '7d': f"{coin.get('priceChange7d', 0):+.2f}%",
                    '30d': f"{coin.get('priceChange30d', 0):+.2f}%",
                    '180d': f"{coin.get('priceChange180d', 0):+.2f}%",
                    'حجم': f"${coin.get('volume', 0):,.0f}",
                    'ارزش بازار': f"${coin.get('marketCap', 0):,.0f}"
                })

            df = pd.DataFrame(df_data)
            df.set_index('#', inplace=True)

            # استایل برای تغییرات قیمت
            def style_percent(val):
                if isinstance(val, str) and '%' in val:
                    try:
                        num = float(val.replace('%', '').replace('+', ''))
                        if num > 0:
                            return 'color: green; background-color: #e8f5e8; font-weight: bold;'
                        elif num < 0:
                            return 'color: red; background-color: #ffebee; font-weight: bold;'
                    except:
                        pass
                return ''

            styled_df = df.style.applymap(style_percent, subset=['1h', '4h', '24h', '7d', '30d', '180d'])
            
            st.dataframe(styled_df, use_container_width=True, height=600)

        else:
            st.warning("""
            **❌ هیچ ارزی یافت نشد!**
            
            راهنمایی:
            - از نام کامل استفاده کنید (مثال: `Bitcoin`)
            - یا از نماد استفاده کنید (مثال: `BTC`)  
            - از فیلترهای مختلف استفاده کنید
            """)

        # دکمه‌های عمل
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 بروزرسانی داده‌ها", use_container_width=True):
                st.session_state.normal_scan = True
                st.rerun()
        with col2:
            if st.button("🤖 تحلیل AI", use_container_width=True, type="secondary"):
                st.session_state.ai_scan = True
                st.rerun()

    else:
        st.error("❌ داده‌ای برای نمایش وجود ندارد. لطفاً ابتدا اسکن کنید.")            



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
    
    # وضعیت اسکنر
    scanner_status = "🟢 فعال" if st.session_state.get('scanner') else "🔴 غیرفعال"
    st.metric("وضعیت اسکنر", scanner_status)
    
    # وضعیت AI
    ai_status = "🟢 فعال" if st.session_state.get('advanced_ai') else "🔴 غیرفعال"
    st.metric("وضعیت AI", ai_status)
    
    # 🔥 وضعیت اتصال به سرور میانی
    if st.session_state.scan_results:
        coins_count = len(st.session_state.scan_results.get('coins', []))
        source = st.session_state.scan_results.get('source', 'unknown')
        
        if source == 'api':
            server_status = "🟢 متصل"
            server_message = f"✅ {coins_count} ارز (سرور)"
            status_color = "success"
        else:
            server_status = "🟠 آفلاین" 
            server_message = f"📱 {coins_count} ارز (دمو)"
            status_color = "warning"
    else:
        server_status = "🔴 قطع"
        server_message = "⚡ آماده اسکن"
        status_color = "error"
    
    st.metric("وضعیت سرور", server_status)
    
    if status_color == "success":
        st.success(server_message)
    elif status_color == "warning":
        st.warning(server_message)
    else:
        st.error(server_message)
    
    # 🔥 اطلاعات اضافی سرور
    if st.session_state.scan_results:
        with st.expander("🔧 اطلاعات فنی سرور", expanded=False):
            st.write(f"**منبع داده:** {st.session_state.scan_results.get('source', 'unknown')}")
            st.write(f"**تعداد ارزها:** {len(st.session_state.scan_results.get('coins', []))}")
            
            timestamp = st.session_state.scan_results.get('timestamp', '')
            if timestamp:
                # تبدیل timestamp به زمان خوانا
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    readable_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                    st.write(f"**آخرین بروزرسانی:** {readable_time}")
                except:
                    st.write(f"**آخرین بروزرسانی:** {timestamp}")
            
            # تست اتصال سریع
            if st.button("🔄 تست اتصال سرور", key='test_connection_btn', use_container_width=True):
                with st.spinner("در حال تست اتصال..."):
                    try:
                        test_scanner = LightweightScanner()
                        test_result = test_scanner.scan_market(limit=5)
                        if test_result.get('source') == 'api':
                            st.success("✅ اتصال سرور برقرار است")
                        else:
                            st.warning("⚠️ سرور در دسترس نیست - حالت دمو فعال شد")
                    except Exception as e:
                        st.error(f"❌ خطا در اتصال: {e}")
    
    if st.session_state.ai_results:
        st.info("🧠 تحلیل AI فعال")
    
    # دکمه راه‌اندازی اضطراری
    if not st.session_state.get('scanner') or not st.session_state.get('advanced_ai'):
        st.markdown("---")
        if st.button("🚀 راه‌اندازی سیستم", use_container_width=True, key='init_system_btn'):
            try:
                if not st.session_state.get('scanner'):
                    st.session_state.scanner = LightweightScanner()
                if not st.session_state.get('advanced_ai'):
                    st.session_state.advanced_ai = AdvancedAI()
                st.success("✅ سیستم راه‌اندازی شد")
                st.rerun()
            except Exception as e:
                st.error(f"❌ خطا: {str(e)}")

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
