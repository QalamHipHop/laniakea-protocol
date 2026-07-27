"""
LaniakeA Protocol - P2P Network Module
Handles node discovery, blockchain synchronization, and message passing.
"""

import asyncio
import websockets
import json
import logging
import time
from typing import Set, Dict, Any, Optional, List
from urllib.parse import urlparse

logger = logging.getLogger("P2PNetwork")

class P2PNetwork:
    """
    Peer-to-Peer Network Manager
    """
    
    def __init__(self, node_url: str, blockchain):
        self.node_url = node_url
        self.blockchain = blockchain
        self.peers: Set[str] = set()
        self.connected_peers: Dict[str, websockets.WebSocketClientProtocol] = {}
        self.is_running = False
        self.discovery_task = None
        self.sync_task = None
        self.server = None
        
        self.logger = logging.getLogger("P2PNetwork")
        self.logger.info(f"P2P Network initialized for node: {self.node_url}")
        
    async def start(self):
        """Start the P2P server and client tasks"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start WebSocket server
        parsed_url = urlparse(self.node_url)
        host = parsed_url.hostname or "0.0.0.0"
        port = parsed_url.port or 8000
        
        # Note: FastAPI (uvicorn) is already running on the main port.
        # We'll use a separate port for P2P communication for simplicity in this model.
        # In a real app, the same port might be used with different paths.
        p2p_port = port + 1
        
        self.server = await websockets.serve(self._handle_connection, host, p2p_port)
        self.logger.info(f"P2P Server listening on ws://{host}:{p2p_port}")
        
        # Start background tasks
        self.discovery_task = asyncio.create_task(self._peer_discovery())
        self.sync_task = asyncio.create_task(self._blockchain_sync())
        
        self.logger.info("P2P Network started")
        
    async def stop(self):
        """Stop the P2P network"""
        self.is_running = False
        
        if self.discovery_task:
            self.discovery_task.cancel()
        if self.sync_task:
            self.sync_task.cancel()
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            
        for peer_url, ws in self.connected_peers.items():
            await ws.close()
            
        self.logger.info("P2P Network stopped")
        
    async def _handle_connection(self, websocket, path):
        """Handle incoming WebSocket connections"""
        peer_url = websocket.remote_address[0] + ":" + str(websocket.remote_address[1])
        self.logger.info(f"Incoming connection from: {peer_url}")
        
        try:
            async for message in websocket:
                await self._handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosedOK:
            self.logger.info(f"Connection closed with {peer_url}")
        except Exception as e:
            self.logger.error(f"Error handling connection from {peer_url}: {e}")
        finally:
            # Remove peer from connected list
            if peer_url in self.connected_peers:
                del self.connected_peers[peer_url]
                
    async def _handle_message(self, websocket, message: str):
        """Process incoming P2P messages"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            payload = data.get("payload")
            
            if message_type == "GET_CHAIN":
                await self._send_message(websocket, "CHAIN", self.blockchain.to_dict())
                
            elif message_type == "CHAIN":
                await self._handle_received_chain(payload)
                
            elif message_type == "NEW_BLOCK":
                await self._handle_new_block(payload)
                
            elif message_type == "NEW_TRANSACTION":
                await self._handle_new_transaction(payload)
                
            elif message_type == "GET_PEERS":
                await self._send_message(websocket, "PEERS", list(self.peers))
                
            elif message_type == "PEERS":
                await self._handle_received_peers(payload)
                
            else:
                self.logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            self.logger.error("Received invalid JSON message")
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            
    async def _send_message(self, websocket, message_type: str, payload: Any):
        """Send a message over a WebSocket"""
        message = json.dumps({"type": message_type, "payload": payload})
        await websocket.send(message)
        
    async def broadcast(self, message_type: str, payload: Any):
        """Broadcast a message to all connected peers"""
        message = json.dumps({"type": message_type, "payload": payload})
        
        # Use a copy of the keys to avoid RuntimeError: Set changed size during iteration
        for peer_url, ws in list(self.connected_peers.items()):
            try:
                await ws.send(message)
            except websockets.exceptions.ConnectionClosed:
                self.logger.warning(f"Peer {peer_url} disconnected during broadcast")
                del self.connected_peers[peer_url]
            except Exception as e:
                self.logger.error(f"Error broadcasting to {peer_url}: {e}")
                
    async def _peer_discovery(self):
        """Periodically discover and connect to new peers"""
        while self.is_running:
            try:
                # 1. Connect to known peers
                for peer_url in self.peers:
                    if peer_url not in self.connected_peers and peer_url != self.node_url:
                        await self._connect_to_peer(peer_url)
                        
                # 2. Ask connected peers for their peer lists
                for peer_url, ws in self.connected_peers.items():
                    await self._send_message(ws, "GET_PEERS", None)
                    
                # 3. Add a few bootstrap nodes (simplified)
                bootstrap_nodes = ["ws://127.0.0.1:8001", "ws://127.0.0.1:8002"]
                for node in bootstrap_nodes:
                    if node not in self.peers and node != self.node_url:
                        self.peers.add(node)
                        
            except Exception as e:
                self.logger.error(f"Error in peer discovery: {e}")
                
            await asyncio.sleep(60) # Discover every minute
            
    async def _connect_to_peer(self, peer_url: str):
        """Establish a connection to a peer"""
        try:
            self.logger.info(f"Connecting to peer: {peer_url}")
            ws = await websockets.connect(peer_url, ping_interval=20, ping_timeout=20)
            self.connected_peers[peer_url] = ws
            self.logger.info(f"Successfully connected to peer: {peer_url}")
            
            # Start a listener task for this peer
            asyncio.create_task(self._listen_to_peer(ws, peer_url))
            
            # Request chain and peer list immediately
            await self._send_message(ws, "GET_CHAIN", None)
            await self._send_message(ws, "GET_PEERS", None)
            
        except Exception as e:
            self.logger.warning(f"Failed to connect to peer {peer_url}: {e}")
            if peer_url in self.peers:
                self.peers.remove(peer_url) # Remove failed peer
                
    async def _listen_to_peer(self, websocket, peer_url: str):
        """Listen for messages from a connected peer"""
        try:
            async for message in websocket:
                await self._handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Peer {peer_url} disconnected")
        except Exception as e:
            self.logger.error(f"Error listening to peer {peer_url}: {e}")
        finally:
            if peer_url in self.connected_peers:
                del self.connected_peers[peer_url]
                
    async def _handle_received_peers(self, peer_list: List[str]):
        """Add new peers to the known list"""
        for peer_url in peer_list:
            if peer_url not in self.peers and peer_url != self.node_url:
                self.peers.add(peer_url)
                self.logger.info(f"Discovered new peer: {peer_url}")
                
    async def _blockchain_sync(self):
        """Periodically synchronize the blockchain with peers"""
        while self.is_running:
            try:
                if not self.connected_peers:
                    await asyncio.sleep(10)
                    continue
                    
                # Request chain from a random peer (simplified)
                peer_url = next(iter(self.connected_peers.keys()))
                ws = self.connected_peers[peer_url]
                
                self.logger.info(f"Requesting chain from {peer_url} for sync...")
                await self._send_message(ws, "GET_CHAIN", None)
                
            except Exception as e:
                self.logger.error(f"Error in blockchain sync: {e}")
                
            await asyncio.sleep(30) # Sync every 30 seconds
            
    async def _handle_received_chain(self, chain_data: Dict[str, Any]):
        """Replace the current chain with a longer, valid chain"""
        
        # Simplified chain replacement logic
        received_chain = chain_data.get("chain", [])
        
        if len(received_chain) > len(self.blockchain.chain):
            self.logger.info(f"Received longer chain (len: {len(received_chain)}). Validating...")
            
            # Note: Full validation is complex and omitted here for brevity.
            # Assuming the received chain is valid for this model.
            
            # Replace chain (simplified)
            # self.blockchain.replace_chain(received_chain) 
            self.logger.warning("Chain replacement logic is simplified/omitted.")
            
        else:
            self.logger.info("Received chain is not longer. No sync needed.")
            
    async def _handle_new_block(self, block_data: Dict[str, Any]):
        """Handle a new block received from a peer"""
        # Simplified block addition logic
        self.logger.info(f"Received new block: {block_data.get('index')}")
        # self.blockchain.add_block(block_data) # Full logic omitted
        
    async def _handle_new_transaction(self, transaction_data: Dict[str, Any]):
        """Handle a new transaction received from a peer"""
        # Simplified transaction addition logic
        self.logger.info(f"Received new transaction: {transaction_data.get('transaction_id')}")
        # self.blockchain.add_transaction(transaction_data) # Full logic omitted

# Global P2P instance (will be initialized in main.py)
p2p_network: Optional[P2PNetwork] = None
