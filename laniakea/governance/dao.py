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
        # Genesis wallet holds the unsold supply, but quorum is computed against
        # the circulating supply so that community participation actually matters.
        self.genesis_balance: int = int(total_supply * 0.30)
        self.token_holders: Dict[str, int] = {
            "Genesis_Wallet": self.genesis_balance,
            "Treasury": int(total_supply * 0.10),
            "Validator_A": int(total_supply * 0.05),
            "Validator_B": int(total_supply * 0.05),
            "Validator_C": int(total_supply * 0.05),
        }

    @property
    def circulating_supply(self) -> int:
        """Tokens not held by the genesis/treasury wallets.

        Quorum is calculated against circulating supply so that the
        community's votes actually count - the genesis wallet alone cannot
        carry or kill a proposal.
        """
        locked = sum(
            bal for addr, bal in self.token_holders.items()
            if addr in {"Genesis_Wallet", "Treasury"}
        )
        return max(self.total_token_supply - locked, 1)

    def register_voter(self, address: str, balance: int) -> None:
        """Register or top-up a token holder so their vote actually weighs.

        If the address already has a balance it is incremented; otherwise a
        new entry is created. The genesis/treasury wallets cannot be
        modified through this method.
        """
        if address in {"Genesis_Wallet", "Treasury"}:
            raise ValueError("Cannot modify genesis/treasury balances.")
        balance = max(int(balance), 1)
        self.token_holders[address] = self.token_holders.get(address, 0) + balance

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

        # Token weight = 1 token = 1 vote. Unknown addresses are auto-registered
        # with the minimum balance so the protocol is open to new participants.
        token_balance = self.token_holders.get(voter_address)
        if token_balance is None:
            token_balance = 1
            self.token_holders[voter_address] = token_balance

        vtype = vote_type.lower()
        if vtype == "for":
            proposal.votes_for += token_balance
        elif vtype == "against":
            proposal.votes_against += token_balance
        else:
            raise ValueError("Invalid vote type. Must be 'for' or 'against'.")

        proposal.voters.add(voter_address)
        print(f"Vote cast by {voter_address} on Proposal {proposal_id}. Type: {vote_type}, Weight: {token_balance}")

    def finalize_proposal(self, proposal_id: int):
        """Checks if a proposal meets the quorum and passes."""
        if proposal_id not in self.proposals:
            raise ValueError("Proposal not found.")

        proposal = self.proposals[proposal_id]
        if proposal.status != "PENDING":
            print(f"Proposal {proposal_id} already finalized.")
            return

        # Quorum check: Total votes must exceed the required percentage of
        # circulating supply (excludes genesis/treasury wallets).
        quorum_reached = proposal.total_votes / self.circulating_supply >= proposal.required_quorum

        if quorum_reached and proposal.votes_for > proposal.votes_against:
            proposal.status = "PASSED"
            print(f"Proposal {proposal_id} PASSED! Quorum reached and majority 'For'.")
        elif quorum_reached and proposal.votes_for <= proposal.votes_against:
            proposal.status = "FAILED"
            print(f"Proposal {proposal_id} FAILED! Quorum reached but majority 'Against' or tie.")
        else:
            proposal.status = "FAILED_QUORUM"
            print(f"Proposal {proposal_id} FAILED! Quorum not reached. Votes: {proposal.total_votes}, Required: {self.circulating_supply * proposal.required_quorum:.0f}")

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
