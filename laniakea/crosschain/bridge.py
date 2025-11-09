# laniakea/crosschain/bridge.py

import time
import uuid
from typing import Dict, Any

class CrossChainTransaction:
    def __init__(self, tx_id: str, source_chain: str, target_chain: str, asset: str, amount: float, sender: str, recipient: str, status: str = "PENDING"):
        self.tx_id = tx_id
        self.source_chain = source_chain
        self.target_chain = target_chain
        self.asset = asset
        self.amount = amount
        self.sender = sender
        self.recipient = recipient
        self.status = status
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

class Bridge:
    """
    A simplified Cross-Chain Bridge mechanism for Laniakea Protocol.
    It manages the locking of assets on the source chain and minting/unlocking on the target chain.
    """
    def __init__(self, supported_chains: list):
        self.supported_chains = supported_chains
        self.pending_transactions: Dict[str, CrossChainTransaction] = {}
        self.completed_transactions: Dict[str, CrossChainTransaction] = {}
        self.chain_balances: Dict[str, Dict[str, float]] = {chain: {"LANA": 1000000.0} for chain in supported_chains} # Simulated balances

    def initiate_transfer(self, source_chain: str, target_chain: str, asset: str, amount: float, sender: str, recipient: str) -> CrossChainTransaction:
        """
        Initiates a cross-chain transfer.
        1. Checks if chains are supported.
        2. Checks if sender has enough balance (simulated).
        3. Locks the asset on the source chain (simulated).
        4. Creates a pending transaction.
        """
        if source_chain not in self.supported_chains or target_chain not in self.supported_chains:
            raise ValueError("Source or target chain not supported.")

        # Simulate balance check and locking
        if self.chain_balances.get(source_chain, {}).get(asset, 0) < amount:
            raise ValueError(f"Insufficient {asset} balance on {source_chain} for locking.")

        # Lock asset (reduce balance on source chain)
        self.chain_balances[source_chain][asset] -= amount
        
        tx_id = str(uuid.uuid4())
        new_tx = CrossChainTransaction(tx_id, source_chain, target_chain, asset, amount, sender, recipient)
        self.pending_transactions[tx_id] = new_tx
        
        print(f"Transfer initiated: {tx_id}. {amount} {asset} locked on {source_chain}.")
        return new_tx

    def complete_transfer(self, tx_id: str) -> CrossChainTransaction:
        """
        Completes a cross-chain transfer.
        1. Mints/Unlocks the asset on the target chain (simulated).
        2. Updates the transaction status.
        """
        if tx_id not in self.pending_transactions:
            raise ValueError("Transaction not found or already completed.")

        tx = self.pending_transactions[tx_id]
        
        # Simulate minting/unlocking on target chain (increase balance)
        if tx.asset not in self.chain_balances[tx.target_chain]:
             self.chain_balances[tx.target_chain][tx.asset] = 0.0
             
        self.chain_balances[tx.target_chain][tx.asset] += tx.amount
        
        tx.status = "COMPLETED"
        tx.timestamp = time.time()
        self.completed_transactions[tx_id] = tx
        del self.pending_transactions[tx_id]
        
        print(f"Transfer completed: {tx_id}. {tx.amount} {tx.asset} minted/unlocked on {tx.target_chain}.")
        return tx

# Example usage
if __name__ == '__main__':
    chains = ["Laniakea_Main", "Laniakea_Sidechain_1", "Ethereum_Sim"]
    laniakea_bridge = Bridge(chains)
    
    print(f"Initial Balance on Laniakea_Main: {laniakea_bridge.chain_balances['Laniakea_Main']['LANA']}")
    print(f"Initial Balance on Laniakea_Sidechain_1: {laniakea_bridge.chain_balances['Laniakea_Sidechain_1']['LANA']}")

    try:
        # Initiate transfer from Main to Sidechain
        tx = laniakea_bridge.initiate_transfer("Laniakea_Main", "Laniakea_Sidechain_1", "LANA", 100.0, "User_A", "User_B")
        print(f"Pending TX: {tx.tx_id}")
        
        # Complete the transfer
        completed_tx = laniakea_bridge.complete_transfer(tx.tx_id)
        print(f"Completed TX Status: {completed_tx.status}")

    except ValueError as e:
        print(f"Error: {e}")

    print(f"Final Balance on Laniakea_Main: {laniakea_bridge.chain_balances['Laniakea_Main']['LANA']}")
    print(f"Final Balance on Laniakea_Sidechain_1: {laniakea_bridge.chain_balances['Laniakea_Sidechain_1']['LANA']}")
