# laniakea/governance/dao.py

import time
from typing import Dict, Any, List

class Proposal:
    def __init__(self, proposal_id: int, title: str, description: str, proposer: str, required_quorum: float = 0.51):
        self.proposal_id = proposal_id
        self.title = title
        self.description = description
        self.proposer = proposer
        self.votes_for = 0
        self.votes_against = 0
        self.required_quorum = required_quorum
        self.status = "PENDING"
        self.created_at = time.time()
        self.voters: set = set()

    @property
    def total_votes(self) -> int:
        return self.votes_for + self.votes_against

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.proposal_id,
            "title": self.title,
            "description": self.description,
            "proposer": self.proposer,
            "votes_for": self.votes_for,
            "votes_against": self.votes_against,
            "total_votes": self.total_votes,
            "required_quorum": self.required_quorum,
            "status": self.status,
            "created_at": self.created_at
        }

class DAO:
    """
    Decentralized Autonomous Organization (DAO) for Laniakea Protocol Governance.
    Manages proposals and voting based on token weight (simulated).
    """
    def __init__(self, total_supply: int = 1000000):
        self.proposals: Dict[int, Proposal] = {}
        self.next_proposal_id = 1
        self.total_token_supply = total_supply # Total tokens for quorum calculation
        self.token_holders: Dict[str, int] = {"Genesis_Wallet": total_supply} # Simulated token distribution

    def create_proposal(self, title: str, description: str, proposer: str) -> Proposal:
        """Creates a new governance proposal."""
        proposal = Proposal(self.next_proposal_id, title, description, proposer)
        self.proposals[self.next_proposal_id] = proposal
        self.next_proposal_id += 1
        print(f"New Proposal created: ID {proposal.proposal_id} - {title}")
        return proposal

    def vote(self, proposal_id: int, voter_address: str, vote_type: str):
        """Casts a vote on a proposal."""
        if proposal_id not in self.proposals:
            raise ValueError("Proposal not found.")
        
        proposal = self.proposals[proposal_id]
        if proposal.status != "PENDING":
            raise ValueError(f"Voting is closed for this proposal (Status: {proposal.status}).")

        if voter_address in proposal.voters:
            raise ValueError("Voter has already voted on this proposal.")

        # Simulate token weight (1 token = 1 vote)
        token_balance = self.token_holders.get(voter_address, 1) # Assume a minimum of 1 vote for any registered user
        
        if vote_type.lower() == "for":
            proposal.votes_for += token_balance
        elif vote_type.lower() == "against":
            proposal.votes_against += token_balance
        else:
            raise ValueError("Invalid vote type. Must be 'for' or 'against'.")
            
        proposal.voters.add(voter_address)
        print(f"Vote cast by {voter_address} on Proposal {proposal_id}. Type: {vote_type}")

    def finalize_proposal(self, proposal_id: int):
        """Checks if a proposal meets the quorum and passes."""
        if proposal_id not in self.proposals:
            raise ValueError("Proposal not found.")
            
        proposal = self.proposals[proposal_id]
        if proposal.status != "PENDING":
            print(f"Proposal {proposal_id} already finalized.")
            return

        # Quorum check: Total votes must exceed the required percentage of total supply
        quorum_reached = proposal.total_votes / self.total_token_supply >= proposal.required_quorum
        
        if quorum_reached and proposal.votes_for > proposal.votes_against:
            proposal.status = "PASSED"
            print(f"Proposal {proposal_id} PASSED! Quorum reached and majority 'For'.")
        elif quorum_reached and proposal.votes_for <= proposal.votes_against:
            proposal.status = "FAILED"
            print(f"Proposal {proposal_id} FAILED! Quorum reached but majority 'Against' or tie.")
        else:
            proposal.status = "FAILED_QUORUM"
            print(f"Proposal {proposal_id} FAILED! Quorum not reached.")

# Example usage
if __name__ == '__main__':
    laniakea_dao = DAO(total_supply=1000)
    laniakea_dao.token_holders["User_A"] = 300
    laniakea_dao.token_holders["User_B"] = 250
    laniakea_dao.token_holders["User_C"] = 100
    
    # Create a proposal
    prop1 = laniakea_dao.create_proposal("Upgrade Consensus", "Propose moving from PoA to PoS.", "User_A")
    
    # Voting
    laniakea_dao.vote(prop1.proposal_id, "User_A", "for") # 300 votes
    laniakea_dao.vote(prop1.proposal_id, "User_B", "for") # 250 votes
    laniakea_dao.vote(prop1.proposal_id, "User_C", "against") # 100 votes
    
    # Finalize
    laniakea_dao.finalize_proposal(prop1.proposal_id)
    
    print("\nProposal Details:")
    print(json.dumps(laniakea_dao.proposals[prop1.proposal_id].to_dict(), indent=2))
