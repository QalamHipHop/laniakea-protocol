"""
Notification Service
Manages user notifications, alerts, and messaging
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from .websocket_manager import WebSocketManager, WebSocketMessage, ConnectionType

class NotificationType(Enum):
    """Types of notifications"""
    SYSTEM = "system"
    SECURITY = "security"
    TRANSACTION = "transaction"
    TASK = "task"
    GOVERNANCE = "governance"
    MARKET = "market"
    SOCIAL = "social"
    PERFORMANCE = "performance"

class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class Notification:
    """Represents a notification"""
    id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    data: Optional[Dict[str, Any]] = None
    target_user: Optional[str] = None
    target_role: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    read: bool = False
    read_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert notification to dictionary"""
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "priority": self.priority.value,
            "data": self.data or {},
            "target_user": self.target_user,
            "target_role": self.target_role,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "read": self.read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "metadata": self.metadata
        }

class NotificationService:
    """
    Advanced notification service
    Manages creation, delivery, and persistence of notifications
    """
    
    def __init__(self, websocket_manager: WebSocketManager):
        self.logger = logging.getLogger("NotificationService")
        self.websocket_manager = websocket_manager
        
        # Storage
        self.notifications: Dict[str, Notification] = {}  # id -> notification
        self.user_notifications: Dict[str, Set[str]] = {}  # user_id -> notification_ids
        self.role_subscriptions: Dict[str, Set[str]] = {}  # role -> user_ids
        
        # Queues and processing
        self.delivery_queue = asyncio.Queue()
        self.cleanup_queue = asyncio.Queue()
        
        # Settings
        self.max_notifications_per_user = 1000
        self.default_expiry_hours = 72
        self.batch_delivery_size = 50
        self.delivery_retry_attempts = 3
        
        # Statistics
        self.stats = {
            "total_notifications": 0,
            "notifications_by_type": {nt.value: 0 for nt in NotificationType},
            "notifications_by_priority": {np.value: 0 for np in NotificationPriority},
            "delivered_notifications": 0,
            "failed_deliveries": 0,
            "read_notifications": 0,
            "expired_notifications": 0
        }
        
        # Background tasks
        self.is_running = False
        self.delivery_task = None
        self.cleanup_task = None
        
        self.logger.info("Notification Service initialized")

    async def start(self):
        """Start the notification service"""
        if self.is_running:
            return
        
        self.is_running = True
        self.delivery_task = asyncio.create_task(self._process_deliveries())
        self.cleanup_task = asyncio.create_task(self._process_cleanup())
        
        # Register WebSocket handlers
        self._register_websocket_handlers()
        
        self.logger.info("Notification Service started")

    async def stop(self):
        """Stop the notification service"""
        self.is_running = False
        
        if self.delivery_task:
            self.delivery_task.cancel()
        
        if self.cleanup_task:
            self.cleanup_task.cancel()
        
        self.logger.info("Notification Service stopped")

    async def create_notification(self, 
                                notification_type: NotificationType,
                                title: str,
                                message: str,
                                priority: NotificationPriority = NotificationPriority.NORMAL,
                                data: Optional[Dict[str, Any]] = None,
                                target_user: Optional[str] = None,
                                target_role: Optional[str] = None,
                                expires_in_hours: Optional[int] = None) -> str:
        """Create and queue a notification"""
        
        # Generate unique ID
        notification_id = self._generate_notification_id()
        
        # Set expiry
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        elif self.default_expiry_hours:
            expires_at = datetime.utcnow() + timedelta(hours=self.default_expiry_hours)
        
        # Create notification
        notification = Notification(
            id=notification_id,
            type=notification_type,
            title=title,
            message=message,
            priority=priority,
            data=data,
            target_user=target_user,
            target_role=target_role,
            expires_at=expires_at
        )
        
        # Store notification
        self.notifications[notification_id] = notification
        
        # Add to user notifications
        if target_user:
            await self._add_to_user_notifications(target_user, notification_id)
        
        # Update statistics
        self.stats["total_notifications"] += 1
        self.stats["notifications_by_type"][notification_type.value] += 1
        self.stats["notifications_by_priority"][priority.value] += 1
        
        # Queue for delivery
        await self.delivery_queue.put(notification)
        
        self.logger.info(f"Created notification: {notification_id} ({notification_type.value})")
        return notification_id

    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read"""
        if notification_id not in self.notifications:
            return False
        
        notification = self.notifications[notification_id]
        
        # Check if user is authorized to mark as read
        if notification.target_user != user_id and notification.target_role:
            # Check if user has the role
            if user_id not in self.role_subscriptions.get(notification.target_role, set()):
                return False
        
        notification.read = True
        notification.read_at = datetime.utcnow()
        
        # Update statistics
        self.stats["read_notifications"] += 1
        
        # Send read confirmation
        await self._send_read_confirmation(notification_id, user_id)
        
        return True

    async def get_user_notifications(self, user_id: str, unread_only: bool = False, 
                                    limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get notifications for a user"""
        if user_id not in self.user_notifications:
            return []
        
        notification_ids = list(self.user_notifications[user_id])
        
        # Filter by read status if requested
        if unread_only:
            notification_ids = [
                nid for nid in notification_ids
                if nid in self.notifications and not self.notifications[nid].read
            ]
        
        # Get notifications and sort by creation time
        notifications = []
        for nid in notification_ids:
            if nid in self.notifications:
                notifications.append(self.notifications[nid])
        
        notifications.sort(key=lambda n: n.created_at, reverse=True)
        
        # Apply pagination
        paginated = notifications[offset:offset + limit]
        
        return [n.to_dict() for n in paginated]

    async def get_notification_count(self, user_id: str, unread_only: bool = False) -> int:
        """Get notification count for a user"""
        if user_id not in self.user_notifications:
            return 0
        
        count = 0
        for notification_id in self.user_notifications[user_id]:
            if notification_id in self.notifications:
                notification = self.notifications[notification_id]
                if not unread_only or not notification.read:
                    count += 1
        
        return count

    async def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        if notification_id not in self.notifications:
            return False
        
        notification = self.notifications[notification_id]
        
        # Check authorization
        if notification.target_user != user_id and notification.target_role:
            if user_id not in self.role_subscriptions.get(notification.target_role, set()):
                return False
        
        # Remove from storage
        del self.notifications[notification_id]
        
        # Remove from user notifications
        if user_id in self.user_notifications:
            self.user_notifications[user_id].discard(notification_id)
        
        return True

    def subscribe_to_role(self, user_id: str, role: str):
        """Subscribe user to role-based notifications"""
        if role not in self.role_subscriptions:
            self.role_subscriptions[role] = set()
        
        self.role_subscriptions[role].add(user_id)
        self.logger.info(f"User {user_id} subscribed to role {role}")

    def unsubscribe_from_role(self, user_id: str, role: str):
        """Unsubscribe user from role-based notifications"""
        if role in self.role_subscriptions:
            self.role_subscriptions[role].discard(user_id)
            self.logger.info(f"User {user_id} unsubscribed from role {role}")

    async def _process_deliveries(self):
        """Process notification deliveries"""
        while self.is_running:
            try:
                # Get batch of notifications
                batch = []
                for _ in range(self.batch_delivery_size):
                    try:
                        notification = await asyncio.wait_for(self.delivery_queue.get(), timeout=1.0)
                        batch.append(notification)
                    except asyncio.TimeoutError:
                        break
                
                if batch:
                    await self._deliver_notification_batch(batch)
                
            except Exception as e:
                self.logger.error(f"Error in delivery processing: {str(e)}")
                await asyncio.sleep(5)

    async def _deliver_notification_batch(self, notifications: List[Notification]):
        """Deliver a batch of notifications"""
        for notification in notifications:
            try:
                await self._deliver_single_notification(notification)
            except Exception as e:
                self.logger.error(f"Failed to deliver notification {notification.id}: {str(e)}")
                self.stats["failed_deliveries"] += 1

    async def _deliver_single_notification(self, notification: Notification):
        """Deliver a single notification"""
        target_connections = []
        
        # Determine target connections
        if notification.target_user:
            # Send to specific user connections
            user_connections = self._get_user_connections(notification.target_user)
            target_connections.extend(user_connections)
        
        if notification.target_role:
            # Send to role subscribers
            role_users = self.role_subscriptions.get(notification.target_role, set())
            for user_id in role_users:
                user_connections = self._get_user_connections(user_id)
                target_connections.extend(user_connections)
        
        # Create WebSocket message
        message = WebSocketMessage(
            "notification",
            notification.to_dict()
        )
        
        # Send to all target connections
        delivered = False
        for connection_id in target_connections:
            try:
                await self.websocket_manager.send_personal_message(message, connection_id)
                delivered = True
            except Exception as e:
                self.logger.warning(f"Failed to deliver to connection {connection_id}: {str(e)}")
        
        if delivered:
            self.stats["delivered_notifications"] += 1

    async def _process_cleanup(self):
        """Process cleanup of expired notifications"""
        while self.is_running:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                current_time = datetime.utcnow()
                expired_ids = []
                
                # Find expired notifications
                for notification_id, notification in self.notifications.items():
                    if notification.expires_at and current_time > notification.expires_at:
                        expired_ids.append(notification_id)
                
                # Remove expired notifications
                for notification_id in expired_ids:
                    notification = self.notifications[notification_id]
                    
                    # Remove from user notifications
                    if notification.target_user and notification.target_user in self.user_notifications:
                        self.user_notifications[notification.target_user].discard(notification_id)
                    
                    # Remove from storage
                    del self.notifications[notification_id]
                    self.stats["expired_notifications"] += 1
                
                if expired_ids:
                    self.logger.info(f"Cleaned up {len(expired_ids)} expired notifications")
                
            except Exception as e:
                self.logger.error(f"Error in cleanup processing: {str(e)}")

    async def _add_to_user_notifications(self, user_id: str, notification_id: str):
        """Add notification to user's notification list"""
        if user_id not in self.user_notifications:
            self.user_notifications[user_id] = set()
        
        # Check limit
        if len(self.user_notifications[user_id]) >= self.max_notifications_per_user:
            # Remove oldest notifications
            user_notification_ids = list(self.user_notifications[user_id])
            user_notification_ids.sort(key=lambda nid: self.notifications[nid].created_at)
            
            # Remove oldest 10%
            to_remove = user_notification_ids[:self.max_notifications_per_user // 10]
            for old_id in to_remove:
                self.user_notifications[user_id].discard(old_id)
                if old_id in self.notifications:
                    del self.notifications[old_id]
        
        self.user_notifications[user_id].add(notification_id)

    def _get_user_connections(self, user_id: str) -> List[str]:
        """Get WebSocket connections for a user"""
        # This would integrate with your authentication system
        # For now, return all active connections
        return list(self.websocket_manager.active_connections.keys())

    def _generate_notification_id(self) -> str:
        """Generate unique notification ID"""
        import uuid
        return str(uuid.uuid4())

    async def _send_read_confirmation(self, notification_id: str, user_id: str):
        """Send read confirmation to client"""
        message = WebSocketMessage(
            "notification_read",
            {
                "notification_id": notification_id,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        connections = self._get_user_connections(user_id)
        for connection_id in connections:
            try:
                await self.websocket_manager.send_personal_message(message, connection_id)
            except Exception:
                pass

    def _register_websocket_handlers(self):
        """Register WebSocket message handlers"""
        async def handle_mark_read(connection_id: str, payload: Dict):
            notification_id = payload.get('notification_id')
            user_id = payload.get('user_id')
            
            if notification_id and user_id:
                success = await self.mark_as_read(notification_id, user_id)
                
                response_message = WebSocketMessage(
                    "mark_read_response",
                    {
                        "notification_id": notification_id,
                        "success": success
                    }
                )
                await self.websocket_manager.send_personal_message(response_message, connection_id)
        
        async def handle_get_notifications(connection_id: str, payload: Dict):
            user_id = payload.get('user_id')
            unread_only = payload.get('unread_only', False)
            limit = payload.get('limit', 50)
            offset = payload.get('offset', 0)
            
            if user_id:
                notifications = await self.get_user_notifications(user_id, unread_only, limit, offset)
                count = await self.get_notification_count(user_id, unread_only)
                
                response_message = WebSocketMessage(
                    "notifications_response",
                    {
                        "notifications": notifications,
                        "count": count,
                        "unread_only": unread_only
                    }
                )
                await self.websocket_manager.send_personal_message(response_message, connection_id)
        
        self.websocket_manager.register_handler("mark_notification_read", handle_mark_read)
        self.websocket_manager.register_handler("get_notifications", handle_get_notifications)

    # Convenience methods for common notification types
    async def notify_system(self, title: str, message: str, priority: NotificationPriority = NotificationPriority.NORMAL,
                           data: Optional[Dict] = None, target_user: Optional[str] = None) -> str:
        """Create system notification"""
        return await self.create_notification(
            NotificationType.SYSTEM, title, message, priority, data, target_user
        )

    async def notify_security(self, title: str, message: str, priority: NotificationPriority = NotificationPriority.HIGH,
                            data: Optional[Dict] = None, target_user: Optional[str] = None) -> str:
        """Create security notification"""
        return await self.create_notification(
            NotificationType.SECURITY, title, message, priority, data, target_user
        )

    async def notify_transaction(self, title: str, message: str, data: Optional[Dict] = None,
                               target_user: Optional[str] = None) -> str:
        """Create transaction notification"""
        return await self.create_notification(
            NotificationType.TRANSACTION, title, message, NotificationPriority.NORMAL, data, target_user
        )

    def get_service_statistics(self) -> Dict[str, Any]:
        """Get notification service statistics"""
        return {
            **self.stats,
            "active_users": len(self.user_notifications),
            "role_subscriptions": {
                role: len(users) for role, users in self.role_subscriptions.items()
            },
            "queue_size": self.delivery_queue.qsize(),
            "cleanup_queue_size": self.cleanup_queue.qsize()
        }

# Global notification service instance (will be initialized in main.py)
notification_service = None