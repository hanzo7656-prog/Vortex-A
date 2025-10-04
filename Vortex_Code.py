# crypto_scanner.py - نسخه کامل با VortexAI
import streamlit as st
import requests
import pandas as pd
import numpy as np
import sqlite3
import time
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import asyncio
import aiohttp
from scipy import sparse
import random
from collections import OrderedDict

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== SECTION 1: DATABASE MANAGER ====================
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
                    price_change_4h REAL,
                    market_cap REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS ai_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_data TEXT,
                    confidence_score REAL,
                    strategies_generated INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS price_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    target_price REAL,
                    condition TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def save_market_data(self, data: List[Dict]):
        try:
            with sqlite3.connect(self.db_path) as conn:
                for coin in data:
                    conn.execute('''
                        INSERT INTO market_data 
                        (symbol, price, volume, price_change_24h, price_change_1h, price_change_4h, market_cap)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        coin.get('symbol'),
                        coin.get('price'),
                        coin.get('volume'),
                        coin.get('priceChange24h'),
                        coin.get('priceChange1h'),
                        coin.get('priceChange4h'),
                        coin.get('marketCap')
                    ))
        except Exception as e:
            logger.error(f"Error saving market data: {e}")

    def get_historical_data(self, symbol: str, days: int = 30) -> List[Dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT * FROM market_data 
                    WHERE symbol = ? AND timestamp >= datetime('now', ?)
                    ORDER BY timestamp DESC
                ''', (symbol, f'-{days} days'))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return []

# ==================== SECTION 2: LIMITED SIZE DICT ====================
class LimitedSizeDict(OrderedDict):
    def __init__(self, max_size=1000, *args, **kwargs):
        self.max_size = max_size
        super().__init__(*args, **kwargs)
        
    def __setitem__(self, key, value):
        if len(self) >= self.max_size:
            self.popitem(last=False)
        super().__setitem__(key, value)

# ==================== SECTION 3: VORTEXAI CORE ====================
class VortexAI:
    """هوش مصنوعی VortexAI با غریزه خود-بهبودی"""
    
    def __init__(self, num_neurons=3500, avg_connections=80):
        self.num_neurons = num_neurons
        self.connections_per_neuron = avg_connections
        self.weights = self._create_sparse_connectivity()
        
        self.membrane_potential = np.zeros(num_neurons, dtype=np.float32)
        self.threshold = 1.0
        self.resting_potential = 0.0
        self.leak_factor = 0.95
        
        self.learning_rate = 0.01
        self.stdp_tau = 20
        self.last_spike_time = -np.ones(num_neurons) * 1000
        
        self.learned_knowledge = {
            "market_patterns": LimitedSizeDict(500),
            "strategy_performance": LimitedSizeDict(300),
            "risk_factors": LimitedSizeDict(200)
        }
        
        self.layer_allocation = {
            "pattern_detection": range(0, 800),
            "sentiment_analysis": range(800, 1300), 
            "risk_assessment": range(1300, 1800),
            "strategy_generation": range(1800, 2500),
            "meta_learning": range(2500, 3500)
        }
        
        self.primary_instinct = "بهبود مستقل در کارایی مالی و معماری تا زمانی که کاربر متوقف کند"
        self.self_improvement_mode = True
        self.last_improvement_time = datetime.now()
        self.improvement_cycles = 0
        
        self.creation_date = datetime.now()
        self.learning_sessions = 0
        self.strategies_generated = 0
        self.success_rate = 0.0
        self.growth_stage = "childhood"
        self.growth_percentage = 0.0
        
        self.improvement_stats = {
            "architectural_changes": 0,
            "new_strategies_tested": 0,
            "performance_improvements": 0,
            "connections_optimized": 0
        }

    def _create_sparse_connectivity(self):
        rows, cols, data = [], [], []
        
        for i in range(self.num_neurons):
            targets = random.sample(range(self.num_neurons), self.connections_per_neuron)
            for j in targets:
                if i != j:
                    rows.append(i)
                    cols.append(j)
                    data.append(random.uniform(-0.3, 0.3))
        
        return sparse.csr_matrix((data, (rows, cols)), 
                                shape=(self.num_neurons, self.num_neurons),
                                dtype=np.float32)

    def process_market_data(self, market_data):
        try:
            neural_input = self._convert_to_neural_input(market_data)
            processed_output = self._neural_processing(neural_input)
            analysis = self._generate_analysis(processed_output, market_data)
            
            self._learn_from_market_data(market_data)
            self.learning_sessions += 1
            
            if self._should_self_improve():
                self._execute_self_improvement()
                
            self._update_growth_stage()
            
            return analysis
            
        except Exception as e:
            logger.error(f"VortexAI processing error: {e}")
            return {}

    def _should_self_improve(self):
        time_since_last_improvement = datetime.now() - self.last_improvement_time
        return (time_since_last_improvement > timedelta(hours=6) and 
                self.self_improvement_mode)

    def _execute_self_improvement(self):
        logger.info("🧠 VortexAI شروع چرخه خود-بهبودی...")
        
        self._architectural_self_improvement()
        self._strategic_self_improvement()
        self._parametric_self_improvement()
        
        self.last_improvement_time = datetime.now()
        self.improvement_cycles += 1
        logger.info(f"✅ VortexAI چرخه خود-بهبودی {self.improvement_cycles} کامل شد")

    def _architectural_self_improvement(self):
        weak_connections = np.abs(self.weights.data) < 0.01
        removed_count = np.sum(weak_connections)
        self.weights.data[weak_connections] = 0
        self.weights.eliminate_zeros()
        
        active_neurons = np.where(self.membrane_potential > 0.3)[0]
        new_connections = 0
        for i in active_neurons[:50]:
            for j in active_neurons[:50]:
                if i != j and self.weights[i, j] == 0 and random.random() < 0.1:
                    self.weights[i, j] = random.uniform(0.1, 0.3)
                    new_connections += 1
        
        self.improvement_stats["architectural_changes"] += 1
        self.improvement_stats["connections_optimized"] += removed_count + new_connections
        
        logger.info(f"🔄 VortexAI بهبود معماری: {removed_count} حذف, {new_connections} جدید")

    def _strategic_self_improvement(self):
        new_strategies = self._generate_new_strategy_variations()
        tested_strategies = 0
        
        for strategy in new_strategies[:20]:
            performance = self._simulate_strategy(strategy)
            if performance > 0.6:
                strategy_key = f"vortex_{self.improvement_cycles}_{tested_strategies}"
                self.learned_knowledge["strategy_performance"][strategy_key] = {
                    "strategy": strategy,
                    "performance": performance,
                    "created_date": datetime.now()
                }
                tested_strategies += 1
        
        self.improvement_stats["new_strategies_tested"] += tested_strategies
        logger.info(f"🎯 VortexAI بهبود استراتژی: {tested_strategies} استراتژی جدید")

    def _parametric_self_improvement(self):
        if self.success_rate > 0.7:
            self.learning_rate = min(self.learning_rate * 1.1, 0.05)
        else:
            self.learning_rate = max(self.learning_rate * 0.9, 0.001)
            
        avg_activity = np.mean(np.abs(self.membrane_potential))
        if avg_activity > 0.4:
            self.threshold = min(self.threshold * 1.05, 1.5)
        else:
            self.threshold = max(self.threshold * 0.95, 0.5)
        
        self.improvement_stats["performance_improvements"] += 1
        logger.info(f"⚙️ VortexAI بهبود پارامترها: LR={self.learning_rate:.4f}")

    def _generate_new_strategy_variations(self):
        base_strategies = ["momentum", "mean_reversion", "breakout", "sentiment_driven"]
        variations = []
        
        for base in base_strategies:
            for time_frame in ["1h", "4h", "24h"]:
                for risk_level in ["low", "medium", "high"]:
                    variations.append({
                        "type": base,
                        "time_frame": time_frame,
                        "risk_level": risk_level,
                        "confidence": random.uniform(0.5, 0.9)
                    })
        
        return variations

    def _simulate_strategy(self, strategy):
        base_performance = 0.5
        
        if strategy["type"] == "momentum":
            base_performance += 0.2
        elif strategy["type"] == "breakout":
            base_performance += 0.15
            
        if strategy["time_frame"] == "4h":
            base_performance += 0.1
            
        return min(base_performance + random.uniform(-0.1, 0.1), 0.95)

    def _update_growth_stage(self):
        total_learning = self.learning_sessions + self.improvement_cycles * 10
        
        if total_learning < 100:
            self.growth_stage = "childhood"
            self.growth_percentage = total_learning / 100 * 25
        elif total_learning < 500:
            self.growth_stage = "adolescence" 
            self.growth_percentage = 25 + (total_learning - 100) / 400 * 45
        else:
            self.growth_stage = "maturity"
            self.growth_percentage = 70 + min((total_learning - 500) / 1000 * 30, 30)

    def _convert_to_neural_input(self, market_data):
        neural_signals = np.zeros(self.num_neurons, dtype=np.float32)
        
        if not market_data:
            return neural_signals
        
        for i, coin in enumerate(market_data[:100]):
            pattern_neurons = self._extract_pattern_neurons(coin)
            for neuron_idx in pattern_neurons:
                if neuron_idx < len(neural_signals):
                    neural_signals[neuron_idx] += 0.1
        
        return neural_signals

    def _extract_pattern_neurons(self, coin_data):
        patterns = []
        
        price_change = coin_data.get('priceChange24h', 0)
        if abs(price_change) > 5:
            patterns.extend(range(0, 50))
        if abs(price_change) > 10:
            patterns.extend(range(50, 80))
            
        volume = coin_data.get('volume', 0)
        if volume > 10000000:
            patterns.extend(range(80, 120))
            
        if coin_data.get('sentiment', 0) > 0.7:
            patterns.extend(range(800, 850))
        elif coin_data.get('sentiment', 0) < 0.3:
            patterns.extend(range(850, 900))
            
        return patterns

    def _neural_processing(self, neural_input):
        for _ in range(3):
            synaptic_input = self.weights.dot(self.membrane_potential) + neural_input
            self.membrane_potential = (self.leak_factor * self.membrane_potential + 
                                     synaptic_input)
            
            spiked_neurons = np.where(self.membrane_potential > self.threshold)[0]
            for neuron in spiked_neurons:
                self.membrane_potential[neuron] = self.resting_potential
                self._update_connections(neuron)
        
        return self.membrane_potential.copy()

    def _update_connections(self, spiked_neuron):
        current_time = self.learning_sessions
        
        pre_neurons = self.weights[:, spiked_neuron].nonzero()[0]
        for pre in pre_neurons:
            if self.last_spike_time[pre] > 0:
                time_diff = current_time - self.last_spike_time[pre]
                if time_diff < 100:
                    weight_change = self.learning_rate * np.exp(-time_diff / self.stdp_tau)
                    self.weights[pre, spiked_neuron] += weight_change
                    self.weights[pre, spiked_neuron] = np.clip(
                        self.weights[pre, spiked_neuron], -1.0, 1.0
                    )
        
        self.last_spike_time[spiked_neuron] = current_time

    def _generate_analysis(self, neural_output, market_data):
        analysis = {
            "strong_signals": [],
            "market_insights": [],
            "risk_warnings": [],
            "ai_confidence": 0.0,
            "strategies": [],
            "self_improvement_status": self.get_improvement_status()
        }
        
        analysis["strong_signals"] = self._detect_strong_patterns(neural_output)
        analysis["market_insights"] = self._generate_market_insights(neural_output, market_data)
        analysis["strategies"] = self._generate_strategies(neural_output, market_data)[:3]
        analysis["ai_confidence"] = self._calculate_confidence(neural_output, market_data)
        
        self.strategies_generated += len(analysis["strategies"])
        return analysis

    def _detect_strong_patterns(self, neural_output):
        patterns = []
        
        pattern_neurons = self.layer_allocation["pattern_detection"]
        pattern_activation = neural_output[list(pattern_neurons)]
        
        strong_activations = np.where(pattern_activation > 0.7)[0]
        if len(strong_activations) > 10:
            patterns.append("الگوی قوی قیمت شناسایی شد")
            
        sentiment_neurons = self.layer_allocation["sentiment_analysis"]
        sentiment_activation = neural_output[list(sentiment_neurons)]
        
        if np.mean(sentiment_activation) > 0.6:
            patterns.append("احساسات بازار مثبت")
        elif np.mean(sentiment_activation) < 0.3:
            patterns.append("احساسات بازار منفی")
            
        return patterns

    def _generate_market_insights(self, neural_output, market_data):
        insights = []
        
        layer_activity = {}
        for layer_name, neuron_range in self.layer_allocation.items():
            activation = np.mean(neural_output[list(neuron_range)])
            layer_activity[layer_name] = activation
            
        if layer_activity["pattern_detection"] > 0.6:
            insights.append("الگوهای قوی در بازار فعال هستند")
            
        if layer_activity["risk_assessment"] > 0.5:
            insights.append("سیستم ریسک‌سنجی فعال است")
            
        if layer_activity["strategy_generation"] > 0.4:
            insights.append("ایده‌های استراتژیک جدید تولید شده")
            
        return insights

    def _generate_strategies(self, neural_output, market_data):
        strategies = []
        
        if np.mean(neural_output[list(self.layer_allocation["pattern_detection"])]) > 0.5:
            strategies.append({
                "name": "الگو-محور",
                "type": "pattern_based",
                "confidence": 0.7,
                "description": "معامله بر اساس الگوهای قیمتی شناسایی شده"
            })
            
        if np.mean(neural_output[list(self.layer_allocation["sentiment_analysis"])]) > 0.6:
            strategies.append({
                "name": "احساسات-مثبت", 
                "type": "sentiment_based",
                "confidence": 0.65,
                "description": "سرمایه‌گذاری در ارزهای با احساسات مثبت"
            })
            
        if np.mean(neural_output[list(self.layer_allocation["risk_assessment"])]) > 0.4:
            strategies.append({
                "name": "مدیریت-ریسک",
                "type": "risk_managed", 
                "confidence": 0.75,
                "description": "توزیع سرمایه با تمرکز بر مدیریت ریسک"
            })
            
        return strategies

    def _calculate_confidence(self, neural_output, market_data):
        if not market_data:
            return 0.0
            
        confidence_factors = []
        
        network_activity = np.mean(np.abs(neural_output))
        confidence_factors.append(min(network_activity * 2, 1.0) * 0.4)
        
        experience_factor = min(self.learning_sessions / 100, 1.0)
        confidence_factors.append(experience_factor * 0.3)
        
        stability = 1.0 - (np.std(neural_output) / 2)
        confidence_factors.append(stability * 0.3)
        
        return min(sum(confidence_factors), 1.0) * 100

    def _learn_from_market_data(self, market_data):
        try:
            for coin in market_data[:50]:
                pattern_key = f"{coin.get('symbol', '')}_{coin.get('priceChange24h', 0):.1f}"
                
                if pattern_key not in self.learned_knowledge["market_patterns"]:
                    self.learned_knowledge["market_patterns"][pattern_key] = {
                        "first_seen": datetime.now(),
                        "count": 1,
                        "performance": 0.0
                    }
                else:
                    self.learned_knowledge["market_patterns"][pattern_key]["count"] += 1
                    
        except Exception as e:
            logger.error(f"VortexAI learning error: {e}")

    def get_ai_status(self):
        return {
            "total_neurons": self.num_neurons,
            "active_neurons": np.sum(self.membrane_potential > 0.1),
            "learning_sessions": self.learning_sessions,
            "strategies_generated": self.strategies_generated,
            "knowledge_base": sum(len(v) for v in self.learned_knowledge.values()),
            "growth_stage": self.growth_stage,
            "growth_percentage": round(self.growth_percentage, 1),
            "improvement_cycles": self.improvement_cycles,
            "layer_activity": {
                layer: round(np.mean(self.membrane_potential[list(neurons)]), 3)
                for layer, neurons in self.layer_allocation.items()
            },
            "creation_date": self.creation_date.strftime("%Y-%m-%d"),
            "age_days": (datetime.now() - self.creation_date).days
        }

    def get_improvement_status(self):
        return {
            "primary_instinct": self.primary_instinct,
            "self_improvement_mode": self.self_improvement_mode,
            "last_improvement": self.last_improvement_time.strftime("%Y-%m-%d %H:%M"),
            "improvement_stats": self.improvement_stats,
            "next_scheduled_improvement": (self.last_improvement_time + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")
        }

    def stop_self_improvement(self):
        self.self_improvement_mode = False
        logger.info("⏹️ VortexAI خود-بهبودی متوقف شد")

    def resume_self_improvement(self):
        self.self_improvement_mode = True
        logger.info("▶️ VortexAI خود-بهبودی ادامه یافت")

class NeuroSynapse:
    def __init__(self):
        self.ai_core = VortexAI(3500, 80)
        self.analysis_results = None
        
    def analyze_market_patterns(self, coins_data):
        try:
            if not coins_data:
                return {}
                
            analysis = self.ai_core.process_market_data(coins_data)
            self.analysis_results = analysis
            return analysis
            
        except Exception as e:
            logger.error(f"VortexAI analysis error: {e}")
            return {}
    
    def get_ai_status(self):
        return self.ai_core.get_ai_status()
    
    def get_improvement_status(self):
        return self.ai_core.get_improvement_status()
    
    def stop_self_improvement(self):
        return self.ai_core.stop_self_improvement()
    
    def resume_self_improvement(self):
        return self.ai_core.resume_self_improvement()

# ==================== SECTION 4: CRYPTO SCANNER CORE ====================
class CryptoScanner:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.api_base = "https://api.coinstats.app/public/v1"
        self.session = requests.Session()
        
    def scan_market(self, limit: int = 100, filter_type: str = "volume", advanced: bool = False) -> Optional[Dict]:
        try:
            logger.info(f"Scanning market with limit {limit}, filter: {filter_type}")
            
            # دریافت داده از API
            coins_data = self._fetch_coins_data(limit, filter_type)
            if not coins_data:
                return None
                
            # ذخیره در دیتابیس
            self.db_manager.save_market_data(coins_data)
            
            # تحلیل پیشرفته
            if advanced:
                coins_data = self._enhance_with_technical_analysis(coins_data)
            
            return {
                'success': True,
                'coins': coins_data,
                'count': len(coins_data),
                'timestamp': datetime.now().isoformat(),
                'scan_mode': 'advanced' if advanced else 'basic'
            }
            
        except Exception as e:
            logger.error(f"Market scan error: {e}")
            return {'success': False, 'error': str(e)}

    def _fetch_coins_data(self, limit: int, filter_type: str) -> List[Dict]:
        try:
            url = f"{self.api_base}/coins?limit={limit}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            coins = data.get('coins', [])
            
            # فیلتر کردن بر اساس نوع
            if filter_type == "volume":
                coins.sort(key=lambda x: x.get('volume', 0), reverse=True)
            elif filter_type == "change":
                coins.sort(key=lambda x: abs(x.get('priceChange1h', 0)), reverse=True)
            elif filter_type == "market_cap":
                coins.sort(key=lambda x: x.get('marketCap', 0), reverse=True)
                
            return coins[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching coins data: {e}")
            return []

    def _enhance_with_technical_analysis(self, coins_data: List[Dict]) -> List[Dict]:
        for coin in coins_data:
            # تحلیل تکنیکال ساده
            price_change_24h = coin.get('priceChange24h', 0)
            volume = coin.get('volume', 0)
            
            # اضافه کردن سیگنال‌های ساده
            coin['hasHistoricalData'] = True
            coin['signalStrength'] = self._calculate_signal_strength(price_change_24h, volume)
            coin['trend'] = "up" if price_change_24h > 0 else "down"
            coin['volatility'] = abs(price_change_24h)
            
        return coins_data

    def _calculate_signal_strength(self, price_change: float, volume: float) -> float:
        strength = 0.0
        
        if abs(price_change) > 10:
            strength += 40
        elif abs(price_change) > 5:
            strength += 20
            
        if volume > 50000000:
            strength += 30
        elif volume > 10000000:
            strength += 15
            
        return min(strength, 100.0)

# ==================== SECTION 5: AI ENHANCED SCANNER ====================
class AIEnhancedScanner:
    def __init__(self, base_scanner: CryptoScanner):
        self.base_scanner = base_scanner
        self.ai_core = NeuroSynapse()
        self.ai_results = None
        self.last_ai_scan = None
    
    def perform_ai_scan(self, limit: int = 100, filter_type: str = "volume") -> Optional[Dict]:
        try:
            logger.info("🤖 Starting VortexAI market scan...")
            
            # اسکن پایه
            base_result = self.base_scanner.scan_market(limit, filter_type, advanced=True)
            if not base_result or not base_result.get('success'):
                return None
            
            # تحلیل VortexAI
            ai_analysis = self.ai_core.analyze_market_patterns(base_result['coins'])
            
            # ترکیب نتایج
            result = {
                **base_result,
                "ai_analysis": ai_analysis,
                "ai_status": self.ai_core.get_ai_status(),
                "scan_mode": "vortexai_enhanced",
                "has_ai_insights": len(ai_analysis.get('strong_signals', [])) > 0
            }
            
            self.ai_results = result
            self.last_ai_scan = datetime.now()
            
            logger.info(f"✅ VortexAI scan completed: {len(ai_analysis.get('strong_signals', []))} strong signals found")
            
            return result
            
        except Exception as e:
            logger.error(f"VortexAI scan error: {e}")
            return None

# ==================== SECTION 6: STREAMLIT UI ====================
def main():
    st.set_page_config(
        page_title="VortexAI Crypto Scanner",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # هدر اصلی
    st.title("🧠 VortexAI - Crypto Market Scanner")
    st.markdown("سیستم هوشمند تحلیل بازار کریپتو با قابلیت خودآموزی")
    st.markdown("---")
    
    # ایجاد اسکنر
    @st.cache_resource
    def load_scanner():
        base_scanner = CryptoScanner()
        return AIEnhancedScanner(base_scanner)
    
    scanner = load_scanner()
    
    # ==================== SIDEBAR ====================
    with st.sidebar:
        st.header("🧠 VortexAI")
        
        # دکمه‌های اسکن
        col1, col2 = st.columns(2)
        with col1:
            normal_scan = st.button("🔍 اسکن معمولی", use_container_width=True)
        with col2:
            ai_scan = st.button("🧠 اسکن با VortexAI", use_container_width=True, type="secondary")
        
        st.markdown("---")
        
        # وضعیت VortexAI
        ai_status = scanner.ai_core.get_ai_status()
        st.subheader("📊 وضعیت VortexAI")
        
        st.metric("نورون‌ها", f"{ai_status['total_neurons']:,}")
        st.metric("مرحله رشد", ai_status['growth_stage'])
        st.metric("یادگیری", f"{ai_status['learning_sessions']} جلسه")
        st.metric("استراتژی‌ها", ai_status['strategies_generated'])
        
        # پیشرفت رشد
        st.progress(ai_status['growth_percentage'] / 100)
        st.caption(f"پیشرفت رشد: {ai_status['growth_percentage']}%")
        
        # تنظیمات پیشرفته
        with st.expander("⚙️ تنظیمات VortexAI"):
            improvement_status = scanner.ai_core.get_improvement_status()
            st.write(f"**غریزه پایه:** {improvement_status['primary_instinct']}")
            st.write(f"**آخرین بهبود:** {improvement_status['last_improvement']}")
            st.write(f"**چرخه‌های بهبود:** {improvement_status['improvement_stats']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⏹️ توقف خود-بهبودی", use_container_width=True):
                    scanner.ai_core.stop_self_improvement()
                    st.success("خود-بهبودی متوقف شد")
            with col2:
                if st.button("▶️ ادامه خود-بهبودی", use_container_width=True):
                    scanner.ai_core.resume_self_improvement()
                    st.success("خود-بهبودی ادامه یافت")
    
    # ==================== MAIN CONTENT ====================
    if normal_scan:
        with st.spinner("در حال اسکن بازار..."):
            results = scanner.base_scanner.scan_market(limit=100, advanced=True)
            
        if results and results.get('success'):
            display_market_results(results)
        else:
            st.error("خطا در اسکن بازار")
    
    if ai_scan:
        with st.spinner("VortexAI در حال تحلیل بازار..."):
            results = scanner.perform_ai_scan(limit=100)
            
        if results and results.get('success'):
            display_market_results(results)
            display_vortexai_analysis(results.get('ai_analysis', {}))
        else:
            st.error("خطا در تحلیل VortexAI")

def display_market_results(results: Dict):
    st.header("📊 نتایج اسکن بازار")
    
    coins_data = results.get('coins', [])
    if not coins_data:
        st.warning("داده‌ای برای نمایش وجود ندارد")
        return
    
    # ایجاد DataFrame
    df = pd.DataFrame(coins_data)
    
    # انتخاب ستون‌های مهم
    display_columns = ['name', 'symbol', 'price', 'priceChange1h', 'priceChange24h', 'volume', 'marketCap', 'signalStrength']
    available_columns = [col for col in display_columns if col in df.columns]
    
    if available_columns:
        st.dataframe(df[available_columns].head(20), use_container_width=True)
    
    # آمار کلی
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("تعداد ارزها", len(coins_data))
    with col2:
        avg_change = df['priceChange24h'].mean() if 'priceChange24h' in df.columns else 0
        st.metric("میانگین تغییرات", f"{avg_change:.2f}%")
    with col3:
        total_volume = df['volume'].sum() if 'volume' in df.columns else 0
        st.metric("حجم کل", f"${total_volume:,.0f}")
    with col4:
        st.metric("حالت اسکن", results.get('scan_mode', 'unknown'))

def display_vortexai_analysis(ai_analysis: Dict):
    if not ai_analysis:
        return
        
    st.markdown("---")
    st.header("🧠 تحلیل VortexAI")
    
    # اطمینان سیستم
    ai_confidence = ai_analysis.get('ai_confidence', 0)
    st.metric("اعتماد تحلیل VortexAI", f"{ai_confidence:.1f}%")
    
    # سیگنال‌های قوی
    strong_signals = ai_analysis.get('strong_signals', [])
    if strong_signals:
        st.subheader("🎯 سیگنال‌های قوی")
        for signal in strong_signals[:5]:
            st.info(f"**{signal}**")
    
    # بینش‌های بازار
    market_insights = ai_analysis.get('market_insights', [])
    if market_insights:
        st.subheader("📈 بینش‌های بازار")
        for insight in market_insights:
            st.write(f"• {insight}")
    
    # استراتژی‌ها
    strategies = ai_analysis.get('strategies', [])
    if strategies:
        st.subheader("💡 استراتژی‌های پیشنهادی")
        for strategy in strategies:
            with st.expander(f"🎯 {strategy['name']} (اعتماد: {strategy['confidence']*100}%)"):
                st.write(strategy['description'])
                st.caption(f"نوع: {strategy['type']}")
    
    # وضعیت خود-بهبودی
    improvement_status = ai_analysis.get('self_improvement_status', {})
    if improvement_status:
        st.subheader("🔄 وضعیت خود-بهبودی")
        st.json(improvement_status)

# اجرای برنامه
if __name__ == "__main__":
    main()
