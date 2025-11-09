# laniakea/marketplace/nft.py

import time
import uuid
from typing import Dict, Any

class NFT:
    """
    Non-Fungible Token (NFT) representing a piece of 'Knowledge' or 'Data Asset'
    within the Laniakea Protocol Marketplace.
    """
    def __init__(self, token_id: str, owner: str, metadata_uri: str, asset_type: str, creation_time: float):
        self.token_id = token_id
        self.owner = owner
        self.metadata_uri = metadata_uri
        self.asset_type = asset_type # e.g., 'Scientific Data', 'Algorithm', 'Art'
        self.creation_time = creation_time
        self.is_listed = False
        self.listing_price = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

class Marketplace:
    """
    Manages the creation, listing, and transfer of NFTs.
    """
    def __init__(self):
        self.nfts: Dict[str, NFT] = {}
        self.listings: Dict[str, NFT] = {} # Listed NFTs

    def mint_nft(self, owner: str, metadata_uri: str, asset_type: str) -> NFT:
        """Creates and registers a new NFT."""
        token_id = str(uuid.uuid4())
        new_nft = NFT(token_id, owner, metadata_uri, asset_type, time.time())
        self.nfts[token_id] = new_nft
        print(f"NFT Minted: {token_id} (Type: {asset_type}) for Owner: {owner}")
        return new_nft

    def list_nft(self, token_id: str, price: float):
        """Lists an NFT for sale on the marketplace."""
        if token_id not in self.nfts:
            raise ValueError("NFT not found.")
        
        nft = self.nfts[token_id]
        if nft.is_listed:
            raise ValueError("NFT is already listed.")
            
        nft.is_listed = True
        nft.listing_price = price
        self.listings[token_id] = nft
        print(f"NFT {token_id} listed for {price} LANA.")

    def buy_nft(self, token_id: str, buyer: str):
        """Simulates the purchase of a listed NFT."""
        if token_id not in self.listings:
            raise ValueError("NFT not listed for sale.")
            
        nft = self.listings[token_id]
        seller = nft.owner
        price = nft.listing_price
        
        # Simulate payment transfer (omitted for simplicity)
        
        # Transfer ownership
        nft.owner = buyer
        nft.is_listed = False
        nft.listing_price = 0.0
        del self.listings[token_id]
        
        print(f"NFT {token_id} (Price: {price}) transferred from {seller} to {buyer}.")
        return nft

# Example usage
if __name__ == '__main__':
    marketplace = Marketplace()
    
    # Mint a new Knowledge Asset NFT
    knowledge_nft = marketplace.mint_nft("Dr. Smith", "ipfs://metadata/12345", "Scientific Data")
    
    # List the NFT for sale
    marketplace.list_nft(knowledge_nft.token_id, 500.0)
    
    # Buyer purchases the NFT
    try:
        marketplace.buy_nft(knowledge_nft.token_id, "Laniakea_Research_Fund")
    except ValueError as e:
        print(f"Error during purchase: {e}")
        
    print(f"New Owner of NFT: {knowledge_nft.owner}")
