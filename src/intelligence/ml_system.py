"""
Laniakea Protocol - Machine Learning System
سیستم یادگیری ماشین داخلی برای تحلیل و پیش‌بینی
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from time import time
import json


@dataclass
class TrainingData:
    """داده آموزشی"""
    features: np.ndarray
    labels: np.ndarray
    timestamp: float


class NeuralNetwork:
    """
    شبکه عصبی ساده برای یادگیری الگوها
    """
    
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        """
        Args:
            input_size: تعداد ورودی‌ها
            hidden_size: تعداد نورون‌های لایه مخفی
            output_size: تعداد خروجی‌ها
        """
        # وزن‌ها
        self.w1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros((1, hidden_size))
        self.w2 = np.random.randn(hidden_size, output_size) * 0.01
        self.b2 = np.zeros((1, output_size))
        
        # تاریخچه آموزش
        self.training_history: List[float] = []
        
        print(f"🧠 Neural Network initialized: {input_size}-{hidden_size}-{output_size}")
    
    def sigmoid(self, x: np.ndarray) -> np.ndarray:
        """تابع فعال‌سازی sigmoid"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def sigmoid_derivative(self, x: np.ndarray) -> np.ndarray:
        """مشتق sigmoid"""
        return x * (1 - x)
    
    def forward(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        پیش‌خور
        
        Args:
            X: ورودی
        
        Returns:
            (hidden_output, final_output)
        """
        # لایه مخفی
        z1 = np.dot(X, self.w1) + self.b1
        a1 = self.sigmoid(z1)
        
        # لایه خروجی
        z2 = np.dot(a1, self.w2) + self.b2
        a2 = self.sigmoid(z2)
        
        return a1, a2
    
    def backward(
        self,
        X: np.ndarray,
        y: np.ndarray,
        a1: np.ndarray,
        a2: np.ndarray,
        learning_rate: float = 0.01
    ):
        """
        پس‌انتشار خطا
        
        Args:
            X: ورودی
            y: برچسب واقعی
            a1: خروجی لایه مخفی
            a2: خروجی نهایی
            learning_rate: نرخ یادگیری
        """
        m = X.shape[0]
        
        # محاسبه خطا
        error = a2 - y
        
        # گرادیان لایه خروجی
        d2 = error * self.sigmoid_derivative(a2)
        dw2 = np.dot(a1.T, d2) / m
        db2 = np.sum(d2, axis=0, keepdims=True) / m
        
        # گرادیان لایه مخفی
        d1 = np.dot(d2, self.w2.T) * self.sigmoid_derivative(a1)
        dw1 = np.dot(X.T, d1) / m
        db1 = np.sum(d1, axis=0, keepdims=True) / m
        
        # به‌روزرسانی وزن‌ها
        self.w2 -= learning_rate * dw2
        self.b2 -= learning_rate * db2
        self.w1 -= learning_rate * dw1
        self.b1 -= learning_rate * db1
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 1000,
        learning_rate: float = 0.01,
        verbose: bool = False
    ):
        """
        آموزش شبکه
        
        Args:
            X: داده ورودی
            y: برچسب‌ها
            epochs: تعداد epoch
            learning_rate: نرخ یادگیری
            verbose: نمایش پیشرفت
        """
        for epoch in range(epochs):
            # پیش‌خور
            a1, a2 = self.forward(X)
            
            # محاسبه loss
            loss = np.mean((a2 - y) ** 2)
            self.training_history.append(loss)
            
            # پس‌انتشار
            self.backward(X, y, a1, a2, learning_rate)
            
            if verbose and (epoch + 1) % 100 == 0:
                print(f"Epoch {epoch+1}/{epochs}, Loss: {loss:.6f}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        پیش‌بینی
        
        Args:
            X: ورودی
        
        Returns:
            خروجی
        """
        _, output = self.forward(X)
        return output
    
    def save_weights(self) -> Dict:
        """ذخیره وزن‌ها"""
        return {
            "w1": self.w1.tolist(),
            "b1": self.b1.tolist(),
            "w2": self.w2.tolist(),
            "b2": self.b2.tolist()
        }
    
    def load_weights(self, weights: Dict):
        """بارگذاری وزن‌ها"""
        self.w1 = np.array(weights["w1"])
        self.b1 = np.array(weights["b1"])
        self.w2 = np.array(weights["w2"])
        self.b2 = np.array(weights["b2"])


class ValuePredictor:
    """
    پیش‌بینی‌کننده ارزش راه‌حل‌ها
    
    از داده‌های گذشته یاد می‌گیرد و ارزش راه‌حل‌های جدید را پیش‌بینی می‌کند
    """
    
    def __init__(self):
        # شبکه عصبی برای هر بُعد
        self.models: Dict[str, NeuralNetwork] = {
            "knowledge": NeuralNetwork(10, 20, 1),
            "computation": NeuralNetwork(10, 20, 1),
            "originality": NeuralNetwork(10, 20, 1),
            "consciousness": NeuralNetwork(10, 20, 1)
        }
        
        self.training_data: List[TrainingData] = []
        
        print("🔮 Value Predictor initialized")
    
    def extract_features(self, solution_text: str, task_difficulty: float) -> np.ndarray:
        """
        استخراج ویژگی از راه‌حل
        
        Args:
            solution_text: متن راه‌حل
            task_difficulty: دشواری تسک
        
        Returns:
            بردار ویژگی
        """
        features = []
        
        # ویژگی‌های متن
        features.append(len(solution_text))  # طول
        features.append(len(solution_text.split()))  # تعداد کلمات
        features.append(len(set(solution_text.split())))  # تعداد کلمات یکتا
        features.append(solution_text.count('\n'))  # تعداد خطوط
        
        # ویژگی‌های محتوا
        features.append(float('math' in solution_text.lower()))
        features.append(float('algorithm' in solution_text.lower()))
        features.append(float('theory' in solution_text.lower()))
        features.append(float('proof' in solution_text.lower()))
        
        # ویژگی تسک
        features.append(task_difficulty)
        features.append(task_difficulty ** 2)
        
        return np.array(features).reshape(1, -1)
    
    def train_on_solution(
        self,
        solution_text: str,
        task_difficulty: float,
        actual_values: Dict[str, float]
    ):
        """
        آموزش بر اساس یک راه‌حل
        
        Args:
            solution_text: متن راه‌حل
            task_difficulty: دشواری
            actual_values: ارزش‌های واقعی
        """
        features = self.extract_features(solution_text, task_difficulty)
        
        # آموزش هر مدل
        for dimension, value in actual_values.items():
            if dimension in self.models:
                labels = np.array([[value / 100.0]])  # نرمال‌سازی
                self.models[dimension].train(features, labels, epochs=10, verbose=False)
    
    def predict_value(
        self,
        solution_text: str,
        task_difficulty: float
    ) -> Dict[str, float]:
        """
        پیش‌بینی ارزش راه‌حل
        
        Args:
            solution_text: متن راه‌حل
            task_difficulty: دشواری
        
        Returns:
            ارزش‌های پیش‌بینی شده
        """
        features = self.extract_features(solution_text, task_difficulty)
        
        predictions = {}
        for dimension, model in self.models.items():
            pred = model.predict(features)[0, 0]
            predictions[dimension] = float(pred * 100.0)  # برگرداندن به مقیاس اصلی
        
        return predictions
    
    def get_model_stats(self) -> Dict:
        """آمار مدل‌ها"""
        stats = {}
        for dimension, model in self.models.items():
            if model.training_history:
                stats[dimension] = {
                    "training_iterations": len(model.training_history),
                    "final_loss": model.training_history[-1],
                    "initial_loss": model.training_history[0]
                }
        return stats


class PatternRecognizer:
    """
    تشخیص الگو در بلاک‌چین
    
    الگوهای مفید را شناسایی می‌کند:
    - الگوهای زمانی
    - الگوهای ارزشی
    - الگوهای کاربری
    """
    
    def __init__(self):
        self.patterns: Dict[str, List] = {
            "temporal": [],
            "value": [],
            "user": []
        }
        
        print("🔍 Pattern Recognizer initialized")
    
    def analyze_temporal_patterns(self, blocks: List) -> Dict:
        """
        تحلیل الگوهای زمانی
        
        Args:
            blocks: لیست بلاک‌ها
        
        Returns:
            الگوهای شناسایی شده
        """
        if len(blocks) < 10:
            return {"message": "Not enough data"}
        
        # استخراج زمان‌ها
        timestamps = [b.timestamp for b in blocks]
        
        # محاسبه فاصله زمانی
        intervals = np.diff(timestamps)
        
        patterns = {
            "average_block_time": float(np.mean(intervals)),
            "std_block_time": float(np.std(intervals)),
            "min_block_time": float(np.min(intervals)),
            "max_block_time": float(np.max(intervals))
        }
        
        return patterns
    
    def analyze_value_patterns(self, blocks: List) -> Dict:
        """تحلیل الگوهای ارزشی"""
        if not blocks:
            return {}
        
        # استخراج ارزش‌ها
        total_values = []
        for block in blocks:
            if hasattr(block, 'solution') and block.solution:
                total_values.append(block.solution.value_vector.total_value())
        
        if not total_values:
            return {"message": "No value data"}
        
        values_array = np.array(total_values)
        
        return {
            "average_value": float(np.mean(values_array)),
            "std_value": float(np.std(values_array)),
            "max_value": float(np.max(values_array)),
            "trend": "increasing" if len(values_array) > 1 and values_array[-1] > values_array[0] else "stable"
        }
    
    def detect_anomalies(self, data: np.ndarray, threshold: float = 2.0) -> List[int]:
        """
        تشخیص ناهنجاری
        
        Args:
            data: داده
            threshold: آستانه (چند انحراف معیار)
        
        Returns:
            ایندکس‌های ناهنجار
        """
        mean = np.mean(data)
        std = np.std(data)
        
        anomalies = []
        for i, value in enumerate(data):
            z_score = abs((value - mean) / std) if std > 0 else 0
            if z_score > threshold:
                anomalies.append(i)
        
        return anomalies


class ReinforcementLearner:
    """
    یادگیری تقویتی برای بهینه‌سازی استراتژی
    
    یاد می‌گیرد چه تصمیماتی بهترین نتیجه را دارند
    """
    
    def __init__(self, n_actions: int):
        """
        Args:
            n_actions: تعداد اعمال ممکن
        """
        self.n_actions = n_actions
        self.q_table: Dict[str, np.ndarray] = {}  # state -> Q values
        
        # پارامترها
        self.alpha = 0.1  # نرخ یادگیری
        self.gamma = 0.9  # ضریب تخفیف
        self.epsilon = 0.1  # نرخ اکتشاف
        
        print(f"🎮 Reinforcement Learner initialized with {n_actions} actions")
    
    def get_q_values(self, state: str) -> np.ndarray:
        """دریافت Q values برای یک state"""
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.n_actions)
        return self.q_table[state]
    
    def choose_action(self, state: str) -> int:
        """
        انتخاب عمل (epsilon-greedy)
        
        Args:
            state: وضعیت فعلی
        
        Returns:
            شماره عمل
        """
        if np.random.random() < self.epsilon:
            # اکتشاف
            return np.random.randint(self.n_actions)
        else:
            # بهره‌برداری
            q_values = self.get_q_values(state)
            return int(np.argmax(q_values))
    
    def update(
        self,
        state: str,
        action: int,
        reward: float,
        next_state: str
    ):
        """
        به‌روزرسانی Q-table
        
        Args:
            state: وضعیت فعلی
            action: عمل انجام شده
            reward: پاداش
            next_state: وضعیت بعدی
        """
        current_q = self.get_q_values(state)[action]
        next_max_q = np.max(self.get_q_values(next_state))
        
        # Q-learning update
        new_q = current_q + self.alpha * (reward + self.gamma * next_max_q - current_q)
        
        self.q_table[state][action] = new_q
    
    def get_stats(self) -> Dict:
        """آمار یادگیری"""
        return {
            "states_explored": len(self.q_table),
            "total_q_values": sum(len(q) for q in self.q_table.values()),
            "epsilon": self.epsilon
        }


class MLOrchestrator:
    """
    هماهنگ‌کننده سیستم‌های ML
    
    تمام اجزای ML را مدیریت و هماهنگ می‌کند
    """
    
    def __init__(self):
        self.value_predictor = ValuePredictor()
        self.pattern_recognizer = PatternRecognizer()
        self.rl_learner = ReinforcementLearner(n_actions=5)
        
        print("🎯 ML Orchestrator initialized")
    
    def analyze_blockchain(self, blocks: List) -> Dict:
        """تحلیل کامل بلاک‌چین"""
        return {
            "temporal_patterns": self.pattern_recognizer.analyze_temporal_patterns(blocks),
            "value_patterns": self.pattern_recognizer.analyze_value_patterns(blocks)
        }
    
    def get_stats(self) -> Dict:
        """آمار کامل ML"""
        return {
            "value_predictor": self.value_predictor.get_model_stats(),
            "rl_learner": self.rl_learner.get_stats(),
            "pattern_recognizer": {
                "patterns_found": sum(len(p) for p in self.pattern_recognizer.patterns.values())
            }
        }
