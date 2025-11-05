"""
Real-time Update System
Provides real-time updates for various blockchain and system events
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from .websocket_manager import WebSocketManager, WebSocketMessage, ConnectionType

class UpdateType(Enum):
    """Types of real-time updates"""
    BLOCK_MINED = "block_mined"
    TRANSACTION_CONFIRMED = "transaction_confirmed"
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    SOLUTION_SUBMITTED = "solution_submitted"
    PROPOSAL_CREATED = "proposal_created"
    VOTE_CAST = "vote_cast"
    MARKET_UPDATE = "market_update"
    SYSTEM_ALERT = "system_alert"
    PERFORMANCE_METRIC = "performance_metric"
    SECURITY_EVENT = "security_event"
    NETWORK_STATUS = "network_status"

@dataclass
class UpdateEvent:
    """Represents a real-time update event"""
    event_type: UpdateType
    data: Dict[str, Any]
    priority: str = "normal"  # low, normal, high, critical
    target_audience: Optional[List[ConnectionType]] = None
    expiration: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.target_audience is None:
            self.target_audience = [ConnectionType.DASHBOARD]
        
        # Set default expiration (24 hours from now)
        if self.expiration is None:
            self.expiration = datetime.utcnow() + timedelta(hours=24)

class RealtimeUpdateSystem:
    """
    Advanced real-time update system
    Manages event streams, filtering, and targeted updates
    """
    
    def __init__(self, websocket_manager: WebSocketManager):
        self.logger = logging.getLogger("RealtimeUpdateSystem")
        self.websocket_manager = websocket_manager
        
        # Event management
        self.event_queue = asyncio.Queue()
        self.event_handlers: Dict[UpdateType, List[Callable]] = {}
        self.active_subscriptions: Dict[str, List[UpdateType]] = {}
        
        # Update statistics
        self.update_stats = {
            "events_processed": 0,
            "events_by_type": {event_type.value: 0 for event_type in UpdateType},
            "events_by_priority": {"low": 0, "normal": 0, "high": 0, "critical": 0},
            "failed_events": 0
        }
        
        # Event history (for debugging and analytics)
        self.event_history: List[Dict] = []
        self.max_history_size = 1000
        
        # Filtering and routing
        self.event_filters: Dict[str, Callable] = {}
        self.priority_handlers = {
            "critical": self._handle_critical_event,
            "high": self._handle_high_priority_event,
            "normal": self._handle_normal_event,
            "low": self._handle_low_priority_event
        }
        
        # Background tasks
        self.is_running = False
        self.processing_task = None
        self.cleanup_task = None
        
        self.logger.info("Real-time Update System initialized")

    async def start(self):
        """Start the real-time update system"""
        if self.is_running:
            return
        
        self.is_running = True
        self.processing_task = asyncio.create_task(self._process_events())
        self.cleanup_task = asyncio.create_task(self._cleanup_expired_events())
        
        # Register WebSocket handlers
        self._register_websocket_handlers()
        
        self.logger.info("Real-time Update System started")

    async def stop(self):
        """Stop the real-time update system"""
        self.is_running = False
        
        if self.processing_task:
            self.processing_task.cancel()
        
        if self.cleanup_task:
            self.cleanup_task.cancel()
        
        self.logger.info("Real-time Update System stopped")

    def publish_event(self, event: UpdateEvent):
        """Publish an event to be processed"""
        try:
            # Add to queue
            asyncio.create_task(self.event_queue.put(event))
            self.logger.debug(f"Published event: {event.event_type.value}")
        except Exception as e:
            self.logger.error(f"Failed to publish event: {str(e)}")
            self.update_stats["failed_events"] += 1

    def subscribe_to_updates(self, connection_id: str, update_types: List[UpdateType]):
        """Subscribe a connection to specific update types"""
        self.active_subscriptions[connection_id] = update_types
        self.logger.info(f"Connection {connection_id} subscribed to updates: {[ut.value for ut in update_types]}")

    def unsubscribe_from_updates(self, connection_id: str):
        """Unsubscribe a connection from updates"""
        if connection_id in self.active_subscriptions:
            del self.active_subscriptions[connection_id]
            self.logger.info(f"Connection {connection_id} unsubscribed from updates")

    def register_event_handler(self, event_type: UpdateType, handler: Callable):
        """Register a custom event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        self.logger.info(f"Registered handler for event type: {event_type.value}")

    async def _process_events(self):
        """Main event processing loop"""
        while self.is_running:
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                await self._handle_event(event)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error in event processing loop: {str(e)}")
                await asyncio.sleep(1)

    async def _handle_event(self, event: UpdateEvent):
        """Handle a single event"""
        try:
            # Update statistics
            self.update_stats["events_processed"] += 1
            self.update_stats["events_by_type"][event.event_type.value] += 1
            self.update_stats["events_by_priority"][event.priority] += 1
            
            # Add to history
            self._add_to_history(event)
            
            # Check if event has expired
            if datetime.utcnow() > event.expiration:
                self.logger.debug(f"Event expired: {event.event_type.value}")
                return
            
            # Apply filters
            if not await self._apply_filters(event):
                return
            
            # Execute custom handlers
            await self._execute_custom_handlers(event)
            
            # Handle based on priority
            if event.priority in self.priority_handlers:
                await self.priority_handlers[event.priority](event)
            else:
                await self._handle_normal_event(event)
            
        except Exception as e:
            self.logger.error(f"Error handling event {event.event_type.value}: {str(e)}")
            self.update_stats["failed_events"] += 1

    async def _handle_critical_event(self, event: UpdateEvent):
        """Handle critical priority events"""
        # Create urgent message
        message = WebSocketMessage(
            "critical_update",
            {
                "event_type": event.event_type.value,
                "data": event.data,
                "priority": event.priority,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Broadcast to all connections immediately
        await self.websocket_manager.broadcast_to_all(message)
        
        # Also send to dashboard with special alert
        dashboard_message = WebSocketMessage(
            "system_alert",
            {
                "level": "critical",
                "title": f"Critical Event: {event.event_type.value}",
                "message": event.data.get("message", "Critical system event occurred"),
                "data": event.data
            }
        )
        await self.websocket_manager.broadcast_to_type(dashboard_message, ConnectionType.DASHBOARD)

    async def _handle_high_priority_event(self, event: UpdateEvent):
        """Handle high priority events"""
        message = WebSocketMessage(
            "high_priority_update",
            {
                "event_type": event.event_type.value,
                "data": event.data,
                "priority": event.priority,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Broadcast to specific audience types
        for conn_type in event.target_audience:
            await self.websocket_manager.broadcast_to_type(message, conn_type)

    async def _handle_normal_event(self, event: UpdateEvent):
        """Handle normal priority events"""
        message = WebSocketMessage(
            "update",
            {
                "event_type": event.event_type.value,
                "data": event.data,
                "priority": event.priority,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Send to subscribed connections only
        for connection_id, subscribed_types in self.active_subscriptions.items():
            if event.event_type in subscribed_types:
                await self.websocket_manager.send_personal_message(message, connection_id)

    async def _handle_low_priority_event(self, event: UpdateEvent):
        """Handle low priority events (batch processing)"""
        # For low priority events, we might want to batch them
        message = WebSocketMessage(
            "low_priority_update",
            {
                "event_type": event.event_type.value,
                "data": event.data,
                "priority": event.priority,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Send only to dashboard for monitoring
        await self.websocket_manager.broadcast_to_type(message, ConnectionType.DASHBOARD)

    async def _apply_filters(self, event: UpdateEvent) -> bool:
        """Apply registered filters to event"""
        for filter_name, filter_func in self.event_filters.items():
            try:
                if not filter_func(event):
                    self.logger.debug(f"Event filtered by {filter_name}: {event.event_type.value}")
                    return False
            except Exception as e:
                self.logger.error(f"Error in filter {filter_name}: {str(e)}")
        
        return True

    async def _execute_custom_handlers(self, event: UpdateEvent):
        """Execute custom event handlers"""
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    self.logger.error(f"Error in custom handler for {event.event_type.value}: {str(e)}")

    def _add_to_history(self, event: UpdateEvent):
        """Add event to history"""
        history_entry = {
            "event_type": event.event_type.value,
            "data": event.data,
            "priority": event.priority,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": event.metadata
        }
        
        self.event_history.append(history_entry)
        
        # Maintain history size
        if len(self.event_history) > self.max_history_size:
            self.event_history = self.event_history[-self.max_history_size:]

    async def _cleanup_expired_events(self):
        """Clean up expired events and data"""
        while self.is_running:
            try:
                # Clean up expired subscriptions
                current_time = datetime.utcnow()
                expired_subscriptions = []
                
                for connection_id in list(self.active_subscriptions.keys()):
                    # Check if connection still exists
                    if connection_id not in self.websocket_manager.active_connections:
                        expired_subscriptions.append(connection_id)
                
                for conn_id in expired_subscriptions:
                    self.unsubscribe_from_updates(conn_id)
                
                # Sleep for 5 minutes before next cleanup
                await asyncio.sleep(300)
                
            except Exception as e:
                self.logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(60)

    def _register_websocket_handlers(self):
        """Register WebSocket message handlers"""
        async def handle_subscribe(connection_id: str, payload: Dict):
            update_types = []
            for type_str in payload.get('update_types', []):
                try:
                    update_type = UpdateType(type_str)
                    update_types.append(update_type)
                except ValueError:
                    continue
            
            if update_types:
                self.subscribe_to_updates(connection_id, update_types)
        
        self.websocket_manager.register_handler("subscribe_updates", handle_subscribe)

    # Convenience methods for common event types
    def publish_block_mined(self, block_data: Dict):
        """Publish block mined event"""
        event = UpdateEvent(
            event_type=UpdateType.BLOCK_MINED,
            data=block_data,
            priority="high",
            target_audience=[ConnectionType.BLOCKCHAIN, ConnectionType.DASHBOARD]
        )
        self.publish_event(event)

    def publish_transaction_confirmed(self, transaction_data: Dict):
        """Publish transaction confirmed event"""
        event = UpdateEvent(
            event_type=UpdateType.TRANSACTION_CONFIRMED,
            data=transaction_data,
            priority="normal",
            target_audience=[ConnectionType.BLOCKCHAIN]
        )
        self.publish_event(event)

    def publish_task_created(self, task_data: Dict):
        """Publish task created event"""
        event = UpdateEvent(
            event_type=UpdateType.TASK_CREATED,
            data=task_data,
            priority="normal",
            target_audience=[ConnectionType.TASKS, ConnectionType.DASHBOARD]
        )
        self.publish_event(event)

    def publish_system_alert(self, alert_data: Dict, priority: str = "normal"):
        """Publish system alert"""
        event = UpdateEvent(
            event_type=UpdateType.SYSTEM_ALERT,
            data=alert_data,
            priority=priority,
            target_audience=[ConnectionType.DASHBOARD, ConnectionType.NOTIFICATIONS]
        )
        self.publish_event(event)

    def get_update_statistics(self) -> Dict:
        """Get update system statistics"""
        return {
            **self.update_stats,
            "active_subscriptions": len(self.active_subscriptions),
            "registered_handlers": {
                event_type.value: len(handlers)
                for event_type, handlers in self.event_handlers.items()
            },
            "event_history_size": len(self.event_history),
            "queue_size": self.event_queue.qsize()
        }

    def get_recent_events(self, limit: int = 50) -> List[Dict]:
        """Get recent events from history"""
        return self.event_history[-limit:]

# Global update system instance (will be initialized in main.py)
update_system = None