# laniakea/consensus/poa.py

from laniakea.blockchain.core import Block, Blockchain
import time
import json

class ProofOfAuthority:
    """
    Proof of Authority (PoA) Consensus Mechanism
    A list of 'authorities' (validators) is pre-approved to create new blocks.
    """
    def __init__(self, authorities):
        self.authorities = set(authorities)
        self.current_authority_index = 0

    def is_authority(self, address):
        """Checks if an address is a recognized authority."""
        return address in self.authorities

    def get_current_authority(self):
        """Returns the address of the current block-signing authority."""
        authority_list = list(self.authorities)
        authority = authority_list[self.current_authority_index % len(authority_list)]
        self.current_authority_index = (self.current_authority_index + 1) % len(authority_list)
        return authority

    def validate_block(self, block: Block, blockchain: Blockchain):
        """
        Validates a block based on PoA rules.
        In a real PoA, this would check the block's signature against the current authority.
        For this simulation, we'll just check the index and previous hash.
        """
        if block.index != len(blockchain.chain) + 1:
            return False, "Invalid block index"
        
        if block.previous_hash != blockchain.last_block.hash:
            return False, "Invalid previous hash"
            
        # In a real system, we would check the signature of the authority here.
        # For now, we assume the 'proof' field contains the authority's ID or a valid token.
        if not self.is_authority(str(block.proof)):
             return False, "Block not signed by a recognized authority"

        return True, "Block is valid"

    def sign_block(self, blockchain: Blockchain, authority_address):
        """
        Simulates the signing and creation of a new block by the current authority.
        """
        if not self.is_authority(authority_address):
            raise ValueError("Address is not a recognized authority.")

        # Simulate block creation
        new_block = Block(
            index=len(blockchain.chain) + 1,
            timestamp=time.time(),
            transactions=blockchain.current_transactions,
            proof=authority_address, # Authority's ID/Address is the 'proof'
            previous_hash=blockchain.last_block.hash
        )
        
        # Reset transactions and add to chain
        blockchain.current_transactions = []
        blockchain.chain.append(new_block)
        
        return new_block

# Example usage
if __name__ == '__main__':
    authorities = ["Validator_A", "Validator_B", "Validator_C"]
    poa_consensus = ProofOfAuthority(authorities)
    laniakea_chain = Blockchain()

    print(f"Current Authority: {poa_consensus.get_current_authority()}")
    
    # Authority A signs the next block
    authority_a = "Validator_A"
    laniakea_chain.new_transaction("User1", "User2", 10)
    new_block = poa_consensus.sign_block(laniakea_chain, authority_a)
    
    print(f"Block {new_block.index} signed by {new_block.proof}")
    
    # Validate the new block
    is_valid, message = poa_consensus.validate_block(new_block, laniakea_chain)
    print(f"Validation: {is_valid} - {message}")
