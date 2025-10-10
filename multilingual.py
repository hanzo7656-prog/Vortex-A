# multilingual.py
class Multilanguage:
    def __init__(self):
        self.dictionaries = {
            'fa': self._persian_dict(),
            'en': self._english_dict()
        }
        self.current_lang = 'fa'
    
    def _persian_dict(self):
        return {
            # عناصر اصلی UI که نیاز به ترجمه دارند
            'app_title': "🔍 VortexAI - اسکنر بازار کریپتو",
            'scan_button': "اسکن بازار",
            'ai_scan_button': "اسکن با VortexAI", 
            'settings_button': "تنظیمات",
            'sidebar_title': "کنترل‌ها",
            'language_label': "زبان",
            'theme_label': "تم",
            'dark_mode': "تیره",
            'light_mode': "روشن",
            
            # نتایج و داده‌ها
            'results_title': "نتایج اسکن",
            'coin_name': "نام ارز", 
            'price': "قیمت",
            'change_24h': "تغییر 24h",
            'change_1h': "تغییر 1h",
            'volume': "حجم",
            'market_cap': "ارزش بازار",
            'signal_strength': "قدرت سیگنال",
            
            # تحلیل AI
            'ai_analysis': "تحلیل هوش مصنوعی",
            'strong_signals': "سیگنال‌های قوی", 
            'risk_warnings': "هشدارهای ریسک",
            'market_insights': "بینش‌های بازار",
            'ai_confidence': "اعتماد هوش مصنوعی",
            
            # وضعیت‌ها
            'scanning': "...در حال اسکن بازار",
            'analyzing': "در حال تحلیل VortexAI...",
            'completed': "تکمیل شد",
            'error': "خطا", 
            'success': "موفق",
            
            # تحلیل تکنیکال
            'technical_analysis': "تحلیل تکنیکال",
            'rsi': "شاخص قدرت نسبی",
            'macd': "واگرایی همگرایی میانگین متحرک",
            'bollinger_bands': "باندهای بولینگر", 
            'moving_average': "میانگین متحرک",

            'real_data': "داده واقعی",
            'no_historical_data': "بدون داده تاریخی",
            'data_quality': "کیفیت داده",
            'server_connection': "اتصال سرور",
            'historical_data_available': "داده تاریخی موجود",
        }
    
    def _english_dict(self):
        return {
            # UI Elements
            'app_title': "VortexAI - Crypto Market Scanner",
            'scan_button': "Scan Market",
            'ai_scan_button': "Scan with VortexAI", 
            'settings_button': "Settings",
            'sidebar_title': "Controls",
            'language_label': "Language", 
            'theme_label': "Theme",
            'dark_mode': "Dark",
            'light_mode': "Light",
            
            # Results
            'results_title': "Scan Results",
            'coin_name': "Coin Name",
            'price': "Price", 
            'change_24h': "24h Change",
            'change_1h': "1h Change",
            'volume': "Volume",
            'market_cap': "Market Cap",
            'signal_strength': "Signal Strength",
            
            # AI Analysis
            'ai_analysis': "AI Analysis", 
            'strong_signals': "Strong Signals",
            'risk_warnings': "Risk Warnings",
            'market_insights': "Market Insights", 
            'ai_confidence': "AI Confidence",
            
            # Status Messages
            'scanning': "Scanning market...",
            'analyzing': "VortexAI analyzing...", 
            'completed': "Completed",
            'error': "Error",
            'success': "Success",
            
            # Technical Analysis
            'technical_analysis': "Technical Analysis",
            'rsi': "Relative Strength Index", 
            'macd': "Moving Average Convergence Divergence",
            'bollinger_bands': "Bollinger Bands",
            'moving_average': "Moving Average",

            'real_data': "Real Data",
            'no_historical_data': "No Historical Data", 
            'data_quality': "Data Quality",
            'server_connection': "Server Connection",
            'historical_data_available': "Historical Data Available",
        }  # ← فقط این } رو نگه دارید
    
    def t(self, key):
        """دریافت ترجمه"""
        return self.dictionaries[self.current_lang].get(key, key)
    
    def set_language(self, lang):
        """تغییر زبان"""
        if lang in self.dictionaries:
            self.current_lang = lang
