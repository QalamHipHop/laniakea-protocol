"""
Knowledge Marketplace Module
Version: 0.0.01
Author: Manus AI

This module implements the core logic for the Knowledge Marketplace, allowing SCDAs
to tokenize, list, and trade their specialized knowledge (represented by 8D vectors).
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
import uuid

logger = logging.getLogger(__name__)

# --- Constants ---
KNOWLEDGE_DOMAINS = [
    "Physics", "Mathematics", "Biology", "Computer Science",
    "Consciousness", "Economics", "Art & Creativity", "Metaphysics"
]
BASE_TOKEN_NAME = "LANA"
KNOWLEDGE_TOKEN_PREFIX = "K-NFT"

# --- Data Structures ---

@dataclass
class KnowledgeAsset:
    """Represents a tokenized piece of knowledge (NFT-like structure)."""
    asset_id: str
    owner_scda_id: str
    knowledge_vector_8d: List[float] # The specific knowledge being tokenized
    domain_focus: str # The primary domain of the knowledge
    complexity_index_at_mint: float
    mint_timestamp: str
    is_listed: bool = False
    list_price: float = 0.0
    listed_timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "owner_scda_id": self.owner_scda_id,
            "knowledge_vector_8d": self.knowledge_vector_8d,
            "domain_focus": self.domain_focus,
            "complexity_index_at_mint": self.complexity_index_at_mint,
            "mint_timestamp": self.mint_timestamp,
            "is_listed": self.is_listed,
            "list_price": self.list_price,
            "listed_timestamp": self.listed_timestamp
        }

@dataclass
class KnowledgeTransaction:
    """Represents a transaction in the marketplace."""
    tx_id: str
    asset_id: str
    seller_scda_id: str
    buyer_scda_id: str
    price: float
    timestamp: str

# --- Core Logic ---

class KnowledgeMarketplace:
    """Manages the creation, listing, and trading of Knowledge Assets."""
    
    def __init__(self):
        self.assets: Dict[str, KnowledgeAsset] = {}
        self.transactions: List[KnowledgeTransaction] = []
        logger.info("KnowledgeMarketplace initialized.")
    
    def _generate_asset_id(self) -> str:
        """Generates a unique ID for a Knowledge Asset."""
        return f"{KNOWLEDGE_TOKEN_PREFIX}-{uuid.uuid4().hex[:8]}"
    
    def tokenize_knowledge(
        self,
        owner_scda_id: str,
        scda_knowledge_vector: List[float],
        complexity_index: float
    ) -> KnowledgeAsset:
        """
        Tokenizes a portion of an SCDA's knowledge vector into a tradable asset.
        
        For simplicity, we tokenize the entire vector, but the value is derived
        from the most dominant domain.
        """
        asset_id = self._generate_asset_id()
        
        # Determine the primary domain focus
        vector_np = np.array(scda_knowledge_vector)
        dominant_index = np.argmax(vector_np)
        domain_focus = KNOWLEDGE_DOMAINS[dominant_index]
        
        asset = KnowledgeAsset(
            asset_id=asset_id,
            owner_scda_id=owner_scda_id,
            knowledge_vector_8d=scda_knowledge_vector,
            domain_focus=domain_focus,
            complexity_index_at_mint=complexity_index,
            mint_timestamp=datetime.now().isoformat()
        )
        
        self.assets[asset_id] = asset
        logger.info(f"Knowledge Asset {asset_id} minted for {owner_scda_id}. Focus: {domain_focus}")
        return asset

    def list_asset(self, asset_id: str, price: float) -> KnowledgeAsset:
        """Lists a Knowledge Asset for sale in the marketplace."""
        if asset_id not in self.assets:
            raise ValueError(f"Asset {asset_id} not found.")
        
        asset = self.assets[asset_id]
        if asset.is_listed:
            raise ValueError(f"Asset {asset_id} is already listed.")
        if price <= 0:
            raise ValueError("Price must be positive.")
            
        asset.is_listed = True
        asset.list_price = price
        asset.listed_timestamp = datetime.now().isoformat()
        
        logger.info(f"Asset {asset_id} listed for {price} {BASE_TOKEN_NAME}.")
        return asset

    def buy_asset(self, asset_id: str, buyer_scda_id: str) -> KnowledgeTransaction:
        """Facilitates the purchase of a listed Knowledge Asset."""
        if asset_id not in self.assets:
            raise ValueError(f"Asset {asset_id} not found.")
        
        asset = self.assets[asset_id]
        if not asset.is_listed:
            raise ValueError(f"Asset {asset_id} is not listed for sale.")
        if asset.owner_scda_id == buyer_scda_id:
            raise ValueError("Cannot buy your own asset.")
            
        # --- Transaction Logic (Simplified) ---
        # In a real system, this would involve token transfer and smart contract execution.
        
        seller_id = asset.owner_scda_id
        price = asset.list_price
        
        # 1. Transfer asset ownership
        asset.owner_scda_id = buyer_scda_id
        asset.is_listed = False
        asset.list_price = 0.0
        asset.listed_timestamp = None
        
        # 2. Record transaction
        tx_id = f"TX-{uuid.uuid4().hex[:8]}"
        transaction = KnowledgeTransaction(
            tx_id=tx_id,
            asset_id=asset_id,
            seller_scda_id=seller_id,
            buyer_scda_id=buyer_scda_id,
            price=price,
            timestamp=datetime.now().isoformat()
        )
        self.transactions.append(transaction)
        
        logger.info(f"Asset {asset_id} sold from {seller_id} to {buyer_scda_id} for {price} {BASE_TOKEN_NAME}.")
        
        # --- Knowledge Integration (Crucial for SCDA Evolution) ---
        # The buyer's SCDA should integrate this new knowledge, potentially boosting
        # their knowledge vector and complexity index. This logic belongs in scda_enhanced.py.
        
        return transaction

    def get_listed_assets(self) -> List[Dict[str, Any]]:
        """Returns a list of all assets currently listed for sale."""
        return [
            asset.to_dict() for asset in self.assets.values()
            if asset.is_listed
        ]

    def get_asset_details(self, asset_id: str) -> Dict[str, Any]:
        """Returns details for a specific asset."""
        if asset_id not in self.assets:
            raise ValueError(f"Asset {asset_id} not found.")
        return self.assets[asset_id].to_dict()

# --- Example Usage ---
if __name__ == "__main__":
    market = KnowledgeMarketplace()
    
    # 1. SCDA 1 tokenizes knowledge (high in Physics)
    asset1 = market.tokenize_knowledge(
        owner_scda_id="scda_alice",
        scda_knowledge_vector=[0.9, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
        complexity_index=15.0
    )
    
    # 2. SCDA 2 tokenizes knowledge (high in Biology)
    asset2 = market.tokenize_knowledge(
        owner_scda_id="scda_bob",
        scda_knowledge_vector=[0.1, 0.1, 0.9, 0.1, 0.1, 0.1, 0.1, 0.1],
        complexity_index=12.0
    )
    
    # 3. List asset 1
    market.list_asset(asset1.asset_id, 100.0)
    
    # 4. List asset 2
    market.list_asset(asset2.asset_id, 80.0)
    
    print("\n--- Listed Assets ---")
    for asset in market.get_listed_assets():
        print(f"ID: {asset['asset_id']}, Owner: {asset['owner_scda_id']}, Focus: {asset['domain_focus']}, Price: {asset['list_price']}")
        
    # 5. SCDA 3 buys asset 1
    try:
        tx = market.buy_asset(asset1.asset_id, "scda_charlie")
        print(f"\n--- Transaction Success ---")
        print(f"Transaction ID: {tx.tx_id}, New Owner: {market.assets[asset1.asset_id].owner_scda_id}")
    except ValueError as e:
        print(f"Transaction Failed: {e}")
