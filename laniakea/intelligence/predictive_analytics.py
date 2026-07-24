"""
Predictive Analytics - تحلیل پیش‌بینی‌کننده
پیش‌بینی روندها، الگوها و آینده شبکه با استفاده از ML و AI
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json

try:
    from openai import OpenAI  # type: ignore
    _OPENAI_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore
    _OPENAI_AVAILABLE = False


class TrendAnalyzer:
    """تحلیلگر روندها"""

    def __init__(self):
        self.data_points = defaultdict(list)
        self.predictions = {}

    def add_data_point(self, metric: str, value: float, timestamp: Optional[datetime] = None):
        """افزودن نقطه داده"""
        if timestamp is None:
            timestamp = datetime.now()

        self.data_points[metric].append({"value": value, "timestamp": timestamp.isoformat()})

    def calculate_trend(self, metric: str, window_size: int = 10) -> Dict[str, Any]:
        """محاسبه روند"""

        if metric not in self.data_points or len(self.data_points[metric]) < 2:
            return {"trend": "insufficient_data"}

        recent_data = self.data_points[metric][-window_size:]
        values = [d["value"] for d in recent_data]

        # محاسبه روند خطی ساده
        n = len(values)
        x = np.arange(n)
        y = np.array(values)

        # Least squares regression
        slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x) ** 2)
        intercept = (np.sum(y) - slope * np.sum(x)) / n

        # تعیین جهت روند
        if slope > 0.1:
            trend_direction = "increasing"
        elif slope < -0.1:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"

        # محاسبه R²
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        return {
            "metric": metric,
            "trend": trend_direction,
            "slope": float(slope),
            "r_squared": float(r_squared),
            "current_value": values[-1],
            "avg_value": float(np.mean(values)),
            "volatility": float(np.std(values)),
            "data_points": len(values),
        }

    def predict_next_value(self, metric: str, steps_ahead: int = 1) -> Optional[float]:
        """پیش‌بینی مقدار بعدی"""

        trend = self.calculate_trend(metric)

        if trend.get("trend") == "insufficient_data":
            return None

        # پیش‌بینی ساده بر اساس روند
        predicted = trend["current_value"] + (trend["slope"] * steps_ahead)

        return max(0, predicted)  # جلوگیری از مقادیر منفی


class PatternRecognizer:
    """شناسایی الگوها در داده‌ها"""

    def __init__(self):
        self.known_patterns = {
            "spike": self._detect_spike,
            "drop": self._detect_drop,
            "cycle": self._detect_cycle,
            "anomaly": self._detect_anomaly,
        }

    def detect_patterns(self, data: List[float]) -> List[Dict[str, Any]]:
        """شناسایی تمام الگوها"""

        if len(data) < 5:
            return []

        patterns = []

        for pattern_name, detector in self.known_patterns.items():
            result = detector(data)
            if result:
                patterns.append({"pattern": pattern_name, **result})

        return patterns

    def _detect_spike(self, data: List[float]) -> Optional[Dict[str, Any]]:
        """شناسایی spike (افزایش ناگهانی)"""

        mean = np.mean(data)
        std = np.std(data)

        for i in range(len(data) - 1):
            if data[i + 1] > mean + 2 * std and data[i] < mean + std:
                return {"position": i + 1, "magnitude": data[i + 1] - data[i], "confidence": 0.8}

        return None

    def _detect_drop(self, data: List[float]) -> Optional[Dict[str, Any]]:
        """شناسایی drop (کاهش ناگهانی)"""

        mean = np.mean(data)
        std = np.std(data)

        for i in range(len(data) - 1):
            if data[i + 1] < mean - 2 * std and data[i] > mean - std:
                return {"position": i + 1, "magnitude": data[i] - data[i + 1], "confidence": 0.8}

        return None

    def _detect_cycle(self, data: List[float]) -> Optional[Dict[str, Any]]:
        """شناسایی چرخه تکراری"""

        if len(data) < 10:
            return None

        # جستجوی الگوی تکراری ساده
        for period in range(2, len(data) // 2):
            correlation = 0
            count = 0

            for i in range(len(data) - period):
                if abs(data[i] - data[i + period]) < np.std(data) * 0.5:
                    correlation += 1
                count += 1

            if correlation / count > 0.7:
                return {"period": period, "confidence": correlation / count}

        return None

    def _detect_anomaly(self, data: List[float]) -> Optional[Dict[str, Any]]:
        """شناسایی ناهنجاری"""

        mean = np.mean(data)
        std = np.std(data)

        anomalies = []

        for i, value in enumerate(data):
            z_score = abs((value - mean) / std) if std > 0 else 0

            if z_score > 3:
                anomalies.append({"position": i, "value": value, "z_score": z_score})

        if anomalies:
            return {
                "count": len(anomalies),
                "positions": [a["position"] for a in anomalies],
                "confidence": 0.9,
            }

        return None


class PredictiveEngine:
    """موتور پیش‌بینی با AI"""

    def __init__(self):
        # Only instantiate the OpenAI client when the optional dep is
        # actually present. Otherwise fall back to a deterministic stub so
        # that the rest of the intelligence package still imports cleanly
        # on minimal installs.
        self.client = OpenAI() if _OPENAI_AVAILABLE else None
        self.trend_analyzer = TrendAnalyzer()
        self.pattern_recognizer = PatternRecognizer()
        self.predictions_history = []
        self._offline = not _OPENAI_AVAILABLE

    async def analyze_blockchain_future(
        self, blockchain_data: Dict[str, Any], network_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """تحلیل و پیش‌بینی آینده بلاک‌چین"""

        # جمع‌آوری داده‌های تاریخی
        historical_summary = {
            "blockchain": blockchain_data,
            "network": network_data,
            "timestamp": datetime.now().isoformat(),
        }

        # پیش‌بینی با AI (با fallback امن در صورت نبود openai)
        if self._offline or self.client is None:
            predictions = self._offline_prediction(historical_summary)
        else:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a blockchain analytics expert specializing in predictive analysis.
Analyze trends and provide actionable insights about the future state of the network.""",
                        },
                        {
                            "role": "user",
                            "content": f"""Analyze this blockchain network data and predict future trends:

Current State:
{json.dumps(historical_summary, indent=2)}

Provide predictions for:
1. Network growth trajectory (next 7 days)
2. Potential bottlenecks or issues
3. Recommended optimizations
4. Value creation opportunities

Format as JSON with keys: growth_prediction, risks, optimizations, opportunities""",
                        },
                    ],
                    temperature=0.7,
                    max_tokens=1500,
                )

                ai_analysis = response.choices[0].message.content

                # تلاش برای parse کردن JSON
                try:
                    predictions = json.loads(ai_analysis)
                except json.JSONDecodeError:
                    predictions = {"raw_analysis": ai_analysis, "parsed": False}
            except Exception as exc:  # pragma: no cover - network failure
                predictions = self._offline_prediction(historical_summary)
                predictions["warning"] = f"online prediction failed: {exc}"

        # افزودن تحلیل‌های آماری
        predictions["statistical_trends"] = self._calculate_statistical_predictions(
            blockchain_data, network_data
        )

        # ذخیره در تاریخچه
        self.predictions_history.append(
            {"timestamp": datetime.now().isoformat(), "predictions": predictions}
        )

        return predictions

    def _calculate_statistical_predictions(
        self, blockchain_data: Dict[str, Any], network_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """محاسبه پیش‌بینی‌های آماری"""

        predictions = {}

        # پیش‌بینی رشد زنجیره
        if "chain_length" in blockchain_data:
            self.trend_analyzer.add_data_point("chain_length", blockchain_data["chain_length"])
            predictions["chain_length_trend"] = self.trend_analyzer.calculate_trend("chain_length")
            predictions["predicted_chain_length_7d"] = self.trend_analyzer.predict_next_value(
                "chain_length", steps_ahead=7
            )

        # پیش‌بینی تعداد همتایان
        if "peer_count" in network_data:
            self.trend_analyzer.add_data_point("peer_count", network_data["peer_count"])
            predictions["peer_count_trend"] = self.trend_analyzer.calculate_trend("peer_count")

        # پیش‌بینی ارزش کل
        if "total_value" in blockchain_data:
            self.trend_analyzer.add_data_point("total_value", blockchain_data["total_value"])
            predictions["value_trend"] = self.trend_analyzer.calculate_trend("total_value")

        return predictions

    def detect_emerging_patterns(self, metric_name: str, data: List[float]) -> Dict[str, Any]:
        """شناسایی الگوهای نوظهور"""

        patterns = self.pattern_recognizer.detect_patterns(data)

        return {
            "metric": metric_name,
            "patterns_found": len(patterns),
            "patterns": patterns,
            "timestamp": datetime.now().isoformat(),
        }

    def generate_forecast_report(self) -> str:
        """تولید گزارش پیش‌بینی"""

        if not self.predictions_history:
            return "No predictions available yet."

        latest = self.predictions_history[-1]

        report = f"""
# 🔮 Laniakea Protocol - Predictive Analytics Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

Based on advanced AI analysis and statistical modeling, here are the key predictions for the Laniakea Protocol network:

## Growth Predictions

{json.dumps(latest['predictions'].get('growth_prediction', {}), indent=2)}

## Identified Risks

{json.dumps(latest['predictions'].get('risks', {}), indent=2)}

## Recommended Optimizations

{json.dumps(latest['predictions'].get('optimizations', {}), indent=2)}

## Value Creation Opportunities

{json.dumps(latest['predictions'].get('opportunities', {}), indent=2)}

## Statistical Trends

{json.dumps(latest['predictions'].get('statistical_trends', {}), indent=2)}

---

*This report is generated by Laniakea's Predictive Analytics Engine*
"""

        return report

    @staticmethod
    def _offline_prediction(historical_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Deterministic fallback used when the OpenAI client is missing."""
        chain = historical_summary.get("blockchain", {}) or {}
        network = historical_summary.get("network", {}) or {}
        return {
            "growth_prediction": {
                "trajectory": "stable",
                "next_7_days_block_growth_estimate": 0,
                "rationale": "offline stub - configure OPENAI_API_KEY to enable live analytics",
            },
            "risks": [
                "no live AI analytics - relying on deterministic stub",
            ],
            "optimizations": [
                "install openai or wire a custom LLM provider for richer insights",
            ],
            "opportunities": [
                "expose chain length and peer count metrics for richer predictions",
            ],
            "raw_snapshot": {
                "chain_length": len(chain) if isinstance(chain, list) else 0,
                "network_keys": list(network.keys()),
            },
        }


# Global instance
_predictive_engine = PredictiveEngine()


def get_predictive_engine() -> PredictiveEngine:
    """دریافت instance جهانی"""
    return _predictive_engine
