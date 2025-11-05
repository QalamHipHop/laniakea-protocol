"""
WebSocket Manager for Real-time Communication
Handles WebSocket connections, message routing, and connection management
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Optional, Any, Callable
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum
import uuid

class ConnectionType(Enum):
    """WebSocket connection types"""
    BLOCKCHAIN = "blockchain"
    TASKS = "tasks"
    NOTIFICATIONS = "notifications"
    MARKETPLACE = "marketplace"
    DASHBOARD = "dashboard"
    GOVERNANCE = "governance"

class WebSocketMessage:
    """WebSocket message structure"""
    def __init__(self, message_type: str, data: Any, target: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.type = message_type
        self.data = data
        self.target = target
        self.timestamp = datetime.utcnow().isoformat()
        self.source = "laniakea-server"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "data": self.data,
            "target": self.target,
            "timestamp": self.timestamp,
            "source": self.source
        }

class WebSocketManager:
    """
    Advanced WebSocket connection manager
    Handles multiple connection types, authentication, and message routing
    """
    
    def __init__(self):
        self.logger = logging.getLogger("WebSocketManager")
        
        # Connection management
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict] = {}
        self.connection_types: Dict[str, Set[str]] = {
            conn_type.value: set() for conn_type in ConnectionType
        }
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
        self.broadcast_subscribers: Dict[str, Set[str]] = {}
        
        # Statistics
        self.connection_stats = {
            "total_connections": 0,
            "connections_by_type": {conn_type.value: 0 for conn_type in ConnectionType},
            "messages_sent": 0,
            "messages_received": 0
        }
        
        # Security
        self.authenticated_connections: Set[str] = set()
        self.rate_limits: Dict[str, Dict] = {}
        
        self.logger.info("WebSocket Manager initialized")

    async def connect(self, websocket: WebSocket, connection_id: str, 
                     connection_type: ConnectionType, metadata: Dict = None) -> bool:
        """Accept and manage a new WebSocket connection"""
        try:
            await websocket.accept()
            
            # Store connection
            self.active_connections[connection_id] = websocket
            self.connection_metadata[connection_id] = metadata or {}
            self.connection_types[connection_type.value].add(connection_id)
            
            # Update connection type
            self.connection_metadata[connection_id]['connection_type'] = connection_type.value
            self.connection_metadata[connection_id]['connected_at'] = datetime.utcnow().isoformat()
            
            # Update statistics
            self.connection_stats["total_connections"] += 1
            self.connection_stats["connections_by_type"][connection_type.value] += 1
            
            # Send welcome message
            welcome_message = WebSocketMessage(
                "connection_established",
                {
                    "connection_id": connection_id,
                    "connection_type": connection_type.value,
                    "server_time": datetime.utcnow().isoformat(),
                    "features": self._get_connection_features(connection_type)
                }
            )
            await self.send_personal_message(welcome_message, connection_id)
            
            self.logger.info(f"WebSocket connection established: {connection_id} ({connection_type.value})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to establish WebSocket connection: {str(e)}")
            return False

    async def disconnect(self, connection_id: str):
        """Handle WebSocket disconnection"""
        if connection_id in self.active_connections:
            # Get connection type before removal
            connection_type = self.connection_metadata.get(connection_id, {}).get('connection_type')
            
            # Remove from active connections
            del self.active_connections[connection_id]
            
            # Clean up metadata
            if connection_id in self.connection_metadata:
                del self.connection_metadata[connection_id]
            
            # Remove from type-specific sets
            if connection_type and connection_type in self.connection_types:
                self.connection_types[connection_type].discard(connection_id)
                
                # Update statistics
                self.connection_stats["connections_by_type"][connection_type] -= 1
            
            # Remove from authenticated set
            self.authenticated_connections.discard(connection_id)
            
            # Clean up rate limits
            if connection_id in self.rate_limits:
                del self.rate_limits[connection_id]
            
            # Update total connections
            self.connection_stats["total_connections"] -= 1
            
            self.logger.info(f"WebSocket connection closed: {connection_id}")

    async def send_personal_message(self, message: WebSocketMessage, connection_id: str):
        """Send a message to a specific connection"""
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message.to_dict()))
                self.connection_stats["messages_sent"] += 1
            except Exception as e:
                self.logger.error(f"Failed to send message to {connection_id}: {str(e)}")
                await self.disconnect(connection_id)

    async def broadcast_to_type(self, message: WebSocketMessage, connection_type: ConnectionType, 
                              exclude_connection: Optional[str] = None):
        """Broadcast message to all connections of a specific type"""
        connections = self.connection_types[connection_type.value].copy()
        
        if exclude_connection:
            connections.discard(exclude_connection)
        
        if connections:
            await asyncio.gather(
                *[self.send_personal_message(message, conn_id) for conn_id in connections],
                return_exceptions=True
            )

    async def broadcast_to_all(self, message: WebSocketMessage, exclude_connections: Set[str] = None):
        """Broadcast message to all active connections"""
        exclude_connections = exclude_connections or set()
        connections = set(self.active_connections.keys()) - exclude_connections
        
        if connections:
            await asyncio.gather(
                *[self.send_personal_message(message, conn_id) for conn_id in connections],
                return_exceptions=True
            )

    async def handle_message(self, connection_id: str, message_data: Dict):
        """Handle incoming WebSocket message"""
        try:
            # Update statistics
            self.connection_stats["messages_received"] += 1
            
            # Rate limiting check
            if not await self._check_rate_limit(connection_id):
                await self._send_rate_limit_warning(connection_id)
                return
            
            message_type = message_data.get('type')
            message_payload = message_data.get('data', {})
            
            # Handle authentication
            if message_type == 'authenticate':
                await self._handle_authentication(connection_id, message_payload)
                return
            
            # Handle subscription
            if message_type == 'subscribe':
                await self._handle_subscription(connection_id, message_payload)
                return
            
            # Route to appropriate handler
            if message_type in self.message_handlers:
                await self.message_handlers[message_type](connection_id, message_payload)
            else:
                # Send unknown message type response
                error_message = WebSocketMessage(
                    "error",
                    {"message": f"Unknown message type: {message_type}"}
                )
                await self.send_personal_message(error_message, connection_id)
                
        except Exception as e:
            self.logger.error(f"Error handling message from {connection_id}: {str(e)}")
            error_message = WebSocketMessage(
                "error",
                {"message": "Internal server error processing message"}
            )
            await self.send_personal_message(error_message, connection_id)

    def register_handler(self, message_type: str, handler: Callable):
        """Register a message handler"""
        self.message_handlers[message_type] = handler
        self.logger.info(f"Registered handler for message type: {message_type}")

    async def _check_rate_limit(self, connection_id: str) -> bool:
        """Check if connection exceeds rate limits"""
        current_time = datetime.utcnow()
        
        if connection_id not in self.rate_limits:
            self.rate_limits[connection_id] = {
                "messages": [],
                "last_reset": current_time
            }
        
        rate_limit_data = self.rate_limits[connection_id]
        
        # Clean old messages (older than 1 minute)
        rate_limit_data["messages"] = [
            msg_time for msg_time in rate_limit_data["messages"]
            if (current_time - msg_time).total_seconds() < 60
        ]
        
        # Check if exceeds limit (100 messages per minute)
        if len(rate_limit_data["messages"]) >= 100:
            return False
        
        # Add current message
        rate_limit_data["messages"].append(current_time)
        return True

    async def _send_rate_limit_warning(self, connection_id: str):
        """Send rate limit warning to connection"""
        warning_message = WebSocketMessage(
            "rate_limit_warning",
            {
                "message": "Rate limit exceeded. Please slow down.",
                "limit": "100 messages per minute"
            }
        )
        await self.send_personal_message(warning_message, connection_id)

    async def _handle_authentication(self, connection_id: str, payload: Dict):
        """Handle WebSocket authentication"""
        # This would integrate with your existing authentication system
        token = payload.get('token')
        
        # For now, accept any token (implement proper authentication)
        self.authenticated_connections.add(connection_id)
        self.connection_metadata[connection_id]['authenticated'] = True
        
        auth_message = WebSocketMessage(
            "authentication_success",
            {"message": "Successfully authenticated"}
        )
        await self.send_personal_message(auth_message, connection_id)

    async def _handle_subscription(self, connection_id: str, payload: Dict):
        """Handle message subscriptions"""
        subscription_type = payload.get('subscription_type')
        
        if subscription_type:
            if subscription_type not in self.broadcast_subscribers:
                self.broadcast_subscribers[subscription_type] = set()
            
            self.broadcast_subscribers[subscription_type].add(connection_id)
            
            sub_message = WebSocketMessage(
                "subscription_success",
                {"subscription_type": subscription_type}
            )
            await self.send_personal_message(sub_message, connection_id)

    def _get_connection_features(self, connection_type: ConnectionType) -> List[str]:
        """Get available features for connection type"""
        features_map = {
            ConnectionType.BLOCKCHAIN: [
                "block_updates", "transaction_confirmations", "network_stats"
            ],
            ConnectionType.TASKS: [
                "task_updates", "solution_submissions", "task_assignments"
            ],
            ConnectionType.NOTIFICATIONS: [
                "system_alerts", "user_notifications", "security_events"
            ],
            ConnectionType.MARKETPLACE: [
                "price_updates", "trade_executions", "market_stats"
            ],
            ConnectionType.DASHBOARD: [
                "real_time_stats", "performance_metrics", "health_status"
            ],
            ConnectionType.GOVERNANCE: [
                "proposal_updates", "voting_events", "dao_changes"
            ]
        }
        
        return features_map.get(connection_type, [])

    def get_connection_stats(self) -> Dict:
        """Get connection statistics"""
        return {
            **self.connection_stats,
            "active_connections": list(self.active_connections.keys()),
            "authenticated_connections": len(self.authenticated_connections),
            "broadcast_subscribers": {
                sub_type: len(subscribers) 
                for sub_type, subscribers in self.broadcast_subscribers.items()
            }
        }

    async def ping_all_connections(self):
        """Ping all active connections to check connectivity"""
        ping_message = WebSocketMessage("ping", {"timestamp": datetime.utcnow().isoformat()})
        
        for connection_id in list(self.active_connections.keys()):
            try:
                await self.send_personal_message(ping_message, connection_id)
            except Exception as e:
                self.logger.warning(f"Failed to ping connection {connection_id}: {str(e)}")
                await self.disconnect(connection_id)

# Global WebSocket manager instance
websocket_manager = WebSocketManager()