"""
Laniakea Protocol - Decentralized Identity System
سیستم هویت غیرمتمرکز (DID)
"""

import hashlib
import json
from time import time
from typing import Dict, List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes


class CredentialType(str, Enum):
    """نوع اعتبارنامه"""
    EDUCATION = "education"
    SKILL = "skill"
    ACHIEVEMENT = "achievement"
    REPUTATION = "reputation"
    CONTRIBUTION = "contribution"


class VerificationStatus(str, Enum):
    """وضعیت تأیید"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    REVOKED = "revoked"


class Credential(BaseModel):
    """اعتبارنامه"""
    id: str
    holder_did: str  # DID دارنده
    issuer_did: str  # DID صادرکننده
    credential_type: CredentialType
    
    # محتوا
    title: str
    description: str
    data: Dict = Field(default_factory=dict)
    
    # تأیید
    status: VerificationStatus = VerificationStatus.PENDING
    verifiers: List[str] = Field(default_factory=list)
    
    # زمان
    issued_at: float
    expires_at: Optional[float] = None
    
    # امضا
    signature: Optional[str] = None
    proof: Optional[Dict] = None


class DIDDocument(BaseModel):
    """سند هویت غیرمتمرکز"""
    did: str  # Decentralized Identifier
    
    # کلیدهای عمومی
    public_keys: List[Dict] = Field(default_factory=list)
    
    # روش‌های احراز هویت
    authentication: List[str] = Field(default_factory=list)
    
    # سرویس‌ها
    services: List[Dict] = Field(default_factory=list)
    
    # اعتبارنامه‌ها
    credentials: List[str] = Field(default_factory=list)
    
    # متادیتا
    created: float
    updated: float
    
    # اعتماد
    reputation_score: float = 0.0
    trust_network: List[str] = Field(default_factory=list)


class IdentityManager:
    """
    مدیر هویت
    
    ایجاد و مدیریت هویت‌های غیرمتمرکز
    """
    
    def __init__(self):
        self.identities: Dict[str, DIDDocument] = {}
        self.credentials: Dict[str, Credential] = {}
        
        # شبکه اعتماد
        self.trust_graph: Dict[str, Set[str]] = {}
        
        print("🆔 Identity Manager initialized")
    
    def create_identity(self, node_id: str, public_key: str) -> DIDDocument:
        """
        ایجاد هویت جدید
        
        Args:
            node_id: شناسه نود
            public_key: کلید عمومی
        
        Returns:
            سند DID
        """
        # ایجاد DID
        did = f"did:laniakea:{node_id}"
        
        # ایجاد سند
        doc = DIDDocument(
            did=did,
            public_keys=[{
                "id": f"{did}#key-1",
                "type": "EcdsaSecp256r1VerificationKey2019",
                "publicKeyPem": public_key
            }],
            authentication=[f"{did}#key-1"],
            created=time(),
            updated=time()
        )
        
        self.identities[did] = doc
        self.trust_graph[did] = set()
        
        print(f"✨ Identity created: {did}")
        return doc
    
    def issue_credential(
        self,
        issuer_did: str,
        holder_did: str,
        credential_type: CredentialType,
        title: str,
        description: str,
        data: Dict = None,
        expires_in: Optional[float] = None
    ) -> Credential:
        """
        صدور اعتبارنامه
        
        Args:
            issuer_did: DID صادرکننده
            holder_did: DID دارنده
            credential_type: نوع
            title: عنوان
            description: توضیحات
            data: داده
            expires_in: زمان انقضا (ثانیه)
        
        Returns:
            اعتبارنامه
        """
        # ایجاد شناسه
        cred_id = hashlib.sha256(
            f"{issuer_did}{holder_did}{title}{time()}".encode()
        ).hexdigest()
        
        # ایجاد اعتبارنامه
        credential = Credential(
            id=cred_id,
            holder_did=holder_did,
            issuer_did=issuer_did,
            credential_type=credential_type,
            title=title,
            description=description,
            data=data or {},
            issued_at=time(),
            expires_at=time() + expires_in if expires_in else None
        )
        
        # ذخیره
        self.credentials[cred_id] = credential
        
        # افزودن به DID دارنده
        if holder_did in self.identities:
            self.identities[holder_did].credentials.append(cred_id)
        
        print(f"📜 Credential issued: {title} to {holder_did}")
        return credential
    
    def verify_credential(
        self,
        credential_id: str,
        verifier_did: str
    ) -> bool:
        """
        تأیید اعتبارنامه
        
        Args:
            credential_id: شناسه اعتبارنامه
            verifier_did: DID تأییدکننده
        
        Returns:
            موفقیت
        """
        if credential_id not in self.credentials:
            return False
        
        credential = self.credentials[credential_id]
        
        # افزودن تأییدکننده
        if verifier_did not in credential.verifiers:
            credential.verifiers.append(verifier_did)
        
        # اگر تعداد کافی تأییدکننده داشت
        if len(credential.verifiers) >= 3:
            credential.status = VerificationStatus.VERIFIED
            
            # افزایش reputation
            if credential.holder_did in self.identities:
                self.identities[credential.holder_did].reputation_score += 10.0
        
        print(f"✅ Credential verified by {verifier_did}")
        return True
    
    def revoke_credential(
        self,
        credential_id: str,
        issuer_did: str
    ) -> bool:
        """لغو اعتبارنامه"""
        if credential_id not in self.credentials:
            return False
        
        credential = self.credentials[credential_id]
        
        if credential.issuer_did != issuer_did:
            return False
        
        credential.status = VerificationStatus.REVOKED
        
        print(f"🚫 Credential revoked: {credential_id[:12]}")
        return True
    
    def add_trust(self, from_did: str, to_did: str):
        """افزودن رابطه اعتماد"""
        if from_did not in self.trust_graph:
            self.trust_graph[from_did] = set()
        
        self.trust_graph[from_did].add(to_did)
        
        # افزودن به trust network
        if from_did in self.identities:
            if to_did not in self.identities[from_did].trust_network:
                self.identities[from_did].trust_network.append(to_did)
        
        print(f"🤝 Trust added: {from_did} -> {to_did}")
    
    def calculate_trust_score(self, did: str, target_did: str) -> float:
        """
        محاسبه امتیاز اعتماد
        
        از الگوریتم PageRank-like استفاده می‌کند
        
        Args:
            did: DID پرس‌وجوکننده
            target_did: DID هدف
        
        Returns:
            امتیاز اعتماد (0-1)
        """
        if did == target_did:
            return 1.0
        
        # اعتماد مستقیم
        if did in self.trust_graph and target_did in self.trust_graph[did]:
            return 0.9
        
        # اعتماد غیرمستقیم (یک درجه)
        if did in self.trust_graph:
            for intermediate in self.trust_graph[did]:
                if intermediate in self.trust_graph and target_did in self.trust_graph[intermediate]:
                    return 0.7
        
        # بر اساس reputation
        if target_did in self.identities:
            rep = self.identities[target_did].reputation_score
            return min(rep / 100.0, 0.5)
        
        return 0.0
    
    def get_identity(self, did: str) -> Optional[DIDDocument]:
        """دریافت سند هویت"""
        return self.identities.get(did)
    
    def get_credentials(self, did: str) -> List[Credential]:
        """دریافت اعتبارنامه‌های یک هویت"""
        if did not in self.identities:
            return []
        
        cred_ids = self.identities[did].credentials
        return [self.credentials[cid] for cid in cred_ids if cid in self.credentials]
    
    def search_identities(
        self,
        credential_type: Optional[CredentialType] = None,
        min_reputation: float = 0.0
    ) -> List[DIDDocument]:
        """جستجوی هویت‌ها"""
        results = []
        
        for did, doc in self.identities.items():
            # فیلتر reputation
            if doc.reputation_score < min_reputation:
                continue
            
            # فیلتر نوع اعتبارنامه
            if credential_type:
                has_type = False
                for cred_id in doc.credentials:
                    if cred_id in self.credentials:
                        if self.credentials[cred_id].credential_type == credential_type:
                            has_type = True
                            break
                if not has_type:
                    continue
            
            results.append(doc)
        
        # مرتب‌سازی بر اساس reputation
        results.sort(key=lambda d: d.reputation_score, reverse=True)
        
        return results
    
    def get_stats(self) -> Dict:
        """آمار سیستم هویت"""
        return {
            "total_identities": len(self.identities),
            "total_credentials": len(self.credentials),
            "verified_credentials": len([c for c in self.credentials.values() if c.status == VerificationStatus.VERIFIED]),
            "trust_relationships": sum(len(trusts) for trusts in self.trust_graph.values()),
            "average_reputation": sum(d.reputation_score for d in self.identities.values()) / len(self.identities) if self.identities else 0
        }


class ReputationSystem:
    """
    سیستم شهرت و اعتبار
    
    محاسبه و مدیریت شهرت کاربران
    """
    
    def __init__(self, identity_manager: IdentityManager):
        self.identity_manager = identity_manager
        
        # تاریخچه فعالیت
        self.activity_history: Dict[str, List[Dict]] = {}
        
        print("⭐ Reputation System initialized")
    
    def record_activity(
        self,
        did: str,
        activity_type: str,
        value: float,
        metadata: Dict = None
    ):
        """
        ثبت فعالیت
        
        Args:
            did: DID کاربر
            activity_type: نوع فعالیت
            value: ارزش
            metadata: متادیتا
        """
        if did not in self.activity_history:
            self.activity_history[did] = []
        
        activity = {
            "type": activity_type,
            "value": value,
            "metadata": metadata or {},
            "timestamp": time()
        }
        
        self.activity_history[did].append(activity)
        
        # به‌روزرسانی reputation
        self._update_reputation(did)
    
    def _update_reputation(self, did: str):
        """به‌روزرسانی امتیاز شهرت"""
        if did not in self.identity_manager.identities:
            return
        
        if did not in self.activity_history:
            return
        
        # محاسبه بر اساس فعالیت‌ها
        activities = self.activity_history[did]
        
        # وزن‌دهی زمانی (فعالیت‌های جدیدتر وزن بیشتر)
        now = time()
        weighted_sum = 0.0
        total_weight = 0.0
        
        for activity in activities:
            age = now - activity["timestamp"]
            weight = 1.0 / (1.0 + age / (30 * 24 * 3600))  # کاهش با زمان
            weighted_sum += activity["value"] * weight
            total_weight += weight
        
        if total_weight > 0:
            reputation = weighted_sum / total_weight
            self.identity_manager.identities[did].reputation_score = reputation
    
    def get_leaderboard(self, limit: int = 10) -> List[Tuple[str, float]]:
        """
        لیست برترین‌ها
        
        Args:
            limit: تعداد
        
        Returns:
            لیست (DID, reputation)
        """
        identities = self.identity_manager.identities.values()
        sorted_identities = sorted(
            identities,
            key=lambda d: d.reputation_score,
            reverse=True
        )
        
        return [(d.did, d.reputation_score) for d in sorted_identities[:limit]]
    
    def get_reputation_breakdown(self, did: str) -> Dict:
        """تجزیه و تحلیل شهرت"""
        if did not in self.activity_history:
            return {}
        
        activities = self.activity_history[did]
        
        # گروه‌بندی بر اساس نوع
        by_type = {}
        for activity in activities:
            activity_type = activity["type"]
            if activity_type not in by_type:
                by_type[activity_type] = []
            by_type[activity_type].append(activity["value"])
        
        # محاسبه آمار
        breakdown = {}
        for activity_type, values in by_type.items():
            breakdown[activity_type] = {
                "count": len(values),
                "total": sum(values),
                "average": sum(values) / len(values)
            }
        
        return breakdown
