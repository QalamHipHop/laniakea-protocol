"""
Social Features Module
Implements social interactions between SCDAs:
- Follow/Followers system
- Knowledge comparison
- Collaboration and team-based problem solving
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    \"\"\"Represents a user's social profile.\"\"\"
    scda_id: str
    username: str
    tier: int
    complexity_index: float
    problems_solved: int
    knowledge_vector_8d: List[float]
    created_at: str
    bio: str = ""


@dataclass
class SocialConnection:
    \"\"\"Represents a social connection (follow relationship).\"\"\"
    follower_id: str
    following_id: str
    established_at: str
    connection_type: str = "follow"  # "follow", "friend", "mentor"


@dataclass
class CollaborationSession:
    \"\"\"Represents a collaborative problem-solving session.\"\"\"
    session_id: str
    participants: List[str]
    problem_id: str
    created_at: str
    status: str = "active"  # "active", "completed", "abandoned"
    shared_knowledge: List[float] = None
    collective_solution: str = ""
    completion_time: Optional[str] = None


class SocialNetwork:
    \"\"\"
    Manages the social network of SCDAs.
    Handles follows, friendships, and collaborative problem-solving.
    \"\"\"
    
    def __init__(self):
        \"\"\"Initialize the Social Network.\"\"\"
        self.user_profiles: Dict[str, UserProfile] = {}
        self.social_connections: List[SocialConnection] = []
        self.collaboration_sessions: Dict[str, CollaborationSession] = {}
        self.knowledge_comparisons: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Social Network initialized")
    
    def create_user_profile(
        self,
        scda_id: str,
        username: str,
        tier: int,
        complexity_index: float,
        problems_solved: int,
        knowledge_vector_8d: List[float],
        bio: str = ""
    ) -> UserProfile:
        \"\"\"Create a new user profile for an SCDA.\"\"\"
        profile = UserProfile(
            scda_id=scda_id,
            username=username,
            tier=tier,
            complexity_index=complexity_index,
            problems_solved=problems_solved,
            knowledge_vector_8d=knowledge_vector_8d,
            created_at=datetime.now().isoformat(),
            bio=bio
        )
        
        self.user_profiles[scda_id] = profile
        logger.info(f"User profile created for {username} ({scda_id})")
        
        return profile
    
    def follow_user(self, follower_id: str, following_id: str) -> Dict[str, Any]:
        \"\"\"
        Establish a follow relationship between two users.
        \"\"\"
        if follower_id not in self.user_profiles:
            return {"error": f"Follower {follower_id} not found"}
        if following_id not in self.user_profiles:
            return {"error": f"Following {following_id} not found"}
        
        # Check if already following
        for conn in self.social_connections:
            if conn.follower_id == follower_id and conn.following_id == following_id:
                return {"error": "Already following this user"}
        
        connection = SocialConnection(
            follower_id=follower_id,
            following_id=following_id,
            established_at=datetime.now().isoformat(),
            connection_type="follow"
        )
        
        self.social_connections.append(connection)
        logger.info(f"{follower_id} is now following {following_id}")
        
        return {
            "status": "success",
            "message": f"Successfully following {self.user_profiles[following_id].username}"
        }
    
    def unfollow_user(self, follower_id: str, following_id: str) -> Dict[str, Any]:
        \"\"\"Remove a follow relationship.\"\"\"
        self.social_connections = [
            conn for conn in self.social_connections
            if not (conn.follower_id == follower_id and conn.following_id == following_id)
        ]
        
        logger.info(f"{follower_id} unfollowed {following_id}")
        
        return {"status": "success", "message": "Successfully unfollowed"}
    
    def get_followers(self, user_id: str) -> List[UserProfile]:
        \"\"\"Get all followers of a user.\"\"\"
        follower_ids = [
            conn.follower_id for conn in self.social_connections
            if conn.following_id == user_id
        ]
        
        return [self.user_profiles[fid] for fid in follower_ids if fid in self.user_profiles]
    
    def get_following(self, user_id: str) -> List[UserProfile]:
        \"\"\"Get all users that a user is following.\"\"\"
        following_ids = [
            conn.following_id for conn in self.social_connections
            if conn.follower_id == user_id
        ]
        
        return [self.user_profiles[fid] for fid in following_ids if fid in self.user_profiles]
    
    def get_follower_count(self, user_id: str) -> int:
        \"\"\"Get the number of followers.\"\"\"
        return len(self.get_followers(user_id))
    
    def get_following_count(self, user_id: str) -> int:
        \"\"\"Get the number of users being followed.\"\"\"
        return len(self.get_following(user_id))
    
    def compare_knowledge_vectors(self, user_id_1: str, user_id_2: str) -> Dict[str, Any]:
        \"\"\"
        Compare the knowledge vectors of two users.
        Returns similarity metrics and differences.
        \"\"\"
        if user_id_1 not in self.user_profiles or user_id_2 not in self.user_profiles:
            return {"error": "One or both users not found"}
        
        profile1 = self.user_profiles[user_id_1]
        profile2 = self.user_profiles[user_id_2]
        
        vec1 = np.array(profile1.knowledge_vector_8d)
        vec2 = np.array(profile2.knowledge_vector_8d)
        
        # Calculate similarity metrics
        cosine_similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-8)
        euclidean_distance = np.linalg.norm(vec1 - vec2)
        
        # Find strongest and weakest domains
        diff = vec1 - vec2
        strongest_domain_idx = np.argmax(np.abs(diff))
        
        domains = ["Physics", "Biology", "Mathematics", "Chemistry", "Engineering", "CS", "Philosophy", "Cosmology"]
        
        comparison = {
            "user_1": {
                "scda_id": user_id_1,
                "username": profile1.username,
                "tier": profile1.tier,
                "complexity_index": profile1.complexity_index
            },
            "user_2": {
                "scda_id": user_id_2,
                "username": profile2.username,
                "tier": profile2.tier,
                "complexity_index": profile2.complexity_index
            },
            "similarity_metrics": {
                "cosine_similarity": float(cosine_similarity),
                "euclidean_distance": float(euclidean_distance)
            },
            "knowledge_differences": {
                "user_1_stronger_in": domains[np.argmax(diff)] if np.max(diff) > 0 else "None",
                "user_2_stronger_in": domains[np.argmin(diff)] if np.min(diff) < 0 else "None"
            },
            "complementary_strengths": self._find_complementary_strengths(profile1, profile2)
        }
        
        # Cache the comparison
        comparison_id = f"{user_id_1}_{user_id_2}"
        self.knowledge_comparisons[comparison_id] = comparison
        
        logger.info(f"Knowledge comparison: {user_id_1} vs {user_id_2}")
        
        return comparison
    
    def _find_complementary_strengths(self, profile1: UserProfile, profile2: UserProfile) -> Dict[str, Any]:
        \"\"\"Find areas where the two users complement each other.\"\"\"
        vec1 = np.array(profile1.knowledge_vector_8d)
        vec2 = np.array(profile2.knowledge_vector_8d)
        
        domains = ["Physics", "Biology", "Mathematics", "Chemistry", "Engineering", "CS", "Philosophy", "Cosmology"]
        
        complementary = {}
        for i, domain in enumerate(domains):
            if vec1[i] > 0.5 and vec2[i] < 0.3:
                complementary[f"{profile1.username}_in_{domain}"] = float(vec1[i])
            elif vec2[i] > 0.5 and vec1[i] < 0.3:
                complementary[f"{profile2.username}_in_{domain}"] = float(vec2[i])
        
        return complementary
    
    def create_collaboration_session(
        self,
        participants: List[str],
        problem_id: str
    ) -> Dict[str, Any]:
        \"\"\"
        Create a collaboration session for multiple users to solve a problem together.
        \"\"\"
        # Verify all participants exist
        for participant_id in participants:
            if participant_id not in self.user_profiles:
                return {"error": f"Participant {participant_id} not found"}
        
        session_id = f"collab_{len(self.collaboration_sessions):04d}"
        
        # Calculate collective knowledge vector
        collective_knowledge = np.zeros(8)
        for participant_id in participants:
            profile = self.user_profiles[participant_id]
            collective_knowledge += np.array(profile.knowledge_vector_8d)
        
        collective_knowledge = (collective_knowledge / len(participants)).tolist()
        
        session = CollaborationSession(
            session_id=session_id,
            participants=participants,
            problem_id=problem_id,
            created_at=datetime.now().isoformat(),
            shared_knowledge=collective_knowledge
        )
        
        self.collaboration_sessions[session_id] = session
        
        logger.info(f"Collaboration session {session_id} created with {len(participants)} participants")
        
        return {
            "session_id": session_id,
            "participants": participants,
            "collective_knowledge": collective_knowledge,
            "message": "Collaboration session created successfully"
        }
    
    def complete_collaboration_session(
        self,
        session_id: str,
        collective_solution: str
    ) -> Dict[str, Any]:
        \"\"\"Mark a collaboration session as completed.\"\"\"
        if session_id not in self.collaboration_sessions:
            return {"error": "Collaboration session not found"}
        
        session = self.collaboration_sessions[session_id]
        session.status = "completed"
        session.collective_solution = collective_solution
        session.completion_time = datetime.now().isoformat()
        
        logger.info(f"Collaboration session {session_id} completed")
        
        return {
            "session_id": session_id,
            "status": "completed",
            "message": "Collaboration session marked as completed"
        }
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        \"\"\"Get a user's profile.\"\"\"
        return self.user_profiles.get(user_id)
    
    def get_user_social_stats(self, user_id: str) -> Dict[str, Any]:
        \"\"\"Get social statistics for a user.\"\"\"
        if user_id not in self.user_profiles:
            return {"error": "User not found"}
        
        profile = self.user_profiles[user_id]
        
        return {
            "username": profile.username,
            "followers": self.get_follower_count(user_id),
            "following": self.get_following_count(user_id),
            "tier": profile.tier,
            "complexity_index": profile.complexity_index,
            "problems_solved": profile.problems_solved,
            "active_collaborations": sum(
                1 for session in self.collaboration_sessions.values()
                if user_id in session.participants and session.status == "active"
            )
        }
    
    def export_social_network(self) -> str:
        \"\"\"Export the complete social network to JSON.\"\"\"
        data = {
            "users": {
                scda_id: {
                    "username": profile.username,
                    "tier": profile.tier,
                    "complexity_index": profile.complexity_index,
                    "problems_solved": profile.problems_solved,
                    "knowledge_vector_8d": profile.knowledge_vector_8d
                }
                for scda_id, profile in self.user_profiles.items()
            },
            "connections": [
                {
                    "follower_id": conn.follower_id,
                    "following_id": conn.following_id,
                    "established_at": conn.established_at,
                    "connection_type": conn.connection_type
                }
                for conn in self.social_connections
            ],
            "collaboration_sessions": {
                session_id: {
                    "participants": session.participants,
                    "problem_id": session.problem_id,
                    "status": session.status,
                    "created_at": session.created_at
                }
                for session_id, session in self.collaboration_sessions.items()
            }
        }
        return json.dumps(data, indent=2)


# Example usage
if __name__ == "__main__":
    social_net = SocialNetwork()
    
    # Create user profiles
    social_net.create_user_profile(
        "scda_001", "Alice", 2, 25.5, 10,
        [0.8, 0.6, 0.9, 0.5, 0.7, 0.4, 0.3, 0.2],
        bio="Passionate about physics and mathematics"
    )
    
    social_net.create_user_profile(
        "scda_002", "Bob", 2, 20.3, 8,
        [0.5, 0.8, 0.6, 0.7, 0.9, 0.8, 0.4, 0.3],
        bio="Computer science enthusiast"
    )
    
    # Follow relationship
    social_net.follow_user("scda_001", "scda_002")
    
    # Compare knowledge
    comparison = social_net.compare_knowledge_vectors("scda_001", "scda_002")
    print(f"Knowledge Comparison: {json.dumps(comparison, indent=2)}")
    
    # Create collaboration
    collab = social_net.create_collaboration_session(["scda_001", "scda_002"], "problem_001")
    print(f"Collaboration: {json.dumps(collab, indent=2)}")
    
    # Get social stats
    stats = social_net.get_user_social_stats("scda_001")
    print(f"Social Stats: {json.dumps(stats, indent=2)}")
