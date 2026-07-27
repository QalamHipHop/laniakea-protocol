"""
Laniakea Protocol - Advanced Interactive Dashboard
داشبورد تعاملی پیشرفته

ویژگی‌ها:
- نمایش real-time آمار شبکه
- نمودارهای تعاملی
- مانیتورینگ عملکرد
- نمایش وضعیت نودها
- آمار بلاکچین
- وضعیت هوش مصنوعی
- لاگ‌های زنده
- کنترل‌های مدیریتی
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import deque, defaultdict
from dataclasses import dataclass, asdict
import psutil  # برای مانیتورینگ سیستم


@dataclass
class SystemMetrics:
    """معیارهای سیستم"""

    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_sent: int
    network_recv: int
    active_connections: int


@dataclass
class BlockchainMetrics:
    """معیارهای بلاکچین"""

    timestamp: float
    block_height: int
    total_transactions: int
    pending_transactions: int
    avg_block_time: float
    network_hashrate: float
    active_nodes: int


@dataclass
class AIMetrics:
    """معیارهای هوش مصنوعی"""

    timestamp: float
    knowledge_graph_size: int
    total_learnings: int
    active_tasks: int
    suggestions_made: int
    evolution_cycles: int
    last_evolution: Optional[str]


class AdvancedDashboard:
    """
    داشبورد تعاملی پیشرفته

    این کلاس داده‌های real-time از تمام بخش‌های سیستم را
    جمع‌آوری و نمایش می‌دهد.
    """

    def __init__(self, history_size: int = 1000, update_interval: float = 1.0):
        """
        راه‌اندازی dashboard

        Args:
            history_size: تعداد نقاط داده برای نگهداری
            update_interval: فاصله به‌روزرسانی (ثانیه)
        """
        self.history_size = history_size
        self.update_interval = update_interval

        # تاریخچه معیارها
        self.system_history: deque = deque(maxlen=history_size)
        self.blockchain_history: deque = deque(maxlen=history_size)
        self.ai_history: deque = deque(maxlen=history_size)

        # آمار کلی
        self.stats = {
            "uptime_start": time.time(),
            "total_requests": 0,
            "total_errors": 0,
            "peak_cpu": 0.0,
            "peak_memory": 0.0,
        }

        # وضعیت نودها
        self.nodes: Dict[str, Dict] = {}

        # رویدادهای اخیر
        self.recent_events: deque = deque(maxlen=100)

        # Alert ها
        self.alerts: List[Dict] = []

        # وضعیت
        self.is_running = False
        self._monitor_task: Optional[asyncio.Task] = None

    async def start(self):
        """شروع مانیتورینگ"""
        if self.is_running:
            return

        self.is_running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        print("✅ Dashboard شروع به کار کرد")

    async def stop(self):
        """توقف مانیتورینگ"""
        self.is_running = False

        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

        print("⏹️ Dashboard متوقف شد")

    async def _monitor_loop(self):
        """حلقه اصلی مانیتورینگ"""
        while self.is_running:
            try:
                # جمع‌آوری معیارها
                await self._collect_system_metrics()
                await self._collect_blockchain_metrics()
                await self._collect_ai_metrics()

                # بررسی alert ها
                await self._check_alerts()

                # به‌روزرسانی آمار
                self._update_stats()

                await asyncio.sleep(self.update_interval)

            except Exception as e:
                print(f"❌ خطا در monitor loop: {e}")
                await asyncio.sleep(5)

    async def _collect_system_metrics(self):
        """جمع‌آوری معیارهای سیستم"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # Memory
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent

            # Network
            net_io = psutil.net_io_counters()
            network_sent = net_io.bytes_sent
            network_recv = net_io.bytes_recv

            # Connections
            connections = len(psutil.net_connections())

            metrics = SystemMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                network_sent=network_sent,
                network_recv=network_recv,
                active_connections=connections,
            )

            self.system_history.append(metrics)

            # به‌روزرسانی peak values
            self.stats["peak_cpu"] = max(self.stats["peak_cpu"], cpu_percent)
            self.stats["peak_memory"] = max(self.stats["peak_memory"], memory_percent)

        except Exception as e:
            print(f"❌ خطا در جمع‌آوری system metrics: {e}")

    async def _collect_blockchain_metrics(self):
        """جمع‌آوری معیارهای بلاکچین"""
        try:
            # این داده‌ها باید از blockchain واقعی بیایند
            # فعلاً داده‌های نمونه
            metrics = BlockchainMetrics(
                timestamp=time.time(),
                block_height=len(self.blockchain_history) + 1,
                total_transactions=len(self.blockchain_history) * 10,
                pending_transactions=5,
                avg_block_time=60.0,
                network_hashrate=1000000.0,
                active_nodes=len(self.nodes),
            )

            self.blockchain_history.append(metrics)

        except Exception as e:
            print(f"❌ خطا در جمع‌آوری blockchain metrics: {e}")

    async def _collect_ai_metrics(self):
        """جمع‌آوری معیارهای هوش مصنوعی"""
        try:
            # این داده‌ها باید از AI system واقعی بیایند
            metrics = AIMetrics(
                timestamp=time.time(),
                knowledge_graph_size=100 + len(self.ai_history),
                total_learnings=50 + len(self.ai_history) * 2,
                active_tasks=3,
                suggestions_made=10 + len(self.ai_history),
                evolution_cycles=len(self.ai_history) // 10,
                last_evolution=datetime.now().isoformat() if self.ai_history else None,
            )

            self.ai_history.append(metrics)

        except Exception as e:
            print(f"❌ خطا در جمع‌آوری AI metrics: {e}")

    async def _check_alerts(self):
        """بررسی و ایجاد alert ها"""
        # بررسی CPU
        if self.system_history:
            latest = self.system_history[-1]

            if latest.cpu_percent > 90:
                self._add_alert("HIGH_CPU", f"CPU usage: {latest.cpu_percent}%", "warning")

            if latest.memory_percent > 90:
                self._add_alert("HIGH_MEMORY", f"Memory usage: {latest.memory_percent}%", "warning")

            if latest.disk_percent > 90:
                self._add_alert("HIGH_DISK", f"Disk usage: {latest.disk_percent}%", "warning")

    def _add_alert(self, alert_type: str, message: str, severity: str = "info"):
        """افزودن alert"""
        alert = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "type": alert_type,
            "message": message,
            "severity": severity,
            "acknowledged": False,
        }

        # جلوگیری از alert های تکراری
        if not any(a["type"] == alert_type and not a["acknowledged"] for a in self.alerts):
            self.alerts.append(alert)
            print(f"⚠️ Alert: {message}")

    def _update_stats(self):
        """به‌روزرسانی آمار کلی"""
        self.stats["uptime"] = time.time() - self.stats["uptime_start"]

    def add_event(self, event_type: str, message: str, **kwargs):
        """افزودن رویداد"""
        event = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "type": event_type,
            "message": message,
            **kwargs,
        }
        self.recent_events.append(event)

    def register_node(self, node_id: str, node_info: Dict):
        """ثبت یک نود"""
        self.nodes[node_id] = {
            **node_info,
            "registered_at": time.time(),
            "last_seen": time.time(),
            "status": "active",
        }
        self.add_event("NODE_JOINED", f"Node {node_id} joined the network")

    def update_node(self, node_id: str, updates: Dict):
        """به‌روزرسانی اطلاعات نود"""
        if node_id in self.nodes:
            self.nodes[node_id].update(updates)
            self.nodes[node_id]["last_seen"] = time.time()

    def remove_node(self, node_id: str):
        """حذف نود"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            self.add_event("NODE_LEFT", f"Node {node_id} left the network")

    def get_summary(self) -> Dict[str, Any]:
        """دریافت خلاصه وضعیت"""
        uptime = time.time() - self.stats["uptime_start"]

        # آخرین معیارها
        latest_system = self.system_history[-1] if self.system_history else None
        latest_blockchain = self.blockchain_history[-1] if self.blockchain_history else None
        latest_ai = self.ai_history[-1] if self.ai_history else None

        return {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "uptime_seconds": uptime,
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "system": {
                "cpu_percent": latest_system.cpu_percent if latest_system else 0,
                "memory_percent": latest_system.memory_percent if latest_system else 0,
                "disk_percent": latest_system.disk_percent if latest_system else 0,
                "active_connections": latest_system.active_connections if latest_system else 0,
                "peak_cpu": self.stats["peak_cpu"],
                "peak_memory": self.stats["peak_memory"],
            },
            "blockchain": {
                "block_height": latest_blockchain.block_height if latest_blockchain else 0,
                "total_transactions": (
                    latest_blockchain.total_transactions if latest_blockchain else 0
                ),
                "pending_transactions": (
                    latest_blockchain.pending_transactions if latest_blockchain else 0
                ),
                "avg_block_time": latest_blockchain.avg_block_time if latest_blockchain else 0,
                "active_nodes": len(self.nodes),
            },
            "ai": {
                "knowledge_graph_size": latest_ai.knowledge_graph_size if latest_ai else 0,
                "total_learnings": latest_ai.total_learnings if latest_ai else 0,
                "active_tasks": latest_ai.active_tasks if latest_ai else 0,
                "suggestions_made": latest_ai.suggestions_made if latest_ai else 0,
                "evolution_cycles": latest_ai.evolution_cycles if latest_ai else 0,
            },
            "alerts": {
                "total": len(self.alerts),
                "unacknowledged": len([a for a in self.alerts if not a["acknowledged"]]),
                "by_severity": self._count_by_severity(),
            },
            "nodes": {
                "total": len(self.nodes),
                "active": len([n for n in self.nodes.values() if n["status"] == "active"]),
                "inactive": len([n for n in self.nodes.values() if n["status"] != "active"]),
            },
        }

    def _count_by_severity(self) -> Dict[str, int]:
        """شمارش alert ها بر اساس شدت"""
        counts = defaultdict(int)
        for alert in self.alerts:
            if not alert["acknowledged"]:
                counts[alert["severity"]] += 1
        return dict(counts)

    def get_time_series(self, metric_type: str, duration_seconds: int = 300) -> List[Dict]:
        """
        دریافت time series برای یک معیار

        Args:
            metric_type: نوع معیار (system/blockchain/ai)
            duration_seconds: مدت زمان (ثانیه)

        Returns:
            لیست داده‌ها
        """
        cutoff = time.time() - duration_seconds

        if metric_type == "system":
            history = self.system_history
        elif metric_type == "blockchain":
            history = self.blockchain_history
        elif metric_type == "ai":
            history = self.ai_history
        else:
            return []

        return [asdict(item) for item in history if item.timestamp >= cutoff]

    def acknowledge_alert(self, alert_index: int):
        """تأیید یک alert"""
        if 0 <= alert_index < len(self.alerts):
            self.alerts[alert_index]["acknowledged"] = True
            self.alerts[alert_index]["acknowledged_at"] = time.time()

    def clear_acknowledged_alerts(self):
        """پاکسازی alert های تأیید شده"""
        self.alerts = [a for a in self.alerts if not a["acknowledged"]]

    def export_metrics(self, filepath: str):
        """صادرات معیارها به فایل"""
        data = {
            "exported_at": datetime.now().isoformat(),
            "system_metrics": [asdict(m) for m in self.system_history],
            "blockchain_metrics": [asdict(m) for m in self.blockchain_history],
            "ai_metrics": [asdict(m) for m in self.ai_history],
            "stats": self.stats,
            "alerts": self.alerts,
            "nodes": self.nodes,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        print(f"✅ Metrics exported to {filepath}")


# Singleton instance
_dashboard_instance: Optional[AdvancedDashboard] = None


def get_dashboard() -> AdvancedDashboard:
    """دریافت instance dashboard"""
    global _dashboard_instance

    if _dashboard_instance is None:
        _dashboard_instance = AdvancedDashboard()

    return _dashboard_instance


# مثال استفاده
async def main():
    """تست dashboard"""
    dashboard = get_dashboard()

    # شروع
    await dashboard.start()

    # ثبت چند نود
    dashboard.register_node("node_1", {"ip": "192.168.1.1", "port": 5000})
    dashboard.register_node("node_2", {"ip": "192.168.1.2", "port": 5001})

    # اجرا برای مدتی
    print("📊 Dashboard در حال اجرا...")
    for i in range(10):
        await asyncio.sleep(2)

        # نمایش خلاصه
        summary = dashboard.get_summary()
        print(f"\n{'='*60}")
        print(f"⏱️  Uptime: {summary['uptime_formatted']}")
        print(f"💻 CPU: {summary['system']['cpu_percent']:.1f}%")
        print(f"🧠 Memory: {summary['system']['memory_percent']:.1f}%")
        print(f"⛓️  Blocks: {summary['blockchain']['block_height']}")
        print(f"🤖 AI Knowledge: {summary['ai']['knowledge_graph_size']} nodes")
        print(f"⚠️  Alerts: {summary['alerts']['unacknowledged']}")

    # توقف
    await dashboard.stop()

    # صادرات
    dashboard.export_metrics("dashboard_metrics.json")


if __name__ == "__main__":
    asyncio.run(main())
