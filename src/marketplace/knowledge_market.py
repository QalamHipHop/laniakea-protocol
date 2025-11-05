"""
NFT Knowledge Marketplace - بازار NFT برای دانش
تبدیل دانش، کشفیات و راه‌حل‌ها به NFT های قابل معامله
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class KnowledgeType(str, Enum):
    """انواع دانش"""

    SCIENTIFIC = "scientific"
    PHILOSOPHICAL = "philosophical"
    MATHEMATICAL = "mathematical"
    ARTISTIC = "artistic"
    TECHNOLOGICAL = "technological"
    DISCOVERY = "discovery"


class KnowledgeAsset(BaseModel):
    """متادیتای NFT"""

    name: str
    description: str
    knowledge_type: KnowledgeType
    creator: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    attributes: Dict[str, Any] = Field(default_factory=dict)
    external_url: Optional[str] = None
    image_url: Optional[str] = None

    # ویژگی‌های خاص Laniakea
    knowledge_value: float = 0.0
    computation_value: float = 0.0
    originality_score: float = 0.0
    consciousness_level: float = 0.0

    # امتیاز کیفیت
    quality_score: float = 0.0
    peer_reviews: int = 0
    citations: int = 0


class KnowledgeAssetToken(BaseModel):
    """NFT دانش"""

    token_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metadata: KnowledgeAsset
    content_hash: str  # هش محتوای دانش
    owner: str
    creator: str
    minted_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    # تاریخچه مالکیت
    ownership_history: List[Dict[str, str]] = Field(default_factory=list)

    # قیمت و معاملات
    current_price: float = 0.0
    last_sale_price: Optional[float] = None
    for_sale: bool = False

    # آمار
    views: int = 0
    likes: int = 0
    downloads: int = 0

    def transfer(self, new_owner: str, price: Optional[float] = None):
        """انتقال مالکیت"""
        self.ownership_history.append(
            {
                "from": self.owner,
                "to": new_owner,
                "timestamp": datetime.now().isoformat(),
                "price": price,
            }
        )

        self.owner = new_owner
        if price is not None:
            self.last_sale_price = price
            self.for_sale = False


class KnowledgeMarketplace:
    """بازار NFT های دانش"""

    def __init__(self):
        self.nfts: Dict[str, KnowledgeAssetToken] = {}
        self.listings: Dict[str, Dict[str, Any]] = {}  # NFT های در حال فروش
        self.collections: Dict[str, List[str]] = {}  # کلکسیون‌های کاربران
        self.offers: Dict[str, List[Dict[str, Any]]] = {}  # پیشنهادات خرید

    def mint_nft(self, content: str, metadata: KnowledgeAsset, creator: str) -> KnowledgeAssetToken:
        """ضرب NFT جدید"""

        # محاسبه هش محتوا
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # محاسبه امتیاز کیفیت
        quality_score = self._calculate_quality_score(metadata)
        metadata.quality_score = quality_score

        # ایجاد NFT
        nft = KnowledgeAssetToken(
            metadata=metadata, content_hash=content_hash, owner=creator, creator=creator
        )

        # ذخیره
        self.nfts[nft.token_id] = nft

        # افزودن به کلکسیون کاربر
        if creator not in self.collections:
            self.collections[creator] = []
        self.collections[creator].append(nft.token_id)

        return nft

    def _calculate_quality_score(self, metadata: KnowledgeAsset) -> float:
        """محاسبه امتیاز کیفیت"""
        score = 0.0

        # بر اساس ارزش‌های چند بُعدی
        score += metadata.knowledge_value * 0.3
        score += metadata.computation_value * 0.2
        score += metadata.originality_score * 0.3
        score += metadata.consciousness_level * 0.2

        # نرمال‌سازی
        return min(score / 100, 1.0)

    def list_for_sale(
        self,
        token_id: str,
        price: float,
        seller: str,
        auction: bool = False,
        auction_duration_hours: int = 24,
    ) -> bool:
        """لیست کردن NFT برای فروش"""

        if token_id not in self.nfts:
            return False

        nft = self.nfts[token_id]

        # بررسی مالکیت
        if nft.owner != seller:
            return False

        # ایجاد لیست
        listing = {
            "token_id": token_id,
            "seller": seller,
            "price": price,
            "auction": auction,
            "listed_at": datetime.now().isoformat(),
            "status": "active",
        }

        if auction:
            listing["auction_end"] = datetime.now().timestamp() + (auction_duration_hours * 3600)
            listing["highest_bid"] = 0.0
            listing["highest_bidder"] = None

        self.listings[token_id] = listing
        nft.for_sale = True
        nft.current_price = price

        return True

    def buy_nft(self, token_id: str, buyer: str, payment: float) -> bool:
        """خرید NFT"""

        if token_id not in self.listings:
            return False

        listing = self.listings[token_id]

        # بررسی قیمت
        if payment < listing["price"]:
            return False

        nft = self.nfts[token_id]
        seller = listing["seller"]

        # انتقال مالکیت
        nft.transfer(buyer, payment)

        # حذف از لیست فروش
        del self.listings[token_id]

        # به‌روزرسانی کلکسیون‌ها
        if seller in self.collections:
            self.collections[seller].remove(token_id)

        if buyer not in self.collections:
            self.collections[buyer] = []
        self.collections[buyer].append(token_id)

        return True

    def place_bid(self, token_id: str, bidder: str, amount: float) -> bool:
        """ثبت پیشنهاد در حراج"""

        if token_id not in self.listings:
            return False

        listing = self.listings[token_id]

        if not listing.get("auction"):
            return False

        # بررسی زمان حراج
        if datetime.now().timestamp() > listing["auction_end"]:
            return False

        # بررسی مبلغ پیشنهاد
        if amount <= listing.get("highest_bid", 0):
            return False

        # ثبت پیشنهاد
        listing["highest_bid"] = amount
        listing["highest_bidder"] = bidder

        return True

    def finalize_auction(self, token_id: str) -> Optional[Dict[str, Any]]:
        """نهایی کردن حراج"""

        if token_id not in self.listings:
            return None

        listing = self.listings[token_id]

        if not listing.get("auction"):
            return None

        # بررسی زمان
        if datetime.now().timestamp() < listing["auction_end"]:
            return None

        winner = listing.get("highest_bidder")
        winning_bid = listing.get("highest_bid", 0)

        if winner and winning_bid > 0:
            # انتقال به برنده
            success = self.buy_nft(token_id, winner, winning_bid)

            if success:
                return {"winner": winner, "amount": winning_bid, "token_id": token_id}

        # حراج بدون برنده
        del self.listings[token_id]
        self.nfts[token_id].for_sale = False

        return None

    def make_offer(self, token_id: str, buyer: str, amount: float, expiry_hours: int = 24) -> str:
        """ثبت پیشنهاد خرید"""

        if token_id not in self.nfts:
            return ""

        offer_id = str(uuid.uuid4())

        offer = {
            "offer_id": offer_id,
            "token_id": token_id,
            "buyer": buyer,
            "amount": amount,
            "created_at": datetime.now().isoformat(),
            "expires_at": datetime.now().timestamp() + (expiry_hours * 3600),
            "status": "pending",
        }

        if token_id not in self.offers:
            self.offers[token_id] = []

        self.offers[token_id].append(offer)

        return offer_id

    def accept_offer(self, token_id: str, offer_id: str, seller: str) -> bool:
        """پذیرش پیشنهاد خرید"""

        if token_id not in self.offers:
            return False

        # پیدا کردن پیشنهاد
        offer = None
        for o in self.offers[token_id]:
            if o["offer_id"] == offer_id:
                offer = o
                break

        if not offer:
            return False

        # بررسی انقضا
        if datetime.now().timestamp() > offer["expires_at"]:
            offer["status"] = "expired"
            return False

        # بررسی مالکیت
        nft = self.nfts[token_id]
        if nft.owner != seller:
            return False

        # انجام معامله
        success = self.buy_nft(token_id, offer["buyer"], offer["amount"])

        if success:
            offer["status"] = "accepted"
            return True

        return False

    def get_trending(self, limit: int = 10) -> List[KnowledgeAssetToken]:
        """دریافت NFT های ترند"""

        # مرتب‌سازی بر اساس ترکیبی از views, likes و quality
        sorted_nfts = sorted(
            self.nfts.values(),
            key=lambda n: (n.views * 0.3 + n.likes * 0.4 + n.metadata.quality_score * 100 * 0.3),
            reverse=True,
        )

        return sorted_nfts[:limit]

    def get_collection(self, owner: str) -> List[KnowledgeAssetToken]:
        """دریافت کلکسیون یک کاربر"""

        if owner not in self.collections:
            return []

        return [
            self.nfts[token_id] for token_id in self.collections[owner] if token_id in self.nfts
        ]

    def search(
        self,
        query: str = "",
        knowledge_type: Optional[KnowledgeType] = None,
        min_quality: float = 0.0,
        max_price: Optional[float] = None,
    ) -> List[KnowledgeAssetToken]:
        """جستجو در NFT ها"""

        results = []

        for nft in self.nfts.values():
            # فیلتر نوع
            if knowledge_type and nft.metadata.knowledge_type != knowledge_type:
                continue

            # فیلتر کیفیت
            if nft.metadata.quality_score < min_quality:
                continue

            # فیلتر قیمت
            if max_price and nft.for_sale and nft.current_price > max_price:
                continue

            # جستجوی متنی
            if query:
                search_text = f"{nft.metadata.name} {nft.metadata.description}".lower()
                if query.lower() not in search_text:
                    continue

            results.append(nft)

        return results

    def get_stats(self) -> Dict[str, Any]:
        """آمار کلی بازار"""

        total_volume = sum(nft.last_sale_price or 0 for nft in self.nfts.values())

        avg_price = total_volume / len(self.nfts) if self.nfts else 0

        return {
            "total_nfts": len(self.nfts),
            "total_owners": len(self.collections),
            "active_listings": len(self.listings),
            "total_volume": total_volume,
            "average_price": avg_price,
            "total_views": sum(nft.views for nft in self.nfts.values()),
            "total_likes": sum(nft.likes for nft in self.nfts.values()),
        }


# Global marketplace instance
_marketplace = KnowledgeMarketplace()


def get_marketplace() -> KnowledgeMarketplace:
    """دریافت instance جهانی marketplace"""
    return _marketplace
