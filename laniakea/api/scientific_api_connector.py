"""
Scientific API Connector Module
Handles integration with external scientific APIs (NASA, arXiv, etc.)
for real-time data fetching and problem generation.
"""

import os
import json
import logging
import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ScientificAPIConnector:
    """
    Unified connector for multiple scientific APIs.
    Manages API keys, rate limiting, and data parsing.
    """
    
    def __init__(self):
        """Initialize API connector with credentials."""
        self.nasa_api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")
        self.arxiv_base_url = "http://export.arxiv.org/api/query"
        self.nasa_base_url = "https://api.nasa.gov"
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_tracker = {}
        
    async def initialize(self):
        """Initialize async session."""
        self.session = aiohttp.ClientSession()
        logger.info("Scientific API Connector initialized")
        
    async def close(self):
        """Close async session."""
        if self.session:
            await self.session.close()
            logger.info("Scientific API Connector closed")
    
    # ==================== NASA APIs ====================
    
    async def get_nasa_apod(self) -> Dict[str, Any]:
        """
        Fetch NASA Astronomy Picture of the Day.
        Returns metadata about the latest astronomical observation.
        """
        if not self.session:
            await self.initialize()
        
        url = f"{self.nasa_base_url}/planetary/apod"
        params = {"api_key": self.nasa_api_key}
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"APOD fetched: {data.get('title', 'Unknown')}")
                    return {
                        "source": "NASA_APOD",
                        "title": data.get("title"),
                        "explanation": data.get("explanation"),
                        "url": data.get("url"),
                        "date": data.get("date"),
                        "media_type": data.get("media_type")
                    }
        except Exception as e:
            logger.error(f"Error fetching APOD: {e}")
        
        return {}
    
    async def get_nasa_exoplanet_data(self) -> Dict[str, Any]:
        """
        Fetch NASA Exoplanet data.
        Returns information about recently discovered exoplanets.
        """
        if not self.session:
            await self.initialize()
        
        url = f"{self.nasa_base_url}/exoplanet/1.0/exoplanets"
        params = {"api_key": self.nasa_api_key, "limit": 10}
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Exoplanet data fetched: {len(data.get('results', []))} planets")
                    return {
                        "source": "NASA_EXOPLANET",
                        "count": len(data.get("results", [])),
                        "results": data.get("results", [])[:5]  # Top 5
                    }
        except Exception as e:
            logger.error(f"Error fetching exoplanet data: {e}")
        
        return {}
    
    async def get_nasa_mission_data(self) -> Dict[str, Any]:
        """
        Fetch NASA Mission data.
        Returns information about ongoing and upcoming NASA missions.
        """
        if not self.session:
            await self.initialize()
        
        url = f"{self.nasa_base_url}/techtransfer/patent"
        params = {"api_key": self.nasa_api_key, "limit": 5}
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Mission/Patent data fetched")
                    return {
                        "source": "NASA_MISSION",
                        "count": len(data.get("results", [])),
                        "results": data.get("results", [])[:3]
                    }
        except Exception as e:
            logger.error(f"Error fetching mission data: {e}")
        
        return {}
    
    # ==================== arXiv APIs ====================
    
    async def search_arxiv(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search arXiv for academic papers.
        Returns metadata about papers matching the query.
        """
        if not self.session:
            await self.initialize()
        
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        
        try:
            async with self.session.get(self.arxiv_base_url, params=params) as response:
                if response.status == 200:
                    text = await response.text()
                    # Parse XML response (simplified)
                    papers = self._parse_arxiv_response(text)
                    logger.info(f"arXiv search returned {len(papers)} papers for query: {query}")
                    return {
                        "source": "ARXIV",
                        "query": query,
                        "count": len(papers),
                        "papers": papers[:5]  # Top 5
                    }
        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
        
        return {}
    
    def _parse_arxiv_response(self, xml_response: str) -> List[Dict[str, Any]]:
        """
        Parse arXiv XML response (simplified).
        In production, use xml.etree.ElementTree or lxml.
        """
        papers = []
        # Simplified parsing - extract basic info
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_response)
            
            for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                title_elem = entry.find("{http://www.w3.org/2005/Atom}title")
                summary_elem = entry.find("{http://www.w3.org/2005/Atom}summary")
                published_elem = entry.find("{http://www.w3.org/2005/Atom}published")
                id_elem = entry.find("{http://www.w3.org/2005/Atom}id")
                
                paper = {
                    "title": title_elem.text if title_elem is not None else "Unknown",
                    "summary": summary_elem.text if summary_elem is not None else "No summary",
                    "published": published_elem.text if published_elem is not None else "",
                    "arxiv_id": id_elem.text.split("/abs/")[-1] if id_elem is not None else ""
                }
                papers.append(paper)
        except Exception as e:
            logger.error(f"Error parsing arXiv response: {e}")
        
        return papers
    
    # ==================== Entropy of Consensus Calculation ====================
    
    async def calculate_difficulty_from_consensus(self, query: str) -> float:
        """
        Calculate problem difficulty based on Entropy of Consensus.
        
        High variance in sources = High difficulty.
        Low variance = Low difficulty.
        """
        # Fetch multiple sources
        arxiv_data = await self.search_arxiv(query, max_results=5)
        nasa_data = await self.get_nasa_apod()
        
        # Simplified consensus calculation
        # In production, use NLP to measure agreement/disagreement
        sources_count = len(arxiv_data.get("papers", [])) + (1 if nasa_data else 0)
        
        # Difficulty is inversely proportional to consensus
        # More sources = higher variance = higher difficulty
        difficulty = min(1.0, sources_count / 10.0)
        
        logger.info(f"Calculated difficulty for '{query}': {difficulty:.2f}")
        return difficulty
    
    # ==================== Unified Data Fetching ====================
    
    async def fetch_scientific_context(self, tier: int) -> Dict[str, Any]:
        """
        Fetch scientific context based on SCDA's current tier.
        Returns data relevant to the tier's knowledge focus.
        """
        context = {
            "tier": tier,
            "timestamp": datetime.now().isoformat(),
            "sources": {}
        }
        
        if tier == 1:  # Single-Cell: Foundational Sciences
            context["sources"]["nasa"] = await self.get_nasa_apod()
            context["sources"]["arxiv"] = await self.search_arxiv("fundamental physics", max_results=5)
        
        elif tier == 2:  # Multi-Cellular: Structured Sciences
            context["sources"]["nasa"] = await self.get_nasa_exoplanet_data()
            context["sources"]["arxiv"] = await self.search_arxiv("biology evolution", max_results=5)
        
        elif tier == 3:  # Humanity: Interdisciplinary Sciences
            context["sources"]["nasa"] = await self.get_nasa_mission_data()
            context["sources"]["arxiv"] = await self.search_arxiv("climate modeling AI", max_results=5)
        
        elif tier >= 4:  # Galactic: Cosmological Sciences
            context["sources"]["nasa"] = await self.get_nasa_apod()
            context["sources"]["arxiv"] = await self.search_arxiv("quantum gravity cosmology", max_results=5)
        
        return context


# Async context manager for easy usage
class APIConnectorContext:
    """Context manager for Scientific API Connector."""
    
    def __init__(self):
        self.connector = ScientificAPIConnector()
    
    async def __aenter__(self):
        await self.connector.initialize()
        return self.connector
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.connector.close()


# Example usage
async def example_usage():
    """Example of how to use the Scientific API Connector."""
    async with APIConnectorContext() as connector:
        # Fetch APOD
        apod = await connector.get_nasa_apod()
        print(f"APOD: {apod.get('title', 'N/A')}")
        
        # Search arXiv
        papers = await connector.search_arxiv("quantum computing", max_results=5)
        print(f"Found {papers.get('count', 0)} papers on quantum computing")
        
        # Calculate difficulty
        difficulty = await connector.calculate_difficulty_from_consensus("dark matter")
        print(f"Difficulty for 'dark matter': {difficulty:.2f}")
        
        # Fetch tier-based context
        context = await connector.fetch_scientific_context(tier=2)
        print(f"Context for Tier 2: {json.dumps(context, indent=2)}")


if __name__ == "__main__":
    asyncio.run(example_usage())
