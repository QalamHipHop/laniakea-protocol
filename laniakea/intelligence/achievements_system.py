"""
Achievements System Module
Manages achievements, unlocks, and progress tracking for SCDAs.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class Achievement:
    """Represents an achievement."""
    achievement_id: str
    name: str
    description: str
    category: str  # "exploration", "knowledge", "social", "evolution"
    unlock_condition: str  # Description of how to unlock
    reward_points: int
    rarity: str  # "common", "rare", "epic", "legendary"
    icon_url: str = ""


@dataclass
class UnlockedAchievement:
    """Represents an unlocked achievement for an SCDA."""
    achievement_id: str
    scda_id: str
    unlocked_at: str
    progress: float = 1.0  # 0.0 to 1.0


@dataclass
class AchievementProgress:
    """Tracks progress towards an achievement."""
    achievement_id: str
    scda_id: str
    progress: float  # 0.0 to 1.0
    current_value: float
    target_value: float
    last_updated: str


class AchievementsSystem:
    """
    Manages achievements for the LaniakeA Protocol.
    Tracks progress, unlocks, and rewards.
    """
    
    def __init__(self):
        """Initialize the Achievements System."""
        self.achievements: Dict[str, Achievement] = {}
        self.unlocked_achievements: Dict[str, List[UnlockedAchievement]] = {}  # scda_id -> list
        self.achievement_progress: Dict[str, List[AchievementProgress]] = {}  # scda_id -> list
        
        # Initialize default achievements
        self._initialize_default_achievements()
        
        logger.info("Achievements System initialized")
    
    def _initialize_default_achievements(self):
        """Initialize a set of default achievements."""
        
        default_achievements = [
            # Exploration Achievements
            Achievement(
                achievement_id="first_step",
                name="First Step",
                description="Solve your first Hard Problem",
                category="exploration",
                unlock_condition="Solve 1 problem",
                reward_points=10,
                rarity="common"
            ),
            Achievement(
                achievement_id="problem_solver",
                name="Problem Solver",
                description="Solve 10 Hard Problems",
                category="exploration",
                unlock_condition="Solve 10 problems",
                reward_points=50,
                rarity="common"
            ),
            Achievement(
                achievement_id="knowledge_seeker",
                name="Knowledge Seeker",
                description="Acquire knowledge in all 8 domains",
                category="knowledge",
                unlock_condition="Reach 0.5 in all 8 knowledge domains",
                reward_points=100,
                rarity="rare"
            ),
            
            # Evolution Achievements
            Achievement(
                achievement_id="multicellular",
                name="Multicellular",
                description="Reach Tier 2 (Multi-Cellular)",
                category="evolution",
                unlock_condition="Reach C(t) >= 10.0",
                reward_points=200,
                rarity="rare"
            ),
            Achievement(
                achievement_id="human_consciousness",
                name="Human Consciousness",
                description="Reach Tier 3 (Humanity)",
                category="evolution",
                unlock_condition="Reach C(t) >= 100.0",
                reward_points=500,
                rarity="epic"
            ),
            Achievement(
                achievement_id="galactic_mind",
                name="Galactic Mind",
                description="Reach Tier 4 (Galactic)",
                category="evolution",
                unlock_condition="Reach C(t) >= 1000.0",
                reward_points=1000,
                rarity="legendary"
            ),
            
            # Social Achievements
            Achievement(
                achievement_id="socialite",
                name="Socialite",
                description="Follow 10 other SCDAs",
                category="social",
                unlock_condition="Have 10 followers",
                reward_points=75,
                rarity="common"
            ),
            Achievement(
                achievement_id="collaborator",
                name="Collaborator",
                description="Complete 5 collaborative problem-solving sessions",
                category="social",
                unlock_condition="Complete 5 collaborations",
                reward_points=150,
                rarity="rare"
            ),
            Achievement(
                achievement_id="mentor",
                name="Mentor",
                description="Help 20 other SCDAs through collaboration",
                category="social",
                unlock_condition="Participate in 20 collaborations",
                reward_points=300,
                rarity="epic"
            ),
            
            # Specialized Achievements
            Achievement(
                achievement_id="physicist",
                name="Physicist",
                description="Reach 0.8 in Physics knowledge",
                category="knowledge",
                unlock_condition="Physics knowledge >= 0.8",
                reward_points=100,
                rarity="rare"
            ),
            Achievement(
                achievement_id="biologist",
                name="Biologist",
                description="Reach 0.8 in Biology knowledge",
                category="knowledge",
                unlock_condition="Biology knowledge >= 0.8",
                reward_points=100,
                rarity="rare"
            ),
            Achievement(
                achievement_id="mathematician",
                name="Mathematician",
                description="Reach 0.8 in Mathematics knowledge",
                category="knowledge",
                unlock_condition="Mathematics knowledge >= 0.8",
                reward_points=100,
                rarity="rare"
            ),
            Achievement(
                achievement_id="cosmologist",
                name="Cosmologist",
                description="Reach 0.8 in Cosmology knowledge",
                category="knowledge",
                unlock_condition="Cosmology knowledge >= 0.8",
                reward_points=150,
                rarity="epic"
            ),
        ]
        
        for achievement in default_achievements:
            self.achievements[achievement.achievement_id] = achievement
        
        logger.info(f"Initialized {len(default_achievements)} default achievements")
    
    def register_scda(self, scda_id: str):
        """Register an SCDA in the achievements system."""
        if scda_id not in self.unlocked_achievements:
            self.unlocked_achievements[scda_id] = []
            self.achievement_progress[scda_id] = []
            
            # Initialize progress for all achievements
            for achievement_id in self.achievements.keys():
                progress = AchievementProgress(
                    achievement_id=achievement_id,
                    scda_id=scda_id,
                    progress=0.0,
                    current_value=0,
                    target_value=1,
                    last_updated=datetime.now().isoformat()
                )
                self.achievement_progress[scda_id].append(progress)
            
            logger.info(f"SCDA {scda_id} registered in achievements system")
    
    def update_progress(
        self,
        scda_id: str,
        achievement_id: str,
        current_value: float,
        target_value: float
    ) -> Optional[UnlockedAchievement]:
        """
        Update progress for an achievement.
        Returns an UnlockedAchievement if the achievement is unlocked.
        """
        if scda_id not in self.achievement_progress:
            self.register_scda(scda_id)
        
        if achievement_id not in self.achievements:
            logger.error(f"Achievement {achievement_id} not found")
            return None
        
        # Find and update progress
        for progress in self.achievement_progress[scda_id]:
            if progress.achievement_id == achievement_id:
                progress.current_value = current_value
                progress.target_value = target_value
                progress.progress = min(1.0, current_value / target_value)
                progress.last_updated = datetime.now().isoformat()
                
                # Check if achievement should be unlocked
                if progress.progress >= 1.0:
                    return self.unlock_achievement(scda_id, achievement_id)
                
                break
        
        return None
    
    def unlock_achievement(self, scda_id: str, achievement_id: str) -> Optional[UnlockedAchievement]:
        """Unlock an achievement for an SCDA."""
        if scda_id not in self.unlocked_achievements:
            self.register_scda(scda_id)
        
        if achievement_id not in self.achievements:
            logger.error(f"Achievement {achievement_id} not found")
            return None
        
        # Check if already unlocked
        for unlocked in self.unlocked_achievements[scda_id]:
            if unlocked.achievement_id == achievement_id:
                logger.debug(f"Achievement {achievement_id} already unlocked for {scda_id}")
                return unlocked
        
        # Unlock the achievement
        unlocked = UnlockedAchievement(
            achievement_id=achievement_id,
            scda_id=scda_id,
            unlocked_at=datetime.now().isoformat()
        )
        
        self.unlocked_achievements[scda_id].append(unlocked)
        
        achievement = self.achievements[achievement_id]
        logger.info(f"🏆 Achievement unlocked: {achievement.name} for {scda_id}")
        
        return unlocked
    
    def get_unlocked_achievements(self, scda_id: str) -> List[Dict[str, Any]]:
        """Get all unlocked achievements for an SCDA."""
        if scda_id not in self.unlocked_achievements:
            return []
        
        result = []
        for unlocked in self.unlocked_achievements[scda_id]:
            achievement = self.achievements[unlocked.achievement_id]
            result.append({
                "achievement_id": achievement.achievement_id,
                "name": achievement.name,
                "description": achievement.description,
                "category": achievement.category,
                "reward_points": achievement.reward_points,
                "rarity": achievement.rarity,
                "unlocked_at": unlocked.unlocked_at
            })
        
        return result
    
    def get_achievement_progress(self, scda_id: str) -> List[Dict[str, Any]]:
        """Get progress for all achievements for an SCDA."""
        if scda_id not in self.achievement_progress:
            return []
        
        result = []
        for progress in self.achievement_progress[scda_id]:
            achievement = self.achievements[progress.achievement_id]
            
            # Check if already unlocked
            is_unlocked = any(
                u.achievement_id == progress.achievement_id
                for u in self.unlocked_achievements.get(scda_id, [])
            )
            
            result.append({
                "achievement_id": achievement.achievement_id,
                "name": achievement.name,
                "description": achievement.description,
                "category": achievement.category,
                "unlock_condition": achievement.unlock_condition,
                "reward_points": achievement.reward_points,
                "rarity": achievement.rarity,
                "progress": progress.progress,
                "current_value": progress.current_value,
                "target_value": progress.target_value,
                "is_unlocked": is_unlocked,
                "last_updated": progress.last_updated
            })
        
        return result
    
    def get_achievement_stats(self, scda_id: str) -> Dict[str, Any]:
        """Get overall achievement statistics for an SCDA."""
        unlocked = self.get_unlocked_achievements(scda_id)
        all_progress = self.get_achievement_progress(scda_id)
        
        total_points = sum(a["reward_points"] for a in unlocked)
        
        # Group by category
        by_category = {}
        for achievement in all_progress:
            category = achievement["category"]
            if category not in by_category:
                by_category[category] = {"total": 0, "unlocked": 0}
            by_category[category]["total"] += 1
            if achievement["is_unlocked"]:
                by_category[category]["unlocked"] += 1
        
        return {
            "total_achievements": len(all_progress),
            "unlocked_achievements": len(unlocked),
            "total_points": total_points,
            "by_category": by_category,
            "completion_percentage": (len(unlocked) / len(all_progress) * 100) if all_progress else 0
        }
    
    def get_achievement_details(self, achievement_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific achievement."""
        if achievement_id not in self.achievements:
            return None
        
        achievement = self.achievements[achievement_id]
        return {
            "achievement_id": achievement.achievement_id,
            "name": achievement.name,
            "description": achievement.description,
            "category": achievement.category,
            "unlock_condition": achievement.unlock_condition,
            "reward_points": achievement.reward_points,
            "rarity": achievement.rarity
        }
    
    def export_achievements(self, scda_id: str) -> str:
        """Export achievements data for an SCDA to JSON."""
        data = {
            "scda_id": scda_id,
            "stats": self.get_achievement_stats(scda_id),
            "unlocked": self.get_unlocked_achievements(scda_id),
            "progress": self.get_achievement_progress(scda_id)
        }
        return json.dumps(data, indent=2)


# Example usage
if __name__ == "__main__":
    achievements = AchievementsSystem()
    
    # Register SCDA
    scda_id = "test_scda_001"
    achievements.register_scda(scda_id)
    
    # Update progress
    achievements.update_progress(scda_id, "first_step", 1, 1)
    achievements.update_progress(scda_id, "problem_solver", 5, 10)
    achievements.update_progress(scda_id, "multicellular", 15.0, 10.0)
    
    # Get stats
    stats = achievements.get_achievement_stats(scda_id)
    print(f"Achievement Stats: {json.dumps(stats, indent=2)}")
    
    # Get progress
    progress = achievements.get_achievement_progress(scda_id)
    print(f"\nAchievement Progress (first 3):")
    for p in progress[:3]:
        print(f"  {p['name']}: {p['progress']*100:.1f}% ({p['current_value']}/{p['target_value']})")
