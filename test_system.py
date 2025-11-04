"""
Laniakea Protocol - System Test
تست کامل سیستم
"""

import asyncio
import sys
from time import time

# اضافه کردن مسیر به sys.path
sys.path.insert(0, '/home/ubuntu/laniakea-protocol')

from src.core.models import (
    Task, Solution, ValueVector, ProblemCategory,
    ValueDimension, CosmicCell
)
from src.core.blockchain import LaniakeaChain
from src.core.hash_modernity import HashModernityEngine, ProofOfValue
from src.core.token_system import TokenEconomics, StakingSystem
from src.simulation.cosmic_simulator import CosmicSimulator


def test_blockchain():
    """تست بلاک‌چین"""
    print("\n" + "=" * 60)
    print("🧪 Testing Blockchain...")
    print("=" * 60)

    chain = LaniakeaChain("test_node")
    chain.create_genesis_block()

    # ایجاد تسک و راه‌حل
    task = Task(
        id="task1",
        title="Calculate Pi",
        description="Calculate Pi to 100 decimal places",
        category=ProblemCategory.MATHEMATICAL,
        author_id="test_node",
        timestamp=time(),
        difficulty=5.0
    )

    solution = Solution(
        id="sol1",
        task_id="task1",
        solver_id="test_node",
        content="3.14159265358979323846...",
        value_vector=ValueVector(
            knowledge=50.0,
            computation=30.0,
            originality=20.0
        ),
        timestamp=time()
    )

    # ایجاد بلاک
    new_block = chain.new_block(
        transactions=[],
        solution=solution,
        previous_hash=LaniakeaChain.hash(chain.last_block)
    )
    new_block.signature = "test_signature"

    # افزودن بلاک
    success = chain.add_block(new_block, {"test_node"})

    print(f"✅ Block added: {success}")
    print(f"📊 Chain length: {len(chain.chain)}")
    print(f"💰 Total value created: {chain.total_value_created.total_value():.2f}")

    # بررسی موجودی
    balance = chain.get_total_balance("test_node")
    print(f"💵 Node balance: {balance.to_dict()}")

    return success


def test_hash_modernity():
    """تست Hash Modernity"""
    print("\n" + "=" * 60)
    print("🧪 Testing Hash Modernity...")
    print("=" * 60)

    engine = HashModernityEngine()

    # ایجاد تسک و راه‌حل
    task = Task(
        id="task2",
        title="Quantum Computing Problem",
        description="Solve quantum entanglement equation",
        category=ProblemCategory.SCIENTIFIC,
        author_id="test_node",
        timestamp=time(),
        difficulty=8.0
    )

    solution = Solution(
        id="sol2",
        task_id="task2",
        solver_id="test_node",
        content="Quantum solution with entanglement...",
        value_vector=ValueVector(
            knowledge=80.0,
            computation=60.0,
            originality=70.0,
            consciousness=40.0
        ),
        timestamp=time()
    )

    # محاسبه discovery hash
    discovery_hash = engine.compute_discovery_hash(
        solution.content,
        {"task": task.title, "category": task.category.value},
        solution.timestamp
    )

    print(f"🔐 Discovery hash: {discovery_hash[:16]}...")

    # ارزیابی نرخ مدرنیته
    modernity_rate = engine.assess_modernity_rate(solution, task, [])
    print(f"📈 Modernity rate: {modernity_rate:.4f}")

    # ایجاد توکن مدرنیته
    token = engine.create_modernity_token(solution, task, modernity_rate)
    print(f"🪙 Modernity token created: {token['id'][:16]}...")

    # Proof of Value
    value_proof = ProofOfValue.calculate_value_proof(solution, task, ["validator1", "validator2"])
    print(f"✨ Value proof: {value_proof:.2f}")

    return True


def test_token_economics():
    """تست اقتصاد توکن"""
    print("\n" + "=" * 60)
    print("🧪 Testing Token Economics...")
    print("=" * 60)

    economics = TokenEconomics()

    # تولید توکن‌ها
    token1 = economics.mint_tokens(
        ValueDimension.KNOWLEDGE,
        100.0,
        "user1",
        "test_reward"
    )

    token2 = economics.mint_tokens(
        ValueDimension.ORIGINALITY,
        50.0,
        "user1",
        "test_reward"
    )

    print(f"📊 Total supply: {economics.total_supply}")
    print(f"💎 Total value: {economics.get_total_value():.2f}")

    # تبدیل توکن
    rate = economics.calculate_exchange_rate(
        ValueDimension.KNOWLEDGE,
        ValueDimension.CONSCIOUSNESS
    )
    print(f"💱 Exchange rate (Knowledge -> Consciousness): {rate:.4f}")

    # Staking
    staking = StakingSystem(economics)
    staking.stake("user1", ValueDimension.KNOWLEDGE, 50.0)

    staker_info = staking.get_staker_info("user1")
    print(f"🔒 Staked: {staker_info}")

    # محاسبه پاداش (برای 1 روز)
    rewards = staking.calculate_rewards("user1", 24 * 3600)
    print(f"🎁 Rewards (1 day): {rewards.to_dict()}")

    return True


def test_cosmic_simulator():
    """تست شبیه‌ساز کیهانی"""
    print("\n" + "=" * 60)
    print("🧪 Testing Cosmic Simulator...")
    print("=" * 60)

    simulator = CosmicSimulator()

    # ایجاد سلول پیدایش
    genesis = simulator.create_genesis_cell()
    print(f"🌱 Genesis cell: {genesis.id[:16]}...")

    # اجرای شبیه‌سازی
    print("\n🚀 Running simulation for 100 steps...")
    simulator.run(100)

    # نمایش آمار
    stats = simulator.get_stats()
    print(f"\n📊 Simulation stats:")
    print(f"   Time: {stats['time']:.2f}")
    print(f"   Alive cells: {stats['alive_cells']}")
    print(f"   Total knowledge: {stats['total_knowledge']:.2f}")
    print(f"   Max generation: {stats['max_generation']}")

    # نمایش وضعیت
    print("\n" + simulator.visualize_state())

    return stats['alive_cells'] > 0


async def test_oracle_system():
    """تست سیستم اوراکل"""
    print("\n" + "=" * 60)
    print("🧪 Testing Oracle System...")
    print("=" * 60)

    from src.oracles.oracle_system import OracleManager

    manager = OracleManager()

    # تست Wikipedia
    result = await manager.query("data", {
        "source": "wikipedia",
        "query": "quantum_computing"
    })

    print(f"📚 Wikipedia query result: {result.get('status', 'unknown')}")
    if result.get('status') == 'success':
        print(f"   Title: {result.get('title', 'N/A')}")
        print(f"   Extract: {result.get('extract', 'N/A')[:100]}...")

    # تست arXiv
    result2 = await manager.query("scientific", {
        "project": "arxiv",
        "search": "artificial intelligence"
    })

    print(f"🔬 arXiv query result: {result2.get('status', 'unknown')}")

    return True


def main():
    """اجرای تست‌ها"""
    print("\n" + "=" * 70)
    print("🌌 LANIAKEA PROTOCOL - SYSTEM TEST")
    print("=" * 70)

    results = {}

    # تست‌های همزمان
    try:
        results['blockchain'] = test_blockchain()
        results['hash_modernity'] = test_hash_modernity()
        results['token_economics'] = test_token_economics()
        results['cosmic_simulator'] = test_cosmic_simulator()
    except Exception as e:
        print(f"❌ Error in sync tests: {e}")
        import traceback
        traceback.print_exc()

    # تست‌های async
    try:
        results['oracle_system'] = asyncio.run(test_oracle_system())
    except Exception as e:
        print(f"❌ Error in async tests: {e}")
        import traceback
        traceback.print_exc()

    # خلاصه نتایج
    print("\n" + "=" * 70)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 70)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<50} {status}")

    all_passed = all(results.values())
    print("=" * 70)

    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✨ Laniakea Protocol is ready for cosmic journey!")
    else:
        print("⚠️ SOME TESTS FAILED")
        print("🔧 Please check the errors above")

    print("=" * 70)

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
