# laniakea/achievements/system.py

import time
from typing import Dict, Any, List

class Achievement:
    def __init__(self, name: str, description: str, condition: str, reward: int):
        self.name = name
        self.description = description
        self.condition = condition # A string describing the condition (e.g., "Mine 10 blocks")
        self.reward = reward # e.g., LANA tokens or a badge
        self.id = name.lower().replace(" ", "_")

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

class AchievementSystem:
    """
    Manages the definition and tracking of user achievements within the protocol.
    """
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.user_progress: Dict[str, Dict[str, Any]] = {} # {user_id: {achievement_id: {status: "UNLOCKED"|"IN_PROGRESS", progress: 0.5}}}

        # Define initial achievements
        self._define_achievements()

    def _define_achievements(self):
        """Initializes the list of available achievements."""
        achievements_list = [
            Achievement("First Block Miner", "Mine your very first block on the Laniakea chain.", "blockchain.blocks_mined >= 1", 50),
            Achievement("Cross-Chain Pioneer", "Complete 5 successful cross-chain transfers.", "crosschain.transfers_completed >= 5", 100),
            Achievement("Quantum Entangler", "Submit 10 quantum computing jobs.", "quantum.jobs_submitted >= 10", 150),
            Achievement("DAO Diplomat", "Vote on 3 different governance proposals.", "governance.votes_cast >= 3", 75),
            Achievement("Cosmic Explorer", "Run the cosmic simulation for 100 steps.", "simulation.steps_run >= 100", 120),
        ]
        for ach in achievements_list:
            self.achievements[ach.id] = ach

    def get_achievement(self, achievement_id: str) -> Achievement | None:
        """Retrieves an achievement by its ID."""
        return self.achievements.get(achievement_id)

    def update_user_progress(self, user_id: str, metric_key: str, value: Any):
        """
        Updates a user's metric and checks if any achievement conditions are met.
        (Simplified: In a real system, this would be triggered by events).
        """
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}

        # Update the user's raw metric (e.g., blocks_mined)
        current_value = self.user_progress[user_id].get(metric_key, 0)
        self.user_progress[user_id][metric_key] = value
        
        # Check for achievement unlocks
        for ach_id, ach in self.achievements.items():
            if ach_id not in self.user_progress[user_id] or self.user_progress[user_id][ach_id].get("status") != "UNLOCKED":
                # Simple check: assumes condition is a direct comparison
                condition_parts = ach.condition.split()
                if len(condition_parts) == 3 and condition_parts[0] == metric_key:
                    operator = condition_parts[1]
                    required_value = float(condition_parts[2])
                    
                    is_unlocked = False
                    if operator == ">=" and value >= required_value:
                        is_unlocked = True
                    elif operator == "==" and value == required_value:
                        is_unlocked = True
                        
                    if is_unlocked:
                        self._unlock_achievement(user_id, ach_id)

    def _unlock_achievement(self, user_id: str, achievement_id: str):
        """Marks an achievement as unlocked and grants the reward."""
        ach = self.achievements[achievement_id]
        self.user_progress[user_id][achievement_id] = {
            "status": "UNLOCKED",
            "unlocked_at": time.time(),
            "reward_granted": ach.reward
        }
        print(f"*** ACHIEVEMENT UNLOCKED for {user_id}: {ach.name} (+{ach.reward} reward) ***")

# Example usage
if __name__ == '__main__':
    system = AchievementSystem()
    user_a = "User_A_Wallet"
    
    # User A mines their first block
    system.update_user_progress(user_a, "blockchain.blocks_mined", 1)
    
    # User A completes a cross-chain transfer (not enough for achievement yet)
    system.update_user_progress(user_a, "crosschain.transfers_completed", 1)
    
    # User A completes 5 cross-chain transfers
    system.update_user_progress(user_a, "crosschain.transfers_completed", 5)
    
    print("\nUser A Progress:")
    import json
    print(json.dumps(system.user_progress.get(user_a, {}), indent=2))
