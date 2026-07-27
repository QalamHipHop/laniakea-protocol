"""
LaniakeA Protocol - Database Extensions for SCDA
Extends BlockchainDatabase with SCDA-specific methods
"""

from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger("DatabaseExtensions")


def add_scda_methods(blockchain_db_class):
    """
    Decorator to add SCDA-specific methods to BlockchainDatabase
    """
    
    def get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve SCDA user data from database
        
        Args:
            user_id: User identifier
            
        Returns:
            User data dictionary or None
        """
        try:
            query = "SELECT * FROM users WHERE username = %s"
            results = self.db.execute(query, (user_id,))
            
            if results and len(results) > 0:
                user_data = dict(results[0])
                
                # Get SCDA-specific data from analytics table
                scda_query = """
                    SELECT data FROM analytics 
                    WHERE metric_name = 'scda_state' 
                    AND data->>'user_id' = %s 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """
                scda_results = self.db.execute(scda_query, (user_id,))
                
                if scda_results and len(scda_results) > 0:
                    scda_data = scda_results[0].get('data', {})
                    user_data.update(scda_data)
                
                return user_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving user data for {user_id}: {e}")
            return None
    
    def save_user_data(self, user_id: str, data: Dict[str, Any]) -> bool:
        """
        Save SCDA user data to database
        
        Args:
            user_id: User identifier
            data: User data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import time
            
            # Save SCDA state to analytics table
            query = """
                INSERT INTO analytics 
                (metric_name, metric_value, timestamp, data)
                VALUES (%s, %s, %s, %s)
            """
            
            params = (
                'scda_state',
                data.get('complexity_index', 0.0),
                int(time.time() * 1000),
                json.dumps({
                    'user_id': user_id,
                    'complexity_index': data.get('complexity_index', 0.0),
                    'energy': data.get('energy', 0.0),
                    'knowledge_vector': data.get('knowledge_vector', {}),
                    'solved_problems': data.get('solved_problems', [])
                })
            )
            
            self.db.execute(query, params)
            logger.info(f"✅ SCDA state saved for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving user data for {user_id}: {e}")
            return False
    
    # Add methods to class
    blockchain_db_class.get_user_data = get_user_data
    blockchain_db_class.save_user_data = save_user_data
    
    return blockchain_db_class
