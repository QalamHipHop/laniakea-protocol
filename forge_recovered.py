# این محتوای کامل forge_v1.8.py از پاسخ قبلی است.
# کپی کردن کل آن در اینجا برای اطمینان از کامل بودن اسکریپت.
import os
import textwrap

print("🔥 Forging Laniakea Universe v1.8 - The Flawless Edition...")
PROJECT_STRUCTURE = {
    "requirements.txt": """
        pydantic==2.7.1
        fastapi==0.110.0
        uvicorn[standard]>=0.27.1
        websockets==12.0
        aiohttp==3.9.3
        kademlia==2.0.1
        python-dotenv==1.0.1
        cryptography==42.0.5
        aiosqlite==0.19.0
    """,
    ".env.example": """
        # BOOTSTRAP_NODES=
        IS_AUTHORITY=true
    """,
    "src/__init__.py": "", "src/core/__init__.py": "", "src/network/__init__.py": "", "src/consensus/__init__.py": "",
    "src/config.py": """
        import os
        from typing import List, Tuple, Set
        from dotenv import load_dotenv
        load_dotenv()
        HOST: str = "0.0.0.0"
        BLOCK_REWARD: float = 50.0
        BLOCK_TIME: int = 15
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
        def is_authority() -> bool: return os.getenv("IS_AUTHORITY", "false").lower() == "true"
    """,
    "src/core/models.py": """
        from pydantic import BaseModel
        from typing import List, Optional, Dict, Any
        class Transaction(BaseModel): id: str; sender: str; recipient: str; amount: float; timestamp: float; signature: Optional[str] = None
        class KnowledgeBlock(BaseModel): index: int; timestamp: float; transactions: List[Transaction]; author_id: str; previous_hash: str; signature: str
        class NodeInfo(BaseModel): node_id: str; host: str; p2p_port: int; api_port: int
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
                os.environ["MY_NODE_ID"] = self.node_id; print(f"🔑 Wallet loaded. Node ID: {self.node_id[:12]}...")
            def _get_node_id(self) -> str:
                pub_key_bytes = self.public_key.public_bytes(encoding=serialization.Encoding.X962, format=serialization.PublicFormat.CompressedPoint)
                return hashlib.sha256(pub_key_bytes).hexdigest()
            def sign(self, data: bytes) -> str: return self.private_key.sign(data, ec.ECDSA(hashes.SHA256())).hex()
            @staticmethod
            def verify(public_key: ec.EllipticCurvePublicKey, signature_hex: str, data: bytes) -> bool:
                try: public_key.verify(bytes.fromhex(signature_hex), data, ec.ECDSA(hashes.SHA256())); return True
                except (InvalidSignature, ValueError): return False
    """,
    "src/core/blockchain.py": """
        import hashlib, json
        from time import time
        from typing import List, Optional
        from src.core.models import KnowledgeBlock, Transaction
        from src.config import BLOCK_REWARD
        class LaniakeaChain:
            def __init__(self, node_id: str): self.chain: List[KnowledgeBlock] = []; self.node_id = node_id
            def create_genesis_block(self):
                genesis_block = self.new_block(transactions=[], previous_hash='0' * 64, is_genesis=True)
                genesis_block.signature = "genesis_signature"
                self.chain.append(genesis_block)
            def new_block(self, transactions: List[Transaction], previous_hash: str, is_genesis: bool = False) -> KnowledgeBlock:
                if not is_genesis:
                    transactions.insert(0, Transaction(id=hashlib.sha256(str(time()).encode()).hexdigest(), sender="0", recipient=self.node_id, amount=BLOCK_REWARD, timestamp=time()))
                return KnowledgeBlock(index=len(self.chain), timestamp=time(), transactions=transactions, author_id=self.node_id, previous_hash=previous_hash, signature="")
            @staticmethod
            def get_block_hash_payload(block: KnowledgeBlock) -> bytes: return json.dumps(block.dict(exclude={'signature'}), sort_keys=True).encode()
            @staticmethod
            def hash(block: KnowledgeBlock) -> str: return hashlib.sha256(LaniakeaChain.get_block_hash_payload(block)).hexdigest()
            @property
            def last_block(self) -> Optional[KnowledgeBlock]: return self.chain[-1] if self.chain else None
    """,
    "src/network/p2p.py": """
        import asyncio, websockets, json
        from typing import Callable, Set, Dict, Any
        class P2PManager:
            def __init__(self, host: str, port: int, message_handler: Callable):
                self.host, self.port = host, port; self.server = None
                self.peers: Set[websockets.WebSocketServerProtocol] = set()
                self.message_handler = message_handler
            async def start(self):
                self.server = await websockets.serve(self.handler, self.host, self.port); print(f"🔗 P2P Node listening at ws://{self.host}:{self.port}")
            async def handler(self, websocket: websockets.WebSocketServerProtocol, path: str):
                self.peers.add(websocket)
                try:
                    async for message in websocket: await self.message_handler(json.loads(message))
                except websockets.ConnectionClosed: pass
                finally: self.peers.remove(websocket)
            async def broadcast(self, message: Dict[str, Any]):
                if self.peers: await asyncio.gather(*[peer.send(json.dumps(message)) for peer in self.peers], return_exceptions=True)
    """,
    "main.py": """
        import asyncio, argparse, uvicorn, json, hashlib
        from fastapi import FastAPI
        from src.config import HOST, get_bootstrap_nodes, is_authority, AUTHORITY_NODES, BLOCK_TIME
        from src.core.models import NodeInfo
        from src.core.blockchain import LaniakeaChain
        from src.core.wallet import Wallet
        from src.network.p2p import P2PManager
        class AppState:
            def __init__(self): self.wallet: Wallet=None; self.node_info:NodeInfo=None; self.blockchain:LaniakeaChain=None; self.p2p_manager:P2PManager=None
        app_state=AppState(); app=FastAPI(title="Laniakea Node API v1.8")
        async def handle_p2p_message(data: dict):
            if data.get('type') == 'NEW_BLOCK_ANNOUNCEMENT' and data.get('payload', {}).get('author_id') in AUTHORITY_NODES and data.get('payload', {}).get('index') == len(app_state.blockchain.chain):
                app_state.blockchain.chain.append(data['payload']); print(f"📦 New block #{data['payload']['index']} accepted.")
        @app.get("/")
        def get_node_info(): return app_state.node_info
        @app.get("/blockchain")
        def get_blockchain(): return {"length": len(app_state.blockchain.chain)}
        async def authority_mining_process():
            while True:
                await asyncio.sleep(BLOCK_TIME)
                if is_authority() and app_state.node_info.node_id in AUTHORITY_NODES:
                    last_block = app_state.blockchain.last_block
                    new_block = app_state.blockchain.new_block(transactions=[], previous_hash=LaniakeaChain.hash(last_block))
                    new_block.signature = app_state.wallet.sign(LaniakeaChain.get_block_hash_payload(new_block))
                    app_state.blockchain.chain[-1] = new_block
                    await app_state.p2p_manager.broadcast({"type": "NEW_BLOCK_ANNOUNCEMENT", "payload": new_block.dict()})
                    print(f"✅ Forged block #{new_block.index}")
        async def main():
            parser=argparse.ArgumentParser(); parser.add_argument('--p2p-port', type=int, required=True); parser.add_argument('--api-port', type=int, required=True); args=parser.parse_args()
            app_state.wallet=Wallet(f"data_node_{args.p2p_port}"); node_id=app_state.wallet.node_id
            if is_authority(): AUTHORITY_NODES.add(node_id)
            app_state.node_info=NodeInfo(node_id=node_id, host=HOST, p2p_port=args.p2p_port, api_port=args.api_port)
            app_state.blockchain=LaniakeaChain(node_id); app_state.blockchain.create_genesis_block()
            app_state.p2p_manager=P2PManager(HOST, args.p2p_port, handle_p2p_message)
            app.state=app_state
            print(f"--- 🌌 Initializing Laniakea Node {node_id[:8]} (v1.8) ---")
            tasks = [
                asyncio.create_task(app_state.p2p_manager.start()),
                asyncio.create_task(uvicorn.Server(uvicorn.Config(app, host=HOST, port=args.api_port, log_level="warning")).serve())
            ]
            if is_authority(): tasks.append(asyncio.create_task(authority_mining_process()))
            await asyncio.gather(*tasks)
        if __name__ == "__main__":
            try: asyncio.run(main())
            except KeyboardInterrupt: print("\\n🛑 Shutting down...")
    """,
}
def forge_universe():
    # ... (کد کامل این تابع از پاسخ قبلی برای ساختن فایل‌ها)
    root_dir = os.path.dirname(os.path.abspath(__file__))
    for file_path, content in PROJECT_STRUCTURE.items():
        full_path = os.path.join(root_dir, file_path)
        dir_name = os.path.dirname(full_path)
        if dir_name and not os.path.exists(dir_name): os.makedirs(dir_name)
        if dir_name.startswith("src") and not os.path.exists(os.path.join(dir_name, "__init__.py")):
            with open(os.path.join(dir_name, "__init__.py"), "w") as f: pass
        with open(full_path, "w") as f: f.write(textwrap.dedent(content).strip())
    print(f"  ✨ Universe forged successfully!")

forge_universe()
