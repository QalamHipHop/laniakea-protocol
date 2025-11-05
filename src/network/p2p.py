"""
Laniakea Protocol - P2P Network Manager
مدیریت شبکه همتا به همتا
"""

import asyncio
import websockets
import json
from typing import Callable, Set, Dict, Any


class P2PManager:
    """
    مدیر شبکه P2P
    """

    def __init__(self, host: str, port: int, message_handler: Callable):
        """
        Args:
            host: آدرس هاست
            port: پورت
            message_handler: تابع مدیریت پیام‌ها
        """
        self.host = host
        self.port = port
        self.server = None
        self.peers: Set[websockets.WebSocketServerProtocol] = set()
        self.message_handler = message_handler

        print(f"🔗 P2P Manager initialized for {host}:{port}")

    async def start(self):
        """شروع سرور P2P"""
        self.server = await websockets.serve(self.handler, self.host, self.port)
        print(f"🔗 P2P Node listening at ws://{self.host}:{self.port}")

        # نگه داشتن سرور
        await asyncio.Future()

    async def handler(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """
        مدیریت اتصال یک peer

        Args:
            websocket: WebSocket connection
            path: مسیر
        """
        # افزودن peer
        self.peers.add(websocket)
        peer_addr = websocket.remote_address
        print(f"👋 New peer connected: {peer_addr}")

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.message_handler(data)
                except json.JSONDecodeError:
                    print(f"⚠️ Invalid JSON from {peer_addr}")
                except Exception as e:
                    print(f"⚠️ Error handling message from {peer_addr}: {e}")

        except websockets.ConnectionClosed:
            print(f"👋 Peer disconnected: {peer_addr}")
        finally:
            self.peers.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """
        ارسال پیام به تمام peers

        Args:
            message: پیام (دیکشنری)
        """
        if not self.peers:
            return

        message_json = json.dumps(message)

        # ارسال به تمام peers
        await asyncio.gather(
            *[peer.send(message_json) for peer in self.peers], return_exceptions=True
        )

    async def send_to_peer(self, peer: websockets.WebSocketServerProtocol, message: Dict[str, Any]):
        """
        ارسال پیام به یک peer خاص

        Args:
            peer: peer
            message: پیام
        """
        try:
            await peer.send(json.dumps(message))
        except Exception as e:
            print(f"⚠️ Error sending to peer: {e}")

    def get_network_stats(self) -> Dict[str, Any]:
        """دریافت آمار شبکه"""
        # آمار شبکه باید شامل اطلاعاتی مانند تعداد peers متصل، ترافیک، و TPS باشد.
        # در حال حاضر، فقط تعداد peers را برمی‌گردانیم.
        return {
            "connected_peers": len(self.peers),
            "tps": 0.0,  # باید در آینده محاسبه شود
            "host": self.host,
            "port": self.port,
        }

    async def stop(self):
        """توقف سرور P2P"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("🔗 P2P Node stopped.")

    async def connect_to_peer(self, host: str, port: int):
        """
        اتصال به یک peer خارجی

        Args:
            host: آدرس
            port: پورت
        """
        try:
            uri = f"ws://{host}:{port}"
            async with websockets.connect(uri) as websocket:
                print(f"🔗 Connected to peer: {uri}")

                # دریافت پیام‌ها
                async for message in websocket:
                    data = json.loads(message)
                    await self.message_handler(data)

        except Exception as e:
            print(f"⚠️ Failed to connect to {host}:{port}: {e}")
