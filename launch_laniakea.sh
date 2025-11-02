#!/bin/bash

# ==============================================================================
#  LANIAKEA V2.2 - LAUNCH SINGULARITY SCRIPT (REVISED & EXPANDED)
#  This single script forges the universe, configures it, and launches a
#  functional, synchronized, multi-node network.
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status.

# --- مرحله ۱: آفرینش جهان (Forge the Universe) ---
echo "🔥 Forging Laniakea Universe v2.2 from the master blueprint..."

# ایجاد اسکریپت forge.py که تمام فایل‌های پروژه را می‌سازد.
cat > forge.py << 'EOF'
import os
import textwrap

# این دیکشنری، نقشه کامل و بی‌نقص پروژه است.
PROJECT_STRUCTURE = {
    "requirements.txt": """
        pydantic==2.7.1
        fastapi==0.110.0
        uvicorn[standard]>=0.27.1
        websockets==12.0
        aiohttp==3.9.3
        python-dotenv==1.0.1
        cryptography==42.0.5
        aiosqlite==0.19.0
    """,
    "src/__init__.py": "",
    "src/core/__init__.py": "",
    "src/network/__init__.py": "",
    "src/consensus/__init__.py": "",
    "src/metasystem/__init__.py": "",
    "src/config.py": """
        import os
        from typing import List, Tuple, Set
        from dotenv import load_dotenv

        load_dotenv()
        HOST: str = os.getenv("HOST", "127.0.0.1") # Use 127.0.0.1 for local testing
        BLOCK_REWARD: float = 10.0
        BLOCK_TIME: int = 15 # زمان بلاک کوتاه‌تر برای تست سریع‌تر

        # این مجموعه در زمان اجرا با node_id گره‌های Authority پر می‌شود.
        AUTHORITY_NODES: Set[str] = set()

        def get_bootstrap_nodes() -> List[Tuple[str, int]]:
            nodes_str = os.getenv("BOOTSTRAP_NODES", "")
            if not nodes_str: return []
            nodes = []
            for node_str in nodes_str.split(','):
                try:
                    host, port_str = node_str.strip().split(':')
                    nodes.append((host, int(port_str)))
                except (ValueError, IndexError): pass
            return nodes

        def is_authority() -> bool:
            return os.getenv("IS_AUTHORITY", "false").lower() == "true"
    """,
    "src/core/models.py": """
        from pydantic import BaseModel, Field
        from typing import Dict, Any, List, Optional, Set

        class ValueVector(BaseModel): knowledge: float = 0.0
        class Task(BaseModel): id: str; title: str; description: str; author_id: str
        class Solution(BaseModel): id: str; task_id: str; solver_id: str; content: str; value_vector: ValueVector
        class Transaction(BaseModel): id: str; sender: str; recipient: str; amount: float; timestamp: float; signature: Optional[str] = None
        class KnowledgeBlock(BaseModel):
            index: int
            timestamp: float
            transactions: List[Transaction]
            solution: Optional[Solution] = None
            author_id: str # The Node ID of the authority who created the block
            previous_hash: str
            signature: str # Signature of the block hash payload by the author

        class NodeInfo(BaseModel): node_id: str; host: str; p2p_port: int; api_port: int; specialties: Set[str] = Field(default_factory=set)

        # مدل‌های مربوط به پیام‌های P2P
        class P2PMessage(BaseModel):
            type: str
            payload: Dict[str, Any]
    """,
    "src/core/wallet.py": """
        import os, hashlib
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives import serialization, hashes
        from cryptography.exceptions import InvalidSignature

        class Wallet:
            def __init__(self, data_dir: str):
                wallet_file = os.path.join(data_dir, "wallet.pem"); os.makedirs(data_dir, exist_ok=True)
                if os.path.exists(wallet_file):
                    with open(wallet_file, "rb") as f: self.private_key = serialization.load_pem_private_key(f.read(), password=None)
                else:
                    self.private_key = ec.generate_private_key(ec.SECP256R1())
                    with open(wallet_file, "wb") as f: f.write(self.private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()))
                self.public_key = self.private_key.public_key(); self.node_id = self._get_node_id()
                os.environ["MY_NODE_ID"] = self.node_id

            def _get_node_id(self) -> str:
                pub_key_bytes = self.public_key.public_bytes(encoding=serialization.Encoding.X962, format=serialization.PublicFormat.CompressedPoint)
                return hashlib.sha256(pub_key_bytes).hexdigest()

            def sign(self, data: bytes) -> str:
                return self.private_key.sign(data, ec.ECDSA(hashes.SHA256())).hex()

            @staticmethod
            def get_public_key_from_node_id(node_id: str) -> ec.EllipticCurvePublicKey:
                # This is a placeholder. In a real system, you'd need a way to fetch
                # the full public key for a given node_id, e.g., from a DHT or a trusted source.
                # For this demo, we can't verify signatures of other nodes without their public key.
                # So we will skip signature verification from other nodes for now.
                # A more advanced implementation is needed for full security.
                return None

            @staticmethod
            def verify_signature(public_key: ec.EllipticCurvePublicKey, signature_hex: str, data: bytes) -> bool:
                try:
                    signature_bytes = bytes.fromhex(signature_hex)
                    public_key.verify(signature_bytes, data, ec.ECDSA(hashes.SHA256()))
                    return True
                except (InvalidSignature, ValueError):
                    return False
    """,
    "src/core/blockchain.py": """
        import hashlib, json
        from time import time
        from typing import List, Optional
        from src.core.models import KnowledgeBlock, Transaction, Solution
        from src.config import BLOCK_REWARD

        class LaniakeaChain:
            def __init__(self, node_id: str):
                self.chain: List[KnowledgeBlock] = []
                self.node_id = node_id

            def create_genesis_block(self):
                genesis_block = KnowledgeBlock(
                    index=0,
                    timestamp=time(),
                    transactions=[],
                    solution=None,
                    author_id="0",
                    previous_hash='0' * 64,
                    signature="genesis_signature" # امضای جنسیس معتبر نیست
                )
                self.chain.append(genesis_block)

            def new_block(self, transactions: List[Transaction], solution: Optional[Solution], previous_hash: str) -> KnowledgeBlock:
                all_txs = list(transactions)
                # جایزه ماینر
                all_txs.insert(0, Transaction(id=self.tx_id(), sender="0", recipient=self.node_id, amount=BLOCK_REWARD, timestamp=time()))
                # جایزه حل‌کننده مسئله
                if solution and solution.value_vector.knowledge > 0:
                    all_txs.insert(1, Transaction(id=self.tx_id(), sender="0", recipient=solution.solver_id, amount=solution.value_vector.knowledge, timestamp=time()))

                block = KnowledgeBlock(
                    index=len(self.chain),
                    timestamp=time(),
                    transactions=all_txs,
                    solution=solution,
                    author_id=self.node_id,
                    previous_hash=previous_hash,
                    signature="" # امضا بعدا اضافه می‌شود
                )
                return block

            def add_block(self, block: KnowledgeBlock, known_authorities: set) -> bool:
                # اعتبارسنجی بلاک جدید قبل از اضافه کردن به زنجیره
                last_block = self.last_block
                if block.index != last_block.index + 1:
                    print(f"❌ Invalid block index: expected {last_block.index + 1}, got {block.index}")
                    return False
                if block.previous_hash != self.hash(last_block):
                    print("❌ Invalid previous hash.")
                    return False
                if block.author_id not in known_authorities:
                    print(f"❌ Block author '{block.author_id[:8]}' is not a known authority.")
                    return False
                # NOTE: Signature verification of foreign blocks is skipped for simplicity,
                # as we don't have a mechanism to exchange full public keys.
                self.chain.append(block)
                return True

            def tx_id(self):
                return hashlib.sha256(str(time.time_ns()).encode()).hexdigest()

            @staticmethod
            def get_block_hash_payload(block: KnowledgeBlock) -> bytes:
                # امضا باید از محتوای هش شده خارج شود
                dump = block.model_dump(exclude={'signature'})
                return json.dumps(dump, sort_keys=True).encode()

            @staticmethod
            def hash(block: KnowledgeBlock) -> str:
                if not block: return '0' * 64
                return hashlib.sha256(LaniakeaChain.get_block_hash_payload(block)).hexdigest()

            @property
            def last_block(self) -> Optional[KnowledgeBlock]:
                return self.chain[-1] if self.chain else None
    """,
    "src/metasystem/cognitive_core.py": """
        from src.core.models import KnowledgeBlock
        class CognitiveCore:
            def __init__(self): print("🧠 Cognitive Core v2.2 Activated.")
            def observe(self, block: KnowledgeBlock):
                if block.solution and block.solution.value_vector.knowledge > 50:
                    print(f"✨ Cognitive Insight: High-knowledge solution '{block.solution.id[:8]}' integrated into the chain by '{block.author_id[:8]}'.")
                else:
                    print(f"📄 Observation: Block #{block.index} processed.")
    """,
    "src/network/p2p.py": """
        import asyncio, websockets, json
        from typing import Callable, Set, Dict, Any, Coroutine, List, Tuple
        from src.core.models import P2PMessage

        class P2PManager:
            def __init__(self, host: str, port: int, message_handler: Callable[[Dict], Coroutine]):
                self.host, self.port = host, port
                self.server = None
                self.peers: Set[websockets.WebSocketClientProtocol] = set()
                self.message_handler = message_handler

            async def start(self):
                self.server = await websockets.serve(self.register_peer, self.host, self.port)
                print(f"🔗 P2P Node listening at ws://{self.host}:{self.port}")

            async def connect_to_bootstrap_nodes(self, bootstrap_nodes: List[Tuple[str, int]]):
                for host, port in bootstrap_nodes:
                    if host == self.host and port == self.port: continue # به خودمان وصل نشویم
                    uri = f"ws://{host}:{port}"
                    try:
                        websocket = await websockets.connect(uri)
                        await self.register_peer(websocket)
                        print(f"🤝 Connected to bootstrap peer: {uri}")
                    except (ConnectionRefusedError, OSError):
                        print(f"⚠️ Could not connect to bootstrap peer: {uri}")

            async def register_peer(self, websocket: websockets.WebSocketServerProtocol):
                if websocket in self.peers: return
                self.peers.add(websocket)
                try:
                    async for message_str in websocket:
                        try:
                            message = P2PMessage.model_validate_json(message_str)
                            await self.message_handler(message.model_dump())
                        except Exception as e:
                            print(f"Error processing message: {e}")
                except websockets.ConnectionClosed:
                    print(f"🚪 Peer disconnected: {websocket.remote_address}")
                finally:
                    self.peers.remove(websocket)

            async def broadcast(self, message: P2PMessage):
                if not self.peers: return
                message_json = message.model_dump_json()
                tasks = [peer.send(message_json) for peer in self.peers]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        peer = list(self.peers)[i]
                        print(f"Failed to send to {peer.remote_address}: {result}")
    """,
    "main.py": """
        import asyncio, argparse, uvicorn, json, hashlib, time
        from fastapi import FastAPI, Body
        from typing import Dict, List, Optional, Set
        from src.config import HOST, get_bootstrap_nodes, is_authority, AUTHORITY_NODES, BLOCK_TIME
        from src.core.models import NodeInfo, Task, Solution, ValueVector, KnowledgeBlock, P2PMessage
        from src.core.blockchain import LaniakeaChain
        from src.core.wallet import Wallet
        from src.network.p2p import P2PManager
        from src.metasystem.cognitive_core import CognitiveCore

        class LaniakeaNode:
            def __init__(self):
                # Core Components
                self.wallet: Optional[Wallet] = None
                self.node_info: Optional[NodeInfo] = None
                self.blockchain: Optional[LaniakeaChain] = None
                self.p2p_manager: Optional[P2PManager] = None
                self.cognitive_core: CognitiveCore = CognitiveCore()
                self.api_app: FastAPI = FastAPI(title="Laniakea Node API v2.2")

                # State Pools
                self.task_pool: Dict[str, Task] = {}
                self.solution_pool: Dict[str, Solution] = {}
                self.known_authorities: Set[str] = set()

            def get_current_miner(self) -> Optional[str]:
                """
                الگوریتم اجماع نوبتی ساده (Simple Round-Robin Consensus)
                بر اساس هش آی‌دی گره، یک ترتیب ثابت برای ماینرها ایجاد می‌کند.
                """
                if not self.known_authorities:
                    return None
                sorted_authorities = sorted(list(self.known_authorities))
                last_block_index = self.blockchain.last_block.index
                miner_index = (last_block_index + 1) % len(sorted_authorities)
                return sorted_authorities[miner_index]

            async def handle_p2p_message(self, data: dict):
                msg_type = data.get('type')
                payload = data.get('payload', {})
                # print(f"Received P2P Message: {msg_type}")

                if msg_type == 'NEW_TASK':
                    task = Task(**payload)
                    if task.id not in self.task_pool:
                        self.task_pool[task.id] = task
                        print(f"📥 New task received: '{task.title}'")

                elif msg_type == 'NEW_SOLUTION':
                    solution = Solution(**payload)
                    if solution.id not in self.solution_pool:
                        self.solution_pool[solution.id] = solution
                        print(f"💡 New solution received for task '{solution.task_id[:8]}'")

                elif msg_type == 'ANNOUNCE_AUTHORITY':
                    node_id = payload.get('node_id')
                    if node_id and node_id not in self.known_authorities:
                        self.known_authorities.add(node_id)
                        print(f"👑 New authority registered: {node_id[:12]}")

                elif msg_type == 'NEW_BLOCK_ANNOUNCEMENT':
                    new_block = KnowledgeBlock(**payload)
                    if new_block.index > self.blockchain.last_block.index:
                        print(f"🔔 Received new block #{new_block.index} from {new_block.author_id[:8]}")
                        # اعتبارسنجی و افزودن بلاک
                        if self.blockchain.add_block(new_block, self.known_authorities):
                            print(f"🔗 Block #{new_block.index} added to chain. New length: {len(self.blockchain.chain)}")
                            self.cognitive_core.observe(new_block)
                            # پاک کردن تسک و راه حل استفاده شده از پول
                            if new_block.solution:
                                self.solution_pool.pop(new_block.solution.id, None)
                                self.task_pool.pop(new_block.solution.task_id, None)
                        else:
                            print(f"⚠️ Discarded invalid block #{new_block.index}")

                elif msg_type == 'REQUEST_STATE':
                    # یک گره دیگر درخواست وضعیت فعلی را دارد
                    state_payload = {
                        'authorities': list(self.known_authorities),
                        'chain': [b.model_dump() for b in self.blockchain.chain]
                    }
                    await self.p2p_manager.broadcast(P2PMessage(type='RESPONSE_STATE', payload=state_payload))

                elif msg_type == 'RESPONSE_STATE':
                     # ما درخواست وضعیت کرده بودیم و پاسخ را دریافت کردیم
                    if len(payload.get('chain', [])) > len(self.blockchain.chain):
                        print("Syncing state from network...")
                        self.known_authorities.update(payload.get('authorities', []))
                        
                        new_chain = [KnowledgeBlock(**b) for b in payload['chain']]
                        # A simple validation: check genesis block
                        if new_chain and new_chain[0].signature == "genesis_signature":
                             self.blockchain.chain = new_chain
                             print(f"✅ Chain synchronized. New length: {len(self.blockchain.chain)}")


            async def authority_mining_process(self):
                while True:
                    await asyncio.sleep(BLOCK_TIME)
                    if not is_authority() or not self.known_authorities:
                        continue
                    
                    current_miner = self.get_current_miner()
                    if current_miner != self.node_info.node_id:
                        # نوبت ما برای ماینینگ نیست
                        continue

                    print(f"⛏️ It's my turn to forge a block...")
                    # انتخاب یک راه حل از استخر برای گنجاندن در بلاک
                    solution_to_include = None
                    if self.solution_pool:
                        solution_id = next(iter(self.solution_pool))
                        solution_to_include = self.solution_pool.pop(solution_id)

                    last_block = self.blockchain.last_block
                    new_block = self.blockchain.new_block(
                        transactions=[], # در حال حاضر تراکنش‌ها فقط جوایز هستند
                        solution=solution_to_include,
                        previous_hash=LaniakeaChain.hash(last_block)
                    )
                    # امضای بلاک
                    hash_payload = LaniakeaChain.get_block_hash_payload(new_block)
                    new_block.signature = self.wallet.sign(hash_payload)

                    # اضافه کردن بلاک به زنجیره محلی و انتشار آن در شبکه
                    # اینجا از add_block استفاده می‌کنیم تا مطمئن شویم بلاک خودمان هم معتبر است
                    if self.blockchain.add_block(new_block, self.known_authorities):
                        self.cognitive_core.observe(new_block)
                        await self.p2p_manager.broadcast(P2PMessage(type="NEW_BLOCK_ANNOUNCEMENT", payload=new_block.model_dump()))
                        msg = f"✅ F
