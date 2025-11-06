"""
Laniakea Protocol - Enhanced Blockchain Engine v0.0.01
موتور بلک‌چین چند بعدی با قابلیت ارزش‌گذاری پیشرفته و امنیت بالقوه
"""

import hashlib
import json
import asyncio
from time import time
from typing import List, Optional, Dict, Set, Any, Union
from src.core.models import (
    KnowledgeBlock,
    Transaction,
    Solution,
    ValueVector,
    ValueDimension,
    NodeInfo,
)
from src.config import BLOCK_REWARD
from src.core.standards import (
    LaniakeaLogger, secure_exception_handler, validate_input,
    sanitize_string, PerformanceMonitor, GLOBAL_SECURITY_CONFIG
)


class LaniakeaChain:
    """
    زنجیره بلک‌های دانشی Laniakea - نسخه امن و بهینه‌سازی شده
    
    ویژگی‌های جدید:
    - امنیت پیشرفته با validation لایه‌ای
    - مدیریت خطای استاندارد
    - مانیتورینگ عملکرد
    - قابلیت بازیابی از خطا
    - قفل‌سازی async برای عملیات همزمان
    """

    def __init__(self, node_id: str):
        # اعتبارسنجی ورودی
        validate_input({"node_id": node_id}, ["node_id"])
        self.node_id = sanitize_string(node_id, max_length=100)
        
        # استانداردهای لاگینگ و مانیتورینگ
        self.logger = LaniakeaLogger(f"LaniakeaChain.{self.node_id}")
        self.monitor = PerformanceMonitor(self.logger)
        
        # داده‌های زنجیره
        self.chain: List[KnowledgeBlock] = []
        self.balances: Dict[str, Dict[str, float]] = {}
        self.total_value_created = ValueVector()
        
        # متغیرهای امنیتی
        self._security_config = GLOBAL_SECURITY_CONFIG
        self._last_block_hash = None
        self._lock = asyncio.Lock()
        
        self.logger.info(f"Initializing LaniakeaChain for node: {self.node_id}")
        
        # ایجاد بلک پیدایش با مدیریت خطا
        try:
            if not self.chain:
                self.create_genesis_block()
        except Exception as e:
            self.logger.critical("Failed to create genesis block", exception=e)
            raise

    @secure_exception_handler(LaniakeaLogger("LaniakeaChain"))
    def create_genesis_block(self) -> None:
        """ایجاد بلک پیدایش با امنیت پیشرفته"""
        self.monitor.start_timer("genesis_block_creation")
        
        try:
            # ایجاد داده‌های بلک پیدایش
            genesis_metadata = {
                "message": "In the beginning, there was curiosity...",
                "genesis": True,
                "version": "0.0.01",
                "creator": "Laniakea Protocol",
                "security_level": "maximum"
            }
            
            genesis_block = KnowledgeBlock(
                index=0,
                timestamp=time(),
                transactions=[],
                solution=None,
                author_id="genesis",
                previous_hash="0" * 64,
                signature="genesis_signature_v0.0.01",
                nonce=0,
                difficulty=0.0,
                metadata=genesis_metadata,
            )
            
            # اعتبارسنجی بلک پیدایش
            if self._validate_block_integrity(genesis_block):
                self.chain.append(genesis_block)
                self._last_block_hash = self.calculate_hash(genesis_block)
                self.logger.info("Genesis block created successfully")
            else:
                raise ValueError("Genesis block validation failed")
                
        except Exception as e:
            self.logger.critical("Failed to create genesis block", exception=e)
            raise
        finally:
            self.monitor.end_timer("genesis_block_creation")

    def calculate_hash(self, block: KnowledgeBlock) -> str:
        """محاسبه هش بلک با الگوریتم امن"""
        try:
            # ایجاد رشته از داده‌های بلک
            block_string = json.dumps({
                "index": block.index,
                "timestamp": block.timestamp,
                "transactions": [str(tx) for tx in block.transactions],
                "solution": str(block.solution) if block.solution else None,
                "author_id": block.author_id,
                "previous_hash": block.previous_hash,
                "nonce": block.nonce,
                "difficulty": block.difficulty,
                "metadata": block.metadata
            }, sort_keys=True)
            
            # محاسبه هش با SHA-256
            return hashlib.sha256(block_string.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error("Hash calculation failed", exception=e)
            return ""

    def _validate_block_integrity(self, block: KnowledgeBlock) -> bool:
        """اعتبارسنجی یکپارچگی داخلی بلک"""
        try:
            # بررسی فیلدهای ضروری
            required_fields = ['index', 'timestamp', 'previous_hash', 'author_id']
            for field in required_fields:
                if not hasattr(block, field) or getattr(block, field) is None:
                    self.logger.error(f"Missing required field: {field}")
                    return False
            
            # بررسی محدوده مقادیر
            if block.index < 0 or block.difficulty < 0:
                self.logger.error("Invalid block index or difficulty")
                return False
            
            # بررسی طول هش
            if len(block.previous_hash) != 64:
                self.logger.error("Invalid previous hash length")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error("Block integrity validation failed", exception=e)
            return False

    @secure_exception_handler(LaniakeaLogger("LaniakeaChain"))
    async def add_block(self, block: KnowledgeBlock) -> bool:
        """اضافه کردن بلک جدید به زنجیره با امنیت پیشرفته"""
        async with self._lock:
            self.monitor.start_timer("block_addition")
            
            try:
                # اعتبارسنجی بلک جدید
                if not self._validate_block_integrity(block):
                    self.logger.error("Block integrity validation failed")
                    return False
                
                # بررسی هش قبلی
                if self.chain:
                    last_block = self.chain[-1]
                    expected_previous_hash = self.calculate_hash(last_block)
                    if block.previous_hash != expected_previous_hash:
                        self.logger.error("Invalid previous hash")
                        return False
                
                # محاسبه و اعتبارسنجی هش بلک
                current_hash = self.calculate_hash(block)
                if not self._is_valid_proof(block, current_hash):
                    self.logger.error("Invalid proof of work")
                    return False
                
                # اضافه کردن بلک به زنجیره
                self.chain.append(block)
                self._last_block_hash = current_hash
                
                # پردازش تراکنش‌ها
                self._process_block_transactions(block)
                
                self.logger.info(f"Block {block.index} added successfully")
                return True
                
            except Exception as e:
                self.logger.error("Failed to add block", exception=e)
                return False
            finally:
                self.monitor.end_timer("block_addition")

    def _is_valid_proof(self, block: KnowledgeBlock, hash_value: str) -> bool:
        """اعتبارسنجی Proof of Work/Value"""
        try:
            if block.difficulty <= 0:
                return True  # بلک پیدایش یا بلک‌های بدون دشواری
            
            # محاسبه پیشوند مورد نیاز
            prefix = "0" * int(block.difficulty)
            return hash_value.startswith(prefix)
            
        except Exception as e:
            self.logger.error("Proof validation failed", exception=e)
            return False

    def _process_block_transactions(self, block: KnowledgeBlock) -> None:
        """پردازش تراکنش‌های بلک"""
        try:
            for transaction in block.transactions:
                self._process_single_transaction(transaction)
        except Exception as e:
            self.logger.error("Transaction processing failed", exception=e)

    def _process_single_transaction(self, transaction: Transaction) -> None:
        """پردازش یک تراکنش واحد"""
        try:
            if transaction.from_node:
                # کسر از فرستنده
                if transaction.from_node not in self.balances:
                    self.balances[transaction.from_node] = {}
                
                for dimension, amount in transaction.value_vector.dimensions.items():
                    current_balance = self.balances[transaction.from_node].get(dimension, 0.0)
                    if current_balance >= amount:
                        self.balances[transaction.from_node][dimension] = current_balance - amount
                    else:
                        self.logger.warning(f"Insufficient balance for {dimension}")
            
            # افزودن به گیرنده
            if transaction.to_node not in self.balances:
                self.balances[transaction.to_node] = {}
            
            for dimension, amount in transaction.value_vector.dimensions.items():
                current_balance = self.balances[transaction.to_node].get(dimension, 0.0)
                self.balances[transaction.to_node][dimension] = current_balance + amount
                
        except Exception as e:
            self.logger.error("Single transaction processing failed", exception=e)

    def get_latest_block(self) -> Optional[KnowledgeBlock]:
        """دریافت آخرین بلک زنجیره"""
        try:
            return self.chain[-1] if self.chain else None
        except Exception as e:
            self.logger.error("Failed to get latest block", exception=e)
            return None

    def get_balance(self, node_id: str, dimension: ValueDimension) -> float:
        """دریافت موجودی یک نود در یک بعد مشخص"""
        try:
            validate_input({"node_id": node_id, "dimension": dimension}, ["node_id", "dimension"])
            
            if node_id not in self.balances:
                return 0.0
            
            return self.balances[node_id].get(dimension.value, 0.0)
            
        except Exception as e:
            self.logger.error("Failed to get balance", exception=e)
            return 0.0

    def validate_chain(self) -> bool:
        """اعتبارسنجی کامل زنجیره"""
        try:
            self.monitor.start_timer("chain_validation")
            
            if len(self.chain) == 0:
                self.logger.warning("Empty chain")
                return False
            
            # بررسی بلک پیدایش
            if self.chain[0].index != 0:
                self.logger.error("Invalid genesis block index")
                return False
            
            # بررسی بلک‌های متوالی
            for i in range(1, len(self.chain)):
                current_block = self.chain[i]
                previous_block = self.chain[i - 1]
                
                # بررسی ایندکس
                if current_block.index != i:
                    self.logger.error(f"Invalid block index at {i}")
                    return False
                
                # بررسی هش قبلی
                expected_previous_hash = self.calculate_hash(previous_block)
                if current_block.previous_hash != expected_previous_hash:
                    self.logger.error(f"Invalid previous hash at block {i}")
                    return False
                
                # اعتبارسنجی یکپارچگی بلک
                if not self._validate_block_integrity(current_block):
                    self.logger.error(f"Block integrity failed at {i}")
                    return False
            
            self.logger.info("Chain validation completed successfully")
            return True
            
        except Exception as e:
            self.logger.error("Chain validation failed", exception=e)
            return False
        finally:
            self.monitor.end_timer("chain_validation")

    def get_chain_stats(self) -> Dict[str, Any]:
        """دریافت آمار زنجیره"""
        try:
            return {
                "total_blocks": len(self.chain),
                "latest_block_index": self.chain[-1].index if self.chain else -1,
                "total_nodes": len(self.balances),
                "total_value_created": self.total_value_created.to_dict(),
                "chain_valid": self.validate_chain(),
                "last_block_hash": self._last_block_hash
            }
        except Exception as e:
            self.logger.error("Failed to get chain stats", exception=e)
            return {}

    def __str__(self) -> str:
        """نمایش رشته‌ای زنجیره"""
        return f"LaniakeaChain(node={self.node_id}, blocks={len(self.chain)})"

    def __repr__(self) -> str:
        """نمایش رسمی زنجیره"""
        return f"<LaniakeaChain node_id='{self.node_id}' blocks={len(self.chain)}>"