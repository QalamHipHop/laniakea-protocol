"""
Live Dashboard - داشبورد زنده و تعاملی
رابط کاربری پیشرفته برای مانیتورینگ real-time
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from collections import deque


class MetricsCollector:
    """جمع‌آوری و ذخیره متریک‌ها"""

    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics = {
            "blockchain": deque(maxlen=max_history),
            "network": deque(maxlen=max_history),
            "cognitive": deque(maxlen=max_history),
            "performance": deque(maxlen=max_history),
            "simulation": deque(maxlen=max_history),
        }
        self.alerts = deque(maxlen=100)

    def record(self, category: str, data: Dict[str, Any]):
        """ثبت یک متریک"""
        entry = {"timestamp": datetime.now().isoformat(), **data}

        if category in self.metrics:
            self.metrics[category].append(entry)

    def get_recent(self, category: str, limit: int = 100) -> List[Dict[str, Any]]:
        """دریافت متریک‌های اخیر"""
        if category not in self.metrics:
            return []

        return list(self.metrics[category])[-limit:]

    def get_summary(self) -> Dict[str, Any]:
        """خلاصه کلی متریک‌ها"""
        summary = {}

        for category, data in self.metrics.items():
            if data:
                latest = data[-1]
                summary[category] = {"latest": latest, "count": len(data)}

        return summary


class DashboardGenerator:
    """تولید HTML داشبورد"""

    def __init__(self, metrics_collector: MetricsCollector):
        self.collector = metrics_collector

    def generate_html(self, blockchain_data: Dict = None, network_data: Dict = None) -> str:
        """تولید HTML داشبورد"""

        if blockchain_data is None:
            blockchain_data = {}
        if network_data is None:
            network_data = {}

        chain_length = blockchain_data.get("chain_length", 0)
        total_value = blockchain_data.get("total_value", 0)
        active_tasks = blockchain_data.get("active_tasks", 0)
        peer_count = network_data.get("peer_count", 0)
        tps = network_data.get("tps", 0.0)

        html = """<!DOCTYPE html>
	<html lang="fa" dir="rtl">
	<head>
	    <meta charset="UTF-8">
	    <title>Laniakea Protocol - Live Dashboard</title>
	    <link rel="stylesheet" href="/static/style.css">
	</head>
	<body>
	    <div class="container">
	        <header>
	            <h1>🌌 پروتوکل لانیاکیا</h1>
	            <p class="subtitle">داشبورد زنده نود (v0.0.1)</p>
	        </header>
	        
	        <div class="stats-grid">
	            <div class="stat-card">
	                <span class="label">ارتفاع بلاک‌چین</span>
	                <span class="value">{chain_length}</span>
	            </div>
	            
	            <div class="stat-card">
	                <span class="label">نودهای متصل</span>
	                <span class="value">{peer_count}</span>
	            </div>
	            
	            <div class="stat-card">
	                <span class="label">ارزش دانشی کل</span>
	                <span class="value">{total_value:.0f}</span>
	            </div>
	            
	            <div class="stat-card">
	                <span class="label">تسک‌های فعال</span>
	                <span class="value">{active_tasks}</span>
	            </div>
	            
	            <div class="stat-card">
	                <span class="label">TPS شبکه</span>
	                <span class="value">{tps:.2f}</span>
	            </div>
	        </div>
	        
	        <footer>
	            <span class="update-time">آخرین به‌روزرسانی: {timestamp}</span>
	            <p>Laniakea Protocol v0.0.1 - The Cosmic Computational Organism</p>
	        </footer>
	    </div>
	</body>
	</html>""".format(
            chain_length=chain_length,
            peer_count=peer_count,
            total_value=total_value,
            active_tasks=active_tasks,
            tps=tps,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        return html


# Global instance
_metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """دریافت instance جهانی collector"""
    return _metrics_collector


def generate_dashboard(blockchain_data: Dict = None, network_data: Dict = None) -> str:
    """تولید HTML داشبورد"""
    generator = DashboardGenerator(_metrics_collector)
    return generator.generate_html(blockchain_data, network_data)
