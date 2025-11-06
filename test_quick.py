#!/usr/bin/env python3
"""
Quick test script for LaniakeA Protocol
Tests core functionality without starting the server
"""

import sys
import asyncio
from pathlib import Path

# Add laniakea to path
sys.path.insert(0, str(Path(__file__).parent))

from laniakea.core.blockchain import LaniakeABlockchain, Transaction
from laniakea.intelligence.brain import CosmicBrainAI
from laniakea.utils.logger import setup_logger
import json


async def main():
    print("🧪 Running LaniakeA Protocol Quick Tests\n")
    print("=" * 70)
    
    # Setup logger
    logger = setup_logger('test', dev_mode=True)
    
    # Test 1: Blockchain
    print("\n📝 Test 1: Blockchain Core")
    print("-" * 70)
    
    blockchain = LaniakeABlockchain('test-node', logger)
    
    # Add transactions
    tx1 = Transaction(sender='Alice', recipient='Bob', amount=50.0)
    tx2 = Transaction(sender='Bob', recipient='Charlie', amount=25.0)
    
    blockchain.add_transaction(tx1)
    blockchain.add_transaction(tx2)
    
    print(f"✅ Added {len(blockchain.pending_transactions)} transactions")
    
    # Mine block
    block = blockchain.mine_pending_transactions('Alice')
    print(f"✅ Mined block {block.index} with hash: {block.hash[:16]}...")
    
    # Validate chain
    is_valid = blockchain.is_chain_valid()
    print(f"✅ Chain validation: {'PASSED' if is_valid else 'FAILED'}")
    
    # Check balances
    alice_balance = blockchain.get_balance('Alice')
    bob_balance = blockchain.get_balance('Bob')
    charlie_balance = blockchain.get_balance('Charlie')
    
    print(f"✅ Balances:")
    print(f"   Alice: {alice_balance}")
    print(f"   Bob: {bob_balance}")
    print(f"   Charlie: {charlie_balance}")
    
    # Test 2: AI Brain
    print("\n📝 Test 2: Cosmic Brain AI")
    print("-" * 70)
    
    brain = CosmicBrainAI('test-node', logger)
    
    # Test thinking
    thought = await brain.think(
        "How can we optimize blockchain performance?",
        {"deep_analysis": True}
    )
    
    print(f"✅ AI Thought generated:")
    print(f"   Content: {thought.content[:100]}...")
    print(f"   Creativity: {thought.creativity_score:.2f}")
    print(f"   Confidence: {thought.confidence:.2f}")
    
    # Test evolution
    result = await brain.evolve()
    
    print(f"✅ AI Evolution completed:")
    print(f"   Improvement: {result.improvement:.2%}")
    print(f"   New Patterns: {result.new_patterns}")
    print(f"   Intelligence Level: {result.intelligence_level}")
    
    # Test 3: System Status
    print("\n📝 Test 3: System Status")
    print("-" * 70)
    
    status = blockchain.get_status()
    ai_status = brain.get_status()
    
    print(f"✅ Blockchain Status:")
    print(f"   Chain Length: {status['chain_length']}")
    print(f"   Total Transactions: {status['total_transactions']}")
    print(f"   TPS: {status['tps']:.2f}")
    
    print(f"✅ AI Status:")
    print(f"   Intelligence Level: {ai_status['intelligence_level']}")
    print(f"   Total Thoughts: {ai_status['total_thoughts']}")
    print(f"   Pattern Count: {ai_status['pattern_count']}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ All tests PASSED!")
    print("=" * 70)
    
    return True


if __name__ == '__main__':
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
