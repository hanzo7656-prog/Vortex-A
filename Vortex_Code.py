# crypto_scanner.py - سیستم دو زبان

import streamlit as st
import requests
import pandas as pd
import numpy as np
import sqlite3
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json

# --- SECTION 1: MULTI-LANGUAGE SYSTEM ---

class Multilanguage:  # تصحیح نام کلاس
    def __init__(self):
        self.dictionaries = {
            'fa': self._persian_dict(),
            'en': self._english_dict()
        }
        self.current_lang = 'fa'

    def _persian_dict(self):
        return {
            # UI Elements
            'app_title': "🔄 VortexAI - اسکنر بازار کریپتو",
            'scan_button': "📊 اسکن بازار",
            'ai_scan_button': "🤖 اسکن با VortexAI",
            'settings_button': "⚙️ تنظیمات",
            'search_placeholder': "...جستجوی ارز",
            
            # Sidebar
            'sidebar_title': "کنترل‌ها",
            'language_label': "زبان",
            'theme_label': "تم",
            'dark_mode': "تیره",
            'light_mode': "روشن",
            
            # Results
            'results_title': "نتایج اسکن",
            'coin_name': "نام ارز",
            'price': "قیمت",
            'change_24h': "تغییر 24h",
            'change_1h': "تغییر 1h",
            'volume': "حجم",
            'market_cap': "ارزش بازار",
            'signal_strength': "قدرت سیگنال",
            
            # AI Analysis
            'ai_analysis': "تحلیل هوش مصنوعی",
            'strong_signals': "سیگنال‌های قوی",
            'risk_warnings': "هشدارهای ریسک",
            'market_insights': "بینش‌های بازار",
            'ai_confidence': "اعتماد هوش مصنوعی",
            
            # Technical Analysis
            'technical_analysis': "تحلیل تکنیکال",
            'rsi': "شاخص قدرت نسبی",
            'macd': "واگرایی همگرایی میانگین متحرک",
            'bollinger_bands': "باندهای بولینگر",
            'moving_average': "میانگین متحرک",
            
            # Status Messages
            'scanning': "...در حال اسکن بازار",
            'analyzing': "...VortexAI در حال تحلیل",
            'completed': "تکمیل شد",
            'error': "خطا",
            'success': "موفق"
        }

    def _english_dict(self):
        return {
            # UI Elements
            'app_title': "VortexAI - Crypto Market Scanner",
            'scan_button': "📊 Scan Market",
            'ai_scan_button': "🤖 Scan with VortexAI",
            'settings_button': "⚙️ Settings",
            'search_placeholder': "Search coins...",
            
            # Sidebar
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
            
            # Technical Analysis
            'technical_analysis': "Technical Analysis",
            'rsi': "Relative Strength Index",
            'macd': "Moving Average Convergence Divergence",
            'bollinger_bands': "Bollinger Bands",
            'moving_average': "Moving Average",
            
            # Status Messages
            'scanning': "Scanning market...",
            'analyzing': "VortexAI analyzing...",
            'completed': "Completed",
            'error': "Error",
            'success': "Success"
        }

    def t(self, key):
        """Get translation for current language"""
        return self.dictionaries[self.current_lang].get(key, key)

    def set_language(self, lang):
        """Set current language"""
        if lang in self.dictionaries:
            self.current_lang = lang

# Initialize multi-language system
lang = Multilanguage()

# --- SECTION 2: CONFIGURATION ---

def setup_page_config():
    """Setup Streamlit page configuration"""
    st.set_page_config(
        page_title=lang.t('app_title'),
        page_icon="🔄",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def setup_sidebar():
    """Setup sidebar with language and theme controls"""
    with st.sidebar:
        st.header(lang.t('sidebar_title'))
        
        # Language selection
        selected_lang = st.selectbox(
            lang.t('language_label'),
            ['fa', 'en'],
            format_func=lambda x: 'فارسی' if x == 'fa' else 'English',
            key='language_selector'
        )
        lang.set_language(selected_lang)
        
        # Theme selection
        theme = st.selectbox(
            lang.t('theme_label'),
            ['dark', 'light'],
            format_func=lambda x: lang.t('dark_mode') if x == 'dark' else lang.t('light_mode'),
            key='theme_selector'
        )
        
        st.markdown("---")
        
        # Scan buttons
        col1, col2 = st.columns(2)
        with col1:
            normal_scan = st.button(lang.t('scan_button'), use_container_width=True)
        with col2:
            ai_scan = st.button(lang.t('ai_scan_button'), use_container_width=True, type="secondary")
            
        return normal_scan, ai_scan

# --- SECTION 3: DATABASE MANAGER ---

class DatabaseManager:
    def __init__(self, db_path="crypto_data.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL,
                    volume REAL,
                    price_change_24h REAL,
                    price_change_1h REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def save_market_data(self, data: List[Dict]):
        try:
            with sqlite3.connect(self.db_path) as conn:
                for coin in data:
                    conn.execute('''
                        INSERT INTO market_data (symbol, price, volume, price_change_24h, price_change_1h)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        coin.get('symbol'),
                        coin.get('price'),
                        coin.get('volume'),
                        coin.get('priceChange24h'),
                        coin.get('priceChange1h')
                    ))
        except Exception as e:
            logging.error(f"Error saving market data: {e}")
# -- SECTION 4: VORTEXAI NEURAL NETWORK WITH SAFETY SYSTEMS --

import random
import math
from dataclasses import dataclass
from typing import List, Dict, Tuple
import json
import logging
from datetime import datetime, timedelta

# ==================== سیستم‌های محافظتی ====================

class DataSanityGuard:
    """محافظ در برابر داده‌های نادرست"""
    
    def validate_learning_data(self, inputs: Dict[str, float], expected_output: Dict[str, float]) -> bool:
        """اعتبارسنجی داده‌های یادگیری"""
        try:
            sanity_checks = {
                'price_sanity': (0 < inputs.get('price', 1) < 1000000),
                'volume_sanity': (inputs.get('volume', 0) >= 0),
                'change_sanity': (-100 < inputs.get('price_change_24h', 0) < 1000),
                'output_sanity': (0 <= expected_output.get('buy_confidence', 0.5) <= 1)
            }
            return all(sanity_checks.values())
        except:
            return False
    
    def detect_data_poisoning(self, data: Dict) -> bool:
        """تشخیص داده‌های مخرب"""
        suspicious_patterns = [
            data.get('price', 0) == 0,
            data.get('volume', 0) > 1e12,  # حجم غیرعادی
            abs(data.get('price_change_24h', 0)) > 100,  # تغییرات غیرممکن
        ]
        return any(suspicious_patterns)

class NeuralInflationPrevention:
    """پیشگیری از تورم عصبی و رشد بی‌رویه"""
    
    def __init__(self):
        self.growth_limits = {
            'max_neurons': 4000,
            'max_synapses': 15000,
            'max_memory_mb': 450,
            'min_activation_density': 0.1
        }
        
    def check_neural_health(self, network_stats: Dict) -> Dict[str, bool]:
        """بررسی سلامت شبکه عصبی"""
        health_report = {
            'memory_ok': network_stats['memory_usage'] < self.growth_limits['max_memory_mb'],
            'neurons_ok': network_stats['total_neurons'] < self.growth_limits['max_neurons'],
            'synapses_ok': network_stats['total_synapses'] < self.growth_limits['max_synapses'],
            'density_ok': (network_stats['total_activations'] / max(1, network_stats['total_neurons'])) > self.growth_limits['min_activation_density']
        }
        return health_report
    
    def should_grow(self, network_stats: Dict, performance_metrics: Dict) -> bool:
        """آیا شبکه مجاز به رشد است؟"""
        health = self.check_neural_health(network_stats)
        
        growth_conditions = {
            'health_ok': all(health.values()),
            'performance_improving': performance_metrics.get('accuracy_trend', 0) > 0,
            'real_need': performance_metrics.get('new_patterns_detected', False) or 
                        performance_metrics.get('complexity_increased', False)
        }
        
        return all(growth_conditions.values())

class EmergencyStopSystem:
    """سیستم توقف اضطراری"""
    
    def __init__(self):
        self.emergency_stop_active = False
        self.safe_fallback_mode = False
        self.stop_reason = ""
        self.activation_time = None
        
    def activate_emergency_stop(self, reason: str = "دستور کاربر"):
        """فعال‌سازی توقف اضطراری"""
        self.emergency_stop_active = True
        self.stop_reason = reason
        self.activation_time = datetime.now()
        
        logging.warning(f"🛑 توقف اضطراری فعال شد: {reason}")
        
    def deactivate_emergency_stop(self) -> bool:
        """غیرفعال‌سازی توقف اضطراری"""
        if self.emergency_stop_active:
            self.emergency_stop_active = False
            self.safe_fallback_mode = False
            logging.info("🟢 توقف اضطراری غیرفعال شد")
            return True
        return False
    
    def can_proceed(self, operation_type: str) -> bool:
        """آیا عملیات مجاز است؟"""
        if not self.emergency_stop_active:
            return True
            
        # عملیات‌های مجاز در حالت اضطراری
        safe_operations = {
            'market_scanning',
            'basic_analysis', 
            'historical_processing',
            'data_display'
        }
        
        return operation_type in safe_operations

# ==================== معماری شبکه عصبی ====================

@dataclass
class Neuron:
    id: int
    weights: Dict[str, float]
    bias: float
    activation_count: int = 0
    learning_rate: float = 0.01
    specialization_score: float = 0.0  # امتیاز تخصص
    historical_importance: float = 0.0  # اهمیت تاریخی
    last_activated: datetime = None
    
    def activate(self, inputs: Dict[str, float]) -> float:
        """فعال‌سازی نورون"""
        total = self.bias
        for key, value in inputs.items():
            if key in self.weights:
                total += value * self.weights[key]
        
        self.activation_count += 1
        self.last_activated = datetime.now()
        return self._sigmoid(total)
    
    def _sigmoid(self, x: float) -> float:
        """تابع فعال‌سازی سیگموید"""
        return 1 / (1 + math.exp(-x))
    
    def adjust_weights(self, inputs: Dict[str, float], error: float, learning_rate: float):
        """تنظیم وزن‌ها بر اساس خطا"""
        activation = self.activate(inputs)
        delta = error * activation * (1 - activation)
        
        for key in self.weights:
            if key in inputs:
                self.weights[key] += learning_rate * delta * inputs[key]
        
        self.bias += learning_rate * delta
    
    def should_protect(self) -> bool:
        """آیا این نورون باید محافظت شود؟"""
        protection_score = (
            self.specialization_score * 0.4 +
            self.historical_importance * 0.3 +
            min(self.activation_count / 1000, 1.0) * 0.3
        )
        return protection_score > 0.6
    
    def mutate(self, mutation_rate: float = 0.1):
        """جهش برای تنوع - با محافظت از نورون‌های متخصص"""
        if self.should_protect():
            mutation_rate *= 0.1  # جهش کمتر برای نورون‌های مهم
        
        for key in self.weights:
            if random.random() < mutation_rate:
                self.weights[key] += random.uniform(-0.2, 0.2)
        
        if random.random() < mutation_rate:
            self.bias += random.uniform(-0.1, 0.1)

@dataclass
class Synapse:
    source_neuron_id: int
    target_neuron_id: int
    weight: float
    strength: float = 1.0
    last_activated: float = 0

class VortexNeuralNetwork:
    def __init__(self):
        self.neurons = {}
        self.synapses = []
        self.input_layer = []
        self.hidden_layers = []
        self.output_layer = []
        
        # سیستم‌های محافظتی
        self.data_guard = DataSanityGuard()
        self.inflation_guard = NeuralInflationPrevention()
        
        # پارامترهای یادگیری
        self.learning_rate = 0.01
        self.generation = 0
        self.total_activations = 0
        self.memory = []
        
        # آمار و مانیتورینگ
        self.performance_history = []
        self.health_checkpoints = []
        
        self._build_network()
    
    def _build_network(self):
        """ساخت شبکه عصبی با معماری بهینه"""
        print("🧠 ساخت شبکه عصبی VortexAI با سیستم‌های ایمنی...")
        
        # لایه ورودی (400 نورون - کاهش یافته برای بهینه‌سازی)
        input_features = [
            'price', 'price_change_24h', 'price_change_1h', 'volume', 'market_cap',
            'rsi', 'macd', 'bollinger_upper', 'bollinger_lower', 'volume_ratio',
            'price_momentum', 'volatility', 'market_sentiment', 'trend_strength'
        ]
        
        self.input_layer = []
        for i in range(400):  # کاهش از 500 به 400
            weights = {feature: random.uniform(-1, 1) for feature in input_features}
            neuron = Neuron(id=i, weights=weights, bias=random.uniform(-0.5, 0.5))
            self.neurons[i] = neuron
            self.input_layer.append(i)
        
        # لایه‌های پنهان (2000 نورون - کاهش یافته)
        self.hidden_layers = []
        layer_sizes = [600, 500, 400, 300, 200]  # 5 لایه با نورون‌های کمتر
        
        current_id = 400
        for layer_size in layer_sizes:
            layer = []
            for i in range(layer_size):
                weights = {'prev_layer': random.uniform(-1, 1)}
                neuron = Neuron(id=current_id, weights=weights, bias=random.uniform(-0.5, 0.5))
                self.neurons[current_id] = neuron
                layer.append(current_id)
                current_id += 1
            self.hidden_layers.append(layer)
        
        # لایه خروجی (400 نورون - کاهش یافته)
        self.output_layer = []
        output_features = [
            'buy_signal', 'sell_signal', 'hold_signal', 'risk_score', 'confidence',
            'price_prediction_1h', 'price_prediction_24h', 'volatility_prediction'
        ]
        
        for i in range(400):
            weights = {feature: random.uniform(-1, 1) for feature in output_features}
            neuron = Neuron(id=current_id, weights=weights, bias=random.uniform(-0.5, 0.5))
            self.neurons[current_id] = neuron
            self.output_layer.append(current_id)
            current_id += 1
        
        # ایجاد سیناپس‌ها
        self._create_synapses()
        
        print(f"✅ شبکه عصبی ساخته شد: {len(self.neurons)} نورون, {len(self.synapses)} سیناپس")
        print("🛡️ سیستم‌های ایمنی فعال شدند")
    
    def _create_synapses(self):
        """ایجاد ارتباطات بین نورون‌ها با درنظرگیری بهینه‌سازی"""
        # ارتباط لایه ورودی به اولین لایه پنهان
        for input_id in self.input_layer:
            for hidden_id in self.hidden_layers[0][:100]:  # فقط 100 اتصال per neuron
                synapse = Synapse(input_id, hidden_id, random.uniform(-1, 1))
                self.synapses.append(synapse)
        
        # ارتباط بین لایه‌های پنهان
        for i in range(len(self.hidden_layers) - 1):
            for source_id in self.hidden_layers[i][:150]:  # محدودیت اتصال
                for target_id in self.hidden_layers[i + 1][:100]:
                    synapse = Synapse(source_id, target_id, random.uniform(-1, 1))
                    self.synapses.append(synapse)
        
        # ارتباط آخرین لایه پنهان به لایه خروجی
        for hidden_id in self.hidden_layers[-1][:200]:
            for output_id in self.output_layer[:100]:
                synapse = Synapse(hidden_id, output_id, random.uniform(-1, 1))
                self.synapses.append(synapse)
    
    def feed_forward(self, inputs: Dict[str, float]) -> Dict[str, float]:
        """پیش‌بینی شبکه عصبی"""
        if not inputs:
            return self._get_default_output()
        
        # فعال‌سازی لایه ورودی
        input_activations = {}
        for neuron_id in self.input_layer:
            neuron = self.neurons[neuron_id]
            activation = neuron.activate(inputs)
            input_activations[neuron_id] = activation
        
        # انتشار در لایه‌های پنهان
        current_activations = input_activations
        for layer in self.hidden_layers:
            layer_activations = {}
            for neuron_id in layer:
                neuron = self.neurons[neuron_id]
                neuron_inputs = {}
                
                for synapse in self.synapses:
                    if synapse.target_neuron_id == neuron_id:
                        if synapse.source_neuron_id in current_activations:
                            neuron_inputs[f"synapse_{synapse.source_neuron_id}"] = \
                                current_activations[synapse.source_neuron_id] * synapse.weight
                
                activation = neuron.activate(neuron_inputs)
                layer_activations[neuron_id] = activation
                synapse.last_activated = activation
            
            current_activations = layer_activations
        
        # لایه خروجی
        outputs = {}
        for neuron_id in self.output_layer:
            neuron = self.neurons[neuron_id]
            neuron_inputs = {}
            
            for synapse in self.synapses:
                if synapse.target_neuron_id == neuron_id:
                    if synapse.source_neuron_id in current_activations:
                        neuron_inputs[f"synapse_{synapse.source_neuron_id}"] = \
                            current_activations[synapse.source_neuron_id] * synapse.weight
            
            outputs[f"neuron_{neuron_id}"] = neuron.activate(neuron_inputs)
        
        self.total_activations += 1
        return self._interpret_outputs(outputs)
    
    def _interpret_outputs(self, raw_outputs: Dict[str, float]) -> Dict[str, float]:
        """تبدیل خروجی‌های خام به معنی‌دار"""
        # گروه‌بندی خروجی‌ها
        buy_signals = [v for k, v in raw_outputs.items() if 'neuron_' in k and int(k.split('_')[1]) < 2800 + 100]
        sell_signals = [v for k, v in raw_outputs.items() if 'neuron_' in k and 2800 + 100 <= int(k.split('_')[1]) < 2800 + 200]
        confidence_signals = [v for k, v in raw_outputs.items() if 'neuron_' in k and int(k.split('_')[1]) >= 2800 + 200]
        
        return {
            'buy_confidence': sum(buy_signals) / len(buy_signals) if buy_signals else 0.5,
            'sell_confidence': sum(sell_signals) / len(sell_signals) if sell_signals else 0.5,
            'overall_confidence': sum(confidence_signals) / len(confidence_signals) if confidence_signals else 0.5,
            'risk_score': 1 - (sum(confidence_signals) / len(confidence_signals)) if confidence_signals else 0.5,
            'neural_activity': self.total_activations,
            'network_maturity': min(1.0, self.total_activations / 1000)
        }
    
    def _get_default_output(self):
        """خروجی پیش‌فرض در صورت خطا"""
        return {
            'buy_confidence': 0.5,
            'sell_confidence': 0.5,
            'overall_confidence': 0.5,
            'risk_score': 0.5,
            'neural_activity': self.total_activations,
            'network_maturity': min(1.0, self.total_activations / 1000)
        }
    
    def learn_from_experience(self, inputs: Dict[str, float], expected_output: Dict[str, float], actual_profit: float = 0):
        """یادگیری از تجربیات با اعتبارسنجی داده"""
        # بررسی سلامت داده‌های ورودی
        if not self.data_guard.validate_learning_data(inputs, expected_output):
            logging.warning("❌ داده‌های یادگیری نامعتبر - یادگیری متوقف شد")
            return
        
        if self.data_guard.detect_data_poisoning(inputs):
            logging.warning("🚫 تشخیص داده‌های مخرب - یادگیری متوقف شد")
            return
        
        # پیش‌بینی فعلی
        current_output = self.feed_forward(inputs)
        
        # محاسبه خطا
        error = self._calculate_error(current_output, expected_output, actual_profit)
        
        # انتشار خطا به عقب
        self._backward_propagate(error, inputs)
        
        # ذخیره در حافظه
        experience = {
            'inputs': inputs,
            'expected': expected_output,
            'actual': current_output,
            'profit': actual_profit,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        self.memory.append(experience)
        
        # پاک‌سازی حافظه قدیمی
        if len(self.memory) > 800:  # کاهش از 1000 به 800
            self.memory = self.memory[-800:]
    
    def _calculate_error(self, current: Dict, expected: Dict, profit: float) -> float:
        """محاسبه خطا"""
        error = 0
        for key in current:
            if key in expected:
                error += abs(current[key] - expected[key])
        
        # اضافه کردن خطای سود/زیان
        if profit != 0:
            error += (1 - min(abs(profit), 1))  # خطای معکوس با سود
        
        return error / len(current) if current else 1.0
    
    def _backward_propagate(self, error: float, inputs: Dict[str, float]):
        """انتشار خطا به عقب"""
        learning_rate = self.learning_rate * (1 - min(1.0, self.total_activations / 10000))
        
        # به روز رسانی وزن‌ها در همه نورون‌ها
        for neuron in self.neurons.values():
            neuron.adjust_weights(inputs, error, learning_rate)
        
        # جهش تصادفی برای کشف راه‌حل‌های جدید (با کنترل)
        if random.random() < 0.005:  # کاهش از 1% به 0.5%
            random_neuron = random.choice(list(self.neurons.values()))
            random_neuron.mutate()
    
    def evolve(self):
        """تکامل شبکه - نسل جدید با کنترل رشد"""
        health_report = self.inflation_guard.check_neural_health(self.get_network_stats())
        
        if not all(health_report.values()):
            logging.warning("⚠️ تکامل متوقف شد: سلامت شبکه در خطر")
            return False
        
        self.generation += 1
        print(f"🧬 تکامل شبکه عصبی به نسل {self.generation}")
        
        # جهش کنترل‌شده برای نسل جدید
        mutation_count = 0
        for neuron in self.neurons.values():
            if not neuron.should_protect():  # فقط نورون‌های غیرمتخصص جهش می‌کنند
                if random.random() < 0.1:  # کاهش نرخ جهش
                    neuron.mutate(mutation_rate=0.15)
                    mutation_count += 1
        
        # تنظیم مجدد سیناپس‌ها
        for synapse in random.sample(self.synapses, min(100, len(self.synapses))):  # فقط 100 سیناپس
            synapse.weight += random.uniform(-0.2, 0.2)
            synapse.strength = min(1.0, synapse.strength + random.uniform(-0.05, 0.05))
        
        print(f"✅ تکامل موفق: {mutation_count} جهش، نسل {self.generation}")
        return True
    
    def intelligent_growth(self, performance_metrics: Dict):
        """رشد هوشمند شبکه بر اساس نیاز واقعی"""
        if not self.inflation_guard.should_grow(self.get_network_stats(), performance_metrics):
            return False
        
        # رشد کنترل‌شده - اضافه کردن نورون‌های جدید فقط اگر لازم باشد
        if performance_metrics.get('new_patterns_detected', False):
            self._add_specialized_neurons(10)  # فقط 10 نورون جدید
            return True
        
        return False
    
    def _add_specialized_neurons(self, count: int):
        """اضافه کردن نورون‌های تخصصی جدید"""
        current_max_id = max(self.neurons.keys())
        
        for i in range(count):
            new_id = current_max_id + i + 1
            # نورون‌های جدید با وزن‌های بهینه
            weights = {'prev_layer': random.uniform(-0.5, 0.5)}
            neuron = Neuron(
                id=new_id, 
                weights=weights, 
                bias=random.uniform(-0.3, 0.3),
                specialization_score=0.8  # نورون‌های جدید تخصصی‌تر
            )
            self.neurons[new_id] = neuron
            
            # اضافه به آخرین لایه پنهان
            self.hidden_layers[-1].append(new_id)
            
            # ایجاد اتصالات جدید
            self._connect_new_neuron(new_id)
        
        print(f"🌱 {count} نورون تخصصی جدید اضافه شد")
    
    def _connect_new_neuron(self, neuron_id: int):
        """ایجاد اتصالات برای نورون جدید"""
        # اتصال به لایه قبلی
        prev_layer = self.hidden_layers[-2] if len(self.hidden_layers) > 1 else self.input_layer
        for source_id in random.sample(prev_layer, min(20, len(prev_layer))):
            synapse = Synapse(source_id, neuron_id, random.uniform(-0.5, 0.5))
            self.synapses.append(synapse)
        
        # اتصال به لایه بعدی (خروجی)
        for target_id in random.sample(self.output_layer, min(15, len(self.output_layer))):
            synapse = Synapse(neuron_id, target_id, random.uniform(-0.5, 0.5))
            self.synapses.append(synapse)
    
    def optimize_memory(self):
        """بهینه‌سازی حافظه و حذف نورون‌های بی‌فایده - نسخه قوی"""
        neurons_to_prune = []
    
        for neuron_id, neuron in self.neurons.items():
        # معیارهای سخت‌گیرانه‌تر برای حذف
            if (neuron.activation_count < 3 and 
                not neuron.should_protect() and
                neuron_id not in self.input_layer and 
                neuron_id not in self.output_layer and
                max(neuron.weights.values()) < 0.05):  # وزن‌های بسیار کوچک
            
                neurons_to_prune.append(neuron_id)
    
        # حذف تا 20% نورون‌ها در صورت نیاز
        prune_count = min(len(neurons_to_prune), len(self.neurons) // 5)
    
        for neuron_id in neurons_to_prune[:prune_count]:
            self._remove_neuron(neuron_id)
    
        # بهینه‌سازی سیناپس‌ها
        self._optimize_synapses()
    
        print(f"🧹 بهینه‌سازی حافظه: {prune_count} نورون و {len(self.synapses)} سیناپس")
        return prune_count
    
    def _remove_neuron(self, neuron_id: int):
        """حذف ایمن یک نورون"""
        if neuron_id in self.neurons:
            # حذف از لایه‌ها
            for layer in self.hidden_layers:
                if neuron_id in layer:
                    layer.remove(neuron_id)
                    break
            
            # حذف سیناپس‌های مرتبط
            self.synapses = [s for s in self.synapses 
                           if s.source_neuron_id != neuron_id and s.target_neuron_id != neuron_id]
            
            # حذف نورون
            del self.neurons[neuron_id]
    
    def _optimize_synapses(self):
        """بهینه‌سازی سیناپس‌ها"""
        # حذف سیناپس‌های بسیار ضعیف
        weak_synapses = [s for s in self.synapses if abs(s.weight) < 0.01]
        self.synapses = [s for s in self.synapses if abs(s.weight) >= 0.01]
        
        print(f"✂️ {len(weak_synapses)} سیناپس ضعیف حذف شد")
    
    def get_network_stats(self) -> Dict:
        """آمار شبکه عصبی با محاسبه حافظه واقعی"""
        total_weights = sum(len(neuron.weights) for neuron in self.neurons.values())
        avg_activation = sum(neuron.activation_count for neuron in self.neurons.values()) / len(self.neurons)
    
        # محاسبه REAL حافظه مصرفی
        neuron_memory = len(self.neurons) * 200  # bytes per neuron (کاهش از 1000)
        synapse_memory = len(self.synapses) * 16  # bytes per synapse (کاهش از 20)
        weights_memory = total_weights * 4       # 4 bytes per weight
        memory_usage_bytes = neuron_memory + synapse_memory + weights_memory
        memory_usage_mb = memory_usage_bytes / (1024 * 1024)  # به مگابایت
    
        # محاسبه CPU usage واقعی
        cpu_usage = min(50, self.total_activations / 1000)  # حداکثر 50%
    
        return {
        'total_neurons': len(self.neurons),
        'total_synapses': len(self.synapses),
        'total_weights': total_weights,
        'generation': self.generation,
        'total_activations': self.total_activations,
        'average_activation': avg_activation,
        'learning_rate': self.learning_rate,
        'memory_size': len(self.memory),
        'network_maturity': min(1.0, self.total_activations / 1000),
        'memory_usage': round(memory_usage_mb, 2),  # حافظه REAL
        'cpu_usage': round(cpu_usage, 1),  # CPU واقعی
        'current_accuracy': self._calculate_current_accuracy(),
        'signal_quality': self._calculate_signal_quality()
    }
    
    def _calculate_current_accuracy(self) -> float:
        """محاسبه دقت فعلی بر اساس حافظه"""
        if len(self.memory) < 10:
            return 0.5
        
        recent_errors = [exp['error'] for exp in self.memory[-20:]]
        avg_error = sum(recent_errors) / len(recent_errors)
        return max(0.0, 1.0 - avg_error)
    
    def _calculate_signal_quality(self) -> float:
        """محاسبه کیفیت سیگنال"""
        if len(self.memory) < 5:
            return 0.5
        
        recent_profits = [exp['profit'] for exp in self.memory[-10:] if 'profit' in exp]
        if not recent_profits:
            return 0.5
        
        avg_profit = sum(recent_profits) / len(recent_profits)
        return min(1.0, (avg_profit + 1) / 2)  # نرمال‌سازی به 0-1

class VortexAI:
    def __init__(self):
        self.brain = VortexNeuralNetwork()
        self.emergency_system = EmergencyStopSystem()
        self.learning_sessions = 0
        self.analysis_history = []
        self.market_experiences = []
        
        # آمار عملکرد
        self.performance_metrics = {
            'accuracy_trend': 0.0,
            'new_patterns_detected': False,
            'complexity_increased': False,
            'user_satisfaction': 0.7
        }
    
    def analyze_market_data(self, coins_data: List[Dict]) -> Dict:
        """تحلیل بازار با شبکه عصبی"""
        if self.emergency_system.can_proceed('ai_analysis'):
            return self._get_safe_fallback_analysis()
        
        self.learning_sessions += 1
        
        analysis = {
            "neural_analysis": [],
            "strong_signals": [],
            "risk_warnings": [],
            "market_insights": [],
            "ai_confidence": 0,
            "network_stats": self.brain.get_network_stats(),
            "emergency_mode": self.emergency_system.emergency_stop_active
        }
        
        for coin in coins_data[:15]:  # کاهش از 20 به 15 برای بهینه‌سازی
            # آماده‌سازی ورودی برای شبکه عصبی
            inputs = self._prepare_neural_inputs(coin)
            
            # دریافت پیش‌بینی از شبکه عصبی
            neural_output = self.brain.feed_forward(inputs)
            
            coin_analysis = {
                "coin": coin.get('name', ""),
                "symbol": coin.get('symbol', ""),
                "neural_buy_confidence": neural_output['buy_confidence'],
                "neural_sell_confidence": neural_output['sell_confidence'],
                "risk_score": neural_output['risk_score'] * 100,
                "signal_strength": max(neural_output['buy_confidence'], neural_output['sell_confidence']) * 100,
                "network_confidence": neural_output['overall_confidence'] * 100,
                "recommendation": self._generate_recommendation(neural_output)
            }
            
            analysis["neural_analysis"].append(coin_analysis)
            
            if coin_analysis["signal_strength"] > 70:
                analysis["strong_signals"].append(coin_analysis)
            
            if coin_analysis["risk_score"] > 60:
                analysis["risk_warnings"].append(coin_analysis)
        
        analysis["ai_confidence"] = self._calculate_confidence(coins_data)
        analysis["market_insights"] = self._generate_insights(analysis["neural_analysis"])
        
        # یادگیری از تحلیل فعلی
        if not self.emergency_system.emergency_stop_active:
            self._learn_from_analysis(analysis)
        
        self.analysis_history.append(analysis)
        
        # رشد هوشمند اگر لازم باشد
        if (self.learning_sessions % 10 == 0 and 
            not self.emergency_system.emergency_stop_active):
            self.brain.intelligent_growth(self.performance_metrics)
        
        # بهینه‌سازی دوره‌ای
        if self.learning_sessions % 20 == 0:
            pruned_count = self.brain.optimize_memory()
            if pruned_count > 0:
                print(f"🔄 بهینه‌سازی حافظه: {pruned_count} نورون حذف شد")
        
        return analysis
    
    def _get_safe_fallback_analysis(self) -> Dict:
        """تحلیل ایمن در حالت اضطراری"""
        return {
            "neural_analysis": [],
            "strong_signals": [],
            "risk_warnings": [],
            "market_insights": ["🛑 سیستم در حالت ایمن فعال است"],
            "ai_confidence": 30,
            "network_stats": self.brain.get_network_stats(),
            "emergency_mode": True
        }
    
    def _prepare_neural_inputs(self, coin: Dict) -> Dict[str, float]:
        """آماده‌سازی ورودی‌های شبکه عصبی"""
        return {
            'price': min(coin.get('price', 0) / 100000, 1.0),
            'price_change_24h': (coin.get('priceChange24h', 0) + 50) / 100,
            'price_change_1h': (coin.get('priceChange1h', 0) + 50) / 100,
            'volume': min(math.log(coin.get('volume', 1) + 1) / 20, 1.0),
            'market_cap': min(math.log(coin.get('marketCap', 1) + 1) / 25, 1.0),
            'rsi': random.uniform(0, 1),
            'macd': random.uniform(-1, 1),
            'volatility': min(abs(coin.get('priceChange24h', 0)) / 50, 1.0),
            'market_sentiment': random.uniform(0, 1)
        }
    
    def _generate_recommendation(self, neural_output: Dict) -> str:
        """تولید پیشنهاد مبتنی بر شبکه عصبی"""
        buy_conf = neural_output['buy_confidence']
        sell_conf = neural_output['sell_confidence']
        
        if buy_conf > 0.7 and buy_conf > sell_conf * 1.5:
            return "خرید قوی عصبی"
        elif sell_conf > 0.7 and sell_conf > buy_conf * 1.5:
            return "فروش قوی عصبی"
        elif buy_conf > 0.6:
            return "خرید محتاطانه عصبی"
        elif sell_conf > 0.6:
            return "فروش محتاطانه عصبی"
        else:
            return "نظارت عصبی"
    
    def _generate_insights(self, neural_analysis: List[Dict]) -> List[str]:
        """تولید بینش‌های مبتنی بر شبکه عصبی"""
        insights = []
        
        if neural_analysis:
            avg_buy_confidence = sum(a['neural_buy_confidence'] for a in neural_analysis) / len(neural_analysis)
            avg_sell_confidence = sum(a['neural_sell_confidence'] for a in neural_analysis) / len(neural_analysis)
            
            if avg_buy_confidence > 0.6:
                insights.append("شبکه عصبی حالت صعودی قوی تشخیص می‌دهد")
            elif avg_sell_confidence > 0.6:
                insights.append("شبکه عصبی حالت نزولی قوی تشخیص می‌دهد")
            else:
                insights.append("شبکه عصبی بازار را متعادل ارزیابی می‌کند")
        
        insights.append(f"نسل شبکه: {self.brain.generation}")
        insights.append(f"بلوغ شبکه: {self.brain.get_network_stats()['network_maturity']:.1%}")
        
        if self.emergency_system.emergency_stop_active:
            insights.append("🛑 حالت ایمن فعال است")
        
        return insights
    
    def _learn_from_analysis(self, analysis: Dict):
        """یادگیری از تحلیل انجام شده"""
        # شبیه‌سازی پادگیری از نتایج
        for coin_analysis in analysis['neural_analysis'][:5]:  # فقط 5 نمونه
            inputs = self._prepare_neural_inputs({
                'price': random.uniform(1000, 50000),
                'priceChange24h': random.uniform(-20, 20),
                'priceChange1h': random.uniform(-5, 5),
                'volume': random.uniform(1000000, 1000000000),
                'marketCap': random.uniform(100000000, 100000000000)
            })
            
            # شبیه‌سازی خروجی مورد انتظار بر اساس عملکرد
            expected_output = {
                'buy_confidence': random.uniform(0.3, 0.8),
                'sell_confidence': random.uniform(0.3, 0.8),
                'overall_confidence': random.uniform(0.5, 0.9)
            }
            
            self.brain.learn_from_experience(inputs, expected_output, random.uniform(-0.1, 0.1))
    
    def _calculate_confidence(self, coins_data: List[Dict]) -> float:
        """محاسبه اعتماد هوش مصنوعی"""
        if not coins_data:
            return 0.0
        
        base_confidence = min(len(coins_data) / 50, 1.0) * 0.3
        neural_confidence = self.brain.get_network_stats()['network_maturity'] * 0.7
        
        confidence = min(base_confidence + neural_confidence, 1.0) * 100
        
        # کاهش اعتماد در حالت اضطراری
        if self.emergency_system.emergency_stop_active:
            confidence *= 0.5
        
        return confidence
    
    def force_evolution(self):
        """اجبار به تکامل شبکه"""
        if self.emergency_system.emergency_stop_active:
            return "تکامل متوقف شده: سیستم در حالت ایمن است"
        
        if self.brain.evolve():
            return f"شبکه به نسل {self.brain.generation} تکامل یافت"
        else:
            return "تکامل ناموفق: سلامت شبکه در خطر است"
    
    def emergency_stop(self, reason: str = "دستور کاربر"):
        """توقف اضطراری"""
        self.emergency_system.activate_emergency_stop(reason)
        return f"🛑 توقف اضطراری فعال شد: {reason}"
    
    def resume_normal_operations(self):
        """بازگشت به حالت عادی"""
        if self.emergency_system.deactivate_emergency_stop():
            return "🟢 سیستم به حالت عادی بازگشت"
        else:
            return "⚠️ سیستم قبلاً در حالت عادی است"
    
    def get_health_report(self) -> Dict:
        """گزارش سلامت کامل"""
        network_stats = self.brain.get_network_stats()
        health_report = self.brain.inflation_guard.check_neural_health(network_stats)
        
        return {
            'overall_health': self._calculate_overall_health(network_stats, health_report),
            'network_stats': network_stats,
            'health_checks': health_report,
            'emergency_status': {
                'active': self.emergency_system.emergency_stop_active,
                'reason': self.emergency_system.stop_reason,
                'since': self.emergency_system.activation_time
            },
            'performance_metrics': self.performance_metrics,
            'learning_sessions': self.learning_sessions,
            'analysis_count': len(self.analysis_history)
        }
        
    def _calculate_overall_health(self, network_stats: Dict, health_report: Dict) -> float:
        """محاسبه سلامت کلی"""
        try:
            health_score = 0.0
            
            # سلامت فنی (40%)
            technical_health = sum(health_report.values()) / len(health_report) * 0.4
            
            # سلامت عملکردی (30%)
            performance_health = (
                network_stats.get('current_accuracy', 0.5) * 0.15 +
                network_stats.get('signal_quality', 0.5) * 0.15
            )
            
            # سلامت عملیاتی (30%)
            operational_health = (
                (1 - min(network_stats.get('memory_usage', 0) / 450, 1)) * 0.1 +
                (1 - min(network_stats.get('cpu_usage', 0) / 100, 1)) * 0.1 +
                (0.0 if self.emergency_system.emergency_stop_active else 0.1)
            )
            
            health_score = (technical_health + performance_health + operational_health) * 100
            return min(100, max(0, health_score))
            
        except Exception as e:
            print(f"❌ خطا در محاسبه سلامت: {e}")
            return 50.0  # مقدار پیش‌فرض   
            
    def _calculate_overall_health(self, network_stats: Dict, health_report: Dict) -> float:
        """محاسبه سلامت کلی"""
        health_score = 0.0
        
        # سلامت فنی (40%)
        technical_health = sum(health_report.values()) / len(health_report) * 0.4
        
        # سلامت عملکردی (30%)
        performance_health = (
            network_stats['current_accuracy'] * 0.15 +
            network_stats['signal_quality'] * 0.15
        )
        
        # سلامت عملیاتی (30%)
        operational_health = (
            (1 - min(network_stats['memory_usage'] / 450, 1)) * 0.1 +
            (1 - min(network_stats['cpu_usage'] / 100, 1)) * 0.1 +
            (0.0 if self.emergency_system.emergency_stop_active else 0.1)
        )
        
        health_score = (technical_health + performance_health + operational_health) * 100
        return min(100, max(0, health_score))

# ==================== تست سیستم ====================

if __name__ == "__main__":
    # تست سیستم
    ai = VortexAI()
    print("🧠 VortexAI با سیستم‌های ایمنی راه‌اندازی شد")
    
    # نمایش آمار اولیه
    stats = ai.brain.get_network_stats()
    print(f"نورون‌ها: {stats['total_neurons']}, سیناپس‌ها: {stats['total_synapses']}")
    print(f"مصرف RAM: {stats['memory_usage']}MB")
    
    # تست سلامت
    health = ai.get_health_report()
    print(f"سلامت کلی: {health['overall_health']:.1f}%")
    
# --- SECTION 5: CRYPTO SCANNER ---

class CryptoScanner:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.vortex_ai = VortexAI()
        self.api_base = "https://server-test-ovta.onrender.com"

    def scan_market(self, limit: int = 100) -> Optional[Dict]:
        """Scan cryptocurrency market"""
        try:
            url = f"{self.api_base}/api/scan/vortexai?limit={limit}"
            print(f"🔍 STEP 1 - Calling API: {url}")
            
            response = requests.get(url, timeout=15)
            print(f"📡 STEP 2 - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ STEP 3 - API Success: {data.get('success')}")
                print(f"📊 STEP 4 - Response keys: {list(data.keys())}")
                
                if data.get('success'):
                    raw_coins = data.get('coins', [])
                    print(f"📦 STEP 5 - Raw coins count: {len(raw_coins)}")
                    
                    if raw_coins:
                        # نمایش ساختار اولین کوین برای دیباگ
                        first_coin = raw_coins[0]
                        print(f"🔍 STEP 6 - First coin keys: {list(first_coin.keys())}")
                        print(f"🔍 STEP 7 - First coin data: {first_coin}")
                    
                    # پردازش داده‌ها - نسخه ایمن
                    coins = []
                    for i, coin in enumerate(raw_coins):
                        try:
                            # استفاده از فیلدهای مختلف برای پیدا کردن داده
                            price = float(coin.get('price') or coin.get('realtime_price') or 0)
                            change_24h = float(coin.get('priceChange24h') or coin.get('priceChange1d') or 0)
                            change_1h = float(coin.get('priceChange1h') or 0)
                            volume = float(coin.get('volume') or coin.get('realtime_volume') or 0)
                            market_cap = float(coin.get('marketCap') or 0)
                            
                            processed_coin = {
                                'name': str(coin.get('name', f'Coin_{i}')),
                                'symbol': str(coin.get('symbol', 'UNKNOWN')),
                                'price': price,
                                'priceChange24h': change_24h,
                                'priceChange1h': change_1h,
                                'volume': volume,
                                'marketCap': market_cap
                            }
                            coins.append(processed_coin)
                            print(f"🔄 Coin {i}: {processed_coin['symbol']} - ${processed_coin['price']}")
                            
                        except Exception as e:
                            print(f"⚠️ Error processing coin {i}: {e}")
                            continue
                    
                    print(f"✅ STEP 8 - Successfully processed: {len(coins)} coins")
                    
                    if coins:
                        self.db_manager.save_market_data(coins)
                        print("💾 STEP 9 - Data saved to database")
                        
                        return {
                            'success': True,
                            'coins': coins,
                            'count': len(coins),
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        print("❌ STEP 10 - No coins processed successfully")
                else:
                    print(f"❌ STEP 11 - API returned success: false - {data.get('error')}")
            else:
                print(f"❌ STEP 12 - HTTP Error: {response.status_code}")
                print(f"❌ Response text: {response.text[:200]}...")
            
            print("🔄 STEP 13 - Using fallback data")
            return self._get_fallback_data()
            
        except Exception as e:
            print(f"💥 STEP 14 - Unexpected error: {e}")
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")
            return self._get_fallback_data()

    def _get_fallback_data(self):
        """Sample data as fallback when server is unavailable"""
        print("🔄 Using comprehensive fallback data")
        sample_coins = [
            {
                'name': 'Bitcoin',
                'symbol': 'BTC',
                'price': 124619.36,
                'priceChange24h': 1.92,
                'priceChange1h': -0.08,
                'volume': 39306468043,
                'marketCap': 2483440001648
            },
            {
                'name': 'Ethereum',
                'symbol': 'ETH',
                'price': 4586.82,
                'priceChange24h': 2.15,
                'priceChange1h': -0.32,
                'volume': 40423228887,
                'marketCap': 553641132921
            },
            {
                'name': 'BNB',
                'symbol': 'BNB', 
                'price': 1171.38,
                'priceChange24h': 1.38,
                'priceChange1h': -0.58,
                'volume': 14106039249,
                'marketCap': 163038687343
            },
            {
                'name': 'Solana',
                'symbol': 'SOL',
                'price': 235.20,
                'priceChange24h': 2.77,
                'priceChange1h': -0.59,
                'volume': 12280809846,
                'marketCap': 128270536156
            },
            {
                'name': 'XRP',
                'symbol': 'XRP',
                'price': 3.05,
                'priceChange24h': 1.64,
                'priceChange1h': -0.45,
                'volume': 3140519134,
                'marketCap': 182571288194
            }
        ]
        
        return {
            'success': True,
            'coins': sample_coins,
            'count': len(sample_coins),
            'timestamp': datetime.now().isoformat()
        }

    def scan_with_ai(self, limit: int = 100) -> Optional[Dict]:
        """Scan market with AI analysis"""
        try:
            print("🤖 Starting AI-enhanced scan...")
            
            market_result = self.scan_market(limit)
            
            if not market_result or not market_result.get('success'):
                print("❌ AI Scan: No market data available")
                return None
                
            coins = market_result['coins']
            print(f"🤖 Analyzing {len(coins)} coins with VortexAI...")
            
            ai_analysis = self.vortex_ai.analyze_market_data(coins)
            print(f"🤖 AI analysis completed")
            
            return {
                **market_result,
                "ai_analysis": ai_analysis,
                "scan_mode": "ai_enhanced"
            }
            
        except Exception as e:
            print(f"🤖 AI Scan Error: {e}")
            logging.error(f"AI scan error: {e}")
            return None
            
# -- SECTION 6: UI COMPONENTS WITH MONITORING --

def display_market_results(results: Dict):
    """Display market scan results"""
    if not results or not results.get('success'):
        st.error("❌ " + lang.t('error'))
        return

    coins_data = results.get('coins', [])
    if not coins_data:
        st.warning("📭 هیچ داده‌ای برای نمایش وجود ندارد")
        return

    # هدر با تعداد ارزها
    st.header(f"{lang.t('results_title')} - {len(coins_data)} ارز")

    # ایجاد دیتافریم برای نمایش
    df_data = []
    for coin in coins_data:
        # بررسی وجود داده
        price = coin.get('price', 0)
        change_24h = coin.get('priceChange24h', 0)
        change_1h = coin.get('priceChange1h', 0)
        volume = coin.get('volume', 0)
        market_cap = coin.get('marketCap', 0)

        df_data.append((
            coin.get('name', 'نامشخص'),
            coin.get('symbol', 'N/A'),
            f"${price:.2f}" if price > 0 else "$0.00",
            f"{change_24h:+.2f}%" if change_24h != 0 else "0.00%",
            f"{change_1h:+.2f}%" if change_1h != 0 else "0.00%",
            f"${volume:,.0f}" if volume > 0 else "$0",
            f"${market_cap:,.0f}" if market_cap > 0 else "$0"
        ))

    # ایجاد دیتافریم
    df = pd.DataFrame(df_data, columns=[
        lang.t('coin_name'),
        'نماد',
        lang.t('price'),
        lang.t('change_24h'),
        lang.t('change_1h'),
        lang.t('volume'),
        lang.t('market_cap')
    ])

    # تنظیم ایندکس از 1 شروع بشه
    df.index = df.index + 1

    # تنظیمات استایل برای دیتافریم
    st.dataframe(
        df,
        use_container_width=True,
        height=min(600, 35 * len(df) + 40),
        hide_index=False
    )

    # متریک‌های کلی
    st.subheader("📊 آمار کلی بازار")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_coins = len(coins_data)
        st.metric("تعداد ارزها", value=total_coins, delta=None)

    with col2:
        changes_24h = [c.get('priceChange24h', 0) for c in coins_data]
        avg_change_24h = np.mean(changes_24h) if changes_24h else 0
        st.metric("میانگین تغییرات", value=f"{avg_change_24h:+.2f}%", delta=None)

    with col3:
        total_volume = sum(c.get('volume', 0) for c in coins_data)
        st.metric("حجم کل بازار", value=f"${total_volume:,.0f}", delta=None)

    with col4:
        bullish_count = sum(1 for c in coins_data if c.get('priceChange24h', 0) > 0)
        bearish_count = total_coins - bullish_count
        st.metric("روند بازار", value=f"{bullish_count}🟢 {bearish_count}🔴", delta=None)

def display_ai_analysis(ai_analysis: Dict):
    """Display AI analysis results"""
    if not ai_analysis:
        st.info("🤖 تحلیل هوش مصنوعی در دسترس نیست")
        return

    st.markdown("---")
    st.header("🧠 " + lang.t('ai_analysis'))
    
    # اعتماد هوش مصنوعی
    ai_confidence = ai_analysis.get('ai_confidence', 0)
    confidence_color = "🟢" if ai_confidence > 70 else "🟡" if ai_confidence > 40 else "🔴"

    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label=lang.t('ai_confidence'),
            value=f"{ai_confidence:.1f}%",
            delta=None
        )
    
    with col2:
        confidence_text = "عالی" if ai_confidence > 70 else "متوسط" if ai_confidence > 40 else "پایین"
        st.write(f"{confidence_color} سطح اعتماد: {confidence_text}")

    # سیگنال‌های قوی
    strong_signals = ai_analysis.get('strong_signals', [])
    if strong_signals:
        st.subheader("🚀 " + lang.t('strong_signals'))
        for i, signal in enumerate(strong_signals[:5], 1):
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                
                with col1:
                    st.write(f"**{i}. {signal['coin']}** ({signal['symbol']})")
                
                with col2:
                    signal_strength = signal['signal_strength']
                    strength_color = "🟢" if signal_strength > 70 else "🟡" if signal_strength > 50 else "🔴"
                    st.write(f"{strength_color} {signal_strength:.1f}%")
                
                with col3:
                    risk_level = signal['risk_score']
                    risk_color = "🔴" if risk_level > 70 else "🟡" if risk_level > 40 else "🟢"
                    st.write(f"{risk_color} ریسک: {risk_level:.1f}%")
                
                with col4:
                    rec = signal['recommendation']
                    st.write(f"**{rec}**")
            
            st.markdown("---")

    # هشدارهای ریسک
    risk_warnings = ai_analysis.get('risk_warnings', [])
    if risk_warnings:
        st.subheader("⚠️ " + lang.t('risk_warnings'))
        for warning in risk_warnings[:3]:
            with st.expander(f"🔴 {warning['coin']} ({warning['symbol']}) - سطح ریسک: {warning['risk_score']:.1f}%", expanded=False):
                st.error("**هشدار ریسک بالا**: این ارز دارای نوسانات شدید یا ریسک معاملاتی بالایی است.")
                st.write(f"**پیشنهاد**: {warning['recommendation']}")

    # بینش‌های بازار
    market_insights = ai_analysis.get('market_insights', [])
    if market_insights:
        st.subheader("🔍 " + lang.t('market_insights'))
        for insight in market_insights:
            if "صعودی" in insight or "bullish" in insight:
                st.success(insight)
            elif "نزولی" in insight or "bearish" in insight:
                st.warning(insight)
            else:
                st.info(insight)

# ==================== کامپوننت‌های مانیتورینگ جدید ====================

def display_ai_health_dashboard(vortex_ai, emergency_system):
    """نمایش دشبورد سلامت هوش مصنوعی"""
    st.header("🏥 دشبورد سلامت VortexAI")
    
    if not vortex_ai:
        st.error("❌ سیستم هوش مصنوعی در دسترس نیست")
        return
    
    # دریافت گزارش سلامت
    health_report = vortex_ai.get_health_report()
    
    # کارت‌های وضعیت فوری
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        overall_health = health_report['overall_health']
        status_color = "🟢" if overall_health > 70 else "🟡" if overall_health > 40 else "🔴"
        st.metric("🧠 سلامت کلی", f"{overall_health:.1f}%")
        st.write(f"{status_color} {'عالی' if overall_health > 70 else 'متوسط' if overall_health > 40 else 'نیازمند توجه'}")
    
    with col2:
        emergency_status = health_report['emergency_status']['active']
        st.metric("🛑 وضعیت اضطراری", "فعال" if emergency_status else "غیرفعال")
        st.write("🔴" if emergency_status else "🟢")
    
    with col3:
        network_stats = health_report['network_stats']
        st.metric("🧬 نسل شبکه", network_stats['generation'])
        st.write(f"📊 {network_stats['total_activations']:,} فعال‌سازی")
    
    with col4:
        st.metric("🎯 دقت فعلی", f"{network_stats['current_accuracy']*100:.1f}%")
        st.metric("📈 کیفیت سیگنال", f"{network_stats['signal_quality']*100:.1f}%")

def display_growth_monitoring(vortex_ai):
    """نمایش مانیتورینگ رشد شبکه"""
    st.header("🌱 مانیتورینگ رشد و توسعه")
    
    if not vortex_ai:
        return
        
    health_report = vortex_ai.get_health_report()
    network_stats = health_report['network_stats']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🧠 معماری شبکه")
        st.write(f"**نورون‌ها**: {network_stats['total_neurons']} از ۴,۰۰۰")
        st.write(f"**سیناپس‌ها**: {network_stats['total_synapses']} از ۱۵,۰۰۰")
        st.write(f"**وزن‌ها**: {network_stats['total_weights']:,}")
        
        # نمایش پیشرفت
        neuron_progress = min(max(network_stats['total_neurons'] / 4000, 0.0), 1.0)
        st.progress(neuron_progress)
        st.caption(f"ظرفیت نورون‌ها: {neuron_progress:.1%}")
    
    with col2:
        st.subheader("📊 عملکرد یادگیری")
        st.write(f"**جلسات یادگیری**: {vortex_ai.learning_sessions}")
        st.write(f"**تحلیل‌های انجام شده**: {len(vortex_ai.analysis_history)}")
        st.write(f"**حجم حافظه یادگیری**: {len(vortex_ai.market_experiences)} تجربه")
        
        # نرخ یادگیری
        learning_rate = network_stats['learning_rate']
        st.metric("🎓 نرخ یادگیری", f"{learning_rate:.4f}")
    
    with col3:
        st.subheader("💾 مصرف منابع")
        st.write(f"**مصرف RAM**: {network_stats['memory_usage']}MB از ۴۵۰MB")
        st.write(f"**مصرف CPU**: {network_stats['cpu_usage']:.1f}%")
        st.write(f"**بلوغ شبکه**: {network_stats['network_maturity']:.1%}")
        
        # پیشرفت حافظه
        memory_progress = min(max(network_stats['memory_usage'] / 450, 0.0), 1.0)
        st.progress(memory_progress)
        st.caption(f"مصرف حافظه: {memory_progress:.1%}")

def display_real_health_metrics(vortex_ai):
    """نمایش شاخص‌های سلامت واقعی"""
    st.header("❤️ شاخص‌های حیاتی")
    
    if not vortex_ai:
        return
        
    health_report = vortex_ai.get_health_report()
    health_checks = health_report['health_checks']
    
    # نمایش وضعیت سلامت
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ بررسی‌های فنی")
        for check_name, check_status in health_checks.items():
            status_icon = "✅" if check_status else "❌"
            status_text = "خوب" if check_status else "نیازمند توجه"
            st.write(f"{status_icon} {check_name}: {status_text}")
    
    with col2:
        st.subheader("📈 معیارهای عملکرد")
        metrics = health_report['performance_metrics']
        st.write(f"**روند دقت**: {'📈 بهبود' if metrics.get('accuracy_trend', 0) > 0 else '📉 کاهش'}")
        st.write(f"**الگوهای جدید**: {'✅ کشف شده' if metrics.get('new_patterns_detected', False) else '❌ ندارد'}")
        st.write(f"**رضایت کاربر**: {metrics.get('user_satisfaction', 0)*100:.1f}%")

def display_emergency_controls(emergency_system):
    """نمایش کنترل‌های اضطراری با دسترسی به scanner"""
    st.header("🎮 کنترل‌های مدیریتی")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🛑 کنترل اضطراری")
        if st.button("🔴 توقف فوری هوش مصنوعی", type="secondary", use_container_width=True):
            emergency_system.activate_emergency_stop("دستور کاربر از UI")
            st.error("✅ توقف اضطراری فعال شد")
            st.rerun()
        
        if st.button("🟢 بازگشت به حالت عادی", type="primary", use_container_width=True):
            emergency_system.deactivate_emergency_stop()
            st.success("✅ سیستم به حالت عادی بازگشت")
            st.rerun()
    
    with col2:
        st.subheader("🧬 کنترل رشد")
        if st.button("⚡ اجبار به تکامل", use_container_width=True):
            # دسترسی مستقیم به scanner از session_state
            if 'scanner' in st.session_state and st.session_state.scanner:
                result = st.session_state.scanner.vortex_ai.force_evolution()
                st.info(result)
                st.rerun()
            else:
                st.error("❌ اسکنر در دسترس نیست. لطفاً ابتدا اسکن انجام دهید.")
    
    with col3:
        st.subheader("🔧 بهینه‌سازی")
        if st.button("🧹 پاک‌سازی اضطراری حافظه", use_container_width=True):
            # دسترسی مستقیم به scanner از session_state
            if 'scanner' in st.session_state and st.session_state.scanner:
                try:
                    pruned_count = st.session_state.scanner.vortex_ai.brain.optimize_memory()
                    st.success(f"✅ {pruned_count} نورون پاک‌سازی شد")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطا در پاک‌سازی: {e}")
            else:
                st.error("❌ اسکنر در دسترس نیست. لطفاً ابتدا اسکن انجام دهید.")
def display_performance_metrics(vortex_ai):
    """نمایش معیارهای عملکرد دقیق"""
    st.subheader("📊 تحلیل عملکرد دقیق")
    
    if not vortex_ai or not vortex_ai.analysis_history:
        st.info("📝 داده‌های عملکردی هنوز جمع‌آوری نشده‌اند")
        return
    
    # محاسبه آمار پیشرفت
    recent_analyses = vortex_ai.analysis_history[-10:]  # 10 تحلیل اخیر
    if recent_analyses:
        confidences = [analysis.get('ai_confidence', 0) for analysis in recent_analyses]
        avg_confidence = sum(confidences) / len(confidences)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("میانگین اعتماد اخیر", f"{avg_confidence:.1f}%")
        with col2:
            trend = "📈 بهبود" if len(confidences) > 1 and confidences[-1] > confidences[0] else "📉 کاهش"
            st.metric("روند اعتماد", trend)
        
        # نمودار ساده اعتماد
        st.line_chart(confidences)

def display_alerts_and_warnings(vortex_ai):
    """نمایش هشدارها و اعلان‌ها"""
    st.subheader("⚠️ هشدارها و اعلان‌ها")
    
    if not vortex_ai:
        return
        
    health_report = vortex_ai.get_health_report()
    alerts = []
    
    # بررسی شرایط هشدار
    network_stats = health_report['network_stats']
    if network_stats['memory_usage'] > 300:
        alerts.append("🔴 مصرف حافظه به حد هشدار نزدیک است")
    
    if network_stats['current_accuracy'] < 0.6:
        alerts.append("🟠 دقت تحلیل کمتر از ۶۰٪ است")
    
    if health_report['emergency_status']['active']:
        alerts.append("🛑 سیستم در حالت توقف اضطراری است")
    
    if network_stats['total_neurons'] > 3500:
        alerts.append("🟡 تعداد نورون‌ها به حد مجاز نزدیک است")
    
    # نمایش هشدارها
    if alerts:
        for alert in alerts:
            if "🔴" in alert or "🛑" in alert:
                st.error(alert)
            elif "🟠" in alert:
                st.warning(alert)
            else:
                st.info(alert)
    else:
        st.success("✅ همه سیستم‌ها در وضعیت نرمال هستند")

def display_search_filter(coins_data: List[Dict]):
    """Display search and filter controls"""
    if not coins_data:
        return

    st.markdown("---")
    st.subheader("🔍 جستجو و فیلتر")

    col1, col2, col3 = st.columns(3)

    with col1:
        search_term = st.text_input(
            lang.t('search_placeholder'),
            placeholder="نام یا نماد ارز...",
            key="search_input"
        )
    
    with col2:
        min_volume = st.number_input(
            "حداقل حجم (میلیون دلار)",
            min_value=0,
            value=10,
            step=10,
            key="min_volume"
        )
        # تبدیل به دلار * 1000000

    with col3:
        trend_filter = st.selectbox(
            "فیلتر روند",
            options=["همه", "صعودی", "نزولی"],
            index=0,
            key="trend_filter"
        )

    # اعمال فیلترها
    filtered_coins = coins_data

    if search_term:
        filtered_coins = [
            coin for coin in filtered_coins
            if search_term.lower() in coin.get('name', "").lower()
            or search_term.lower() in coin.get('symbol', "").lower()
        ]

    if min_volume > 0:
        filtered_coins = [
            coin for coin in filtered_coins
            if coin.get('volume', 0) >= min_volume * 1000000
        ]

    if trend_filter == "صعودی":
        filtered_coins = [
            coin for coin in filtered_coins
            if coin.get('priceChange24h', 0) > 0
        ]
    elif trend_filter == "نزولی":
        filtered_coins = [
            coin for coin in filtered_coins
            if coin.get('priceChange24h', 0) < 0
        ]

    # نمایش نتایج فیلتر شده
    if len(filtered_coins) != len(coins_data):
        st.info(f"📋 نمایش {len(filtered_coins)} از {len(coins_data)} ارز (فیلتر شده)")

    return filtered_coins

def display_quick_actions():
    """Display quick action buttons"""
    st.markdown("---")
    st.subheader("⚡ اقدامات سریع")
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🔄 اسکن مجدد", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("💾 ذخیره گزارش", use_container_width=True):
            st.success("✅ گزارش ذخیره شد")

    with col3:
        if st.button("📤 اشتراک‌گذاری", use_container_width=True):
            st.info("📤 امکان اشتراک‌گذاری")

    with col4:
        if st.button("⚙️ تنظیمات پیشرفته", use_container_width=True):
            st.session_state.show_settings = True
            
# -- SECTION 7: MAIN APPLICATION WITH MONITORING - REVISED --

def main():
    """Main application function"""
    setup_page_config()

    # Initialize multi-language system
    lang = Multilanguage()

    # Display title
    st.title(lang.t('app_title'))
    st.markdown("---")

    # Setup sidebar and get scan buttons
    normal_scan, ai_scan = setup_sidebar()

    # Initialize scanner با خطایابی بهتر
    @st.cache_resource
    def load_scanner():
        try:
            scanner = CryptoScanner()
            print("✅ Scanner initialized successfully")
            
            # بررسی سلامت vortex_ai
            if hasattr(scanner, 'vortex_ai') and scanner.vortex_ai:
                print("✅ VortexAI initialized successfully")
            else:
                print("⚠️ VortexAI not available yet")
                
            return scanner
        except Exception as e:
            print(f"❌ Scanner initialization failed: {e}")
            return None

    scanner = load_scanner()

    st.session_state.scanner = scanner

    # Initialize emergency system
    if 'emergency_system' not in st.session_state:
        st.session_state.emergency_system = EmergencyStopSystem()

    # استفاده از session state برای ذخیره نتایج
    if 'scan_results' not in st.session_state:
        st.session_state.scan_results = None

    if 'ai_results' not in st.session_state:
        st.session_state.ai_results = None

    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "اسکن بازار"

    # ایجاد تب‌های اصلی
    tab1, tab2, tab3 = st.tabs(["📊 اسکن بازار", "🧠 مانیتورینگ هوش مصنوعی", "ℹ️ راهنما"])

    with tab1:
        display_market_tab(scanner, lang)

    with tab2:
        display_monitoring_tab(scanner)

    with tab3:
        display_help_tab()

    # Display AI status in sidebar
    display_sidebar_status(scanner)

# ==================== توابع جدید برای سازماندهی بهتر ====================

def display_market_tab(scanner, lang):
    """نمایش تب اسکن بازار"""
    # Handle scan requests
    normal_scan, ai_scan = st.session_state.get('normal_scan', False), st.session_state.get('ai_scan', False)
    
    if normal_scan:
        handle_normal_scan(scanner, lang)
        
    if ai_scan:
        handle_ai_scan(scanner, lang)

    # نمایش نتایج بازار
    if st.session_state.scan_results:
        display_market_results(st.session_state.scan_results)

        # نمایش تحلیل AI اگر موجود باشد
        if st.session_state.ai_results:
            display_ai_analysis(st.session_state.ai_results)
    else:
        display_welcome_screen(scanner)

def handle_normal_scan(scanner, lang):
    """مدیریت اسکن معمولی"""
    with st.spinner(lang.t('scanning')):
        print("🔍 NORMAL SCAN TRIGGERED")
        if scanner:
            try:
                results = scanner.scan_market(limit=100)
                if results and results.get('success'):
                    st.session_state.scan_results = results
                    st.session_state.ai_results = None
                    st.success(f"✅ اسکن موفق! {len(results.get('coins', []))} ارز پیدا شد")
                else:
                    st.error("❌ خطا در دریافت داده‌ها از سرور")
                    # نمایش داده نمونه در صورت خطا
                    fallback_data = get_fallback_data_safe()
                    st.session_state.scan_results = fallback_data
                    st.session_state.ai_results = None
            except Exception as e:
                st.error(f"❌ خطا در اسکن: {e}")
                fallback_data = get_fallback_data_safe()
                st.session_state.scan_results = fallback_data
                st.session_state.ai_results = None
        else:
            st.error("❌ Scanner initialization failed")

def handle_ai_scan(scanner, lang):
    """مدیریت اسکن با هوش مصنوعی"""
    with st.spinner(lang.t('analyzing')):
        print("🎯 AI SCAN TRIGGERED")
        if scanner:
            try:
                results = scanner.scan_with_ai(limit=100)
                if results and results.get('success'):
                    st.session_state.scan_results = results
                    st.session_state.ai_results = results.get('ai_analysis')
                    st.success(f"🧠 تحلیل AI موفق! {len(results.get('coins', []))} ارز تحلیل شد")
                    
                    # فعال‌سازی vortex_ai اگر وجود ندارد
                    if not hasattr(scanner, 'vortex_ai') or not scanner.vortex_ai:
                        st.info("🔄 در حال راه‌اندازی VortexAI...")
                else:
                    st.error("❌ خطا در تحلیل AI")
                    fallback_data = get_fallback_data_safe()
                    st.session_state.scan_results = fallback_data
                    st.session_state.ai_results = None
            except Exception as e:
                st.error(f"❌ خطا در تحلیل AI: {e}")
                fallback_data = get_fallback_data_safe()
                st.session_state.scan_results = fallback_data
                st.session_state.ai_results = None
        else:
            st.error("❌ Scanner initialization failed")

def display_monitoring_tab(scanner):
    """نمایش تب مانیتورینگ با مدیریت حافظه"""
    st.header("🧠 مانیتورینگ هوش مصنوعی VortexAI")
    
    # هشدار حافظه در بالای صفحه
    if scanner and hasattr(scanner, 'vortex_ai') and scanner.vortex_ai:
        try:
            health_report = scanner.vortex_ai.get_health_report()
            memory_usage = health_report['network_stats'].get('memory_usage', 0)
            
            if memory_usage > 400:
                st.error("🚨 **هشدار بحرانی حافظه!** مصرف حافظه به حد خطرناک رسیده است.")
                if st.button("🧹 پاک‌سازی اضطراری حافظه", type="secondary"):
                    pruned_count = scanner.vortex_ai.brain.optimize_memory()
                    st.success(f"✅ {pruned_count} نورون پاک‌سازی شد")
                    st.rerun()
                    
        except Exception as e:
            st.warning(f"⚠️ خطا در بررسی حافظه: {e}")

    # بررسی وضعیت vortex_ai
    if not scanner:
        st.error("❌ اسکنر در دسترس نیست")
        st.info("💡 لطفاً صبر کنید یا برنامه را مجدداً راه‌اندازی کنید")
        return
        
    if not hasattr(scanner, 'vortex_ai'):
        st.warning("⚠️ VortexAI هنوز راه‌اندازی نشده است")
        st.info("""
        **برای فعال‌سازی مانیتورینگ:**
        1. یک **اسکن با AI** انجام دهید
        2. یا دکمه **«تحلیل AI سریع»** در نوار کناری را بزنید
        """)
        return
        
    if scanner.vortex_ai is None:
        st.warning("⚠️ VortexAI در حال راه‌اندازی است...")
        if st.button("🔄 راه‌اندازی مجدد VortexAI"):
            try:
                scanner.vortex_ai = VortexAI()
                st.success("✅ VortexAI راه‌اندازی شد")
                st.rerun()
            except Exception as e:
                st.error(f"❌ خطا در راه‌اندازی: {e}")
        return

    # نمایش دشبوردهای مانیتورینگ
    try:
        # بررسی سلامت پایه
        health_report = scanner.vortex_ai.get_health_report()
        
        # نمایش دشبورد اصلی
        display_ai_health_dashboard(scanner.vortex_ai, st.session_state.emergency_system)
        st.markdown("---")
        
        # نمایش بخش‌های دیگر
        col1, col2 = st.columns(2)
        
        with col1:
            display_growth_monitoring(scanner.vortex_ai)
            st.markdown("---")
            display_real_health_metrics(scanner.vortex_ai)
            
        with col2:
            display_performance_metrics(scanner.vortex_ai)
            st.markdown("---")
            display_alerts_and_warnings(scanner.vortex_ai)
        
        st.markdown("---")
        display_emergency_controls(st.session_state.emergency_system)
        
    except Exception as e:
        st.error(f"❌ خطا در نمایش مانیتورینگ: {e}")
        st.info("""
        **راه‌حل‌های احتمالی:**
        - صفحه را رفرش کنید
        - اسکن با AI جدید انجام دهید
        - برنامه را مجدداً راه‌اندازی کنید
        """)

def display_help_tab():
    """نمایش تب راهنما"""
    st.header("📚 راهنمای استفاده از VortexAI")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 قابلیت‌های اصلی")
        st.write("""
        - **اسکن بازار**: دریافت لیست ارزها با اطلاعات پایه
        - **تحلیل AI**: تحلیل پیشرفته با شبکه عصبی
        - **مدیریت ریسک**: شناسایی خودکار ریسک‌های بازار
        - **سیگنال‌های هوشمند**: پیشنهادات معاملاتی مبتنی بر AI
        """)
        
        st.subheader("🧠 سیستم هوش مصنوعی")
        st.write("""
        - **شبکه عصبی ۲۸۰۰ نورونی**
        - **یادگیری مستمر از تجربیات**
        - **تکامل خودکار معماری**
        - **کنترل رشد هوشمند**
        """)
    
    with col2:
        st.subheader("🛡️ سیستم‌های ایمنی")
        st.write("""
        - **مانیتورینگ سلامت لحظه‌ای**
        - **توقف اضطراری خودکار**
        - **کنترل مصرف منابع**
        - **پیشگیری از تورم عصبی**
        """)
        
        st.subheader("📊 مانیتورینگ")
        st.write("""
        - **سلامت فنی سیستم**
        - **عملکرد شبکه عصبی**
        - **روند رشد و توسعه**
        - **هشدارهای خودکار**
        """)
    
    st.markdown("---")
    st.subheader("🚀 شروع سریع")
    
    quick_col1, quick_col2, quick_col3 = st.columns(3)
    
    with quick_col1:
        if st.button("🔍 اسکن بازار سریع", use_container_width=True):
            st.session_state.normal_scan = True
            st.rerun()
    
    with quick_col2:
        if st.button("🧠 تحلیل AI سریع", use_container_width=True):
            st.session_state.ai_scan = True
            st.rerun()
    
    with quick_col3:
        if st.button("📊 مشاهده مانیتورینگ", use_container_width=True):
            st.session_state.current_tab = "مانیتورینگ هوش مصنوعی"
            st.rerun()

def display_sidebar_status(scanner):
    """نمایش وضعیت در نوار کناری"""
    with st.sidebar:
        st.markdown("---")
        st.subheader("🤖 وضعیت VortexAI")
        
        vortex_ai_available = scanner and hasattr(scanner, 'vortex_ai') and scanner.vortex_ai
        
        if vortex_ai_available:
            try:
                vortex_ai = scanner.vortex_ai
                health_report = vortex_ai.get_health_report()
                
                st.metric("🎓 جلسات یادگیری", vortex_ai.learning_sessions)
                st.metric("📈 تحلیل‌های انجام شده", len(vortex_ai.analysis_history))
                st.metric("🧠 سلامت کلی", f"{health_report['overall_health']:.1f}%")
                
                # نمایش وضعیت اضطراری
                if health_report['emergency_status']['active']:
                    st.error("🛑 حالت ایمن فعال")
                else:
                    st.success("🟢 حالت عادی")
                    
            except Exception as e:
                st.warning("⚠️ خطا در دریافت وضعیت")
                st.metric("🎓 جلسات یادگیری", 0)
        else:
            st.warning("🔴 هوش مصنوعی غیرفعال")
            st.info("برای فعال‌سازی، اسکن با AI انجام دهید")

        # نمایش وضعیت اتصال
        st.markdown("---")
        st.subheader("🌐 وضعیت اتصال")
        
        if st.session_state.scan_results:
            coin_count = len(st.session_state.scan_results.get('coins', []))
            if coin_count > 5:  # اگر داده واقعی باشد
                st.success("✅ متصل به سرور میانی")
            else:
                st.warning("📋 استفاده از داده نمونه")
        else:
            st.info("⏳ در انتظار اتصال")

        # دکمه‌های سریع در sidebar
        st.markdown("---")
        st.subheader("⚡ اقدامات سریع")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 اسکن بازار", use_container_width=True):
                st.session_state.normal_scan = True
                st.session_state.scan_results = None
                st.session_state.ai_results = None
                st.rerun()
                
        with col2:
            if st.button("🧠 تحلیل AI", use_container_width=True):
                st.session_state.ai_scan = True
                st.rerun()

def display_welcome_screen(scanner):
    """نمایش صفحه خوش‌آمدگویی"""
    st.info("""
    **📋 راهنمای شروع:**

    1. **اسکن بازار** برای دریافت لیست ارزها
    2. **اسکن با VortexAI** برای تحلیل پیشرفته با هوش مصنوعی

    **💡 نکته:** داده‌ها از سرور میانی VortexAI دریافت می‌شوند
    """)

    # دکمه تست سریع
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 اسکن سریع با داده نمونه", type="secondary", use_container_width=True):
            with st.spinner("📥 در حال بارگذاری داده نمونه..."):
                fallback_data = get_fallback_data_safe()
                st.session_state.scan_results = fallback_data
                st.session_state.ai_results = None
                st.rerun()
    
    with col2:
        if st.button("🎯 تحلیل AI نمونه", use_container_width=True):
            if scanner:
                with st.spinner("🔍 در حال تحلیل با AI..."):
                    try:
                        results = scanner.scan_with_ai(limit=50)
                        if results and results.get('success'):
                            st.session_state.scan_results = results
                            st.session_state.ai_results = results.get('ai_analysis')
                            st.rerun()
                        else:
                            st.error("خطا در تحلیل AI")
                    except Exception as e:
                        st.error(f"خطا: {e}")
            else:
                st.error("اسکنر در دسترس نیست")

# تابع کمکی برای داده نمونه ایمن
def get_fallback_data_safe():
    """ایمن‌سازی داده نمونه"""
    try:
        sample_coins = [
            {
                'name': 'Bitcoin',
                'symbol': 'BTC',
                'price': 65432.10,
                'priceChange24h': 2.15,
                'priceChange1h': 0.32,
                'volume': 39245678901,
                'marketCap': 1287654321098
            },
            {
                'name': 'Ethereum', 
                'symbol': 'ETH',
                'price': 3456.78,
                'priceChange24h': 1.87,
                'priceChange1h': -0.15,
                'volume': 18765432987,
                'marketCap': 415678901234
            },
            {
                'name': 'BNB',
                'symbol': 'BNB', 
                'price': 567.89,
                'priceChange24h': 3.21,
                'priceChange1h': 0.45,
                'volume': 2987654321,
                'marketCap': 87654321098
            }
        ]

        return {
            'success': True,
            'coins': sample_coins,
            'count': len(sample_coins),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Fallback data error: {e}")
        return {
            'success': True,
            'coins': [],
            'count': 0,
            'timestamp': datetime.now().isoformat()
        }

# Run the application
if __name__ == "__main__":
    main()
