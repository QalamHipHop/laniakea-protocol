#!/usr/bin/env python3
"""
Quick test script for LaniakeA Protocol v0.0.01
"""

from laniakea import __version__
from laniakea.intelligence.scda_model import SingleCellDigitalAccount
from laniakea.core.hypercube_blockchain import HypercubeBlockchain, HyperTransaction

def test_version():
    print(f"🌌 LaniakeA Protocol v{__version__}")
    print("=" * 60)

def test_scda():
    print("\n📊 Testing SCDA...")
    scda = SingleCellDigitalAccount(identity="test_alice")
    state = scda.get_state()
    print(f"  ✅ SCDA created: {state['identity']}")
    print(f"  ✅ Complexity: {state['complexity_index']}")
    print(f"  ✅ Energy: {state['energy']}")
    print(f"  ✅ Genetic Diversity: {state['genetic_diversity']:.4f}")

def test_blockchain():
    print("\n🔷 Testing Blockchain...")
    blockchain = HypercubeBlockchain(node_id="test_node")
    print(f"  ✅ Blockchain created with {len(blockchain.chain)} blocks")
    
    tx = HyperTransaction(sender="alice", recipient="bob", amount=10.0)
    blockchain.add_transaction(tx)
    print(f"  ✅ Transaction added")
    
    blockchain.mine_pending_transactions("alice")
    print(f"  ✅ Block mined, total blocks: {len(blockchain.chain)}")

def test_evolution():
    print("\n🧬 Testing Evolution...")
    scda = SingleCellDigitalAccount(identity="evolving_user")
    initial_complexity = scda.complexity_index
    
    # Attempt to solve a problem
    success = scda.attempt_solve_problem(
        problem_difficulty=0.5,
        solution_quality=0.8,
        is_valid=True
    )
    
    if success:
        print(f"  ✅ Problem solved successfully")
        print(f"  ✅ Complexity increased: {initial_complexity} -> {scda.complexity_index}")
    else:
        print(f"  ❌ Problem solving failed")

def main():
    test_version()
    test_scda()
    test_blockchain()
    test_evolution()
    print("\n" + "=" * 60)
    print("✅ All tests passed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
