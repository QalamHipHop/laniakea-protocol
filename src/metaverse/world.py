"""
Laniakea Protocol - Metaverse System
سیستم متاورس و جهان مجازی
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from time import time
import json


class EntityType(str, Enum):
    """نوع موجودیت"""
    AVATAR = "avatar"
    OBJECT = "object"
    BUILDING = "building"
    PORTAL = "portal"
    NFT = "nft"


@dataclass
class Vector3:
    """بردار 3 بُعدی"""
    x: float
    y: float
    z: float
    
    def distance_to(self, other: 'Vector3') -> float:
        """محاسبه فاصله"""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return np.sqrt(dx**2 + dy**2 + dz**2)
    
    def to_dict(self) -> Dict:
        return {"x": self.x, "y": self.y, "z": self.z}


@dataclass
class Entity:
    """موجودیت در متاورس"""
    id: str
    entity_type: EntityType
    owner_did: str
    
    # موقعیت و جهت
    position: Vector3
    rotation: Vector3
    scale: Vector3
    
    # ویژگی‌ها
    properties: Dict
    metadata: Dict
    
    # تعامل
    interactable: bool = True
    visible: bool = True
    
    # زمان
    created_at: float = 0.0
    updated_at: float = 0.0


class Avatar:
    """
    آواتار کاربر در متاورس
    """
    
    def __init__(
        self,
        did: str,
        name: str,
        position: Vector3 = None
    ):
        self.did = did
        self.name = name
        self.position = position or Vector3(0, 0, 0)
        self.rotation = Vector3(0, 0, 0)
        
        # وضعیت
        self.health = 100.0
        self.energy = 100.0
        self.level = 1
        self.experience = 0.0
        
        # اینونتوری
        self.inventory: List[str] = []
        
        # فعالیت
        self.last_active = time()
        self.online = True
        
        print(f"👤 Avatar created: {name}")
    
    def move_to(self, target: Vector3):
        """حرکت به مقصد"""
        self.position = target
        self.last_active = time()
    
    def add_experience(self, amount: float):
        """افزودن تجربه"""
        self.experience += amount
        
        # سطح بندی
        required_exp = self.level * 100
        if self.experience >= required_exp:
            self.level += 1
            self.experience -= required_exp
            print(f"⬆️ {self.name} leveled up to {self.level}!")
    
    def add_item(self, item_id: str):
        """افزودن آیتم"""
        self.inventory.append(item_id)
    
    def to_dict(self) -> Dict:
        return {
            "did": self.did,
            "name": self.name,
            "position": self.position.to_dict(),
            "level": self.level,
            "health": self.health,
            "energy": self.energy,
            "online": self.online
        }


class Region:
    """
    منطقه در متاورس
    
    هر منطقه یک فضای 3D است
    """
    
    def __init__(
        self,
        region_id: str,
        name: str,
        size: Tuple[float, float, float] = (1000, 1000, 1000)
    ):
        self.region_id = region_id
        self.name = name
        self.size = size
        
        # موجودیت‌ها
        self.entities: Dict[str, Entity] = {}
        
        # آواتارها
        self.avatars: Dict[str, Avatar] = {}
        
        # محیط
        self.environment = {
            "time_of_day": 12.0,  # 0-24
            "weather": "clear",
            "temperature": 20.0,
            "gravity": 9.8
        }
        
        # قوانین
        self.rules = {
            "allow_flying": True,
            "allow_building": True,
            "pvp_enabled": False
        }
        
        print(f"🌍 Region created: {name}")
    
    def add_entity(self, entity: Entity):
        """افزودن موجودیت"""
        self.entities[entity.id] = entity
    
    def remove_entity(self, entity_id: str):
        """حذف موجودیت"""
        if entity_id in self.entities:
            del self.entities[entity_id]
    
    def add_avatar(self, avatar: Avatar):
        """افزودن آواتار"""
        self.avatars[avatar.did] = avatar
        print(f"👋 {avatar.name} entered {self.name}")
    
    def remove_avatar(self, did: str):
        """حذف آواتار"""
        if did in self.avatars:
            avatar = self.avatars[did]
            del self.avatars[did]
            print(f"👋 {avatar.name} left {self.name}")
    
    def get_nearby_entities(
        self,
        position: Vector3,
        radius: float
    ) -> List[Entity]:
        """دریافت موجودیت‌های نزدیک"""
        nearby = []
        for entity in self.entities.values():
            if entity.position.distance_to(position) <= radius:
                nearby.append(entity)
        return nearby
    
    def get_nearby_avatars(
        self,
        position: Vector3,
        radius: float
    ) -> List[Avatar]:
        """دریافت آواتارهای نزدیک"""
        nearby = []
        for avatar in self.avatars.values():
            if avatar.position.distance_to(position) <= radius:
                nearby.append(avatar)
        return nearby
    
    def update_environment(self, delta_time: float):
        """به‌روزرسانی محیط"""
        # پیشروی زمان
        self.environment["time_of_day"] += delta_time / 3600
        if self.environment["time_of_day"] >= 24:
            self.environment["time_of_day"] -= 24
    
    def get_stats(self) -> Dict:
        """آمار منطقه"""
        return {
            "name": self.name,
            "entities": len(self.entities),
            "avatars": len(self.avatars),
            "online_avatars": len([a for a in self.avatars.values() if a.online]),
            "environment": self.environment
        }


class MetaverseWorld:
    """
    جهان متاورس کامل
    
    مدیریت مناطق، آواتارها و تعاملات
    """
    
    def __init__(self):
        self.regions: Dict[str, Region] = {}
        self.avatars: Dict[str, Avatar] = {}
        
        # پورتال‌ها (اتصال بین مناطق)
        self.portals: Dict[str, Tuple[str, str, Vector3, Vector3]] = {}
        
        # رویدادها
        self.events: List[Dict] = []
        
        # زمان
        self.world_time = 0.0
        
        print("🌌 Metaverse World initialized")
    
    def create_region(
        self,
        region_id: str,
        name: str,
        size: Tuple[float, float, float] = (1000, 1000, 1000)
    ) -> Region:
        """ایجاد منطقه جدید"""
        region = Region(region_id, name, size)
        self.regions[region_id] = region
        return region
    
    def create_avatar(
        self,
        did: str,
        name: str,
        spawn_region: str
    ) -> Optional[Avatar]:
        """ایجاد آواتار"""
        if spawn_region not in self.regions:
            return None
        
        avatar = Avatar(did, name)
        self.avatars[did] = avatar
        
        # اضافه کردن به منطقه
        self.regions[spawn_region].add_avatar(avatar)
        
        return avatar
    
    def teleport_avatar(
        self,
        did: str,
        target_region: str,
        target_position: Vector3
    ) -> bool:
        """تلپورت آواتار"""
        if did not in self.avatars:
            return False
        
        if target_region not in self.regions:
            return False
        
        avatar = self.avatars[did]
        
        # حذف از منطقه فعلی
        for region in self.regions.values():
            if did in region.avatars:
                region.remove_avatar(did)
        
        # افزودن به منطقه جدید
        avatar.position = target_position
        self.regions[target_region].add_avatar(avatar)
        
        print(f"✨ {avatar.name} teleported to {self.regions[target_region].name}")
        return True
    
    def create_portal(
        self,
        portal_id: str,
        from_region: str,
        to_region: str,
        from_position: Vector3,
        to_position: Vector3
    ):
        """ایجاد پورتال"""
        self.portals[portal_id] = (from_region, to_region, from_position, to_position)
        
        # ایجاد موجودیت پورتال
        if from_region in self.regions:
            portal_entity = Entity(
                id=portal_id,
                entity_type=EntityType.PORTAL,
                owner_did="system",
                position=from_position,
                rotation=Vector3(0, 0, 0),
                scale=Vector3(2, 3, 0.5),
                properties={"destination": to_region},
                metadata={"to_position": to_position.to_dict()}
            )
            self.regions[from_region].add_entity(portal_entity)
        
        print(f"🌀 Portal created: {from_region} -> {to_region}")
    
    def interact(
        self,
        avatar_did: str,
        entity_id: str
    ) -> Optional[Dict]:
        """تعامل با موجودیت"""
        if avatar_did not in self.avatars:
            return None
        
        avatar = self.avatars[avatar_did]
        
        # پیدا کردن موجودیت
        entity = None
        for region in self.regions.values():
            if entity_id in region.entities:
                entity = region.entities[entity_id]
                break
        
        if not entity:
            return None
        
        # بررسی فاصله
        if avatar.position.distance_to(entity.position) > 10:
            return {"error": "Too far"}
        
        # اجرای تعامل بر اساس نوع
        if entity.entity_type == EntityType.PORTAL:
            # تلپورت
            dest_region = entity.properties.get("destination")
            dest_pos_dict = entity.metadata.get("to_position", {})
            dest_pos = Vector3(**dest_pos_dict)
            
            self.teleport_avatar(avatar_did, dest_region, dest_pos)
            
            return {"action": "teleport", "destination": dest_region}
        
        elif entity.entity_type == EntityType.NFT:
            # جمع‌آوری NFT
            avatar.add_item(entity_id)
            avatar.add_experience(50)
            
            return {"action": "collect", "item": entity_id}
        
        return {"action": "interact", "entity": entity_id}
    
    def update(self, delta_time: float = 1.0):
        """به‌روزرسانی جهان"""
        self.world_time += delta_time
        
        # به‌روزرسانی مناطق
        for region in self.regions.values():
            region.update_environment(delta_time)
        
        # بررسی آواتارهای آفلاین
        for avatar in self.avatars.values():
            if time() - avatar.last_active > 300:  # 5 دقیقه
                avatar.online = False
    
    def get_world_stats(self) -> Dict:
        """آمار جهان"""
        total_avatars = len(self.avatars)
        online_avatars = len([a for a in self.avatars.values() if a.online])
        
        return {
            "world_time": self.world_time,
            "regions": len(self.regions),
            "total_avatars": total_avatars,
            "online_avatars": online_avatars,
            "portals": len(self.portals),
            "events": len(self.events)
        }
    
    def get_region_stats(self, region_id: str) -> Optional[Dict]:
        """آمار منطقه"""
        if region_id not in self.regions:
            return None
        return self.regions[region_id].get_stats()


class SocialSpace:
    """
    فضای اجتماعی
    
    مکان‌های تعامل اجتماعی در متاورس
    """
    
    def __init__(self, metaverse: MetaverseWorld):
        self.metaverse = metaverse
        
        # اتاق‌های چت
        self.chat_rooms: Dict[str, List[str]] = {}
        
        # رویدادها
        self.social_events: List[Dict] = []
        
        print("💬 Social Space initialized")
    
    def create_chat_room(self, room_id: str, region_id: str):
        """ایجاد اتاق چت"""
        self.chat_rooms[room_id] = []
        print(f"💬 Chat room created: {room_id}")
    
    def join_chat_room(self, room_id: str, avatar_did: str):
        """پیوستن به اتاق چت"""
        if room_id not in self.chat_rooms:
            self.create_chat_room(room_id, "default")
        
        if avatar_did not in self.chat_rooms[room_id]:
            self.chat_rooms[room_id].append(avatar_did)
    
    def send_message(
        self,
        room_id: str,
        sender_did: str,
        message: str
    ) -> Dict:
        """ارسال پیام"""
        if room_id not in self.chat_rooms:
            return {"error": "Room not found"}
        
        if sender_did not in self.chat_rooms[room_id]:
            return {"error": "Not in room"}
        
        msg = {
            "room_id": room_id,
            "sender": sender_did,
            "message": message,
            "timestamp": time()
        }
        
        return msg
    
    def create_event(
        self,
        event_id: str,
        title: str,
        region_id: str,
        start_time: float,
        duration: float
    ):
        """ایجاد رویداد اجتماعی"""
        event = {
            "id": event_id,
            "title": title,
            "region_id": region_id,
            "start_time": start_time,
            "duration": duration,
            "participants": []
        }
        
        self.social_events.append(event)
        print(f"🎉 Event created: {title}")
    
    def get_stats(self) -> Dict:
        """آمار فضای اجتماعی"""
        return {
            "chat_rooms": len(self.chat_rooms),
            "total_participants": sum(len(members) for members in self.chat_rooms.values()),
            "events": len(self.social_events)
        }
