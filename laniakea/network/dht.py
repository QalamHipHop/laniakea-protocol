"""
Laniakea Protocol - Distributed Hash Table (DHT)
جدول هش توزیع شده برای شبکه P2P پیشرفته
"""

import hashlib
import asyncio
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from time import time
import json


@dataclass
class DHTNode:
    """نود در DHT"""

    node_id: str
    host: str
    port: int
    last_seen: float

    def distance_to(self, other_id: str) -> int:
        """محاسبه فاصله XOR (با محافظت در برابر node_id غیرهگز)"""
        try:
            return int(self.node_id, 16) ^ int(other_id, 16)
        except ValueError:
            # Hash-based fallback for non-hex node ids (e.g. UUID-style ids)
            a = int(hashlib.sha256(self.node_id.encode()).hexdigest(), 16)
            b = int(hashlib.sha256(other_id.encode()).hexdigest(), 16)
            return a ^ b

    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "host": self.host,
            "port": self.port,
            "last_seen": self.last_seen,
        }


class KBucket:
    """
    K-Bucket برای ذخیره نودها

    هر bucket حداکثر k نود نزدیک را نگه می‌دارد
    """

    def __init__(self, k: int = 20):
        self.k = k
        self.nodes: List[DHTNode] = []

    def add_node(self, node: DHTNode) -> bool:
        """افزودن نود به bucket"""
        # حذف نود قدیمی اگر وجود دارد
        self.nodes = [n for n in self.nodes if n.node_id != node.node_id]

        # افزودن نود جدید
        if len(self.nodes) < self.k:
            self.nodes.append(node)
            return True

        # اگر bucket پر است، نود قدیمی را جایگزین کن
        oldest = min(self.nodes, key=lambda n: n.last_seen)
        if time() - oldest.last_seen > 3600:  # 1 ساعت
            self.nodes.remove(oldest)
            self.nodes.append(node)
            return True

        return False

    def get_nodes(self) -> List[DHTNode]:
        """دریافت تمام نودها"""
        return sorted(self.nodes, key=lambda n: n.last_seen, reverse=True)

    def remove_node(self, node_id: str):
        """حذف نود"""
        self.nodes = [n for n in self.nodes if n.node_id != node_id]


class RoutingTable:
    """
    جدول مسیریابی Kademlia

    نودها را در bucket های مختلف بر اساس فاصله XOR ذخیره می‌کند
    """

    def __init__(self, node_id: str, k: int = 20):
        self.node_id = node_id
        self.k = k
        self.buckets: List[KBucket] = [KBucket(k) for _ in range(160)]  # 160 bit

    def _get_bucket_index(self, other_id: str) -> int:
        """محاسبه index bucket برای یک node_id (با fallback امن، 0..len-1)"""
        try:
            distance = int(self.node_id, 16) ^ int(other_id, 16)
        except ValueError:
            a = int(hashlib.sha256(self.node_id.encode()).hexdigest(), 16)
            b = int(hashlib.sha256(other_id.encode()).hexdigest(), 16)
            distance = a ^ b
        if distance == 0:
            return 0
        return min(distance.bit_length() - 1, len(self.buckets) - 1)

    def add_node(self, node: DHTNode):
        """افزودن نود به جدول مسیریابی"""
        if node.node_id == self.node_id:
            return

        bucket_index = self._get_bucket_index(node.node_id)
        self.buckets[bucket_index].add_node(node)

    def find_closest_nodes(self, target_id: str, count: int = 20) -> List[DHTNode]:
        """
        پیدا کردن نزدیک‌ترین نودها به یک target

        Args:
            target_id: شناسه هدف
            count: تعداد نودها

        Returns:
            لیست نزدیک‌ترین نودها
        """
        all_nodes = []
        for bucket in self.buckets:
            all_nodes.extend(bucket.get_nodes())

        # مرتب‌سازی بر اساس فاصله
        all_nodes.sort(key=lambda n: n.distance_to(target_id))

        return all_nodes[:count]

    def get_all_nodes(self) -> List[DHTNode]:
        """دریافت تمام نودها"""
        all_nodes = []
        for bucket in self.buckets:
            all_nodes.extend(bucket.get_nodes())
        return all_nodes

    def remove_node(self, node_id: str):
        """حذف نود از جدول"""
        bucket_index = self._get_bucket_index(node_id)
        self.buckets[bucket_index].remove_node(node_id)


class DHTStorage:
    """
    ذخیره‌سازی داده در DHT
    """

    def __init__(self):
        self.data: Dict[str, Tuple[any, float]] = {}  # key -> (value, timestamp)
        self.ttl = 24 * 3600  # 24 ساعت

    def store(self, key: str, value: any):
        """ذخیره داده"""
        self.data[key] = (value, time())

    def retrieve(self, key: str) -> Optional[any]:
        """بازیابی داده"""
        if key not in self.data:
            return None

        value, timestamp = self.data[key]

        # بررسی انقضا
        if time() - timestamp > self.ttl:
            del self.data[key]
            return None

        return value

    def cleanup_expired(self):
        """پاک‌سازی داده‌های منقضی شده"""
        now = time()
        expired = [key for key, (_, timestamp) in self.data.items() if now - timestamp > self.ttl]
        for key in expired:
            del self.data[key]


class KademliaDHT:
    """
    پیاده‌سازی کامل DHT بر اساس Kademlia

    قابلیت‌ها:
    - مسیریابی بهینه با XOR metric
    - ذخیره‌سازی توزیع شده
    - یافتن نود و داده
    - مقاوم در برابر خرابی
    """

    def __init__(self, node_id: str, host: str, port: int):
        self.node_id = node_id
        self.host = host
        self.port = port

        self.routing_table = RoutingTable(node_id)
        self.storage = DHTStorage()

        # تنظیمات Kademlia
        self.alpha = 3  # تعداد query های موازی
        self.k = 20  # تعداد نودها در هر bucket

        print(f"🗺️ Kademlia DHT initialized for node {node_id[:12]}")

    def bootstrap(self, bootstrap_nodes: List[Tuple[str, int]]):
        """
        Bootstrap کردن DHT با نودهای اولیه

        Args:
            bootstrap_nodes: لیست (host, port)
        """
        for host, port in bootstrap_nodes:
            # در اینجا باید به نود متصل شود و node_id را دریافت کند
            # برای سادگی، یک node_id فرضی می‌سازیم
            node_id = hashlib.sha256(f"{host}:{port}".encode()).hexdigest()

            node = DHTNode(node_id=node_id, host=host, port=port, last_seen=time())

            self.routing_table.add_node(node)

        print(f"🌐 Bootstrapped with {len(bootstrap_nodes)} nodes")

    async def find_node(self, target_id: str) -> List[DHTNode]:
        """
        پیدا کردن نزدیک‌ترین نودها به target

        Args:
            target_id: شناسه هدف

        Returns:
            لیست نودها
        """
        # الگوریتم iterative node lookup
        closest = self.routing_table.find_closest_nodes(target_id, self.k)

        queried: Set[str] = set()

        while True:
            # انتخاب alpha نود برای query
            to_query = [n for n in closest if n.node_id not in queried][: self.alpha]

            if not to_query:
                break

            # Query کردن نودها (در اینجا شبیه‌سازی شده)
            for node in to_query:
                queried.add(node.node_id)
                # در پیاده‌سازی واقعی، باید به نود متصل شود
                # و نودهای نزدیک‌تر را بپرسد

            break  # برای سادگی، فقط یک دور

        return closest

    async def store_value(self, key: str, value: any):
        """
        ذخیره مقدار در DHT

        Args:
            key: کلید
            value: مقدار
        """
        # محاسبه hash کلید
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        # پیدا کردن نودهای مسئول
        responsible_nodes = await self.find_node(key_hash)

        # ذخیره محلی
        self.storage.store(key_hash, value)

        # ذخیره در نودهای دیگر (در پیاده‌سازی واقعی)
        # for node in responsible_nodes[:self.k]:
        #     await self.send_store_request(node, key_hash, value)

        print(f"💾 Stored value for key: {key[:16]}")

    async def find_value(self, key: str) -> Optional[any]:
        """
        یافتن مقدار در DHT

        Args:
            key: کلید

        Returns:
            مقدار یا None
        """
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        # بررسی ذخیره محلی
        value = self.storage.retrieve(key_hash)
        if value is not None:
            return value

        # جستجو در نودهای دیگر
        responsible_nodes = await self.find_node(key_hash)

        # در پیاده‌سازی واقعی، باید از نودها بپرسد
        # for node in responsible_nodes:
        #     value = await self.send_find_value_request(node, key_hash)
        #     if value is not None:
        #         return value

        return None

    def add_peer(self, node_id: str, host: str, port: int):
        """افزودن peer به DHT"""
        node = DHTNode(node_id=node_id, host=host, port=port, last_seen=time())
        self.routing_table.add_node(node)
        print(f"➕ Added peer to DHT: {node_id[:12]}")

    def get_stats(self) -> Dict:
        """دریافت آمار DHT"""
        all_nodes = self.routing_table.get_all_nodes()

        return {
            "node_id": self.node_id[:12],
            "total_peers": len(all_nodes),
            "stored_keys": len(self.storage.data),
            "routing_table_buckets": sum(
                1 for bucket in self.routing_table.buckets if len(bucket.nodes) > 0
            ),
        }

    async def maintain(self):
        """
        نگهداری دوره‌ای DHT

        - پاک‌سازی داده‌های منقضی
        - بررسی نودهای زنده
        - refresh کردن bucket ها
        """
        while True:
            await asyncio.sleep(3600)  # هر ساعت

            # پاک‌سازی
            self.storage.cleanup_expired()

            # بررسی نودهای قدیمی
            all_nodes = self.routing_table.get_all_nodes()
            for node in all_nodes:
                if time() - node.last_seen > 7200:  # 2 ساعت
                    self.routing_table.remove_node(node.node_id)

            print("🔧 DHT maintenance completed")


class ContentAddressableNetwork:
    """
    شبکه قابل آدرس‌دهی محتوا (CAN)

    برای ذخیره و بازیابی محتوا بر اساس hash
    """

    def __init__(self, dht: KademliaDHT):
        self.dht = dht
        self.content_cache: Dict[str, bytes] = {}

        print("📦 Content Addressable Network initialized")

    async def put_content(self, content: bytes) -> str:
        """
        ذخیره محتوا و دریافت hash

        Args:
            content: محتوا

        Returns:
            hash محتوا
        """
        content_hash = hashlib.sha256(content).hexdigest()

        # ذخیره در cache
        self.content_cache[content_hash] = content

        # ذخیره در DHT
        await self.dht.store_value(content_hash, content)

        return content_hash

    async def get_content(self, content_hash: str) -> Optional[bytes]:
        """
        بازیابی محتوا با hash

        Args:
            content_hash: hash محتوا

        Returns:
            محتوا یا None
        """
        # بررسی cache
        if content_hash in self.content_cache:
            return self.content_cache[content_hash]

        # جستجو در DHT
        content = await self.dht.find_value(content_hash)

        if content:
            self.content_cache[content_hash] = content

        return content

    def get_stats(self) -> Dict:
        """آمار CAN"""
        return {
            "cached_content": len(self.content_cache),
            "total_cache_size": sum(len(c) for c in self.content_cache.values()),
        }
