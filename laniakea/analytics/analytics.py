"""
LaniakeA Protocol - Advanced Analytics Module
Provides comprehensive blockchain metrics and analytics.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

logger = logging.getLogger("Analytics")


class BlockchainAnalytics:
    """Blockchain analytics and metrics"""
    
    def __init__(self):
        """Initialize analytics"""
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.events: List[Dict] = []
    
    def record_metric(self, metric_name: str, value: float, metadata: Dict = None):
        """Record a metric"""
        self.metrics[metric_name].append(value)
        
        event = {
            "metric": metric_name,
            "value": value,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        }
        self.events.append(event)
        
        logger.debug(f"Recorded metric: {metric_name} = {value}")
    
    def get_metric_stats(self, metric_name: str) -> Dict[str, Any]:
        """Get statistics for a metric"""
        values = self.metrics.get(metric_name, [])
        
        if not values:
            return {
                "metric": metric_name,
                "count": 0,
                "data": []
            }
        
        return {
            "metric": metric_name,
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": statistics.mean(values),
            "median": statistics.median(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0,
            "sum": sum(values),
            "data": values[-100:]  # Last 100 values
        }
    
    def get_all_metrics(self) -> Dict[str, Dict]:
        """Get statistics for all metrics"""
        return {
            metric: self.get_metric_stats(metric)
            for metric in self.metrics.keys()
        }


class TransactionAnalytics:
    """Transaction analytics"""
    
    def __init__(self):
        """Initialize transaction analytics"""
        self.transactions: List[Dict] = []
        self.stats = {
            "total": 0,
            "pending": 0,
            "confirmed": 0,
            "failed": 0,
            "total_volume": 0,
            "total_fees": 0
        }
    
    def add_transaction(self, tx_data: Dict):
        """Add transaction for analysis"""
        self.transactions.append({
            **tx_data,
            "timestamp": datetime.utcnow()
        })
        
        # Update stats
        self.stats["total"] += 1
        status = tx_data.get("status", "pending").lower()
        
        if status == "pending":
            self.stats["pending"] += 1
        elif status == "confirmed":
            self.stats["confirmed"] += 1
        elif status == "failed":
            self.stats["failed"] += 1
        
        self.stats["total_volume"] += tx_data.get("amount", 0)
        self.stats["total_fees"] += tx_data.get("fee", 0)
    
    def get_transaction_stats(self) -> Dict[str, Any]:
        """Get transaction statistics"""
        if not self.transactions:
            return {
                "total": 0,
                "stats": self.stats,
                "tps": 0,
                "avg_fee": 0,
                "avg_amount": 0
            }
        
        # Calculate TPS (transactions per second)
        time_span = (datetime.utcnow() - self.transactions[0]["timestamp"]).total_seconds()
        tps = self.stats["total"] / time_span if time_span > 0 else 0
        
        # Calculate averages
        amounts = [tx.get("amount", 0) for tx in self.transactions if tx.get("amount")]
        fees = [tx.get("fee", 0) for tx in self.transactions if tx.get("fee")]
        
        return {
            "total": self.stats["total"],
            "stats": self.stats,
            "tps": round(tps, 4),
            "avg_fee": statistics.mean(fees) if fees else 0,
            "avg_amount": statistics.mean(amounts) if amounts else 0,
            "pending_count": self.stats["pending"],
            "confirmed_count": self.stats["confirmed"],
            "failed_count": self.stats["failed"]
        }
    
    def get_transaction_volume_by_hour(self) -> Dict[str, int]:
        """Get transaction volume by hour"""
        volume_by_hour = defaultdict(int)
        
        for tx in self.transactions:
            hour = tx["timestamp"].strftime("%Y-%m-%d %H:00")
            volume_by_hour[hour] += 1
        
        return dict(volume_by_hour)
    
    def get_top_senders(self, limit: int = 10) -> List[Dict]:
        """Get top transaction senders"""
        sender_stats = defaultdict(lambda: {"count": 0, "volume": 0})
        
        for tx in self.transactions:
            sender = tx.get("sender", "unknown")
            sender_stats[sender]["count"] += 1
            sender_stats[sender]["volume"] += tx.get("amount", 0)
        
        top_senders = sorted(
            sender_stats.items(),
            key=lambda x: x[1]["volume"],
            reverse=True
        )[:limit]
        
        return [
            {
                "sender": sender,
                "transaction_count": stats["count"],
                "total_volume": stats["volume"]
            }
            for sender, stats in top_senders
        ]


class SmartContractAnalytics:
    """Smart contract analytics"""
    
    def __init__(self):
        """Initialize contract analytics"""
        self.contracts: Dict[str, Dict] = {}
        self.executions: List[Dict] = []
    
    def register_contract(self, contract_address: str, contract_data: Dict):
        """Register contract for analysis"""
        self.contracts[contract_address] = {
            **contract_data,
            "created_at": datetime.utcnow(),
            "execution_count": 0,
            "total_gas_used": 0,
            "failed_executions": 0
        }
    
    def record_execution(self, contract_address: str, execution_data: Dict):
        """Record contract execution"""
        if contract_address in self.contracts:
            self.contracts[contract_address]["execution_count"] += 1
            self.contracts[contract_address]["total_gas_used"] += execution_data.get("gas_used", 0)
            
            if execution_data.get("status") == "failed":
                self.contracts[contract_address]["failed_executions"] += 1
        
        self.executions.append({
            "contract_address": contract_address,
            **execution_data,
            "timestamp": datetime.utcnow()
        })
    
    def get_contract_stats(self, contract_address: str) -> Dict[str, Any]:
        """Get statistics for a contract"""
        contract = self.contracts.get(contract_address)
        
        if not contract:
            return {"error": "Contract not found"}
        
        return {
            "address": contract_address,
            "owner": contract.get("owner"),
            "created_at": contract["created_at"].isoformat(),
            "execution_count": contract["execution_count"],
            "total_gas_used": contract["total_gas_used"],
            "failed_executions": contract["failed_executions"],
            "success_rate": (
                (contract["execution_count"] - contract["failed_executions"]) / 
                contract["execution_count"] * 100
                if contract["execution_count"] > 0 else 0
            )
        }
    
    def get_all_contracts_stats(self) -> List[Dict]:
        """Get statistics for all contracts"""
        return [
            self.get_contract_stats(address)
            for address in self.contracts.keys()
        ]


class NetworkAnalytics:
    """Network and P2P analytics"""
    
    def __init__(self):
        """Initialize network analytics"""
        self.peer_connections: Dict[str, Dict] = {}
        self.bandwidth_usage: List[Dict] = []
        self.latency_samples: List[float] = []
    
    def record_peer_connection(self, peer_id: str, peer_info: Dict):
        """Record peer connection"""
        self.peer_connections[peer_id] = {
            **peer_info,
            "connected_at": datetime.utcnow(),
            "messages_sent": 0,
            "messages_received": 0,
            "bytes_sent": 0,
            "bytes_received": 0
        }
    
    def record_peer_disconnection(self, peer_id: str):
        """Record peer disconnection"""
        if peer_id in self.peer_connections:
            del self.peer_connections[peer_id]
    
    def record_bandwidth(self, direction: str, bytes_count: int):
        """Record bandwidth usage"""
        self.bandwidth_usage.append({
            "direction": direction,  # "sent" or "received"
            "bytes": bytes_count,
            "timestamp": datetime.utcnow()
        })
    
    def record_latency(self, latency_ms: float):
        """Record network latency"""
        self.latency_samples.append(latency_ms)
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        # Peer stats
        connected_peers = len(self.peer_connections)
        
        # Bandwidth stats
        total_sent = sum(b["bytes"] for b in self.bandwidth_usage if b["direction"] == "sent")
        total_received = sum(b["bytes"] for b in self.bandwidth_usage if b["direction"] == "received")
        
        # Latency stats
        avg_latency = statistics.mean(self.latency_samples) if self.latency_samples else 0
        
        return {
            "connected_peers": connected_peers,
            "total_bandwidth_sent": total_sent,
            "total_bandwidth_received": total_received,
            "average_latency_ms": round(avg_latency, 2),
            "peer_list": list(self.peer_connections.keys())
        }


class AnalyticsEngine:
    """Main analytics engine"""
    
    def __init__(self):
        """Initialize analytics engine"""
        self.blockchain = BlockchainAnalytics()
        self.transactions = TransactionAnalytics()
        self.contracts = SmartContractAnalytics()
        self.network = NetworkAnalytics()
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary"""
        tx_stats = self.transactions.get_transaction_stats()
        network_stats = self.network.get_network_stats()
        blockchain_stats = self.blockchain.get_all_metrics()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "transactions": tx_stats,
            "network": network_stats,
            "blockchain": blockchain_stats,
            "contracts": {
                "total": len(self.contracts.contracts),
                "total_executions": len(self.contracts.executions)
            }
        }
    
    def export_analytics(self) -> Dict[str, Any]:
        """Export all analytics data"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "blockchain": self.blockchain.get_all_metrics(),
            "transactions": self.transactions.get_transaction_stats(),
            "transaction_volume_by_hour": self.transactions.get_transaction_volume_by_hour(),
            "top_senders": self.transactions.get_top_senders(),
            "contracts": self.contracts.get_all_contracts_stats(),
            "network": self.network.get_network_stats()
        }


# Global analytics engine
_analytics_engine: Optional[AnalyticsEngine] = None


def get_analytics_engine() -> AnalyticsEngine:
    """Get global analytics engine"""
    global _analytics_engine
    if _analytics_engine is None:
        _analytics_engine = AnalyticsEngine()
    return _analytics_engine
