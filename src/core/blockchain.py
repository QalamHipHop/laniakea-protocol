"""
Laniakea Protocol - Blockchain Engine
موتور بلاک‌چین چند بُعدی با قابلیت ارزش‌گذاری پیشرفته
"""

import hashlib
import json
from time import time
from typing import List, Optional, Dict, Set
from src.core.models import (
    KnowledgeBlock, Transaction, Solution, ValueVector,
    ValueDimension, NodeInfo
)
from src.config import BLOCK_REWARD


class LaniakeaChain:
    """
    زنجیره بلاک‌های دانشی Laniakea
    """

    def __init__(self, node_id: str):
        self.chain: List[KnowledgeBlock] = []
        self.node_id = node_id
        self.balances: Dict[str, Dict[str, float]] = {}  # {node_id: {dimension: balance}}
        self.total_value_created = ValueVector()

    def create_genesis_block(self):
        """ایجاد بلاک پیدایش"""
        genesis_block = KnowledgeBlock(
            index=0,
            timestamp=time(),
            transactions=[],
            solution=None,
            author_id="genesis",
            previous_hash='0' * 64,
            signature="genesis_signature",
            nonce=0,
            difficulty=0.0,
            metadata={
                "message": "In the beginning, there was curiosity...",
                "genesis": True
            }
        )
        self.chain.append(genesis_block)
        print("🌌 Genesis block created: The cosmic journey begins...")

    def new_block(
        self,
        transactions: List[Transaction],
        solution: Optional[Solution],
        previous_hash: str,
        is_genesis: bool = False
    ) -> KnowledgeBlock:
        """
        ایجاد بلاک جدید
        """
        all_txs = list(transactions)

        # اضافه کردن پاداش بلاک (به صورت توکن knowledge)
        if not is_genesis:
            block_reward_tx = Transaction(
                id=self._generate_tx_id(),
                sender="0",  # از سیستم
                recipient=self.node_id,
                amount=BLOCK_REWARD,
                dimension=ValueDimension.KNOWLEDGE,
                timestamp=time(),
                metadata={"type": "block_reward"}
            )
            all_txs.insert(0, block_reward_tx)

        # اضافه کردن پاداش برای راه‌حل
        if solution:
            solution_rewards = self._calculate_solution_rewards(solution)
            for dimension, amount in solution_rewards.items():
                if amount > 0:
                    reward_tx = Transaction(
                        id=self._generate_tx_id(),
                        sender="0",  # از سیستم
                        recipient=solution.solver_id,
                        amount=amount,
                        dimension=dimension,
                        timestamp=time(),
                        metadata={
                            "type": "solution_reward",
                            "solution_id": solution.id,
                            "task_id": solution.task_id
                        }
                    )
                    all_txs.append(reward_tx)

        new_block = KnowledgeBlock(
            index=len(self.chain),
            timestamp=time(),
            transactions=all_txs,
            solution=solution,
            author_id=self.node_id,
            previous_hash=previous_hash,
            signature="",  # خواهد شد پر
            nonce=0,
            difficulty=self._calculate_difficulty(),
            metadata={}
        )

        return new_block

    def add_block(self, block: KnowledgeBlock, known_authorities: Set[str]) -> bool:
        """
        افزودن بلاک به زنجیره با اعتبارسنجی
        """
        # اعتبارسنجی‌های پایه
        if not self._validate_block(block, known_authorities):
            return False

        # افزودن بلاک
        self.chain.append(block)

        # به‌روزرسانی موجودی‌ها
        self._update_balances(block)

        # به‌روزرسانی آمار کلی
        if block.solution:
            self._update_total_value(block.solution.value_vector)

        return True

    def _validate_block(self, block: KnowledgeBlock, known_authorities: Set[str]) -> bool:
        """اعتبارسنجی بلاک"""
        # بررسی شماره بلاک
        if block.index != len(self.chain):
            print(f"❌ Invalid block index: {block.index} != {len(self.chain)}")
            return False

        # بررسی هش بلاک قبلی
        if self.chain:
            expected_prev_hash = self.hash(self.chain[-1])
            if block.previous_hash != expected_prev_hash:
                print(f"❌ Invalid previous hash")
                return False

        # بررسی authority (برای بلاک‌های غیر genesis)
        if block.index > 0 and block.author_id not in known_authorities:
            print(f"❌ Block author {block.author_id[:8]} is not an authority")
            return False

	        # بررسی امضا
	        if not block.signature:
	            print(f"❌ Block has no signature")
	            return False
	
	        # در اینجا باید کلید عمومی نود اعتبارسنج (author_id) را از یک منبع معتبر (مانند سیستم Reputation)
	        # دریافت کرده و امضا را اعتبارسنجی کنیم.
	        # فرض می‌کنیم یک تابع کمکی برای دریافت کلید عمومی وجود دارد.
	        # from src.core.wallet import Wallet
	        # public_key = get_public_key_for_node(block.author_id)
	        # if not public_key:
	        #     print(f"❌ Could not retrieve public key for author {block.author_id[:8]}")
	        #     return False
	        
	        # if not Wallet.verify(public_key, block.signature, self.get_block_hash_payload(block)):
	        #     print(f"❌ Invalid signature for block {block.index}")
	        #     return False
	
	        return True

    def _update_balances(self, block: KnowledgeBlock):
        """به‌روزرسانی موجودی‌های نودها"""
        for tx in block.transactions:
            # کاهش از فرستنده (اگر فرستنده سیستم نباشد)
            if tx.sender != "0":
                if tx.sender not in self.balances:
                    self.balances[tx.sender] = {}
                dim = tx.dimension.value
                current = self.balances[tx.sender].get(dim, 0.0)
                self.balances[tx.sender][dim] = current - tx.amount

            # افزایش به گیرنده
            if tx.recipient not in self.balances:
                self.balances[tx.recipient] = {}
            dim = tx.dimension.value
            current = self.balances[tx.recipient].get(dim, 0.0)
            self.balances[tx.recipient][dim] = current + tx.amount

    def _update_total_value(self, value_vector: ValueVector):
        """به‌روزرسانی ارزش کل ایجاد شده"""
        self.total_value_created.knowledge += value_vector.knowledge
        self.total_value_created.computation += value_vector.computation
        self.total_value_created.originality += value_vector.originality
        self.total_value_created.consciousness += value_vector.consciousness
        self.total_value_created.environmental += value_vector.environmental
        self.total_value_created.health += value_vector.health

    def _calculate_solution_rewards(self, solution: Solution) -> Dict[ValueDimension, float]:
        """محاسبه پاداش‌های راه‌حل بر اساس ارزش‌های آن"""
        rewards = {}
        vv = solution.value_vector

        if vv.knowledge > 0:
            rewards[ValueDimension.KNOWLEDGE] = vv.knowledge * 1.0
        if vv.computation > 0:
            rewards[ValueDimension.COMPUTATION] = vv.computation * 1.0
        if vv.originality > 0:
            rewards[ValueDimension.ORIGINALITY] = vv.originality * 1.5  # پاداش بیشتر برای خلاقیت
        if vv.consciousness > 0:
            rewards[ValueDimension.CONSCIOUSNESS] = vv.consciousness * 2.0  # پاداش بیشتر برای آگاهی
        if vv.environmental > 0:
            rewards[ValueDimension.ENVIRONMENTAL] = vv.environmental * 1.2
        if vv.health > 0:
            rewards[ValueDimension.HEALTH] = vv.health * 1.2

        return rewards

    def _calculate_difficulty(self) -> float:
        """محاسبه سطح دشواری بر اساس طول زنجیره"""
        base_difficulty = 1.0
        growth_rate = 0.01
        return base_difficulty + (len(self.chain) * growth_rate)

    def _generate_tx_id(self) -> str:
        """تولید شناسه یکتا برای تراکنش"""
        return hashlib.sha256(f"{time()}{self.node_id}".encode()).hexdigest()

    @staticmethod
    def get_block_hash_payload(block: KnowledgeBlock) -> bytes:
        """دریافت payload برای هش کردن بلاک"""
        block_dict = block.model_dump(exclude={'signature'})
        return json.dumps(block_dict, sort_keys=True).encode()

    @staticmethod
    def hash(block: KnowledgeBlock) -> str:
        """محاسبه هش بلاک"""
        if not block:
            return '0' * 64
        return hashlib.sha256(LaniakeaChain.get_block_hash_payload(block)).hexdigest()

    @property
    def last_block(self) -> Optional[KnowledgeBlock]:
        """دریافت آخرین بلاک"""
        return self.chain[-1] if self.chain else None

    def get_balance(self, node_id: str, dimension: ValueDimension) -> float:
        """دریافت موجودی یک نود در یک بُعد خاص"""
        if node_id not in self.balances:
            return 0.0
        return self.balances[node_id].get(dimension.value, 0.0)

    def get_total_balance(self, node_id: str) -> ValueVector:
        """دریافت موجودی کل یک نود در تمام ابعاد"""
        if node_id not in self.balances:
            return ValueVector()

        balances = self.balances[node_id]
        return ValueVector(
            knowledge=balances.get(ValueDimension.KNOWLEDGE.value, 0.0),
            computation=balances.get(ValueDimension.COMPUTATION.value, 0.0),
            originality=balances.get(ValueDimension.ORIGINALITY.value, 0.0),
            consciousness=balances.get(ValueDimension.CONSCIOUSNESS.value, 0.0),
            environmental=balances.get(ValueDimension.ENVIRONMENTAL.value, 0.0),
            health=balances.get(ValueDimension.HEALTH.value, 0.0)
        )

    def get_chain_stats(self) -> Dict:
        """دریافت آمار زنجیره"""
        total_transactions = sum(len(block.transactions) for block in self.chain)
        total_solutions = sum(1 for block in self.chain if block.solution)

        return {
            "length": len(self.chain),
            "total_transactions": total_transactions,
            "total_solutions": total_solutions,
            "total_value_created": self.total_value_created.to_dict(),
            "current_difficulty": self._calculate_difficulty(),
            "unique_participants": len(self.balances)
        }
