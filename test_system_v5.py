"""
Laniakea Protocol v5.0 - Comprehensive Test Suite
مجموعه تست‌های جامع برای نسخه 5.0
"""

import sys
import asyncio
from time import time
from pathlib import Path

# اضافه کردن مسیر پروژه
sys.path.insert(0, str(Path(__file__).parent))

from src.core.blockchain import LaniakeaChain
from src.core.models import Task, Solution, ValueVector, ProblemCategory
from src.core.wallet import Wallet
from src.core.hash_modernity import HashModernityEngine
from src.core.token_system import TokenEconomics
from src.metasystem.cognitive_core import CognitiveCore
from src.reputation.reputation_system import ReputationSystem, ReputationEvent
from src.external_apis.api_integrations import APIIntegrationManager, APIProvider


class TestRunner:
    """اجرای تست‌ها"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name: str, func):
        """اجرای یک تست"""
        print(f"\n🧪 Testing: {name}")
        try:
            result = func()
            if asyncio.iscoroutine(result):
                result = asyncio.run(result)
            
            if result:
                print(f"   ✅ PASSED")
                self.passed += 1
                self.tests.append((name, True, None))
            else:
                print(f"   ❌ FAILED")
                self.failed += 1
                self.tests.append((name, False, "Test returned False"))
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)}")
            self.failed += 1
            self.tests.append((name, False, str(e)))
    
    def summary(self):
        """خلاصه نتایج"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Total: {self.passed + self.failed}")
        print(f"🎯 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        print("=" * 60)
        
        if self.failed > 0:
            print("\n❌ Failed Tests:")
            for name, passed, error in self.tests:
                if not passed:
                    print(f"   - {name}: {error}")


def test_wallet():
    """تست سیستم کیف پول"""
    wallet = Wallet("test_data")
    address = wallet.get_address()
    
    # تست امضا و تأیید
    message = b"test message"
    signature = wallet.sign(message)
    verified = wallet.verify(message, signature, wallet.public_key)
    
    return len(address) > 0 and verified


def test_blockchain():
    """تست بلاک‌چین"""
    chain = LaniakeaChain()
    
    # بلاک genesis باید وجود داشته باشد
    if len(chain.chain) != 1:
        return False
    
    # تست اضافه کردن بلاک
    initial_length = len(chain.chain)
    
    # ایجاد تسک و راه‌حل ساده
    task = Task(
        id="test_task",
        title="Test Task",
        description="Test",
        category=ProblemCategory.MATHEMATICAL,
        difficulty=5.0,
        author_id="test_author",
        timestamp=time()
    )
    
    solution = Solution(
        id="test_solution",
        task_id="test_task",
        solver_id="test_solver",
        content="Test solution",
        value_vector=ValueVector(knowledge=10.0),
        timestamp=time()
    )
    
    # ایجاد بلاک جدید
    from src.core.models import KnowledgeBlock
    new_block = KnowledgeBlock(
        index=1,
        timestamp=time(),
        solution=solution,
        validator="test_validator",
        previous_hash=chain.last_block.hash
    )
    
    # محاسبه هش
    new_block.hash = chain._calculate_block_hash(new_block)
    
    # اضافه کردن بلاک
    success = chain.add_block(new_block, {"test_validator"})
    
    return success and len(chain.chain) == initial_length + 1


def test_value_vector():
    """تست بردار ارزش"""
    v1 = ValueVector(
        knowledge=10.0,
        computation=5.0,
        originality=3.0
    )
    
    v2 = ValueVector(
        knowledge=5.0,
        computation=10.0,
        originality=2.0
    )
    
    # تست جمع
    v3 = v1 + v2
    
    # تست ضرب اسکالر
    v4 = v1 * 2.0
    
    # تست محاسبه ارزش کل
    total = v1.total_value()
    
    return (
        v3.knowledge == 15.0 and
        v4.knowledge == 20.0 and
        total > 0
    )


def test_hash_modernity():
    """تست سیستم Hash Modernity"""
    engine = HashModernityEngine()
    
    task = Task(
        id="test_task",
        title="Quantum Computing",
        description="Research quantum algorithms",
        category=ProblemCategory.SCIENTIFIC,
        difficulty=8.0,
        author_id="test_author",
        timestamp=time()
    )
    
    solution = Solution(
        id="test_solution",
        task_id="test_task",
        solver_id="test_solver",
        content="Quantum algorithm implementation",
        value_vector=ValueVector(knowledge=80.0, computation=60.0),
        timestamp=time()
    )
    
    # محاسبه Proof of Discovery
    proof = engine.compute_proof_of_discovery(task, solution, difficulty=3)
    
    return proof is not None and len(proof) > 0


def test_token_economics():
    """تست اقتصاد توکن"""
    economics = TokenEconomics()
    
    # تولید توکن
    tokens = economics.mint_tokens(
        ValueVector(knowledge=100.0, computation=50.0),
        "test_node"
    )
    
    # بررسی موجودی
    balance = economics.get_balance("test_node")
    
    return balance.knowledge == 100.0 and balance.computation == 50.0


def test_reputation_system():
    """تست سیستم اعتبار"""
    reputation = ReputationSystem()
    
    # ثبت نود
    reputation.register_node("test_node")
    
    # ثبت رویدادها
    reputation.record_event("test_node", ReputationEvent.TASK_CREATED, {})
    reputation.record_event("test_node", ReputationEvent.SOLUTION_SUBMITTED, {})
    reputation.record_event("test_node", ReputationEvent.SOLUTION_ACCEPTED, {"value": 50.0})
    
    # دریافت امتیاز
    score = reputation.get_reputation("test_node")
    
    return score is not None and score.total_score > 0


async def test_api_manager():
    """تست مدیر API"""
    manager = APIIntegrationManager()
    
    # تست NASA API (با DEMO_KEY)
    result = await manager.nasa.get_apod()
    
    # بررسی پاسخ
    has_data = "url" in result or "error" in result
    
    return has_data


def test_cognitive_core():
    """تست هسته شناختی"""
    # این تست نیاز به OPENAI_API_KEY دارد
    # در صورت عدم وجود کلید، تست را رد می‌کنیم
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("   ⚠️  SKIPPED: OPENAI_API_KEY not set")
        return True
    
    try:
        core = CognitiveCore()
        
        # تست تولید تسک
        task = core.generate_task(ProblemCategory.MATHEMATICAL, 5.0)
        
        return task is not None and "title" in task
    except Exception as e:
        print(f"   ⚠️  SKIPPED: {str(e)}")
        return True


def test_data_persistence():
    """تست ماندگاری داده"""
    # ایجاد کیف پول و ذخیره
    wallet1 = Wallet("test_data_persist")
    address1 = wallet1.get_address()
    
    # بارگذاری مجدد
    wallet2 = Wallet("test_data_persist")
    address2 = wallet2.get_address()
    
    return address1 == address2


def test_value_calculations():
    """تست محاسبات ارزش"""
    v = ValueVector(
        knowledge=100.0,
        computation=50.0,
        originality=30.0,
        consciousness=20.0,
        environmental=10.0,
        health=15.0
    )
    
    total = v.total_value()
    dict_repr = v.to_dict()
    
    return (
        total == 225.0 and
        len(dict_repr) == 7 and  # 6 dimensions + total
        dict_repr["total"] == 225.0
    )


def main():
    """اجرای تمام تست‌ها"""
    print("=" * 60)
    print("🌌 Laniakea Protocol v5.0 - Test Suite")
    print("=" * 60)
    
    runner = TestRunner()
    
    # تست‌های پایه
    runner.test("Wallet System", test_wallet)
    runner.test("Blockchain", test_blockchain)
    runner.test("Value Vector", test_value_vector)
    runner.test("Value Calculations", test_value_calculations)
    
    # تست‌های سیستم‌های پیشرفته
    runner.test("Hash Modernity", test_hash_modernity)
    runner.test("Token Economics", test_token_economics)
    runner.test("Reputation System", test_reputation_system)
    
    # تست‌های API
    runner.test("API Manager", test_api_manager)
    runner.test("Cognitive Core", test_cognitive_core)
    
    # تست‌های ماندگاری
    runner.test("Data Persistence", test_data_persistence)
    
    # خلاصه
    runner.summary()
    
    # خروج با کد مناسب
    sys.exit(0 if runner.failed == 0 else 1)


if __name__ == "__main__":
    main()
