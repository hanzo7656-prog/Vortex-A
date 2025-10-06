# advanced_ai.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class AdvancedAI:
    def __init__(self):
        self.analysis_history = []
        self.market_patterns = {}
        self.risk_levels = {
            'low': {'min': 0, 'max': 30, 'color': '🟢', 'action': 'امن'},
            'medium': {'min': 31, 'max': 60, 'color': '🟡', 'action': 'محتاطانه'},
            'high': {'min': 61, 'max': 80, 'color': '🟠', 'action': 'پرریسک'},
            'extreme': {'min': 81, 'max': 100, 'color': '🔴', 'action': 'بسیار پرریسک'}
        }
    
    def analyze_market_trend(self, coins_data):
        """تحلیل پیشرفته روند بازار"""
        if not coins_data:
            return self._get_default_analysis()
        
        # محاسبات پیشرفته
        trends = self._calculate_market_trends(coins_data)
        signals = self._generate_trading_signals(coins_data)
        risks = self._assess_market_risks(coins_data)
        
        analysis = {
            'market_summary': self._generate_market_summary(trends),
            'trading_signals': signals,
            'risk_assessment': risks,
            'timestamp': datetime.now().isoformat(),
            'coins_analyzed': len(coins_data),
            'market_sentiment': self._calculate_sentiment(trends),
            'recommended_actions': self._get_recommended_actions(signals, risks)
        }
        
        # ذخیره در تاریخچه
        self.analysis_history.append(analysis)
        if len(self.analysis_history) > 50:
            self.analysis_history = self.analysis_history[-50:]
        
        return analysis
    
    def _calculate_market_trends(self, coins_data):
        """محاسبه روندهای بازار"""
        trends = {
            'total_coins': len(coins_data),
            'bullish_coins': 0,
            'bearish_coins': 0,
            'neutral_coins': 0,
            'avg_24h_change': 0,
            'total_volume': 0,
            'dominant_trend': 'neutral'
        }
        
        if not coins_data:
            return trends
        
        changes_24h = []
        volumes = []
        
        for coin in coins_data:
            change = coin.get('priceChange24h', 0)
            volume = coin.get('volume', 0)
            
            changes_24h.append(change)
            volumes.append(volume)
            
            if change > 2:
                trends['bullish_coins'] += 1
            elif change < -2:
                trends['bearish_coins'] += 1
            else:
                trends['neutral_coins'] += 1
        
        trends['avg_24h_change'] = sum(changes_24h) / len(changes_24h)
        trends['total_volume'] = sum(volumes)
        
        # تعیین روند غالب
        bullish_ratio = trends['bullish_coins'] / trends['total_coins']
        bearish_ratio = trends['bearish_coins'] / trends['total_coins']
        
        if bullish_ratio > 0.6:
            trends['dominant_trend'] = 'strong_bullish'
        elif bullish_ratio > 0.4:
            trends['dominant_trend'] = 'bullish'
        elif bearish_ratio > 0.6:
            trends['dominant_trend'] = 'strong_bearish'
        elif bearish_ratio > 0.4:
            trends['dominant_trend'] = 'bearish'
        else:
            trends['dominant_trend'] = 'neutral'
        
        return trends
    
    def _generate_trading_signals(self, coins_data):
        """تولید سیگنال‌های معاملاتی"""
        signals = {
            'strong_buy': [],
            'buy': [],
            'hold': [],
            'sell': [],
            'strong_sell': []
        }
        
        for coin in coins_data:
            signal = self._analyze_coin_signal(coin)
            signals[signal['action']].append(signal)
        
        return signals
    
    def _analyze_coin_signal(self, coin):
        """تحلیل سیگنال برای هر ارز"""
        name = coin.get('name', 'Unknown')
        symbol = coin.get('symbol', 'UNK')
        price = coin.get('price', 0)
        change_24h = coin.get('priceChange24h', 0)
        change_1h = coin.get('priceChange1h', 0)
        volume = coin.get('volume', 0)
        
        # محاسبه امتیاز سیگنال
        score = 0
        
        # امتیاز بر اساس تغییرات 24h
        if change_24h > 10:
            score += 30
        elif change_24h > 5:
            score += 20
        elif change_24h > 2:
            score += 10
        elif change_24h < -10:
            score -= 30
        elif change_24h < -5:
            score -= 20
        elif change_24h < -2:
            score -= 10
        
        # امتیاز بر اساس تغییرات 1h
        if change_1h > 3:
            score += 15
        elif change_1h > 1:
            score += 5
        elif change_1h < -3:
            score -= 15
        elif change_1h < -1:
            score -= 5
        
        # امتیاز بر اساس حجم
        if volume > 1000000000:  # حجم بالا
            score += 10
        
        # تعیین اقدام
        if score >= 40:
            action = 'strong_buy'
            confidence = min(95, 70 + score)
            recommendation = "🟢 خرید قوی"
        elif score >= 20:
            action = 'buy'
            confidence = min(85, 60 + score)
            recommendation = "🟡 خرید محتاطانه"
        elif score >= -10:
            action = 'hold'
            confidence = 50
            recommendation = "📊 نظارت و نگهداری"
        elif score >= -30:
            action = 'sell'
            confidence = min(80, 60 - score)
            recommendation = "🟠 فروش محتاطانه"
        else:
            action = 'strong_sell'
            confidence = min(90, 70 - score)
            recommendation = "🔴 فروش قوی"
        
        return {
            'coin': name,
            'symbol': symbol,
            'price': price,
            'change_24h': change_24h,
            'change_1h': change_1h,
            'volume': volume,
            'signal_score': score,
            'action': action,
            'confidence': confidence,
            'recommendation': recommendation,
            'risk_level': self._calculate_risk_level(score)
        }
    
    def _calculate_risk_level(self, score):
        """محاسبه سطح ریسک"""
        risk_score = max(0, min(100, 50 - score))  # تبدیل به مقیاس 0-100
        
        for level, criteria in self.risk_levels.items():
            if criteria['min'] <= risk_score <= criteria['max']:
                return {
                    'level': level,
                    'score': risk_score,
                    'color': criteria['color'],
                    'action': criteria['action']
                }
        
        return {'level': 'medium', 'score': 50, 'color': '🟡', 'action': 'محتاطانه'}
    
    def _assess_market_risks(self, coins_data):
        """ارزیابی ریسک‌های بازار"""
        if not coins_data:
            return {'overall_risk': 'medium', 'score': 50, 'warnings': []}
        
        warnings = []
        risk_scores = []
        
        for coin in coins_data:
            change_24h = coin.get('priceChange24h', 0)
            volume = coin.get('volume', 0)
            
            # شناسایی ریسک‌ها
            if abs(change_24h) > 20:
                warnings.append(f"نوسان شدید در {coin.get('name')}: {change_24h:.1f}%")
                risk_scores.append(80)
            elif abs(change_24h) > 10:
                warnings.append(f"نوسان بالا در {coin.get('name')}: {change_24h:.1f}%")
                risk_scores.append(60)
            elif volume < 1000000:  # حجم بسیار پایین
                warnings.append(f"حجم معاملات پایین در {coin.get('name')}")
                risk_scores.append(70)
            else:
                risk_scores.append(30)
        
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 50
        
        # تعیین سطح کلی ریسک
        if avg_risk >= 70:
            overall_risk = 'extreme'
        elif avg_risk >= 50:
            overall_risk = 'high'
        elif avg_risk >= 30:
            overall_risk = 'medium'
        else:
            overall_risk = 'low'
        
        return {
            'overall_risk': overall_risk,
            'score': avg_risk,
            'warnings': warnings[:5],  # فقط 5 هشدار اول
            'risk_color': self.risk_levels[overall_risk]['color']
        }
    
    def _generate_market_summary(self, trends):
        """تولید خلاصه بازار"""
        trend_descriptions = {
            'strong_bullish': '📈 بازار بسیار صعودی',
            'bullish': '📈 بازار صعودی', 
            'neutral': '📊 بازار متعادل',
            'bearish': '📉 بازار نزولی',
            'strong_bearish': '📉 بازار بسیار نزولی'
        }
        
        return {
            'dominant_trend': trend_descriptions.get(trends['dominant_trend'], '📊 بازار متعادل'),
            'bullish_percentage': f"{(trends['bullish_coins'] / trends['total_coins']) * 100:.1f}%",
            'bearish_percentage': f"{(trends['bearish_coins'] / trends['total_coins']) * 100:.1f}%",
            'average_change': f"{trends['avg_24h_change']:.2f}%",
            'total_volume': f"${trends['total_volume']:,.0f}",
            'market_strength': self._assess_market_strength(trends)
        }
    
    def _assess_market_strength(self, trends):
        """ارزیابی قدرت بازار"""
        strength_score = (
            (trends['bullish_coins'] / trends['total_coins']) * 50 +
            (max(0, trends['avg_24h_change']) * 2) +
            (min(1, trends['total_volume'] / 10000000000) * 20)
        )
        
        if strength_score > 70:
            return "💪 بسیار قوی"
        elif strength_score > 50:
            return "👍 قوی"
        elif strength_score > 30:
            return "👌 متوسط"
        else:
            return "⚠️ ضعیف"
    
    def _calculate_sentiment(self, trends):
        """محاسبه احساسات بازار"""
        sentiment_score = (
            (trends['bullish_coins'] - trends['bearish_coins']) / trends['total_coins'] * 100
        )
        
        if sentiment_score > 30:
            return "🎯 بسیار مثبت"
        elif sentiment_score > 10:
            return "😊 مثبت"
        elif sentiment_score > -10:
            return "😐 خنثی"
        elif sentiment_score > -30:
            return "😟 منفی"
        else:
            return "😰 بسیار منفی"
    
    def _get_recommended_actions(self, signals, risks):
        """پیشنهاد اقدامات بر اساس تحلیل"""
        actions = []
        
        # پیشنهادات بر اساس سیگنال‌ها
        strong_buy_count = len(signals['strong_buy'])
        strong_sell_count = len(signals['strong_sell'])
        
        if strong_buy_count > 5:
            actions.append("💰 فرصت‌های خرید عالی زیادی وجود دارد")
        elif strong_sell_count > 5:
            actions.append("⚡ مراقب سیگنال‌های فروش قوی باشید")
        
        # پیشنهادات بر اساس ریسک
        if risks['overall_risk'] == 'extreme':
            actions.append("🔴 شرایط پرریسک - معاملات با احتیاط")
        elif risks['overall_risk'] == 'high':
            actions.append("🟠 ریسک بالا - مدیریت سرمایه دقیق")
        elif risks['overall_risk'] == 'low':
            actions.append("🟢 شرایط کم‌ریسک - فرصت‌های مناسب")
        
        # پیشنهادات عمومی
        if not actions:
            actions.append("📊 بازار در شرایط عادی - تصمیم‌گیری با تحلیل بیشتر")
        
        return actions
    
    def _get_default_analysis(self):
        """تحلیل پیش‌فرض در صورت عدم وجود داده"""
        return {
            'market_summary': {
                'dominant_trend': '📊 داده‌ای برای تحلیل موجود نیست',
                'bullish_percentage': '0%',
                'bearish_percentage': '0%', 
                'average_change': '0%',
                'total_volume': '$0',
                'market_strength': '⚠️ نامشخص'
            },
            'trading_signals': {'strong_buy': [], 'buy': [], 'hold': [], 'sell': [], 'strong_sell': []},
            'risk_assessment': {'overall_risk': 'medium', 'score': 50, 'warnings': [], 'risk_color': '🟡'},
            'market_sentiment': '😐 نامشخص',
            'recommended_actions': ['📝 داده‌های بازار را بارگذاری کنید']
        }
    
    def get_analysis_stats(self):
        """آمار تحلیل‌های انجام شده"""
        return {
            'total_analyses': len(self.analysis_history),
            'last_analysis_time': self.analysis_history[-1]['timestamp'] if self.analysis_history else 'Never',
            'average_coins_analyzed': np.mean([a.get('coins_analyzed', 0) for a in self.analysis_history]) if self.analysis_history else 0
        }
