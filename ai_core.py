# ai_core.py - نسخه نهایی با خود-بهبودی
import numpy as np
from scipy import sparse
import random
from datetime import datetime, timedelta
import logging
from collections import OrderedDict
import json

logger = logging.getLogger(__name__)

class LimitedSizeDict(OrderedDict):
    def __init__(self, max_size=1000, *args, **kwargs):
        self.max_size = max_size
        super().__init__(*args, **kwargs)
        
    def __setitem__(self, key, value):
        if len(self) >= self.max_size:
            self.popitem(last=False)
        super().__setitem__(key, value)

class VortexAI:
    """هوش مصنوعی با غریزه خود-بهبودی"""
    
    def __init__(self, num_neurons=3500, avg_connections=80):
        self.num_neurons = num_neurons
        self.connections_per_neuron = avg_connections
        self.weights = self._create_sparse_connectivity()
        
        # حالت نورون‌ها
        self.membrane_potential = np.zeros(num_neurons, dtype=np.float32)
        self.threshold = 1.0
        self.resting_potential = 0.0
        self.leak_factor = 0.95
        
        # یادگیری و حافظه
        self.learning_rate = 0.01
        self.stdp_tau = 20
        self.last_spike_time = -np.ones(num_neurons) * 1000
        
        # دانش آموخته شده
        self.learned_knowledge = {
            "market_patterns": LimitedSizeDict(500),
            "strategy_performance": LimitedSizeDict(300),
            "risk_factors": LimitedSizeDict(200)
        }
        
        # لایه‌های تخصصی
        self.layer_allocation = {
            "pattern_detection": range(0, 800),
            "sentiment_analysis": range(800, 1300), 
            "risk_assessment": range(1300, 1800),
            "strategy_generation": range(1800, 2500),
            "meta_learning": range(2500, 3500)
        }
        
        # غریزه خود-بهبودی
        self.primary_instinct = "بهبود مستقل در کارایی مالی و معماری تا زمانی که کاربر متوقف کند"
        self.self_improvement_mode = True
        self.last_improvement_time = datetime.now()
        self.improvement_cycles = 0
        
        # رشد و بلوغ
        self.creation_date = datetime.now()
        self.learning_sessions = 0
        self.strategies_generated = 0
        self.success_rate = 0.0
        self.growth_stage = "childhood"
        self.growth_percentage = 0.0
        
        # آمار بهبود
        self.improvement_stats = {
            "architectural_changes": 0,
            "new_strategies_tested": 0,
            "performance_improvements": 0,
            "connections_optimized": 0
        }

    def _create_sparse_connectivity(self):
        """ایجاد اتصالات اسپارس"""
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
        """پردازش داده‌های بازار و خود-بهبودی"""
        try:
            # پردازش اصلی
            neural_input = self._convert_to_neural_input(market_data)
            processed_output = self._neural_processing(neural_input)
            analysis = self._generate_analysis(processed_output, market_data)
            
            # یادگیری از داده‌ها
            self._learn_from_market_data(market_data)
            self.learning_sessions += 1
            
            # خود-بهبودی دوره‌ای
            if self._should_self_improve():
                self._execute_self_improvement()
                
            # به‌روزرسانی مرحله رشد
            self._update_growth_stage()
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in market data processing: {e}")
            return {}

    def _should_self_improve(self):
        """بررسی是否需要自身改进"""
        time_since_last_improvement = datetime.now() - self.last_improvement_time
        return (time_since_last_improvement > timedelta(hours=6) and 
                self.self_improvement_mode)

    def _execute_self_improvement(self):
        """执行自我改进周期"""
        logger.info("🧠 شروع چرخه خود-بهبودی...")
        
        # 1. بهبود معماری
        self._architectural_self_improvement()
        
        # 2. بهبود استراتژی
        self._strategic_self_improvement()
        
        # 3. بهینه‌سازی پارامترها
        self._parametric_self_improvement()
        
        self.last_improvement_time = datetime.now()
        self.improvement_cycles += 1
        logger.info(f"✅ چرخه خود-بهبودی {self.improvement_cycles} کامل شد")

    def _architectural_self_improvement(self):
        """بهبود معماری شبکه"""
        # حذف اتصالات ضعیف
        weak_connections = np.abs(self.weights.data) < 0.01
        removed_count = np.sum(weak_connections)
        self.weights.data[weak_connections] = 0
        self.weights.eliminate_zeros()
        
        # ایجاد اتصالات جدید بین نورون‌های پرکار
        active_neurons = np.where(self.membrane_potential > 0.3)[0]
        new_connections = 0
        for i in active_neurons[:50]:  # 50 نورون پرکار
            for j in active_neurons[:50]:
                if i != j and self.weights[i, j] == 0 and random.random() < 0.1:
                    self.weights[i, j] = random.uniform(0.1, 0.3)
                    new_connections += 1
        
        self.improvement_stats["architectural_changes"] += 1
        self.improvement_stats["connections_optimized"] += removed_count + new_connections
        
        logger.info(f"🔄 بهبود معماری: {removed_count} اتصال حذف، {new_connections} اتصال جدید")

    def _strategic_self_improvement(self):
        """بهبود استراتژی‌های مالی"""
        # تست استراتژی‌های جدید در شبیه‌ساز
        new_strategies = self._generate_new_strategy_variations()
        tested_strategies = 0
        
        for strategy in new_strategies[:20]:  # تست 20 استراتژی
            performance = self._simulate_strategy(strategy)
            if performance > 0.6:  # عملکرد قابل قبول
                strategy_key = f"auto_{self.improvement_cycles}_{tested_strategies}"
                self.learned_knowledge["strategy_performance"][strategy_key] = {
                    "strategy": strategy,
                    "performance": performance,
                    "created_date": datetime.now()
                }
                tested_strategies += 1
        
        self.improvement_stats["new_strategies_tested"] += tested_strategies
        logger.info(f"🎯 بهبود استراتژی: {tested_strategies} استراتژی جدید تست شد")

    def _parametric_self_improvement(self):
        """بهبود پارامترهای یادگیری"""
        # تنظیم خودکار learning rate بر اساس عملکرد
        if self.success_rate > 0.7:
            self.learning_rate = min(self.learning_rate * 1.1, 0.05)
        else:
            self.learning_rate = max(self.learning_rate * 0.9, 0.001)
            
        # تنظیم threshold بر اساس فعالیت شبکه
        avg_activity = np.mean(np.abs(self.membrane_potential))
        if avg_activity > 0.4:
            self.threshold = min(self.threshold * 1.05, 1.5)
        else:
            self.threshold = max(self.threshold * 0.95, 0.5)
        
        self.improvement_stats["performance_improvements"] += 1
        logger.info(f"⚙️ بهبود پارامترها: LR={self.learning_rate:.4f}, Threshold={self.threshold:.2f}")

    def _generate_new_strategy_variations(self):
        """تولید انواع جدید استراتژی"""
        base_strategies = ["momentum", "mean_reversion", "breakout", "sentiment_driven"]
        variations = []
        
        for base in base_strategies:
            # تغییر پارامترها
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
        """شبیه‌سازی استراتژی"""
        # شبیه‌سازی ساده عملکرد
        base_performance = 0.5
        
        # بهبود بر اساس نوع استراتژی
        if strategy["type"] == "momentum":
            base_performance += 0.2
        elif strategy["type"] == "breakout":
            base_performance += 0.15
            
        # بهبود بر اساس تایم‌فریم
        if strategy["time_frame"] == "4h":
            base_performance += 0.1
            
        return min(base_performance + random.uniform(-0.1, 0.1), 0.95)

    def _update_growth_stage(self):
        """به‌روزرسانی مرحله رشد"""
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
        """تبدیل داده‌های بازار به ورودی عصبی"""
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
        """استخراج نورون‌های مربوط به الگوهای ارز"""
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
        """پردازش سیگنال در شبکه عصبی"""
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
        """به‌روزرسانی اتصالات بر اساس STDP"""
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
        """تولید تحلیل و استراتژی از خروجی عصبی"""
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
            logger.error(f"Learning error: {e}")

    def get_ai_status(self):
        return {
            "total_neurons": self.num_neurons,
            "active_neurons": np.sum(self.membrane_potential > 0.1),
            "learning_sessions": self.learning_sessions,
            "strategies_generated": self.strategies_generated,
            "knowledge_base": sum(len(v) for v in self.learned_knowledge.values()),
            "growth_stage": self.growth_stage,
            "growth_percentage": self.growth_percentage,
            "improvement_cycles": self.improvement_cycles,
            "layer_activity": {
                layer: np.mean(self.membrane_potential[list(neurons)])
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
        """توقف خود-بهبودی توسط کاربر"""
        self.self_improvement_mode = False
        logger.info("⏹️ خود-بهبودی توسط کاربر متوقف شد")

    def resume_self_improvement(self):
        """ادامه خود-بهبودی توسط کاربر"""
        self.self_improvement_mode = True
        logger.info("▶️ خود-بهبودی توسط کاربر ادامه یافت")

# کلاس اصلی برای استفاده در اسکنر
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
            logger.error(f"Market analysis error: {e}")
            return {}
    
    def get_ai_status(self):
        return self.ai_core.get_ai_status()
    
    def get_improvement_status(self):
        return self.ai_core.get_improvement_status()
    
    def stop_self_improvement(self):
        return self.ai_core.stop_self_improvement()
    
    def resume_self_improvement(self):
        return self.ai_core.resume_self_improvement()
