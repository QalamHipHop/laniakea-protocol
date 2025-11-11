"""
LaniakeA Protocol - Performance Testing with Locust
Benchmarks for 8-Dimensional computations and core API endpoints.
"""

from locust import HttpUser, task, between
import json

# Mock credentials for JWT authentication
MOCK_USERNAME = "testuser"
MOCK_PASSWORD = "testpass"

class LaniakeaUser(HttpUser):
    wait_time = between(1, 2.5)
    host = "http://localhost:8000" # Should be the host where the app is running

    def on_start(self):
        """Called when a Locust user starts running."""
        self.login()

    def login(self):
        """Authenticate and get a JWT token."""
        response = self.client.post(
            "/token",
            data={
                "username": MOCK_USERNAME,
                "password": MOCK_PASSWORD
            },
            name="/token"
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.client.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            print(f"Login failed with status code {response.status_code}: {response.text}")
            self.token = None
            self.client.environment.runner.quit() # Stop the test if login fails

    @task(10)
    def get_status(self):
        """Test the core status endpoint."""
        self.client.get("/api/v1/status", name="/api/v1/status")

    @task(5)
    def create_transaction(self):
        """Test creating a new transaction."""
        payload = {
            "sender": "locust_sender_1",
            "recipient": "locust_recipient_1",
            "amount": 10.0,
            "metadata": {"test_run": "locust"}
        }
        self.client.post(
            "/api/v1/transaction",
            json=payload,
            name="/api/v1/transaction"
        )

    @task(2)
    def mine_block(self):
        """Test mining a block (heavy computation)."""
        self.client.post(
            "/api/v1/mine",
            params={"miner_address": "locust_miner"},
            name="/api/v1/mine"
        )

    @task(1)
    def get_blockchain(self):
        """Test fetching the entire blockchain (heavy load)."""
        self.client.get("/api/v1/blockchain", name="/api/v1/blockchain")

    @task(3)
    def get_token_price(self):
        """Test external API integration (CoinGecko)."""
        self.client.get("/api/v1/external/coingecko/price/ethereum", name="/api/v1/external/coingecko/price/[coin_id]")

    @task(3)
    def search_arxiv(self):
        """Test external API integration (arXiv search)."""
        self.client.get("/api/v1/external/arxiv/search?query=hypercube", name="/api/v1/external/arxiv/search")
