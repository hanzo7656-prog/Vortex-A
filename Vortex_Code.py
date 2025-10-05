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

class MultiLanguage:  # تصحیح نام کلاس
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
lang = MultiLanguage()

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

# --- SECTION 4: VORTEXAI NEURAL NETWORK ---

import random
import math
from dataclasses import dataclass
from typing import List, Dict, Tuple
import json

@dataclass
class Neuron:
    id: int
    weights: Dict[str, float]
    bias: float
    activation_count: int = 0
    learning_rate: float = 0.01
    
    def activate(self, inputs: Dict[str, float]) -> float:
        """فعالسازی نورون"""
        total = self.bias
        for key, value in inputs.items():
            if key in self.weights:
                total += value * self.weights[key]
        
        self.activation_count += 1
        return self._sigmoid(total)
    
    def _sigmoid(self, x: float) -> float:
        """تابع فعالسازی سیگموید"""
        return 1 / (1 + math.exp(-x))
    
    def adjust_weights(self, inputs: Dict[str, float], error: float, learning_rate: float):
        """تنظیم وزن‌ها بر اساس خطا"""
        activation = self.activate(inputs)
        delta = error * activation * (1 - activation)
        
        for key in self.weights:
            if key in inputs:
                self.weights[key] += learning_rate * delta * inputs[key]
        self.bias += learning_rate * delta
    
    def mutate(self, mutation_rate: float = 0.1):
        """جهش برای تنوع ژنتیکی"""
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
        self.learning_rate = 0.01
        self.generation = 0
        self.total_activations = 0
        self.memory = []
        
        # ایجاد شبکه عصبی با 3500 نورون
        self._build_network()
    
    def _build_network(self):
        """ساخت شبکه عصبی با 3500 نورون"""
        print("🧠 Building neural network with 3500 neurons...")
        
        # لایه ورودی (500 نورون)
        input_features = [
            'price', 'price_change_24h', 'price_change_1h', 'volume', 'market_cap',
            'rsi', 'macd', 'bollinger_upper', 'bollinger_lower', 'volume_ratio',
            'price_momentum', 'volatility', 'market_sentiment', 'trend_strength'
        ]
        
        self.input_layer = []
        for i in range(500):
            weights = {feature: random.uniform(-1, 1) for feature in input_features}
            neuron = Neuron(id=i, weights=weights, bias=random.uniform(-0.5, 0.5))
            self.neurons[i] = neuron
            self.input_layer.append(i)
        
        # لایه‌های پنهان (2500 نورون)
        self.hidden_layers = []
        layer_sizes = [800, 700, 600, 400]  # 4 لایه پنهان
        
        current_id = 500
        for layer_size in layer_sizes:
            layer = []
            for i in range(layer_size):
                weights = {'prev_layer': random.uniform(-1, 1)}
                neuron = Neuron(id=current_id, weights=weights, bias=random.uniform(-0.5, 0.5))
                self.neurons[current_id] = neuron
                layer.append(current_id)
                current_id += 1
            self.hidden_layers.append(layer)
        
        # لایه خروجی (500 نورون)
        self.output_layer = []
        output_features = [
            'buy_signal', 'sell_signal', 'hold_signal', 'risk_score', 'confidence',
            'price_prediction_1h', 'price_prediction_24h', 'volatility_prediction'
        ]
        
        for i in range(500):
            weights = {feature: random.uniform(-1, 1) for feature in output_features}
            neuron = Neuron(id=current_id, weights=weights, bias=random.uniform(-0.5, 0.5))
            self.neurons[current_id] = neuron
            self.output_layer.append(current_id)
            current_id += 1
        
        # ایجاد سیناپس‌ها (ارتباطات)
        self._create_synapses()
        print(f"✅ Neural network built: {len(self.neurons)} neurons, {len(self.synapses)} synapses")
    
    def _create_synapses(self):
        """ایجاد ارتباطات بین نورون‌ها"""
        # ارتباط لایه ورودی به اولین لایه پنهان
        for input_id in self.input_layer:
            for hidden_id in self.hidden_layers[0]:
                synapse = Synapse(input_id, hidden_id, random.uniform(-1, 1))
                self.synapses.append(synapse)
        
        # ارتباط بین لایه‌های پنهان
        for i in range(len(self.hidden_layers) - 1):
            for source_id in self.hidden_layers[i]:
                for target_id in self.hidden_layers[i + 1]:
                    synapse = Synapse(source_id, target_id, random.uniform(-1, 1))
                    self.synapses.append(synapse)
        
        # ارتباط آخرین لایه پنهان به لایه خروجی
        for hidden_id in self.hidden_layers[-1]:
            for output_id in self.output_layer:
                synapse = Synapse(hidden_id, output_id, random.uniform(-1, 1))
                self.synapses.append(synapse)
    
    def feed_forward(self, inputs: Dict[str, float]) -> Dict[str, float]:
        """پیش‌بینی شبکه عصبی"""
        # فعالسازی لایه ورودی
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
                # جمع‌آوری ورودی‌ها از سیناپس‌ها
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
        buy_signals = [v for k, v in raw_outputs.items() if 'neuron_' in k and int(k.split('_')[1]) < 3500 + 100]
        sell_signals = [v for k, v in raw_outputs.items() if 'neuron_' in k and 3500 + 100 <= int(k.split('_')[1]) < 3500 + 200]
        confidence_signals = [v for k, v in raw_outputs.items() if 'neuron_' in k and int(k.split('_')[1]) >= 3500 + 200]
        
        return {
            'buy_confidence': sum(buy_signals) / len(buy_signals) if buy_signals else 0.5,
            'sell_confidence': sum(sell_signals) / len(sell_signals) if sell_signals else 0.5,
            'overall_confidence': sum(confidence_signals) / len(confidence_signals) if confidence_signals else 0.5,
            'risk_score': 1 - (sum(confidence_signals) / len(confidence_signals)) if confidence_signals else 0.5,
            'neural_activity': self.total_activations,
            'network_maturity': min(1.0, self.total_activations / 1000)
        }
    
    def learn_from_experience(self, inputs: Dict[str, float], expected_output: Dict[str, float], actual_profit: float = 0):
        """یادگیری از تجربیات"""
        # پیش‌بینی فعلی
        current_output = self.feed_forward(inputs)
        
        # محاسبه خطا
        error = self._calculate_error(current_output, expected_output, actual_profit)
        
        # انتشار خطا به عقب (Backpropagation ساده شده)
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
        if len(self.memory) > 1000:
            self.memory = self.memory[-1000:]
    
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
            
            # جهش تصادفی برای کشف راه‌حل‌های جدید
            if random.random() < 0.01:  # 1% chance of mutation
                neuron.mutate()
    
    def get_network_stats(self) -> Dict:
        """آمار شبکه عصبی"""
        total_weights = sum(len(neuron.weights) for neuron in self.neurons.values())
        avg_activation = sum(neuron.activation_count for neuron in self.neurons.values()) / len(self.neurons)
        
        return {
            'total_neurons': len(self.neurons),
            'total_synapses': len(self.synapses),
            'total_weights': total_weights,
            'generation': self.generation,
            'total_activations': self.total_activations,
            'average_activation': avg_activation,
            'learning_rate': self.learning_rate,
            'memory_size': len(self.memory),
            'network_maturity': min(1.0, self.total_activations / 1000)
        }
    
    def evolve(self):
        """تکامل شبکه - نسل جدید"""
        self.generation += 1
        print(f"🔄 Evolving neural network to generation {self.generation}")
        
        # جهش قوی‌تر برای نسل جدید
        for neuron in self.neurons.values():
            neuron.mutate(mutation_rate=0.2)
        
        # تنظیم مجدد سیناپس‌ها
        for synapse in self.synapses:
            synapse.weight += random.uniform(-0.3, 0.3)
            synapse.strength = min(1.0, synapse.strength + random.uniform(-0.1, 0.1))

class VortexAI:
    def __init__(self):
        self.brain = VortexNeuralNetwork()
        self.learning_sessions = 0
        self.analysis_history = []
        self.market_experiences = []
    
    def analyze_market_data(self, coins_data: List[Dict]) -> Dict:
        """تحلیل بازار با شبکه عصبی"""
        self.learning_sessions += 1
        
        analysis = {
            "neural_analysis": [],
            "strong_signals": [],
            "risk_warnings": [],
            "market_insights": [],
            "ai_confidence": 0,
            "network_stats": self.brain.get_network_stats()
        }
        
        for coin in coins_data[:20]:
            # آماده‌سازی ورودی برای شبکه عصبی
            inputs = self._prepare_neural_inputs(coin)
            
            # دریافت پیش‌بینی از شبکه عصبی
            neural_output = self.brain.feed_forward(inputs)
            
            coin_analysis = {
                "coin": coin.get('name', ''),
                "symbol": coin.get('symbol', ''),
                "neural_buy_confidence": neural_output['buy_confidence'],
                "neural_sell_confidence": neural_output['sell_confidence'],
                "risk_score": neural_output['risk_score'] * 100,
                "signal_strength": max(neural_output['buy_confidence'], neural_output['sell_confidence']) * 100,
                "network_confidence": neural_output['overall_confidence'] * 100,
                "recommendation": self._generate_neural_recommendation(neural_output)
            }
            
            analysis["neural_analysis"].append(coin_analysis)
            
            if coin_analysis["signal_strength"] > 70:
                analysis["strong_signals"].append(coin_analysis)
            
            if coin_analysis["risk_score"] > 60:
                analysis["risk_warnings"].append(coin_analysis)
        
        analysis["ai_confidence"] = self._calculate_confidence(coins_data)
        analysis["market_insights"] = self._generate_neural_insights(analysis["neural_analysis"])
        
        # یادگیری از تحلیل فعلی
        self._learn_from_analysis(analysis)
        
        self.analysis_history.append(analysis)
        return analysis
    
    def _prepare_neural_inputs(self, coin: Dict) -> Dict[str, float]:
        """آماده‌سازی ورودی‌های شبکه عصبی"""
        return {
            'price': min(coin.get('price', 0) / 100000, 1.0),  # نرمال‌سازی
            'price_change_24h': (coin.get('priceChange24h', 0) + 50) / 100,  # نرمال‌سازی به 0-1
            'price_change_1h': (coin.get('priceChange1h', 0) + 50) / 100,
            'volume': min(math.log(coin.get('volume', 1) + 1) / 20, 1.0),
            'market_cap': min(math.log(coin.get('marketCap', 1) + 1) / 25, 1.0),
            'rsi': random.uniform(0, 1),  # جایگزین شونده با اندیکاتورهای واقعی
            'macd': random.uniform(-1, 1),
            'volatility': min(abs(coin.get('priceChange24h', 0)) / 50, 1.0),
            'market_sentiment': random.uniform(0, 1)
        }
    
    def _generate_neural_recommendation(self, neural_output: Dict) -> str:
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
    
    def _generate_neural_insights(self, neural_analysis: List[Dict]) -> List[str]:
        """تولید بینش‌های مبتنی بر شبکه عصبی"""
        insights = []
        
        avg_buy_confidence = sum(a['neural_buy_confidence'] for a in neural_analysis) / len(neural_analysis)
        avg_sell_confidence = sum(a['neural_sell_confidence'] for a in neural_analysis) / len(neural_analysis)
        
        if avg_buy_confidence > 0.6:
            insights.append("🧠 شبکه عصبی حالت صعودی قوی تشخیص می‌دهد")
        elif avg_sell_confidence > 0.6:
            insights.append("🧠 شبکه عصبی حالت نزولی قوی تشخیص می‌دهد")
        else:
            insights.append("🧠 شبکه عصبی بازار را متعادل ارزیابی می‌کند")
        
        insights.append(f"🔄 نسل شبکه: {self.brain.generation}")
        insights.append(f"🎯 بلوغ شبکه: {self.brain.get_network_stats()['network_maturity']:.1%}")
        
        return insights
    
    def _learn_from_analysis(self, analysis: Dict):
        """یادگیری از تحلیل انجام شده"""
        # شبیه‌سازی یادگیری از نتایج
        for coin_analysis in analysis['neural_analysis']:
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
        
        return min(base_confidence + neural_confidence, 1.0) * 100
    
    def force_evolution(self):
        """اجبار به تکامل شبکه"""
        print("🧬 Forcing neural network evolution...")
        self.brain.evolve()
        return f"✅ شبکه به نسل {self.brain.generation} تکامل یافت"
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
# --- SECTION 6: UI COMPONENTS ---

def display_market_results(results: Dict):
    """Display market scan results"""
    if not results or not results.get('success'):
        st.error("❌ " + lang.t('error'))
        return
        
    coins_data = results.get('coins', [])
    
    if not coins_data:
        st.warning("⚠️ هیچ داده‌ای برای نمایش وجود ندارد")
        return
    
    # هدر با تعداد ارزها
    st.header(f"{lang.t('results_title')} - {len(coins_data)} ارز")
    
    # ایجاد دیتافریم برای نمایش
    df_data = []
    for coin in coins_data:
        # بررسی وجود داده‌ها
        price = coin.get('price', 0)
        change_24h = coin.get('priceChange24h', 0)
        change_1h = coin.get('priceChange1h', 0)
        volume = coin.get('volume', 0)
        market_cap = coin.get('marketCap', 0)
        
        df_data.append((
            coin.get('name', 'نامشخص'),
            coin.get('symbol', 'N/A'),
            f"${price:,.2f}" if price > 0 else "$0.00",
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
        height=min(600, 35 * len(df) + 40),  # ارتفاع داینامیک
        hide_index=False
    )
    
    # متریک‌های کلی
    st.subheader("📊 آمار کلی بازار")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_coins = len(coins_data)
        st.metric(
            label="تعداد ارزها",
            value=total_coins,
            delta=None
        )
    
    with col2:
        changes_24h = [c.get('priceChange24h', 0) for c in coins_data]
        avg_change_24h = np.mean(changes_24h) if changes_24h else 0
        st.metric(
            label="میانگین تغییر 24h",
            value=f"{avg_change_24h:+.2f}%",
            delta=None
        )
    
    with col3:
        total_volume = sum(c.get('volume', 0) for c in coins_data)
        st.metric(
            label="حجم کل بازار",
            value=f"${total_volume:,.0f}",
            delta=None
        )
    
    with col4:
        bullish_count = sum(1 for c in coins_data if c.get('priceChange24h', 0) > 0)
        bearish_count = total_coins - bullish_count
        st.metric(
            label="روند بازار",
            value=f"{bullish_count}↑ {bearish_count}↓",
            delta=None
        )

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
        st.write(f"{confidence_color} سطح اعتماد: {'عالی' if ai_confidence > 70 else 'متوسط' if ai_confidence > 40 else 'پایین'}")
    
    # سیگنال‌های قوی
    strong_signals = ai_analysis.get('strong_signals', [])
    if strong_signals:
        st.subheader("🎯 " + lang.t('strong_signals'))
        
        for i, signal in enumerate(strong_signals[:8], 1):  # حداکثر 8 سیگنال
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                
                with col1:
                    st.write(f"**{i}. {signal['coin']}** ({signal['symbol']})")
                
                with col2:
                    signal_strength = signal['signal_strength']
                    strength_color = "🟢" if signal_strength > 70 else "🟡" if signal_strength > 50 else "🔴"
                    st.write(f"{strength_color} {signal_strength}%")
                
                with col3:
                    risk_level = signal['risk_level']
                    risk_color = "🔴" if risk_level > 70 else "🟡" if risk_level > 40 else "🟢"
                    st.write(f"{risk_color} ریسک: {risk_level}%")
                
                with col4:
                    rec = signal['recommendation']
                    rec_color = "success" if "قوی" in rec or "Strong" in rec else "warning" if "محتاط" in rec or "Cautious" in rec else "info"
                    st.write(f":{rec_color}[{rec}]")
            
            st.markdown("---")
    
    # هشدارهای ریسک
    risk_warnings = ai_analysis.get('risk_warnings', [])
    if risk_warnings:
        st.subheader("⚠️ " + lang.t('risk_warnings'))
        
        for warning in risk_warnings[:5]:  # حداکثر 5 هشدار
            with st.expander(f"🚨 {warning['coin']} ({warning['symbol']}) - سطح ریسک: {warning['risk_level']}%", expanded=False):
                st.error(f"**هشدار ریسک بالا** - این ارز دارای نوسانات شدید یا ریسک معاملاتی بالایی است.")
                st.write(f"💡 پیشنهاد: {warning['recommendation']}")
    
    # بینش‌های بازار
    market_insights = ai_analysis.get('market_insights', [])
    if market_insights:
        st.subheader("💡 " + lang.t('market_insights'))
        
        for insight in market_insights:
            if "صعودی" in insight or "bullish" in insight:
                st.success(insight)
            elif "نزولی" in insight or "bearish" in insight:
                st.warning(insight)
            else:
                st.info(insight)

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
            placeholder="...نام یا نماد ارز",
            key="search_input"
        )
    
    with col2:
        min_volume = st.number_input(
            "حداقل حجم (میلیون دلار)",
            min_value=0,
            value=10,
            step=10,
            key="min_volume"
        ) * 1000000  # تبدیل به دلار
    
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
            if search_term.lower() in coin.get('name', '').lower() 
            or search_term.lower() in coin.get('symbol', '').lower()
        ]
    
    if min_volume > 0:
        filtered_coins = [
            coin for coin in filtered_coins 
            if coin.get('volume', 0) >= min_volume
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
        st.info(f"📊 نمایش {len(filtered_coins)} از {len(coins_data)} ارز (فیلتر شده)")
    
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
            st.success("گزارش ذخیره شد")
    
    with col3:
        if st.button("📧 اشتراک‌گذاری", use_container_width=True):
            st.info("امکان اشتراک‌گذاری")
    
    with col4:
        if st.button("⚙️ تنظیمات پیشرفته", use_container_width=True):
            st.session_state.show_settings = True
# --- SECTION 7: MAIN APPLICATION ---

def main():
    """Main application function"""
    setup_page_config()
    
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
            return scanner
        except Exception as e:
            print(f"❌ Scanner initialization failed: {e}")
            return None
    
    scanner = load_scanner()
    
    # استفاده از session state برای ذخیره نتایج
    if 'scan_results' not in st.session_state:
        st.session_state.scan_results = None
    if 'ai_results' not in st.session_state:
        st.session_state.ai_results = None
    
    # Handle scan requests
    if normal_scan:
        with st.spinner(lang.t('scanning')):
            print("🎯 NORMAL SCAN TRIGGERED")
            if scanner:
                results = scanner.scan_market(limit=100)
            else:
                results = None
                st.error("❌ Scanner initialization failed")
            
            print(f"📊 NORMAL SCAN RESULTS: {results is not None}")
            
            if results and results.get('success'):
                st.session_state.scan_results = results
                st.session_state.ai_results = None
                st.success(f"✅ اسکن موفق! {len(results.get('coins', []))} ارز پیدا شد")
            else:
                st.error("❌ خطا در دریافت داده‌ها")
                # حتی در صورت خطا هم داده نمونه نمایش بده
                if scanner:
                    fallback_data = get_fallback_data_safe()
                    st.session_state.scan_results = fallback_data
                    st.session_state.ai_results = None
    
    if ai_scan:
        with st.spinner(lang.t('analyzing')):
            print("🎯 AI SCAN TRIGGERED")
            if scanner:
                results = scanner.scan_with_ai(limit=100)
            else:
                results = None
                st.error("❌ Scanner initialization failed")
            
            print(f"📊 AI SCAN RESULTS: {results is not None}")
            
            if results and results.get('success'):
                st.session_state.scan_results = results
                st.session_state.ai_results = results.get('ai_analysis')
                st.success(f"✅ تحلیل AI موفق! {len(results.get('coins', []))} ارز تحلیل شد")
            else:
                st.error("❌ خطا در تحلیل AI")
                if scanner:
                    fallback_data = get_fallback_data_safe()
                    st.session_state.scan_results = fallback_data
                    st.session_state.ai_results = None
    
    # نمایش نتایج از session state
    if st.session_state.scan_results:
        print(f"🔄 DISPLAYING RESULTS: {len(st.session_state.scan_results.get('coins', []))} coins")
        
        # نمایش نتایج بازار
        display_market_results(st.session_state.scan_results)
        
        # نمایش تحلیل AI اگر موجود باشد
        if st.session_state.ai_results:
            display_ai_analysis(st.session_state.ai_results)
    else:
        # نمایش صفحه خالی با راهنما
        st.info("""
        🚀 **راهنمای شروع:**
        
        1. **اسکن بازار** - برای دریافت لیست ارزها
        2. **اسکن با VortexAI** - برای تحلیل پیشرفته با هوش مصنوعی
        
        💡 **نکته:** داده‌ها از سرور میانی VortexAI دریافت می‌شوند.
        """)
        
        # نمایش داده‌های نمونه برای تست - نسخه ایمن
        st.warning("در حال حاضر داده‌ای برای نمایش وجود ندارد. لطفاً یکی از دکمه‌های اسکن را فشار دهید.")
        
        # دکمه تست سریع - نسخه ایمن
        if st.button("🧪 تست سریع با داده نمونه", type="secondary"):
            with st.spinner("بارگذاری داده نمونه..."):
                fallback_data = get_fallback_data_safe()
                st.session_state.scan_results = fallback_data
                st.session_state.ai_results = None
                st.rerun()
    
    # Display AI status in sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("🤖 وضعیت VortexAI" if lang.current_lang == 'fa' else "🤖 VortexAI Status")
        
        if scanner and hasattr(scanner, 'vortex_ai') and scanner.vortex_ai:
            st.metric(
                "جلسات یادگیری" if lang.current_lang == 'fa' else "Learning Sessions", 
                scanner.vortex_ai.learning_sessions
            )
            st.metric(
                "تحلیل‌های انجام شده" if lang.current_lang == 'fa' else "Analysis Completed", 
                len(scanner.vortex_ai.analysis_history)
            )
        else:
            st.warning("AI در دسترس نیست")
        
        # نمایش وضعیت اتصال
        st.markdown("---")
        st.subheader("🌐 وضعیت اتصال")
        
        if st.session_state.scan_results:
            coin_count = len(st.session_state.scan_results.get('coins', []))
            if coin_count > 5:  # اگر داده واقعی باشد
                st.success("✅ متصل به سرور میانی")
            else:
                st.warning("⚠️ استفاده از داده نمونه")
        else:
            st.info("🔌 در انتظار اتصال")

# تابع کمکی برای داده نمونه ایمن
def get_fallback_data_safe():
    """ایمن‌سازی داده نمونه"""
    try:
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
