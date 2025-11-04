"""
Live Dashboard - داشبورد زنده و تعاملی
رابط کاربری پیشرفته برای مانیتورینگ real-time
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque
import hashlib


class MetricsCollector:
    """جمع‌آوری و ذخیره متریک‌ها"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics = {
            'blockchain': deque(maxlen=max_history),
            'network': deque(maxlen=max_history),
            'cognitive': deque(maxlen=max_history),
            'performance': deque(maxlen=max_history),
            'simulation': deque(maxlen=max_history)
        }
        self.alerts = deque(maxlen=100)
    
    def record(self, category: str, data: Dict[str, Any]):
        """ثبت یک متریک"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            **data
        }
        
        if category in self.metrics:
            self.metrics[category].append(entry)
            
            # بررسی آستانه‌ها برای هشدار
            self._check_thresholds(category, data)
    
    def _check_thresholds(self, category: str, data: Dict[str, Any]):
        """بررسی آستانه‌ها و ایجاد هشدار"""
        alerts = []
        
        if category == 'blockchain':
            if data.get('chain_length', 0) > 10000:
                alerts.append({
                    'level': 'info',
                    'message': 'Blockchain reached 10K blocks milestone! 🎉'
                })
        
        elif category == 'network':
            if data.get('peer_count', 0) < 3:
                alerts.append({
                    'level': 'warning',
                    'message': 'Low peer count detected'
                })
        
        elif category == 'performance':
            if data.get('cpu_usage', 0) > 80:
                alerts.append({
                    'level': 'critical',
                    'message': 'High CPU usage detected!'
                })
        
        for alert in alerts:
            alert['timestamp'] = datetime.now().isoformat()
            alert['category'] = category
            self.alerts.append(alert)
    
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
                summary[category] = {
                    'latest': latest,
                    'count': len(data),
                    'first_timestamp': data[0]['timestamp'] if data else None,
                    'last_timestamp': latest['timestamp']
                }
        
        return summary


class DashboardGenerator:
    """تولید HTML داشبورد"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.collector = metrics_collector
    
    def generate_html(self, blockchain_data: Dict = None, network_data: Dict = None) -> str:
        """تولید HTML داشبورد"""
        
        summary = self.collector.get_summary()
        recent_alerts = list(self.collector.alerts)[-10:]
        
        # داده‌های نمودار
        blockchain_metrics = self.collector.get_recent('blockchain', 50)
        network_metrics = self.collector.get_recent('network', 50)
        
        html = f"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌌 Laniakea Protocol - Live Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            animation: fadeIn 1s ease-in;
        }}
        
        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(255,255,255,0.5);
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            animation: slideUp 0.5s ease-out;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        .stat-card .icon {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .stat-card .label {{
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 5px;
        }}
        
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #ffd700;
        }}
        
        .chart-container {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .chart-container h2 {{
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        
        .alerts {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-top: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .alert-item {{
            padding: 10px;
            margin: 10px 0;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .alert-item.info {{
            background: rgba(52, 152, 219, 0.3);
        }}
        
        .alert-item.warning {{
            background: rgba(241, 196, 15, 0.3);
        }}
        
        .alert-item.critical {{
            background: rgba(231, 76, 60, 0.3);
        }}
        
        .pulse {{
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        @keyframes slideUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .live-indicator {{
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #00ff00;
            border-radius: 50%;
            margin-right: 10px;
            animation: pulse 1s infinite;
        }}
        
        .timestamp {{
            text-align: center;
            opacity: 0.7;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌌 LANIAKEA PROTOCOL</h1>
            <p class="subtitle">
                <span class="live-indicator"></span>
                Live Dashboard v0.0.1
            </p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">⛓️</div>
                <div class="label">Blockchain Height</div>
                <div class="value">{blockchain_data.get('chain_length', 0) if blockchain_data else 0}</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">🌐</div>
                <div class="label">Connected Peers</div>
                <div class="value">{network_data.get('peer_count', 0) if network_data else 0}</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">💎</div>
                <div class="label">Total Value</div>
                <div class="value">{blockchain_data.get('total_value', 0):.0f} if blockchain_data else 0}</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">🧠</div>
                <div class="label">AI Insights</div>
                <div class="value">{len(summary.get('cognitive', {{}}))}</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">🎯</div>
                <div class="label">Active Tasks</div>
                <div class="value">{blockchain_data.get('active_tasks', 0) if blockchain_data else 0}</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">⚡</div>
                <div class="label">Network TPS</div>
                <div class="value">{network_data.get('tps', 0):.2f} if network_data else 0}</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>📈 Blockchain Growth</h2>
            <canvas id="blockchainChart"></canvas>
        </div>
        
        <div class="chart-container">
            <h2>🌐 Network Activity</h2>
            <canvas id="networkChart"></canvas>
        </div>
        
        <div class="alerts">
            <h2>🔔 Recent Alerts</h2>
            {''.join([f'''
            <div class="alert-item {alert.get('level', 'info')}">
                <span>{'ℹ️' if alert.get('level') == 'info' else '⚠️' if alert.get('level') == 'warning' else '🚨'}</span>
                <span>{alert.get('message', '')}</span>
                <span style="margin-left: auto; opacity: 0.7; font-size: 0.9em;">{alert.get('timestamp', '')[:19]}</span>
            </div>
            ''' for alert in recent_alerts]) if recent_alerts else '<p style="opacity: 0.7;">No alerts</p>'}
        </div>
        
        <div class="timestamp">
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    
    <script>
        // Blockchain Chart
        const blockchainCtx = document.getElementById('blockchainChart').getContext('2d');
        const blockchainChart = new Chart(blockchainCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps([m['timestamp'][-8:] for m in blockchain_metrics[-20:]])},
                datasets: [{{
                    label: 'Chain Length',
                    data: {json.dumps([m.get('chain_length', 0) for m in blockchain_metrics[-20:]])},
                    borderColor: '#ffd700',
                    backgroundColor: 'rgba(255, 215, 0, 0.1)',
                    tension: 0.4,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        labels: {{
                            color: '#fff'
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        ticks: {{ color: '#fff' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }},
                    x: {{
                        ticks: {{ color: '#fff' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }}
                }}
            }}
        }});
        
        // Network Chart
        const networkCtx = document.getElementById('networkChart').getContext('2d');
        const networkChart = new Chart(networkCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps([m['timestamp'][-8:] for m in network_metrics[-20:]])},
                datasets: [{{
                    label: 'Peer Count',
                    data: {json.dumps([m.get('peer_count', 0) for m in network_metrics[-20:]])},
                    backgroundColor: 'rgba(52, 152, 219, 0.7)',
                    borderColor: '#3498db',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        labels: {{
                            color: '#fff'
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        ticks: {{ color: '#fff' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }},
                    x: {{
                        ticks: {{ color: '#fff' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }}
                }}
            }}
        }});
        
        // Auto-refresh every 5 seconds
        setTimeout(() => {{
            location.reload();
        }}, 5000);
    </script>
</body>
</html>
"""
        
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
