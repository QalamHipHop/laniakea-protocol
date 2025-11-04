"""
Laniakea Protocol - Decentralized Autonomous Organization (DAO)
سیستم حکمرانی خودکار غیرمتمرکز
"""

import hashlib
from time import time
from typing import Dict, List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field


class ProposalType(str, Enum):
    """انواع پیشنهادات"""
    PROTOCOL_UPGRADE = "protocol_upgrade"
    PARAMETER_CHANGE = "parameter_change"
    TREASURY_SPEND = "treasury_spend"
    NODE_REMOVAL = "node_removal"
    EMERGENCY_ACTION = "emergency_action"


class ProposalStatus(str, Enum):
    """وضعیت پیشنهاد"""
    DRAFT = "draft"
    ACTIVE = "active"
    PASSED = "passed"
    REJECTED = "rejected"
    EXECUTED = "executed"
    EXPIRED = "expired"


class Vote(BaseModel):
    """رأی"""
    voter_id: str
    proposal_id: str
    vote: bool  # True = موافق, False = مخالف
    weight: float  # وزن رأی بر اساس stake
    timestamp: float
    reason: Optional[str] = None


class Proposal(BaseModel):
    """پیشنهاد"""
    id: str
    title: str
    description: str
    proposer_id: str
    proposal_type: ProposalType
    
    # محتوای پیشنهاد
    target: str  # هدف تغییر
    action: str  # عمل مورد نظر
    parameters: Dict = Field(default_factory=dict)
    
    # زمان‌بندی
    created_at: float
    voting_starts: float
    voting_ends: float
    
    # وضعیت
    status: ProposalStatus = ProposalStatus.DRAFT
    
    # آرا
    votes_for: float = 0.0
    votes_against: float = 0.0
    total_votes: int = 0
    
    # اجرا
    executed_at: Optional[float] = None
    execution_result: Optional[str] = None


class GovernanceSystem:
    """
    سیستم حکمرانی خودکار
    
    این سیستم امکان تصمیم‌گیری جمعی را فراهم می‌کند:
    - ایجاد پیشنهادات
    - رأی‌گیری وزن‌دار
    - اجرای خودکار
    - مدیریت خزانه
    """
    
    def __init__(self):
        self.proposals: Dict[str, Proposal] = {}
        self.votes: Dict[str, List[Vote]] = {}  # proposal_id -> votes
        self.voter_stakes: Dict[str, float] = {}  # voter_id -> stake amount
        
        # تنظیمات حکمرانی
        self.quorum_percentage = 0.30  # حداقل 30% مشارکت
        self.approval_threshold = 0.60  # حداقل 60% موافق
        self.voting_period = 7 * 24 * 3600  # 7 روز
        self.execution_delay = 2 * 24 * 3600  # 2 روز تأخیر اجرا
        
        # خزانه
        self.treasury_balance = 0.0
        
        print("🏛️ Governance System initialized")
    
    def create_proposal(
        self,
        proposer_id: str,
        title: str,
        description: str,
        proposal_type: ProposalType,
        target: str,
        action: str,
        parameters: Dict = None
    ) -> Proposal:
        """
        ایجاد پیشنهاد جدید
        
        Args:
            proposer_id: شناسه پیشنهاددهنده
            title: عنوان
            description: توضیحات
            proposal_type: نوع پیشنهاد
            target: هدف
            action: عمل
            parameters: پارامترها
        
        Returns:
            پیشنهاد ایجاد شده
        """
        proposal_id = hashlib.sha256(
            f"{proposer_id}{title}{time()}".encode()
        ).hexdigest()
        
        now = time()
        
        proposal = Proposal(
            id=proposal_id,
            title=title,
            description=description,
            proposer_id=proposer_id,
            proposal_type=proposal_type,
            target=target,
            action=action,
            parameters=parameters or {},
            created_at=now,
            voting_starts=now + 3600,  # شروع رأی‌گیری بعد از 1 ساعت
            voting_ends=now + 3600 + self.voting_period,
            status=ProposalStatus.DRAFT
        )
        
        self.proposals[proposal_id] = proposal
        self.votes[proposal_id] = []
        
        print(f"📜 Proposal created: {title}")
        return proposal
    
    def activate_proposal(self, proposal_id: str) -> bool:
        """فعال‌سازی پیشنهاد برای رأی‌گیری"""
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        
        if proposal.status != ProposalStatus.DRAFT:
            return False
        
        if time() >= proposal.voting_starts:
            proposal.status = ProposalStatus.ACTIVE
            print(f"🗳️ Proposal activated: {proposal.title}")
            return True
        
        return False
    
    def cast_vote(
        self,
        voter_id: str,
        proposal_id: str,
        vote: bool,
        reason: Optional[str] = None
    ) -> bool:
        """
        ثبت رأی
        
        Args:
            voter_id: شناسه رأی‌دهنده
            proposal_id: شناسه پیشنهاد
            vote: موافق یا مخالف
            reason: دلیل
        
        Returns:
            موفقیت
        """
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        
        # بررسی وضعیت
        if proposal.status != ProposalStatus.ACTIVE:
            return False
        
        # بررسی زمان
        now = time()
        if now < proposal.voting_starts or now > proposal.voting_ends:
            return False
        
        # بررسی رأی قبلی
        for v in self.votes[proposal_id]:
            if v.voter_id == voter_id:
                return False  # قبلاً رأی داده
        
        # محاسبه وزن رأی
        stake = self.voter_stakes.get(voter_id, 1.0)
        
        # ثبت رأی
        vote_obj = Vote(
            voter_id=voter_id,
            proposal_id=proposal_id,
            vote=vote,
            weight=stake,
            timestamp=now,
            reason=reason
        )
        
        self.votes[proposal_id].append(vote_obj)
        
        # به‌روزرسانی آمار
        if vote:
            proposal.votes_for += stake
        else:
            proposal.votes_against += stake
        
        proposal.total_votes += 1
        
        print(f"✅ Vote cast: {voter_id[:12]} -> {proposal.title} ({'FOR' if vote else 'AGAINST'})")
        return True
    
    def finalize_proposal(self, proposal_id: str) -> bool:
        """
        نهایی‌سازی پیشنهاد بعد از پایان رأی‌گیری
        
        Args:
            proposal_id: شناسه پیشنهاد
        
        Returns:
            موفقیت
        """
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        
        if proposal.status != ProposalStatus.ACTIVE:
            return False
        
        # بررسی زمان
        if time() < proposal.voting_ends:
            return False
        
        # محاسبه نتیجه
        total_stake = sum(self.voter_stakes.values())
        if total_stake == 0:
            total_stake = 1.0
        
        total_voted = proposal.votes_for + proposal.votes_against
        participation = total_voted / total_stake
        
        # بررسی حد نصاب
        if participation < self.quorum_percentage:
            proposal.status = ProposalStatus.EXPIRED
            print(f"⏰ Proposal expired (low participation): {proposal.title}")
            return True
        
        # بررسی آرای موافق
        approval_rate = proposal.votes_for / total_voted if total_voted > 0 else 0
        
        if approval_rate >= self.approval_threshold:
            proposal.status = ProposalStatus.PASSED
            print(f"✅ Proposal passed: {proposal.title} ({approval_rate*100:.1f}% approval)")
        else:
            proposal.status = ProposalStatus.REJECTED
            print(f"❌ Proposal rejected: {proposal.title} ({approval_rate*100:.1f}% approval)")
        
        return True
    
    def execute_proposal(self, proposal_id: str) -> bool:
        """
        اجرای پیشنهاد تصویب شده
        
        Args:
            proposal_id: شناسه پیشنهاد
        
        Returns:
            موفقیت
        """
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        
        if proposal.status != ProposalStatus.PASSED:
            return False
        
        # بررسی تأخیر اجرا
        if time() < proposal.voting_ends + self.execution_delay:
            return False
        
        # اجرای پیشنهاد بر اساس نوع
        try:
            if proposal.proposal_type == ProposalType.PARAMETER_CHANGE:
                result = self._execute_parameter_change(proposal)
            elif proposal.proposal_type == ProposalType.TREASURY_SPEND:
                result = self._execute_treasury_spend(proposal)
            elif proposal.proposal_type == ProposalType.PROTOCOL_UPGRADE:
                result = self._execute_protocol_upgrade(proposal)
            else:
                result = "Execution not implemented for this type"
            
            proposal.status = ProposalStatus.EXECUTED
            proposal.executed_at = time()
            proposal.execution_result = result
            
            print(f"⚡ Proposal executed: {proposal.title}")
            return True
        
        except Exception as e:
            proposal.execution_result = f"Error: {str(e)}"
            print(f"❌ Execution failed: {proposal.title} - {e}")
            return False
    
    def _execute_parameter_change(self, proposal: Proposal) -> str:
        """اجرای تغییر پارامتر"""
        target = proposal.target
        new_value = proposal.parameters.get("new_value")
        
        # در اینجا باید پارامتر واقعی تغییر کند
        # برای مثال:
        if target == "quorum_percentage":
            self.quorum_percentage = float(new_value)
        elif target == "approval_threshold":
            self.approval_threshold = float(new_value)
        
        return f"Changed {target} to {new_value}"
    
    def _execute_treasury_spend(self, proposal: Proposal) -> str:
        """اجرای هزینه از خزانه"""
        recipient = proposal.parameters.get("recipient")
        amount = float(proposal.parameters.get("amount", 0))
        
        if amount > self.treasury_balance:
            raise ValueError("Insufficient treasury balance")
        
        self.treasury_balance -= amount
        
        return f"Transferred {amount} to {recipient}"
    
    def _execute_protocol_upgrade(self, proposal: Proposal) -> str:
        """اجرای ارتقای پروتوکل"""
        # این باید با Cognitive Core هماهنگ شود
        return f"Protocol upgrade scheduled: {proposal.description}"
    
    def update_stake(self, voter_id: str, stake_amount: float):
        """به‌روزرسانی مقدار stake یک رأی‌دهنده"""
        self.voter_stakes[voter_id] = stake_amount
    
    def add_to_treasury(self, amount: float):
        """افزودن به خزانه"""
        self.treasury_balance += amount
        print(f"💰 Treasury balance: {self.treasury_balance:.2f}")
    
    def get_active_proposals(self) -> List[Proposal]:
        """دریافت پیشنهادات فعال"""
        return [
            p for p in self.proposals.values()
            if p.status == ProposalStatus.ACTIVE
        ]
    
    def get_proposal_details(self, proposal_id: str) -> Optional[Dict]:
        """دریافت جزئیات پیشنهاد"""
        if proposal_id not in self.proposals:
            return None
        
        proposal = self.proposals[proposal_id]
        votes = self.votes[proposal_id]
        
        return {
            "proposal": proposal.model_dump(),
            "votes": [v.model_dump() for v in votes],
            "participation": (proposal.votes_for + proposal.votes_against) / sum(self.voter_stakes.values()) if self.voter_stakes else 0
        }
    
    def get_stats(self) -> Dict:
        """دریافت آمار حکمرانی"""
        return {
            "total_proposals": len(self.proposals),
            "active_proposals": len(self.get_active_proposals()),
            "passed_proposals": len([p for p in self.proposals.values() if p.status == ProposalStatus.PASSED]),
            "executed_proposals": len([p for p in self.proposals.values() if p.status == ProposalStatus.EXECUTED]),
            "total_voters": len(self.voter_stakes),
            "treasury_balance": self.treasury_balance,
            "quorum_percentage": self.quorum_percentage,
            "approval_threshold": self.approval_threshold
        }


class AutoGovernance:
    """
    حکمرانی خودکار با AI
    
    Cognitive Core می‌تواند پیشنهادات را تحلیل و توصیه دهد
    """
    
    def __init__(self, governance: GovernanceSystem, cognitive_core=None):
        self.governance = governance
        self.cognitive_core = cognitive_core
        
        print("🤖 Auto-Governance initialized")
    
    def analyze_proposal(self, proposal_id: str) -> Dict:
        """
        تحلیل هوشمند پیشنهاد
        
        Args:
            proposal_id: شناسه پیشنهاد
        
        Returns:
            تحلیل و توصیه
        """
        details = self.governance.get_proposal_details(proposal_id)
        if not details:
            return {"error": "Proposal not found"}
        
        proposal = details["proposal"]
        
        # تحلیل با Cognitive Core
        if self.cognitive_core:
            analysis_prompt = f"""
            Analyze this governance proposal:
            
            Title: {proposal['title']}
            Type: {proposal['proposal_type']}
            Description: {proposal['description']}
            
            Provide:
            1. Impact assessment
            2. Risk analysis
            3. Recommendation (approve/reject)
            4. Reasoning
            """
            
            analysis = self.cognitive_core.ask_question(analysis_prompt)
            
            return {
                "proposal_id": proposal_id,
                "ai_analysis": analysis,
                "current_votes": {
                    "for": proposal['votes_for'],
                    "against": proposal['votes_against']
                }
            }
        
        return {
            "proposal_id": proposal_id,
            "message": "AI analysis not available"
        }
    
    def suggest_improvements(self) -> List[Proposal]:
        """پیشنهاد بهبودهای خودکار"""
        suggestions = []
        
        if self.cognitive_core:
            # درخواست پیشنهادات از Cognitive Core
            prompt = """
            Based on the current state of the Laniakea Protocol,
            suggest 3 governance proposals for improvement.
            
            Format each as:
            Title: ...
            Type: parameter_change/protocol_upgrade/treasury_spend
            Description: ...
            Target: ...
            """
            
            response = self.cognitive_core.ask_question(prompt)
            # پردازش پاسخ و ایجاد پیشنهادات
            # (در اینجا ساده‌سازی شده است)
        
        return suggestions
