# laniakea/dashboard/metrics.py

import time
from typing import Dict, Any, List

class ProtocolMetrics:
    """
    Collects and manages key performance indicators (KPIs) for the Laniakea Protocol.
    """
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "total_transactions": 0,
            "active_users": 0,
            "total_value_locked": 0.0, # TVL in LANA
            "latest_block_height": 0,
            "consensus_latency_ms": 0.0,
            "quantum_job_queue_size": 0,
            "dao_proposals_pending": 0,
            "last_update": time.time()
        }
        self.history: Dict[str, List[Dict[str, Any]]] = {}

    def update_metric(self, key: str, value: Any):
        """Updates a single metric value."""
        if key in self.metrics:
            self.metrics[key] = value
            self.metrics["last_update"] = time.time()
            print(f"Metric updated: {key} = {value}")
        else:
            print(f"Warning: Metric key '{key}' not recognized.")

    def record_history(self, key: str, value: Any):
        """Records a metric value over time."""
        if key not in self.history:
            self.history[key] = []
        
        self.history[key].append({
            "timestamp": time.time(),
            "value": value
        })
        
        # Keep history size manageable (e.g., last 100 entries)
        if len(self.history[key]) > 100:
            self.history[key].pop(0)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Returns all current metrics."""
        return self.metrics

    def get_metric_history(self, key: str) -> List[Dict[str, Any]]:
        """Returns the historical data for a specific metric."""
        return self.history.get(key, [])

# Example usage
if __name__ == '__main__':
    metrics = ProtocolMetrics()
    
    metrics.update_metric("total_transactions", 1500)
    metrics.update_metric("active_users", 450)
    metrics.update_metric("total_value_locked", 125000.75)
    
    metrics.record_history("total_transactions", 1500)
    metrics.record_history("total_transactions", 1505)
    
    print("\nCurrent Metrics:")
    import json
    print(json.dumps(metrics.get_all_metrics(), indent=2))
    
    print("\nTransaction History (last 2):")
    print(metrics.get_metric_history("total_transactions")[-2:])
