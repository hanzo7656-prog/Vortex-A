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
            'app_title': "🔍 VortexAI - اسکنر بازار کریپتو",
            'scan_button': "اسکن بازار",
            'ai_scan_button': "اسکن با VortexAI",
            'settings_button': "تنظیمات",
            'sidebar_title': "کنترل‌ها",
            'language_label': "زبان",
            'theme_label': "تم",
            'dark_mode': "تیره", 
            'light_mode': "روشن",
            'results_title': "نتایج اسکن",
            'coin_name': "نام ارز",
            'price': "قیمت",
            'change_24h': "تغییر 24h",
            'change_1h': "تغییر 1h", 
            'volume': "حجم",
            'market_cap': "ارزش بازار",
            'signal_strength': "قدرت سیگنال",
            'ai_analysis': "تحلیل هوش مصنوعی",
            'scanning': "...در حال اسکن بازار",
            'analyzing': "در حال تحلیل VortexAI...",
            'completed': "تکمیل شد",
            'error': "خطا",
            'success': "موفق"
        }
    
    def _english_dict(self):
        return {
            'app_title': "VortexAI - Crypto Market Scanner",
            'scan_button': "Scan Market", 
            'ai_scan_button': "Scan with VortexAI",
            'settings_button': "Settings",
            'sidebar_title': "Controls",
            'language_label': "Language",
            'theme_label': "Theme",
            'dark_mode': "Dark",
            'light_mode': "Light", 
            'results_title': "Scan Results",
            'coin_name': "Coin Name",
            'price': "Price",
            'change_24h': "24h Change",
            'change_1h': "1h Change",
            'volume': "Volume",
            'market_cap': "Market Cap",
            'signal_strength': "Signal Strength", 
            'ai_analysis': "AI Analysis",
            'scanning': "Scanning market...",
            'analyzing': "VortexAI analyzing...",
            'completed': "Completed",
            'error': "Error",
            'success': "Success"
        }
    
    def t(self, key):
        """دریافت ترجمه"""
        return self.dictionaries[self.current_lang].get(key, key)
    
    def set_language(self, lang):
        """تغییر زبان"""
        if lang in self.dictionaries:
            self.current_lang = lang
