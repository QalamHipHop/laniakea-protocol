"""
Laniakea Protocol - Core Models
مدل‌های پایه برای سیستم بلاک‌چین چند بُعدی
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Set
from enum import Enum


class ValueDimension(str, Enum):
    """ابعاد ارزشی در پروتوکل Laniakea"""
    KNOWLEDGE = "knowledge"  # ارزش دانشی
    COMPUTATION = "computation"  # ارزش محاسباتی
    ORIGINALITY = "originality"  # ارزش خلاقیت
    CONSCIOUSNESS = "consciousness"  # ارزش آگاهی
    ENVIRONMENTAL = "environmental"  # تأثیر محیطی
    HEALTH = "health"  # تأثیر سلامتی


class ValueVector(BaseModel):
    """
    بردار ارزش چند بُعدی
    هر بُعد نشان‌دهنده نوعی از ارزش در کیهان Laniakea است
    """
    knowledge: float = Field(default=0.0, ge=0.0, description="ارزش دانشی")
    computation: float = Field(default=0.0, ge=0.0, description="ارزش محاسباتی")
    originality: float = Field(default=0.0, ge=0.0, description="ارزش خلاقیت")
    consciousness: float = Field(default=0.0, ge=0.0, description="ارزش آگاهی")
    environmental: float = Field(default=0.0, description="تأثیر محیطی (می‌تواند منفی باشد)")
    health: float = Field(default=0.0, description="تأثیر سلامتی")

    def total_value(self) -> float:
        """محاسبه ارزش کل"""
        return (
            self.knowledge +
            self.computation +
            self.originality +
            self.consciousness +
            max(0, self.environmental) +  # فقط تأثیرات مثبت محیطی
            max(0, self.health)  # فقط تأثیرات مثبت سلامتی
        )

    def to_dict(self) -> Dict[str, float]:
        """تبدیل به دیکشنری"""
        return {
            "knowledge": self.knowledge,
            "computation": self.computation,
            "originality": self.originality,
            "consciousness": self.consciousness,
            "environmental": self.environmental,
            "health": self.health
        }


class ProblemCategory(str, Enum):
    """دسته‌بندی مسائل"""
    SCIENTIFIC = "scientific"  # مسائل علمی
    PHILOSOPHICAL = "philosophical"  # مسائل فلسفی
    MATHEMATICAL = "mathematical"  # مسائل ریاضی
    COMPUTATIONAL = "computational"  # مسائل محاسباتی
    ARTISTIC = "artistic"  # مسائل هنری
    COSMIC = "cosmic"  # مسائل کیهانی


class Task(BaseModel):
    """
    تسک یا مسئله‌ای که باید حل شود
    می‌تواند مسئله علمی، فلسفی، ریاضی یا هر چیز دیگری باشد
    """
    id: str = Field(..., description="شناسه یکتا")
    title: str = Field(..., description="عنوان تسک")
    description: str = Field(..., description="توضیحات کامل")
    category: ProblemCategory = Field(..., description="دسته‌بندی مسئله")
    author_id: str = Field(..., description="شناسه ایجادکننده")
    timestamp: float = Field(..., description="زمان ایجاد")
    difficulty: float = Field(default=1.0, ge=0.1, le=10.0, description="سطح دشواری (0.1-10)")
    required_dimensions: List[ValueDimension] = Field(
        default_factory=list,
        description="ابعاد ارزشی مورد نیاز برای حل"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="متادیتای اضافی")


class Solution(BaseModel):
    """
    راه‌حل برای یک تسک
    شامل محتوا و ارزش‌گذاری چند بُعدی
    """
    id: str = Field(..., description="شناسه یکتا")
    task_id: str = Field(..., description="شناسه تسک مرتبط")
    solver_id: str = Field(..., description="شناسه حل‌کننده")
    content: str = Field(..., description="محتوای راه‌حل")
    value_vector: ValueVector = Field(..., description="بردار ارزش راه‌حل")
    timestamp: float = Field(..., description="زمان ارائه")
    proof_of_work: Optional[str] = Field(default=None, description="اثبات کار انجام شده")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="متادیتای اضافی")


class Transaction(BaseModel):
    """
    تراکنش انتقال ارزش
    می‌تواند ارزش ساده یا چند بُعدی منتقل کند
    """
    id: str = Field(..., description="شناسه یکتا")
    sender: str = Field(..., description="فرستنده")
    recipient: str = Field(..., description="گیرنده")
    amount: float = Field(..., ge=0.0, description="مقدار ارزش")
    dimension: ValueDimension = Field(
        default=ValueDimension.KNOWLEDGE,
        description="بُعد ارزشی"
    )
    timestamp: float = Field(..., description="زمان تراکنش")
    signature: Optional[str] = Field(default=None, description="امضای دیجیتال")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="متادیتای اضافی")


class KnowledgeBlock(BaseModel):
    """
    بلاک دانشی در زنجیره Laniakea
    هر بلاک می‌تواند حاوی راه‌حل‌ها، تراکنش‌ها و دانش جدید باشد
    """
    index: int = Field(..., ge=0, description="شماره بلاک")
    timestamp: float = Field(..., description="زمان ایجاد")
    transactions: List[Transaction] = Field(default_factory=list, description="لیست تراکنش‌ها")
    solution: Optional[Solution] = Field(default=None, description="راه‌حل گنجانده شده")
    author_id: str = Field(..., description="شناسه سازنده بلاک")
    previous_hash: str = Field(..., description="هش بلاک قبلی")
    signature: str = Field(..., description="امضای دیجیتال بلاک")
    nonce: int = Field(default=0, description="nonce برای proof of work")
    difficulty: float = Field(default=1.0, description="سطح دشواری")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="متادیتای اضافی")


class NodeSpecialty(str, Enum):
    """تخصص‌های نود"""
    MINING = "mining"  # استخراج بلاک
    SOLVING = "solving"  # حل مسائل
    VALIDATION = "validation"  # اعتبارسنجی
    ORACLE = "oracle"  # اوراکل
    SIMULATION = "simulation"  # شبیه‌سازی
    AI_INFERENCE = "ai_inference"  # استنتاج AI


class NodeInfo(BaseModel):
    """اطلاعات یک نود در شبکه"""
    node_id: str = Field(..., description="شناسه یکتا")
    host: str = Field(..., description="آدرس هاست")
    p2p_port: int = Field(..., description="پورت P2P")
    api_port: int = Field(..., description="پورت API")
    specialties: Set[NodeSpecialty] = Field(
        default_factory=set,
        description="تخصص‌های نود"
    )
    reputation: float = Field(default=0.0, ge=0.0, description="اعتبار نود")
    total_value_created: ValueVector = Field(
        default_factory=ValueVector,
        description="مجموع ارزش ایجاد شده"
    )


class P2PMessage(BaseModel):
    """پیام P2P بین نودها"""
    type: str = Field(..., description="نوع پیام")
    payload: Dict[str, Any] = Field(..., description="محتوای پیام")
    sender_id: Optional[str] = Field(default=None, description="شناسه فرستنده")
    timestamp: float = Field(..., description="زمان ارسال")


class ProposalType(str, Enum):
    """انواع پیشنهادات حکمرانی"""
    PROTOCOL_UPGRADE = "protocol_upgrade"
    PARAMETER_CHANGE = "parameter_change"
    NEW_FEATURE = "new_feature"
    RULE_MODIFICATION = "rule_modification"


class Proposal(BaseModel):
    """پیشنهاد تغییر در پروتوکل"""
    id: str = Field(..., description="شناسه یکتا")
    title: str = Field(..., description="عنوان پیشنهاد")
    description: str = Field(..., description="توضیحات کامل")
    type: ProposalType = Field(..., description="نوع پیشنهاد")
    proposer_id: str = Field(..., description="شناسه پیشنهاددهنده")
    code: Optional[str] = Field(default=None, description="کد اجرایی (در صورت نیاز)")
    votes_for: float = Field(default=0.0, description="آرای موافق")
    votes_against: float = Field(default=0.0, description="آرای مخالف")
    status: str = Field(default="pending", description="وضعیت پیشنهاد")
    created_at: float = Field(..., description="زمان ایجاد")
    expires_at: float = Field(..., description="زمان انقضا")


class CosmicCell(BaseModel):
    """
    تک‌سلولی کیهانی - واحد پایه شبیه‌سازی
    """
    id: str = Field(..., description="شناسه یکتا")
    generation: int = Field(default=0, ge=0, description="نسل سلول")
    energy: float = Field(default=100.0, ge=0.0, description="انرژی سلول")
    knowledge: float = Field(default=0.0, ge=0.0, description="دانش انباشته")
    position: tuple[float, float, float] = Field(
        default=(0.0, 0.0, 0.0),
        description="موقعیت در فضای سه‌بعدی"
    )
    velocity: tuple[float, float, float] = Field(
        default=(0.0, 0.0, 0.0),
        description="سرعت حرکت"
    )
    genome: Dict[str, Any] = Field(
        default_factory=dict,
        description="ژنوم سلول (ویژگی‌های ارثی)"
    )
    state: str = Field(default="alive", description="وضعیت سلول")
