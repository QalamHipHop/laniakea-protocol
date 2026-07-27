"""
Laniakea Protocol - Knowledge Tokenization System
سیستم توکن‌سازی دانش برای تبدیل اجزای بردار دانش SCDA به توکن‌های قابل معامله
Version: 2.0.0
"""

import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import uuid
import numpy as np
from pydantic import BaseModel, Field


class KnowledgeTokenType(str, Enum):
    """انواع توکن‌های دانش"""
    
    DOMAIN_MASTERY = "domain_mastery"  # تسلط بر یک حوزه دانش
    PROBLEM_SOLUTION = "problem_solution"  # حل یک مسئله خاص
    METHODOLOGY = "methodology"  # روش‌شناسی یا الگوریتم
    INSIGHT = "insight"  # بینش یا اکتشاف
    SYNTHESIS = "synthesis"  # ترکیب دانش‌های چندگانه


class KnowledgeTokenMetadata(BaseModel):
    """متادیتای توکن دانش"""
    
    token_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    token_type: KnowledgeTokenType
    creator_scda_id: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # محتوای دانش
    domain: str  # حوزه دانش (e.g., "mathematics", "physics")
    description: str
    content_hash: str  # هش محتوای دانش
    
    # مقادیر چندبعدی
    knowledge_value: float  # ارزش دانشی [0, 1]
    originality_score: float  # امتیاز اصالت [0, 1]
    complexity_level: float  # سطح پیچیدگی [0, 1]
    applicability: float  # قابل‌کاربرد بودن [0, 1]
    
    # آمار
    views: int = 0
    uses: int = 0  # تعداد دفعاتی که توکن استفاده شده است
    citations: int = 0  # تعداد ارجاعات
    
    # قیمت‌گذاری پویا
    base_price: float = 1.0  # قیمت پایه
    current_price: float = 1.0  # قیمت فعلی
    price_history: List[Tuple[str, float]] = Field(default_factory=list)


class KnowledgeToken:
    """توکن دانش قابل معامله"""
    
    def __init__(self, metadata: KnowledgeTokenMetadata, owner_scda_id: str):
        self.metadata = metadata
        self.owner_scda_id = owner_scda_id
        self.rental_offers: List[Dict[str, Any]] = []  # پیشنهادات اجاره
        self.transfer_history: List[Dict[str, Any]] = []
    
    def update_price(self, new_price: float):
        """به‌روزرسانی قیمت توکن"""
        self.metadata.price_history.append((datetime.now().isoformat(), self.metadata.current_price))
        self.metadata.current_price = new_price
    
    def transfer_ownership(self, new_owner_scda_id: str, price: float):
        """انتقال مالکیت توکن"""
        transfer_record = {
            "from": self.owner_scda_id,
            "to": new_owner_scda_id,
            "timestamp": datetime.now().isoformat(),
            "price": price
        }
        self.transfer_history.append(transfer_record)
        self.owner_scda_id = new_owner_scda_id
        self.update_price(price)
    
    def add_rental_offer(self, renter_scda_id: str, rental_price: float, duration_days: int) -> str:
        """افزودن پیشنهاد اجاره"""
        offer_id = str(uuid.uuid4())
        offer = {
            "offer_id": offer_id,
            "renter_id": renter_scda_id,
            "rental_price": rental_price,
            "duration_days": duration_days,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        self.rental_offers.append(offer)
        return offer_id
    
    def accept_rental(self, offer_id: str) -> bool:
        """پذیرش پیشنهاد اجاره"""
        for offer in self.rental_offers:
            if offer["offer_id"] == offer_id:
                offer["status"] = "accepted"
                offer["accepted_at"] = datetime.now().isoformat()
                return True
        return False
    
    def get_valuation(self) -> float:
        """محاسبه ارزش فعلی توکن بر اساس مقادیر چندبعدی"""
        metadata = self.metadata
        
        # ترکیب وزن‌دار مقادیر
        valuation = (
            metadata.knowledge_value * 0.3 +
            metadata.originality_score * 0.25 +
            metadata.complexity_level * 0.2 +
            metadata.applicability * 0.25
        )
        
        # تأثیر استفاده و ارجاع
        usage_multiplier = 1.0 + (metadata.uses * 0.01) + (metadata.citations * 0.02)
        
        return metadata.base_price * valuation * usage_multiplier


class DynamicPricingEngine:
    """موتور قیمت‌گذاری پویا برای توکن‌های دانش"""
    
    def __init__(self):
        self.market_demand: Dict[str, float] = {}  # تقاضای بازار برای هر حوزه
        self.supply_level: Dict[str, int] = {}  # عرضه توکن‌ها در هر حوزه
    
    def calculate_market_price(self, token: KnowledgeToken) -> float:
        """محاسبه قیمت بازار بر اساس تقاضا و عرضه"""
        domain = token.metadata.domain
        
        # دریافت تقاضا و عرضه
        demand = self.market_demand.get(domain, 1.0)
        supply = self.supply_level.get(domain, 1)
        
        # فرمول قیمت: قیمت_پایه × (تقاضا / عرضه)
        supply_factor = max(1, supply)
        market_price = token.metadata.base_price * (demand / supply_factor)
        
        # محدود کردن نوسانات قیمت
        min_price = token.metadata.base_price * 0.5
        max_price = token.metadata.base_price * 3.0
        
        return np.clip(market_price, min_price, max_price)
    
    def update_market_demand(self, domain: str, demand_change: float):
        """به‌روزرسانی تقاضای بازار"""
        current_demand = self.market_demand.get(domain, 1.0)
        self.market_demand[domain] = max(0.1, current_demand + demand_change)
    
    def update_supply(self, domain: str, supply_change: int):
        """به‌روزرسانی عرضه"""
        current_supply = self.supply_level.get(domain, 0)
        self.supply_level[domain] = max(0, current_supply + supply_change)


class KnowledgeTokenMarketplace:
    """بازار توکن‌های دانش"""
    
    def __init__(self):
        self.tokens: Dict[str, KnowledgeToken] = {}
        self.pricing_engine = DynamicPricingEngine()
        self.listings: Dict[str, Dict[str, Any]] = {}  # توکن‌های در حال فروش
        self.rental_contracts: List[Dict[str, Any]] = []  # قراردادهای اجاره
    
    def tokenize_knowledge(self, scda_id: str, domain: str, knowledge_data: Dict[str, Any]) -> KnowledgeToken:
        """تبدیل دانش SCDA به توکن"""
        
        # محاسبه هش محتوا
        content_str = json.dumps(knowledge_data, sort_keys=True)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()
        
        # ایجاد متادیتای توکن
        metadata = KnowledgeTokenMetadata(
            token_type=KnowledgeTokenType.DOMAIN_MASTERY,
            creator_scda_id=scda_id,
            domain=domain,
            description=knowledge_data.get("description", f"Knowledge in {domain}"),
            content_hash=content_hash,
            knowledge_value=knowledge_data.get("knowledge_value", 0.5),
            originality_score=knowledge_data.get("originality_score", 0.5),
            complexity_level=knowledge_data.get("complexity_level", 0.5),
            applicability=knowledge_data.get("applicability", 0.5)
        )
        
        # ایجاد توکن
        token = KnowledgeToken(metadata, scda_id)
        
        # ذخیره توکن
        self.tokens[metadata.token_id] = token
        
        # به‌روزرسانی عرضه
        self.pricing_engine.update_supply(domain, 1)
        
        return token
    
    def list_token_for_sale(self, token_id: str, seller_scda_id: str, price: float) -> bool:
        """فهرست کردن توکن برای فروش"""
        
        if token_id not in self.tokens:
            return False
        
        token = self.tokens[token_id]
        
        # بررسی مالکیت
        if token.owner_scda_id != seller_scda_id:
            return False
        
        # ایجاد لیست
        listing = {
            "token_id": token_id,
            "seller_id": seller_scda_id,
            "price": price,
            "listed_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.listings[token_id] = listing
        token.update_price(price)
        
        return True
    
    def buy_token(self, token_id: str, buyer_scda_id: str, payment: float) -> bool:
        """خرید توکن"""
        
        if token_id not in self.listings:
            return False
        
        listing = self.listings[token_id]
        
        # بررسی قیمت
        if payment < listing["price"]:
            return False
        
        token = self.tokens[token_id]
        seller_id = listing["seller_id"]
        
        # انتقال مالکیت
        token.transfer_ownership(buyer_scda_id, payment)
        
        # حذف از لیست فروش
        del self.listings[token_id]
        
        return True
    
    def rent_token(self, token_id: str, renter_scda_id: str, rental_price: float, duration_days: int) -> Optional[str]:
        """اجاره دادن توکن"""
        
        if token_id not in self.tokens:
            return None
        
        token = self.tokens[token_id]
        
        # افزودن پیشنهاد اجاره
        offer_id = token.add_rental_offer(renter_scda_id, rental_price, duration_days)
        
        # ثبت قرارداد اجاره (اگر پذیرفته شود)
        if token.accept_rental(offer_id):
            contract = {
                "contract_id": str(uuid.uuid4()),
                "token_id": token_id,
                "owner_id": token.owner_scda_id,
                "renter_id": renter_scda_id,
                "rental_price": rental_price,
                "duration_days": duration_days,
                "start_date": datetime.now().isoformat(),
                "status": "active"
            }
            self.rental_contracts.append(contract)
            
            # افزایش استفاده
            token.metadata.uses += 1
            
            return contract["contract_id"]
        
        return None
    
    def update_dynamic_prices(self):
        """به‌روزرسانی قیمت‌های پویا برای تمام توکن‌ها"""
        for token in self.tokens.values():
            market_price = self.pricing_engine.calculate_market_price(token)
            token.update_price(market_price)
    
    def get_trending_tokens(self, limit: int = 10) -> List[KnowledgeToken]:
        """دریافت توکن‌های ترند"""
        sorted_tokens = sorted(
            self.tokens.values(),
            key=lambda t: (t.metadata.views * 0.3 + t.metadata.uses * 0.4 + t.metadata.citations * 0.3),
            reverse=True
        )
        return sorted_tokens[:limit]
    
    def search_tokens(self, domain: Optional[str] = None, min_quality: float = 0.0, 
                     max_price: Optional[float] = None) -> List[KnowledgeToken]:
        """جستجو در توکن‌های دانش"""
        results = []
        
        for token in self.tokens.values():
            # فیلتر حوزه
            if domain and token.metadata.domain != domain:
                continue
            
            # فیلتر کیفیت
            quality = token.get_valuation()
            if quality < min_quality:
                continue
            
            # فیلتر قیمت
            if max_price and token.metadata.current_price > max_price:
                continue
            
            results.append(token)
        
        return results
    
    def get_marketplace_stats(self) -> Dict[str, Any]:
        """آمار کلی بازار توکن‌های دانش"""
        
        total_value = sum(token.get_valuation() for token in self.tokens.values())
        avg_value = total_value / len(self.tokens) if self.tokens else 0
        
        return {
            "total_tokens": len(self.tokens),
            "active_listings": len(self.listings),
            "active_rentals": len([c for c in self.rental_contracts if c["status"] == "active"]),
            "total_market_value": total_value,
            "average_token_value": avg_value,
            "total_uses": sum(token.metadata.uses for token in self.tokens.values()),
            "total_citations": sum(token.metadata.citations for token in self.tokens.values())
        }


# Global marketplace instance
_knowledge_marketplace = KnowledgeTokenMarketplace()


def get_knowledge_marketplace() -> KnowledgeTokenMarketplace:
    """دریافت instance جهانی بازار توکن‌های دانش"""
    return _knowledge_marketplace
