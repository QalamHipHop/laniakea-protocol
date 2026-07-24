"""
Laniakea Protocol - Advanced Rate Limiting System
سیستم محدودسازی نرخ درخواست پیشرفته

این ماژول برای جلوگیری از:
- حملات DDoS
- Brute force attacks
- API abuse
- Resource exhaustion

ویژگی‌ها:
- Rate limiting بر اساس IP
- Rate limiting بر اساس User/Node ID
- Sliding window algorithm
- Token bucket algorithm
- Whitelist/Blacklist
- Dynamic rate adjustment
"""

import time
import hashlib
from typing import Dict, Optional, Tuple, List
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio


@dataclass
class RateLimitConfig:
    """پیکربندی rate limiting"""

    # محدودیت‌های پایه
    requests_per_second: int = 10
    requests_per_minute: int = 100
    requests_per_hour: int = 1000
    requests_per_day: int = 10000

    # محدودیت‌های burst
    burst_size: int = 20

    # زمان block (ثانیه)
    block_duration: int = 300  # 5 دقیقه

    # تعداد تخلفات قبل از block
    violations_before_block: int = 3

    # فعال‌سازی
    enabled: bool = True


@dataclass
class ClientState:
    """وضعیت یک client"""

    # تاریخچه درخواست‌ها (timestamp)
    request_history: deque = field(default_factory=lambda: deque(maxlen=10000))

    # تعداد تخلفات
    violations: int = 0

    # زمان block (اگر block شده)
    blocked_until: Optional[float] = None

    # Token bucket
    tokens: float = 0.0
    last_refill: float = field(default_factory=time.time)

    # آمار
    total_requests: int = 0
    blocked_requests: int = 0
    last_request_time: float = field(default_factory=time.time)


class RateLimiter:
    """
    سیستم Rate Limiting پیشرفته

    از دو الگوریتم استفاده می‌کند:
    1. Sliding Window - برای محدودیت‌های زمانی
    2. Token Bucket - برای مدیریت burst
    """

    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        راه‌اندازی rate limiter

        Args:
            config: پیکربندی rate limiting
        """
        self.config = config or RateLimitConfig()

        # ذخیره وضعیت client ها
        self.clients: Dict[str, ClientState] = defaultdict(ClientState)

        # Whitelist و Blacklist
        self.whitelist: set = set()
        self.blacklist: set = set()

        # آمار کلی
        self.stats = {
            "total_requests": 0,
            "blocked_requests": 0,
            "unique_clients": 0,
            "current_blocks": 0,
        }

        # Lock برای thread safety
        self._lock = asyncio.Lock()

    def _get_client_id(self, identifier: str) -> str:
        """
        تولید شناسه یکتا برای client

        Args:
            identifier: IP یا Node ID

        Returns:
            شناسه hash شده
        """
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]

    def add_to_whitelist(self, identifier: str):
        """افزودن به whitelist"""
        client_id = self._get_client_id(identifier)
        self.whitelist.add(client_id)
        print(f"✅ {identifier} به whitelist اضافه شد")

    def add_to_blacklist(self, identifier: str):
        """افزودن به blacklist"""
        client_id = self._get_client_id(identifier)
        self.blacklist.add(client_id)
        print(f"🚫 {identifier} به blacklist اضافه شد")

    def remove_from_whitelist(self, identifier: str):
        """حذف از whitelist"""
        client_id = self._get_client_id(identifier)
        self.whitelist.discard(client_id)

    def remove_from_blacklist(self, identifier: str):
        """حذف از blacklist"""
        client_id = self._get_client_id(identifier)
        self.blacklist.discard(client_id)

    def _refill_tokens(self, client: ClientState):
        """پر کردن مجدد token bucket"""
        now = time.time()
        elapsed = now - client.last_refill

        # محاسبه token های جدید
        tokens_to_add = elapsed * (self.config.requests_per_second / 1.0)
        client.tokens = min(self.config.burst_size, client.tokens + tokens_to_add)
        client.last_refill = now

    def _check_sliding_window(
        self, client: ClientState, window_seconds: int, max_requests: int
    ) -> bool:
        """
        بررسی محدودیت با sliding window

        Args:
            client: وضعیت client
            window_seconds: اندازه پنجره (ثانیه)
            max_requests: حداکثر درخواست در پنجره

        Returns:
            True اگر مجاز باشد
        """
        now = time.time()
        cutoff = now - window_seconds

        # حذف درخواست‌های قدیمی
        while client.request_history and client.request_history[0] < cutoff:
            client.request_history.popleft()

        # بررسی تعداد
        return len(client.request_history) < max_requests

    async def check_rate_limit(
        self, identifier: str, endpoint: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        بررسی rate limit برای یک درخواست

        Args:
            identifier: IP یا Node ID
            endpoint: نام endpoint (اختیاری)

        Returns:
            (allowed: bool, reason: Optional[str])
        """
        if not self.config.enabled:
            return True, None

        async with self._lock:
            client_id = self._get_client_id(identifier)

            # بررسی whitelist
            if client_id in self.whitelist:
                return True, None

            # بررسی blacklist
            if client_id in self.blacklist:
                self.stats["blocked_requests"] += 1
                return False, "Client is blacklisted"

            client = self.clients[client_id]
            now = time.time()

            # بررسی block
            if client.blocked_until and now < client.blocked_until:
                client.blocked_requests += 1
                self.stats["blocked_requests"] += 1
                remaining = int(client.blocked_until - now)
                return False, f"Blocked for {remaining} more seconds"

            # رفع block اگر زمان آن گذشته
            if client.blocked_until and now >= client.blocked_until:
                client.blocked_until = None
                client.violations = 0
                self.stats["current_blocks"] -= 1

            # Refill tokens
            self._refill_tokens(client)

            # بررسی token bucket
            if client.tokens < 1.0:
                client.violations += 1

                # Block کردن در صورت تخلفات زیاد
                if client.violations >= self.config.violations_before_block:
                    client.blocked_until = now + self.config.block_duration
                    self.stats["current_blocks"] += 1
                    return False, f"Too many violations. Blocked for {self.config.block_duration}s"

                self.stats["blocked_requests"] += 1
                return False, "Rate limit exceeded (burst)"

            # بررسی sliding windows
            checks = [
                (1, self.config.requests_per_second, "per second"),
                (60, self.config.requests_per_minute, "per minute"),
                (3600, self.config.requests_per_hour, "per hour"),
                (86400, self.config.requests_per_day, "per day"),
            ]

            for window, limit, name in checks:
                if not self._check_sliding_window(client, window, limit):
                    client.violations += 1
                    self.stats["blocked_requests"] += 1
                    return False, f"Rate limit exceeded ({name})"

            # درخواست مجاز است
            client.tokens -= 1.0
            client.request_history.append(now)
            client.total_requests += 1
            client.last_request_time = now

            self.stats["total_requests"] += 1
            self.stats["unique_clients"] = len(self.clients)

            return True, None

    def get_client_stats(self, identifier: str) -> Dict:
        """دریافت آمار یک client"""
        client_id = self._get_client_id(identifier)

        if client_id not in self.clients:
            return {"error": "Client not found"}

        client = self.clients[client_id]
        now = time.time()

        return {
            "total_requests": client.total_requests,
            "blocked_requests": client.blocked_requests,
            "violations": client.violations,
            "is_blocked": client.blocked_until and now < client.blocked_until,
            "blocked_until": client.blocked_until,
            "current_tokens": client.tokens,
            "last_request": datetime.fromtimestamp(client.last_request_time).isoformat(),
            "in_whitelist": client_id in self.whitelist,
            "in_blacklist": client_id in self.blacklist,
        }

    def get_stats(self) -> Dict:
        """دریافت آمار کلی"""
        return {
            **self.stats,
            "whitelist_size": len(self.whitelist),
            "blacklist_size": len(self.blacklist),
            "config": {
                "enabled": self.config.enabled,
                "requests_per_second": self.config.requests_per_second,
                "requests_per_minute": self.config.requests_per_minute,
                "burst_size": self.config.burst_size,
            },
        }

    def reset_client(self, identifier: str):
        """ریست کردن وضعیت یک client"""
        client_id = self._get_client_id(identifier)
        if client_id in self.clients:
            del self.clients[client_id]
            print(f"✅ Client {identifier} reset شد")

    def cleanup_old_clients(self, inactive_hours: int = 24):
        """پاکسازی client های غیرفعال"""
        now = time.time()
        cutoff = now - (inactive_hours * 3600)

        to_remove = [
            client_id
            for client_id, client in self.clients.items()
            if client.last_request_time < cutoff
        ]

        for client_id in to_remove:
            del self.clients[client_id]

        if to_remove:
            print(f"🧹 {len(to_remove)} client غیرفعال پاکسازی شد")


# Singleton instance
_rate_limiter_instance: Optional[RateLimiter] = None


def get_rate_limiter(config: Optional[RateLimitConfig] = None) -> RateLimiter:
    """دریافت instance rate limiter"""
    global _rate_limiter_instance

    if _rate_limiter_instance is None:
        _rate_limiter_instance = RateLimiter(config)

    return _rate_limiter_instance


# Decorator برای استفاده آسان
def rate_limit(identifier_func=None):
    """
    Decorator برای اعمال rate limiting به توابع

    مثال:
        @rate_limit(lambda request: request.client.host)
        async def my_endpoint(request):
            ...
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            limiter = get_rate_limiter()

            # استخراج identifier
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            else:
                # پیش‌فرض: استفاده از اولین آرگومان
                identifier = str(args[0]) if args else "default"

            # بررسی rate limit
            allowed, reason = await limiter.check_rate_limit(identifier)

            if not allowed:
                raise Exception(f"Rate limit exceeded: {reason}")

            # اجرای تابع اصلی
            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def main():
    """تست سیستم"""
    print("🧪 تست سیستم Rate Limiting\n")

    # ایجاد limiter با تنظیمات تست
    config = RateLimitConfig(
        requests_per_second=5,
        requests_per_minute=20,
        burst_size=10,
    )
    limiter = RateLimiter(config)

    # تست 1: درخواست‌های عادی
    print("📊 تست 1: درخواست‌های عادی")
    for i in range(15):
        allowed, reason = await limiter.check_rate_limit("192.168.1.1")
        status = "✅" if allowed else "❌"
        print(f"  درخواست {i+1}: {status} {reason or ''}")
        await asyncio.sleep(0.1)

    print("\n" + "=" * 50 + "\n")

    # تست 2: Whitelist
    print("📊 تست 2: Whitelist")
    limiter.add_to_whitelist("192.168.1.100")
    for i in range(5):
        allowed, reason = await limiter.check_rate_limit("192.168.1.100")
        print(f"  درخواست {i+1}: ✅ (whitelisted)")

    print("\n" + "=" * 50 + "\n")

    # نمایش آمار
    print("📈 آمار نهایی:")
    stats = limiter.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
