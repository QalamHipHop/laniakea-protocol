"""
LaniakeA Protocol - Prometheus Metrics
Defines and registers custom Prometheus metrics for the application.
"""

from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry, generate_latest

# Create a custom registry to avoid conflicts with default metrics
REGISTRY = CollectorRegistry()

# --- Metrics Definitions ---

# 1. Counter for total API requests
API_REQUESTS_TOTAL = Counter(
    'laniakea_api_requests_total', 
    'Total number of API requests', 
    ['endpoint', 'method', 'status'],
    registry=REGISTRY
)

# 2. Histogram for API request latency
API_REQUEST_LATENCY = Histogram(
    'laniakea_api_request_latency_seconds', 
    'API request latency in seconds', 
    ['endpoint', 'method'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 10.0, float('inf')),
    registry=REGISTRY
)

# 3. Gauge for current P2P network size
P2P_NETWORK_SIZE = Gauge(
    'laniakea_p2p_network_size', 
    'Current number of active nodes in the P2P network',
    registry=REGISTRY
)

# 4. Gauge for current energy consumption (as requested by user)
ENERGY_CONSUMPTION_GAUGE = Gauge(
    'laniakea_energy_consumption_joules', 
    'Current estimated energy consumption of the protocol in Joules',
    registry=REGISTRY
)

# 5. Counter for total blocks mined
BLOCKS_MINED_TOTAL = Counter(
    'laniakea_blocks_mined_total', 
    'Total number of blocks mined',
    registry=REGISTRY
)

# 6. Counter for total transactions processed
TRANSACTIONS_PROCESSED_TOTAL = Counter(
    'laniakea_transactions_processed_total', 
    'Total number of transactions processed',
    registry=REGISTRY
)

# --- Helper Functions ---

def get_metrics_response():
    """Returns the latest metrics in Prometheus format."""
    return generate_latest(REGISTRY)

def update_p2p_network_size(size: int):
    """Updates the P2P network size gauge."""
    P2P_NETWORK_SIZE.set(size)

def update_energy_consumption(joules: float):
    """Updates the energy consumption gauge."""
    ENERGY_CONSUMPTION_GAUGE.set(joules)

def increment_blocks_mined():
    """Increments the blocks mined counter."""
    BLOCKS_MINED_TOTAL.inc()

def increment_transactions_processed(count: int = 1):
    """Increments the transactions processed counter."""
    TRANSACTIONS_PROCESSED_TOTAL.inc(count)
