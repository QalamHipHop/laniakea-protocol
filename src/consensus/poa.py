"""
Laniakea Protocol - Proof of Authority (PoA)
اثبات اعتبار
"""

from typing import List, Set
import random

class ProofOfAuthority:
    """
    الگوریتم اجماع اثبات اعتبار
    یک مجموعه از نودهای معتبر (authorities) مسئول ایجاد بلاک‌های جدید هستند.
    """

    def __init__(self, authorities: Set[str]):
        """
        Args:
            authorities: مجموعه‌ای از شناسه‌های نودهای معتبر
        """
        self.authorities = list(authorities)

    def select_validator(self, last_block_hash: str) -> str:
        """
        انتخاب یک نود معتبر برای ایجاد بلاک بعدی به صورت قطعی اما شبه‌تصادفی.

        Args:
            last_block_hash: هش بلاک قبلی برای ایجاد seed

        Returns:
            شناسه نود معتبر انتخاب شده
        """
        if not self.authorities:
            raise ValueError("Authority set cannot be empty.")

        # از هش بلاک قبلی برای انتخاب قطعی استفاده می‌کنیم
        seed = int(last_block_hash, 16)
        random.seed(seed)

        # انتخاب یک authority به صورت تصادفی
        validator_index = random.randint(0, len(self.authorities) - 1)
        
        return self.authorities[validator_index]
