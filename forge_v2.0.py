# forge_v2.0.py - The Value-Based Economy Edition
import os
import textwrap

print("🔥 Forging Laniakea Universe v2.0 - The Value-Based Economy...")

PROJECT_STRUCTURE = {
    # فایل‌های کانفیگ و نیازمندی‌ها بدون تغییر زیاد باقی می‌مانند
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
    # ساختار src با مدل‌های جدید
    "src/__init__.py": "", "src/core/__init__.py": "", "src/network/__init__.py": "", "src/consensus/__init__.py": "", "src/metasystem/__init__.py": "",
    "src/config.py": """
        import os
        from typing import List, Tuple, Set
        from dotenv import load_dotenv
        load_dotenv()
        HOST: str = "0.0.0.0"
        BLOCK_REWARD: float = 10.0 # پاداش پایه برای ساخت بلاک
        BLOCK_TIME: int = 20 # افزایش زمان برای پردازش بیشتر
        AUTHORITY_NODES: Set[str] = set()
        def get_bootstrap_nodes() -> List[Tuple[str, int]]:
            # ... (بدون تغییر)
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
        from pydantic import BaseModel, Field
        from typing import Dict, Any, List, Optional, Set

        class ValueVector(BaseModel):
            knowledge: float = 0.0
            computation: float = 0.0
            originality: float = 0.0

        class Task(BaseModel):
            id: str
            title: str
            description: str
            author_id: str

        class Solution(BaseModel):
            id: str
            task_id: str
            solver_id: str
            content: str # محتوای راه‌حل، مثلا یک قطعه کد یا داده
            value_vector: ValueVector

        class Transaction(BaseModel):
            id: str; sender: str; recipient: str; amount: float; timestamp: float; signature: Optional[str] = None

        class KnowledgeBlock(BaseModel):
            index: int
            timestamp: float
            transactions: List[Transaction]
            # هر بلاک اکنون می‌تواند حاوی یک راه‌حل باشد که ارزش خلق کرده
            solution: Optional[Solution] = None
            author_id: str
            previous_hash: str
            signature: str
        
        class NodeInfo(BaseModel):
            node_id: str; host: str; p2p_port: int; api_port: int; specialties: Set[str] = Field(default_factory=set)
    """,
    # Wallet بدون تغییر باقی می‌ماند
    "src/core/wallet.py": """
        # کد کامل Wallet از پاسخ قبلی در اینجا کپی می‌شود
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
    """,
    # بلاک‌چین برای پشتیبانی از Solutions و پاداش ارزش به‌روز می‌شود
    "src/core/blockchain.py": """
        import hashlib, json
        from time import time
        from typing import List, Optional
        from src.core.models import KnowledgeBlock, Transaction, Solution, ValueVector
        from src.config import BLOCK_REWARD
        
        class LaniakeaChain:
            def __init__(self, node_id: str):
                self.chain: List[KnowledgeBlock] = []
                self.node_id = node_id

            def create_genesis_block(self):
                genesis_block = self.new_block(transactions=[], solution=None, previous_hash='0' * 64, is_genesis=True)
                genesis_block.signature = "genesis_signature"
                self.chain.append(genesis_block)

            def new_block(self, transactions: List[Transaction], solution: Optional[Solution], previous_hash: str, is_genesis: bool = False) -> KnowledgeBlock:
                all_txs = list(transactions)
                # اضافه کردن پاداش بلاک
                if not is_genesis:
                    all_txs.insert(0, Transaction(id=self.tx_id(), sender="0", recipient=self.node_id, amount=BLOCK_REWARD, timestamp=time()))
                
                # مرحله ۱۳: اضافه کردن پاداش برای راه‌حل
                if solution:
                    # پاداش بر اساس مجموع ارزش‌های ValueVector محاسبه می‌شود
                    solution_reward_amount = solution.value_vector.knowledge + solution.value_vector.computation + solution.value_vector.originality
                    if solution_reward_amount > 0:
                        all_txs.insert(1, Transaction(id=self.tx_id(), sender="0", recipient=solution.solver_id, amount=solution_reward_amount, timestamp=time()))

                return KnowledgeBlock(
                    index=len(self.chain), timestamp=time(),
                    transactions=all_txs, solution=solution,
                    author_id=self.node_id, previous_hash=previous_hash, signature=""
                )
            
            def tx_id(self): return hashlib.sha256(str(time.time_ns()).encode()).hexdigest()
            
            @staticmethod
            def get_block_hash_payload(block: KnowledgeBlock) -> bytes:
                # Pydantic v2 uses model_dump instead of dict
                block_dict = block.model_dump(exclude={'signature'})
                return json.dumps(block_dict, sort_keys=True).encode()
            
            @staticmethod
            def hash(block: KnowledgeBlock) -> str:
                if not block: return '0' * 64
                return hashlib.sha256(LaniakeaChain.get_block_hash_payload(block)).hexdigest()
            
            @property
            def last_block(self) -> Optional[KnowledgeBlock]:
                return self.chain[-1] if self.chain else None
    """,
    # احیای CognitiveCore
    "src/metasystem/cognitive_core.py": """
        from typing import List
        from src.core.models import KnowledgeBlock

        class CognitiveCore:
            def __init__(self):
                self.observations = 0
                print("🧠 Cognitive Core v2.0 Activated.")

            def observe(self, block: KnowledgeBlock):
                self.observations += 1
                if block.solution and block.solution.value_vector.knowledge > 100:
                    print(f"✨ Cognitive Insight: High-knowledge solution '{block.solution.id[:8]}' observed.")
    """,
    # ارکستراتور نهایی main.py
    "main.py": """
        import asyncio, argparse, uvicorn, json, hashlib
        from fastapi import FastAPI, Body
        from typing import Dict, Any

        from src.config import HOST, get_bootstrap_nodes, is_authority, AUTHORITY_NODES, BLOCK_TIME
        from src.core.models import NodeInfo, Task, Solution, ValueVector
        from src.core.blockchain import LaniakeaChain
        from src.core.wallet import Wallet
        from src.network.p2p import P2PManager
        from src.metasystem.cognitive_core import CognitiveCore

        class AppState:
            def __init__(self):
                self.wallet: Wallet = None; self.node_info: NodeInfo = None
                self.blockchain: LaniakeaChain = None; self.p2p_manager: P2PManager = None
                self.cognitive_core: CognitiveCore = None
                self.task_pool: Dict[str, Task] = {}
                self.solution_pool: Dict[str, Solution] = {} # استخر راه‌حل‌های منتظر ورود به بلاک

        app_state = AppState(); app = FastAPI(title="Laniakea Node API v2.0")

        async def handle_p2p_message(data: dict):
            msg_type = data.get('type')
            if msg_type == 'NEW_TASK':
                task = Task(**data['payload'])
                if task.id not in app_state.task_pool:
                    app_state.task_pool[task.id] = task
                    print(f"📥 New task received: '{task.title}'")
            elif msg_type == 'NEW_SOLUTION':
                solution = Solution(**data['payload'])
                if solution.id not in app_state.solution_pool and solution.task_id in app_state.task_pool:
                    app_state.solution_pool[solution.id] = solution
                    print(f"💡 New solution '{solution.id[:8]}' received for task '{solution.task_id[:8]}'.")

        @app.get("/")
        def get_node_info(): return app_state.node_info

        @app.get("/blockchain")
        def get_blockchain(): return {"length": len(app_state.blockchain.chain)}

        @app.get("/tasks")
        def get_tasks(): return {"tasks": list(app_state.task_pool.values())}

        @app.post("/tasks/create", status_code=201)
        async def create_task(task_data: dict = Body(...)):
            task_id = hashlib.sha256(json.dumps(task_data).encode()).hexdigest()
            task = Task(id=task_id, author_id=app_state.node_info.node_id, **task_data)
            app_state.task_pool[task.id] = task
            await app_state.p2p_manager.broadcast({"type": "NEW_TASK", "payload": task.model_dump()})
            return {"message": "Task broadcasted.", "task_id": task_id}

        @app.post("/solutions/submit", status_code=201)
        async def submit_solution(solution_data: dict = Body(...)):
            # اعتبارسنجی اولیه راه‌حل
            if "task_id" not in solution_data or solution_data["task_id"] not in app_state.task_pool:
                return {"error": "Task ID is invalid or not found."}, 400
            
            solution_id = hashlib.sha256(json.dumps(solution_data).encode()).hexdigest()
            # ارزیابی ساده ارزش (در سیستم واقعی این پیچیده‌تر است)
            value = ValueVector(knowledge=float(solution_data.get("knowledge", 0)))
            
            solution = Solution(id=solution_id, solver_id=app_state.node_info.node_id, value_vector=value, **solution_data)
            app_state.solution_pool[solution.id] = solution
            
            await app_state.p2p_manager.broadcast({"type": "NEW_SOLUTION", "payload": solution.model_dump()})
            return {"message": "Solution submitted to the network.", "solution_id": solution_id}

        async def authority_mining_process():
            while True:
                await asyncio.sleep(BLOCK_TIME)
                if is_authority() and app_state.node_info.node_id in AUTHORITY_NODES:
                    print("👑 Authority node is forging a new block...")
                    
                    # انتخاب یک راه‌حل از استخر (اگر وجود داشته باشد)
                    solution_to_include = None
                    if app_state.solution_pool:
                        solution_id_to_mine = list(app_state.solution_pool.keys())[0]
                        solution_to_include = app_state.solution_pool.pop(solution_id_to_mine)
                        print(f"💰 Including solution '{solution_to_include.id[:8]}' in the new block.")
                    
                    last_block = app_state.blockchain.last_block
                    new_block = app_state.blockchain.new_block(
                        transactions=[], solution=solution_to_include,
                        previous_hash=LaniakeaChain.hash(last_block)
                    )
                    
                    block_hash_payload = LaniakeaChain.get_block_hash_payload(new_block)
                    new_block.signature = app_state.wallet.sign(block_hash_payload)
                    
                    app_state.blockchain.chain[-1] = new_block
                    app_state.cognitive_core.observe(new_block)
                    
                    await app_state.p2p_manager.broadcast({"type": "NEW_BLOCK_ANNOUNCEMENT", "payload": new_block.model_dump()})
                    print(f"✅ Forged and broadcasted block #{new_block.index}")

        async def main():
            # ... (کد parser بدون تغییر)
            parser=argparse.ArgumentParser(); parser.add_argument('--p2p-port', type=int, required=True); parser.add_argument('--api-port', type=int, required=True); args=parser.parse_args()
            
            app_state.wallet = Wallet(f"data_node_{args.p2p_port}"); node_id = app_state.wallet.node_id
            if is_authority(): AUTHORITY_NODES.add(node_id)
            
            app_state.node_info = NodeInfo(node_id=node_id, host=HOST, p2p_port=args.p2p_port, api_port=args.api_port)
            app_state.blockchain = LaniakeaChain(node_id=node_id)
            app_state.blockchain.create_genesis_block()
            
            app_state.p2p_manager = P2PManager(HOST, args.p2p_port, handle_p2p_message)
            app_state.cognitive_core = CognitiveCore()
            
            app.state = app_state
            
            print(f"--- 🌌 Initializing Laniakea Node {node_id[:8]} (v2.0) ---")
            
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
    # ... (کد کامل این تابع از پاسخ‌های قبلی برای ساختن فایل‌ها)
    print("🔥 Forging Laniakea Universe v2.0 - The Value-Based Economy...")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    for file_path, content in PROJECT_STRUCTURE.items():
        full_path = os.path.join(root_dir, file_path)
        dir_name = os.path.dirname(full_path)
        if dir_name and not os.path.exists(dir_name): os.makedirs(dir_name)
        if dir_name.startswith("src") and not os.path.exists(os.path.join(dir_name, "__init__.py")):
            with open(os.path.join(dir_name, "__init__.py"), "w") as f: pass
        with open(full_path, "w") as f: f.write(textwrap.dedent(content).strip())
    print(f"  ✅ Wrote/Updated file: {file_path}")
    print("\n✨ Universe forged successfully! All systems are integrated.")

if __name__ == "__main__":
    forge_universe()
