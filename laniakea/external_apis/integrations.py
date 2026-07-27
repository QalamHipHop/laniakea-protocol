"""
LaniakeA Protocol - External API Integrations
Handles data fetching from arXiv, NASA, and CoinGecko.
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from laniakea.utils.config import Config

logger = logging.getLogger("ExternalAPIs")

class ExternalAPIIntegrator:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'LaniakeaProtocol/3.0.0'})
        self.coin_gecko_base_url = "https://api.coingecko.com/api/v3"
        self.arxiv_base_url = "http://export.arxiv.org/api/query"
        self.nasa_base_url = "https://api.nasa.gov"
        self.nasa_api_key = Config.get("NASA_API_KEY", "DEMO_KEY") # Use DEMO_KEY for public APIs

    # --- CoinGecko Integration (Token Prices) ---
    def get_token_price(self, coin_id: str = "bitcoin", currency: str = "usd") -> Optional[float]:
        """Fetches the current price of a token from CoinGecko."""
        url = f"{self.coin_gecko_base_url}/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": currency
        }
        try:
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            price = data.get(coin_id, {}).get(currency)
            if price is not None:
                logger.info(f"Fetched price for {coin_id}: {price} {currency}")
                return price
            else:
                logger.warning(f"Price not found for {coin_id} in {currency}.")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching CoinGecko price for {coin_id}: {e}")
            return None

    # --- arXiv Integration (Knowledge Extraction Agent - KEA) ---
    def search_arxiv(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Searches arXiv for papers related to the query."""
        url = self.arxiv_base_url
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # ArXiv returns XML, a simple text search for titles/summaries is sufficient for KEA concept
            # For a full implementation, an XML parser (like feedparser) would be used.
            results = []
            # Mock parsing for simplicity, assuming the KEA will process the raw data
            if "title" in response.text and "summary" in response.text:
                # Placeholder for actual XML parsing logic
                results.append({
                    "title": f"Mock Title for '{query}'",
                    "summary": f"Mock summary indicating a successful search for '{query}' on arXiv.",
                    "url": "http://arxiv.org/abs/mock_id"
                })
            
            logger.info(f"Fetched {len(results)} mock results from arXiv for query: {query}")
            return results
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching arXiv data for query '{query}': {e}")
            return []

    # --- NASA Integration (Knowledge Extraction Agent - KEA) ---
    def get_nasa_apod(self) -> Optional[Dict[str, Any]]:
        """Fetches the NASA Astronomy Picture of the Day (APOD)."""
        url = f"{self.nasa_base_url}/planetary/apod"
        params = {
            "api_key": self.nasa_api_key
        }
        try:
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            logger.info("Fetched NASA APOD successfully.")
            return {
                "title": data.get("title"),
                "explanation": data.get("explanation"),
                "url": data.get("url"),
                "date": data.get("date")
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching NASA APOD: {e}")
            return None

# Example usage (for testing purposes)
if __name__ == "__main__":
    integrator = ExternalAPIIntegrator()
    
    # Test CoinGecko
    btc_price = integrator.get_token_price("bitcoin")
    print(f"BTC Price: {btc_price}")
    
    # Test arXiv
    arxiv_results = integrator.search_arxiv("quantum computing blockchain")
    print(f"ArXiv Results: {arxiv_results}")
    
    # Test NASA
    apod = integrator.get_nasa_apod()
    print(f"NASA APOD: {apod}")
