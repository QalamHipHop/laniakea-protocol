"""
LaniakeA Protocol - Database Integration Module
Handles PostgreSQL integration for persistent storage of blockchain data.
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

try:
    import psycopg2
    from psycopg2 import sql, extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logging.warning("psycopg2 not available. Database features will be limited.")

logger = logging.getLogger("Database")


class DatabaseConnection:
    """PostgreSQL database connection manager"""
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 5432,
                 database: str = "laniakea",
                 user: str = "laniakea",
                 password: str = "laniakea"):
        """
        Initialize database connection
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """Connect to database"""
        if not PSYCOPG2_AVAILABLE:
            logger.warning("psycopg2 not available")
            return False
        
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor(cursor_factory=extras.RealDictCursor)
            logger.info(f"✅ Connected to database: {self.database}")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            self.cursor.close()
            self.connection.close()
            logger.info("✅ Disconnected from database")
    
    def execute(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute query and return results"""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.fetchall() or []
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            self.connection.rollback()
            return []
    
    def execute_many(self, query: str, params_list: List[tuple]):
        """Execute multiple queries"""
        try:
            self.cursor.executemany(query, params_list)
            self.connection.commit()
            logger.info(f"✅ Executed {len(params_list)} queries")
        except Exception as e:
            logger.error(f"❌ Batch execution failed: {e}")
            self.connection.rollback()


class BlockchainDatabase:
    """Blockchain data persistence layer"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """Initialize blockchain database"""
        self.db = db_connection
        self.init_tables()
    
    def init_tables(self):
        """Initialize database tables"""
        if not PSYCOPG2_AVAILABLE:
            return
        
        try:
            # Blocks table
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS blocks (
                    id SERIAL PRIMARY KEY,
                    block_hash VARCHAR(255) UNIQUE NOT NULL,
                    previous_hash VARCHAR(255),
                    timestamp BIGINT NOT NULL,
                    nonce BIGINT,
                    difficulty FLOAT,
                    miner_id VARCHAR(255),
                    transactions_count INT,
                    data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Transactions table
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    tx_hash VARCHAR(255) UNIQUE NOT NULL,
                    block_hash VARCHAR(255),
                    sender VARCHAR(255) NOT NULL,
                    receiver VARCHAR(255) NOT NULL,
                    amount FLOAT NOT NULL,
                    fee FLOAT,
                    timestamp BIGINT NOT NULL,
                    status VARCHAR(50),
                    data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (block_hash) REFERENCES blocks(block_hash)
                )
            """)
            
            # Smart Contracts table
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS smart_contracts (
                    id SERIAL PRIMARY KEY,
                    contract_address VARCHAR(255) UNIQUE NOT NULL,
                    owner_address VARCHAR(255) NOT NULL,
                    code TEXT,
                    state JSONB,
                    gas_limit INT,
                    balance FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Contract Executions table
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS contract_executions (
                    id SERIAL PRIMARY KEY,
                    contract_address VARCHAR(255) NOT NULL,
                    function_name VARCHAR(255),
                    caller_address VARCHAR(255),
                    gas_used INT,
                    result JSONB,
                    status VARCHAR(50),
                    timestamp BIGINT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contract_address) REFERENCES smart_contracts(contract_address)
                )
            """)
            
            # Cross-Chain Bridges table
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS cross_chain_bridges (
                    id SERIAL PRIMARY KEY,
                    bridge_id VARCHAR(255) UNIQUE NOT NULL,
                    from_chain VARCHAR(50) NOT NULL,
                    to_chain VARCHAR(50) NOT NULL,
                    from_address VARCHAR(255),
                    to_address VARCHAR(255),
                    amount FLOAT,
                    token_address VARCHAR(255),
                    status VARCHAR(50),
                    from_tx_hash VARCHAR(255),
                    to_tx_hash VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Users table
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255),
                    wallet_address VARCHAR(255) UNIQUE,
                    balance FLOAT DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Analytics table
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id SERIAL PRIMARY KEY,
                    metric_name VARCHAR(255),
                    metric_value FLOAT,
                    timestamp BIGINT NOT NULL,
                    data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            logger.info("✅ Database tables initialized")
        except Exception as e:
            logger.error(f"❌ Table initialization failed: {e}")
    
    def insert_block(self, block_data: Dict) -> bool:
        """Insert block into database"""
        try:
            query = """
                INSERT INTO blocks 
                (block_hash, previous_hash, timestamp, nonce, difficulty, miner_id, transactions_count, data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                block_data.get('hash'),
                block_data.get('previous_hash'),
                block_data.get('timestamp'),
                block_data.get('nonce'),
                block_data.get('difficulty'),
                block_data.get('miner_id'),
                block_data.get('transactions_count', 0),
                json.dumps(block_data)
            )
            self.db.execute(query, params)
            logger.info(f"✅ Block inserted: {block_data.get('hash')[:8]}...")
            return True
        except Exception as e:
            logger.error(f"❌ Block insertion failed: {e}")
            return False
    
    def insert_transaction(self, tx_data: Dict) -> bool:
        """Insert transaction into database"""
        try:
            query = """
                INSERT INTO transactions 
                (tx_hash, block_hash, sender, receiver, amount, fee, timestamp, status, data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                tx_data.get('hash'),
                tx_data.get('block_hash'),
                tx_data.get('sender'),
                tx_data.get('receiver'),
                tx_data.get('amount'),
                tx_data.get('fee', 0),
                tx_data.get('timestamp'),
                tx_data.get('status', 'pending'),
                json.dumps(tx_data)
            )
            self.db.execute(query, params)
            logger.info(f"✅ Transaction inserted: {tx_data.get('hash')[:8]}...")
            return True
        except Exception as e:
            logger.error(f"❌ Transaction insertion failed: {e}")
            return False
    
    def insert_contract(self, contract_data: Dict) -> bool:
        """Insert smart contract into database"""
        try:
            query = """
                INSERT INTO smart_contracts 
                (contract_address, owner_address, code, state, gas_limit, balance)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (
                contract_data.get('address'),
                contract_data.get('owner'),
                contract_data.get('code'),
                json.dumps(contract_data.get('state', {})),
                contract_data.get('gas_limit'),
                contract_data.get('balance', 0)
            )
            self.db.execute(query, params)
            logger.info(f"✅ Contract inserted: {contract_data.get('address')[:8]}...")
            return True
        except Exception as e:
            logger.error(f"❌ Contract insertion failed: {e}")
            return False
    
    def get_blocks(self, limit: int = 10) -> List[Dict]:
        """Get recent blocks"""
        query = "SELECT * FROM blocks ORDER BY created_at DESC LIMIT %s"
        return self.db.execute(query, (limit,))
    
    def get_transactions(self, limit: int = 10) -> List[Dict]:
        """Get recent transactions"""
        query = "SELECT * FROM transactions ORDER BY created_at DESC LIMIT %s"
        return self.db.execute(query, (limit,))
    
    def get_contracts(self, limit: int = 10) -> List[Dict]:
        """Get smart contracts"""
        query = "SELECT * FROM smart_contracts ORDER BY created_at DESC LIMIT %s"
        return self.db.execute(query, (limit,))
    
    def get_analytics(self, metric_name: str, limit: int = 100) -> List[Dict]:
        """Get analytics data"""
        query = """
            SELECT * FROM analytics 
            WHERE metric_name = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        """
        return self.db.execute(query, (metric_name, limit))
    
    def insert_analytics(self, metric_name: str, metric_value: float, data: Dict = None) -> bool:
        """Insert analytics data"""
        try:
            query = """
                INSERT INTO analytics (metric_name, metric_value, timestamp, data)
                VALUES (%s, %s, %s, %s)
            """
            params = (
                metric_name,
                metric_value,
                int(datetime.utcnow().timestamp()),
                json.dumps(data or {})
            )
            self.db.execute(query, params)
            return True
        except Exception as e:
            logger.error(f"❌ Analytics insertion failed: {e}")
            return False


class UserDatabase:
    """User management database layer"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """Initialize user database"""
        self.db = db_connection
    
    def create_user(self, username: str, email: str, password_hash: str) -> bool:
        """Create new user"""
        try:
            query = """
                INSERT INTO users (username, email, password_hash)
                VALUES (%s, %s, %s)
            """
            params = (username, email, password_hash)
            self.db.execute(query, params)
            logger.info(f"✅ User created: {username}")
            return True
        except Exception as e:
            logger.error(f"❌ User creation failed: {e}")
            return False
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        query = "SELECT * FROM users WHERE username = %s"
        results = self.db.execute(query, (username,))
        return results[0] if results else None
    
    def update_user_balance(self, username: str, balance: float) -> bool:
        """Update user balance"""
        try:
            query = "UPDATE users SET balance = %s, updated_at = CURRENT_TIMESTAMP WHERE username = %s"
            self.db.execute(query, (balance, username))
            return True
        except Exception as e:
            logger.error(f"❌ Balance update failed: {e}")
            return False


# Global database instance
_db_instance: Optional[DatabaseConnection] = None


def get_database() -> Optional[DatabaseConnection]:
    """Get global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConnection(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            database=os.getenv("DB_NAME", "laniakea"),
            user=os.getenv("DB_USER", "laniakea"),
            password=os.getenv("DB_PASSWORD", "laniakea")
        )
        _db_instance.connect()
    return _db_instance


def get_blockchain_db() -> Optional[BlockchainDatabase]:
    """Get blockchain database instance"""
    db = get_database()
    return BlockchainDatabase(db) if db else None


def get_user_db() -> Optional[UserDatabase]:
    """Get user database instance"""
    db = get_database()
    return UserDatabase(db) if db else None
