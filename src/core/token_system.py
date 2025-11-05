"""
Laniakea Protocol - Multi-Dimensional Token System
سیستم توکن‌سازی چند بُعدی با اقتصاد پیشرفته
"""

import hashlib
from time import time
from typing import Dict, List, Optional, Any
from src.core.models import ValueDimension, ValueVector, Transaction


class Token:
    """
    توکن چند بُعدی Laniakea
    هر توکن نشان‌دهنده ارزش در یک بُعد خاص است
    """

    def __init__(
        self,
        token_id: str,
        dimension: ValueDimension,
        amount: float,
        owner: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.token_id = token_id
        self.dimension = dimension
        self.amount = amount
        self.owner = owner
        self.created_at = time()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری"""
        return {
            "token_id": self.token_id,
            "dimension": self.dimension.value,
            "amount": self.amount,
            "owner": self.owner,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


class TokenEconomics:
    """
    سیستم اقتصادی توکن‌ها
    """

    def __init__(self):
        self.total_supply: Dict[str, float] = {dim.value: 0.0 for dim in ValueDimension}
        self.burned_tokens: Dict[str, float] = {dim.value: 0.0 for dim in ValueDimension}
        self.inflation_rate = 0.02  # 2% سالانه
        self.burn_rate = 0.01  # 1% برای هر عملیات

        print("💰 Token Economics initialized")

    def mint_tokens(
        self, dimension: ValueDimension, amount: float, recipient: str, reason: str
    ) -> Token:
        """
        تولید توکن جدید

        Args:
            dimension: بُعد ارزشی
            amount: مقدار
            recipient: دریافت‌کننده
            reason: دلیل تولید

        Returns:
            توکن جدید
        """
        token_id = self._generate_token_id(dimension, amount, recipient)

        token = Token(
            token_id=token_id,
            dimension=dimension,
            amount=amount,
            owner=recipient,
            metadata={"reason": reason, "minted_at": time()},
        )

        # افزایش عرضه کل
        self.total_supply[dimension.value] += amount

        print(f"🪙 Minted {amount} {dimension.value} tokens for {recipient[:8]}")
        return token

    def burn_tokens(self, dimension: ValueDimension, amount: float, reason: str) -> bool:
        """
        سوزاندن توکن

        Args:
            dimension: بُعد ارزشی
            amount: مقدار
            reason: دلیل سوزاندن

        Returns:
            True اگر موفق باشد
        """
        if self.total_supply[dimension.value] < amount:
            print(f"⚠️ Insufficient supply to burn {amount} {dimension.value}")
            return False

        self.total_supply[dimension.value] -= amount
        self.burned_tokens[dimension.value] += amount

        print(f"🔥 Burned {amount} {dimension.value} tokens: {reason}")
        return True

    def calculate_exchange_rate(
        self, from_dimension: ValueDimension, to_dimension: ValueDimension
    ) -> float:
        """
        محاسبه نرخ تبدیل بین دو بُعد

        نرخ بر اساس عرضه و تقاضا محاسبه می‌شود

        Args:
            from_dimension: بُعد مبدأ
            to_dimension: بُعد مقصد

        Returns:
            نرخ تبدیل
        """
        from_supply = self.total_supply[from_dimension.value]
        to_supply = self.total_supply[to_dimension.value]

        # نرخ پایه
        base_rate = 1.0

        # تنظیم بر اساس عرضه (کمیاب‌تر = ارزشمندتر)
        if from_supply > 0 and to_supply > 0:
            scarcity_factor = to_supply / from_supply
            base_rate *= scarcity_factor

        # ضرایب خاص برای هر بُعد
        dimension_weights = {
            ValueDimension.KNOWLEDGE: 1.0,
            ValueDimension.COMPUTATION: 0.8,
            ValueDimension.ORIGINALITY: 1.5,
            ValueDimension.CONSCIOUSNESS: 2.0,
            ValueDimension.ENVIRONMENTAL: 1.2,
            ValueDimension.HEALTH: 1.2,
        }

        from_weight = dimension_weights.get(from_dimension, 1.0)
        to_weight = dimension_weights.get(to_dimension, 1.0)

        final_rate = base_rate * (to_weight / from_weight)

        return final_rate

    def exchange_tokens(
        self,
        from_dimension: ValueDimension,
        to_dimension: ValueDimension,
        amount: float,
        owner: str,
    ) -> Optional[Token]:
        """
        تبدیل توکن از یک بُعد به بُعد دیگر

        Args:
            from_dimension: بُعد مبدأ
            to_dimension: بُعد مقصد
            amount: مقدار
            owner: مالک

        Returns:
            توکن جدید
        """
        rate = self.calculate_exchange_rate(from_dimension, to_dimension)
        converted_amount = amount * rate

        # کسر هزینه تبدیل
        fee = converted_amount * self.burn_rate
        final_amount = converted_amount - fee

        # سوزاندن توکن مبدأ
        if not self.burn_tokens(from_dimension, amount, "exchange"):
            return None

        # تولید توکن مقصد
        new_token = self.mint_tokens(
            to_dimension, final_amount, owner, f"exchanged from {from_dimension.value}"
        )

        # سوزاندن fee
        self.burn_tokens(to_dimension, fee, "exchange_fee")

        print(
            f"💱 Exchanged {amount} {from_dimension.value} -> {final_amount:.2f} {to_dimension.value}"
        )
        return new_token

    def get_total_value(self) -> float:
        """محاسبه ارزش کل تمام توکن‌ها"""
        dimension_weights = {
            ValueDimension.KNOWLEDGE.value: 1.0,
            ValueDimension.COMPUTATION.value: 0.8,
            ValueDimension.ORIGINALITY.value: 1.5,
            ValueDimension.CONSCIOUSNESS.value: 2.0,
            ValueDimension.ENVIRONMENTAL.value: 1.2,
            ValueDimension.HEALTH.value: 1.2,
        }

        total = sum(
            self.total_supply[dim] * dimension_weights.get(dim, 1.0) for dim in self.total_supply
        )

        return total

    def get_stats(self) -> Dict[str, Any]:
        """دریافت آمار اقتصادی"""
        return {
            "total_supply": self.total_supply,
            "burned_tokens": self.burned_tokens,
            "total_value": self.get_total_value(),
            "inflation_rate": self.inflation_rate,
            "burn_rate": self.burn_rate,
        }

    def _generate_token_id(self, dimension: ValueDimension, amount: float, recipient: str) -> str:
        """تولید شناسه یکتا برای توکن"""
        data = f"{dimension.value}{amount}{recipient}{time()}"
        return hashlib.sha256(data.encode()).hexdigest()


class StakingSystem:
    """
    سیستم سهام‌گذاری (Staking)
    """

    def __init__(self, token_economics: TokenEconomics):
        self.token_economics = token_economics
        self.stakes: Dict[str, Dict[str, float]] = {}  # {staker: {dimension: amount}}
        self.rewards_pool: Dict[str, float] = {dim.value: 0.0 for dim in ValueDimension}
        self.apy = 0.05  # 5% سالانه

        print("🔒 Staking System initialized")

    def stake(self, staker: str, dimension: ValueDimension, amount: float) -> bool:
        """
        سهام‌گذاری توکن

        Args:
            staker: سهام‌گذار
            dimension: بُعد
            amount: مقدار

        Returns:
            True اگر موفق باشد
        """
        if staker not in self.stakes:
            self.stakes[staker] = {}

        current = self.stakes[staker].get(dimension.value, 0.0)
        self.stakes[staker][dimension.value] = current + amount

        print(f"🔒 {staker[:8]} staked {amount} {dimension.value}")
        return True

    def unstake(self, staker: str, dimension: ValueDimension, amount: float) -> bool:
        """
        برداشت سهام

        Args:
            staker: سهام‌گذار
            dimension: بُعد
            amount: مقدار

        Returns:
            True اگر موفق باشد
        """
        if staker not in self.stakes:
            return False

        current = self.stakes[staker].get(dimension.value, 0.0)
        if current < amount:
            return False

        self.stakes[staker][dimension.value] = current - amount

        print(f"🔓 {staker[:8]} unstaked {amount} {dimension.value}")
        return True

    def calculate_rewards(self, staker: str, time_period: float) -> ValueVector:
        """
        محاسبه پاداش سهام‌گذاری

        Args:
            staker: سهام‌گذار
            time_period: مدت زمان (ثانیه)

        Returns:
            پاداش‌ها
        """
        if staker not in self.stakes:
            return ValueVector()

        # محاسبه پاداش برای هر بُعد
        rewards = ValueVector()
        stakes = self.stakes[staker]

        # تبدیل time_period از ثانیه به سال
        years = time_period / (365.25 * 24 * 3600)

        for dim_str, staked_amount in stakes.items():
            reward = staked_amount * self.apy * years

            # اختصاص به بُعد مناسب
            if dim_str == ValueDimension.KNOWLEDGE.value:
                rewards.knowledge = reward
            elif dim_str == ValueDimension.COMPUTATION.value:
                rewards.computation = reward
            elif dim_str == ValueDimension.ORIGINALITY.value:
                rewards.originality = reward
            elif dim_str == ValueDimension.CONSCIOUSNESS.value:
                rewards.consciousness = reward
            elif dim_str == ValueDimension.ENVIRONMENTAL.value:
                rewards.environmental = reward
            elif dim_str == ValueDimension.HEALTH.value:
                rewards.health = reward

        return rewards

    def distribute_rewards(self, staker: str, time_period: float) -> ValueVector:
        """
        توزیع پاداش‌ها

        Args:
            staker: سهام‌گذار
            time_period: مدت زمان

        Returns:
            پاداش‌های توزیع شده
        """
        rewards = self.calculate_rewards(staker, time_period)

        # تولید توکن‌های پاداش
        for dim in ValueDimension:
            amount = getattr(rewards, dim.value, 0.0)
            if amount > 0:
                self.token_economics.mint_tokens(dim, amount, staker, "staking_reward")

        print(f"🎁 Distributed {rewards.total_value():.2f} total rewards to {staker[:8]}")
        return rewards

    def get_total_staked(self) -> Dict[str, float]:
        """دریافت مجموع سهام‌گذاری‌ها"""
        total = {dim.value: 0.0 for dim in ValueDimension}

        for stakes in self.stakes.values():
            for dim, amount in stakes.items():
                total[dim] += amount

        return total

    def get_staker_info(self, staker: str) -> Dict[str, Any]:
        """دریافت اطلاعات سهام‌گذار"""
        if staker not in self.stakes:
            return {"staked": {}, "total": 0.0}

        stakes = self.stakes[staker]
        total = sum(stakes.values())

        return {"staked": stakes, "total": total}
