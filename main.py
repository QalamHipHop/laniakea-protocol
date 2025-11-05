"""
Laniakea Protocol v5.0 - Enhanced Main Entry Point
نقطه ورود اصلی پروتوکل Laniakea نسخه 5.0

ویژگی‌های جدید:
- سیستم Reputation پیشرفته
- یکپارچگی کامل با API های خارجی
- رابط کاربری وب
- بهبود عملکرد و امنیت
"""

import asyncio
import argparse
import uvicorn
import hashlib
from time import time
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.config import HOST, get_bootstrap_nodes, is_authority, AUTHORITY_NODES, BLOCK_TIME
from src.core.models import (
    NodeInfo, Task, Solution, ValueVector, ProblemCategory,
    NodeSpecialty, Proposal
)
from src.core.blockchain import LaniakeaChain
from src.core.wallet import Wallet
from src.core.hash_modernity import HashModernityEngine, ProofOfValue
from src.core.token_system import TokenEconomics, StakingSystem
from src.network.p2p import P2PManager
from src.metasystem.cognitive_core import CognitiveCore
from src.oracles.oracle_system import OracleManager
from src.simulation.cosmic_simulator import CosmicSimulator
from src.dashboard.live_dashboard import get_metrics_collector, generate_dashboard
from src.intelligence.self_evolution import SelfEvolutionEngine
from src.intelligence.predictive_analytics import get_predictive_engine
from src.marketplace import get_marketplace, KnowledgeAsset, KnowledgeType

# ماژول‌های جدید v5.0
from src.reputation.reputation_system import get_reputation_system, ReputationEvent
from src.external_apis.api_integrations import get_api_manager, APIProvider


class AppState:
    """وضعیت اپلیکیشن"""

    def __init__(self):
        # اجزای اصلی
        self.wallet: Optional[Wallet] = None
        self.node_info: Optional[NodeInfo] = None
        self.blockchain: Optional[LaniakeaChain] = None
        self.p2p_manager: Optional[P2PManager] = None

        # سیستم‌های پیشرفته
        self.cognitive_core: Optional[CognitiveCore] = None
        self.oracle_manager: Optional[OracleManager] = None
        self.hash_modernity: Optional[HashModernityEngine] = None
        self.token_economics: Optional[TokenEconomics] = None
        self.staking_system: Optional[StakingSystem] = None
        self.cosmic_simulator: Optional[CosmicSimulator] = None

        # سیستم‌های v5.0
        self.metrics_collector = get_metrics_collector()
        self.predictive_engine = get_predictive_engine()
        self.knowledge_marketplace = get_marketplace()
        self.evolution_engine: Optional[SelfEvolutionEngine] = None
        self.reputation_system = get_reputation_system()
        self.api_manager = get_api_manager()

        # استخرها
        self.task_pool: Dict[str, Task] = {}
        self.solution_pool: Dict[str, Solution] = {}
        self.known_authorities: set = set()


# ایجاد instance های global
app_state = AppState()
app = FastAPI(
    title="Laniakea Protocol Node v0.0.01",
    version="0.0.01",
    description="A cosmic computational organism with advanced features"
)

# سرویس‌دهی فایل‌های استاتیک (مانند CSS و JS)
# فرض می‌کنیم فایل‌های استاتیک در پوشه web/static قرار دارند.
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "web" / "static")), name="static")

# اضافه کردن CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# P2P Message Handlers
# ============================================================================

async def handle_p2p_message(data: dict):
    """مدیریت پیام‌های P2P"""
    msg_type = data.get('type')
    payload = data.get('payload', {})

    if msg_type == 'NEW_TASK':
        task = Task(**payload)
        if task.id not in app_state.task_pool:
            app_state.task_pool[task.id] = task
            print(f"📥 New task received: '{task.title}'")
            
            # ثبت رویداد در سیستم Reputation
            app_state.reputation_system.record_event(
                task.author_id,
                ReputationEvent.TASK_CREATED,
                {"task_id": task.id}
            )

    elif msg_type == 'NEW_SOLUTION':
        solution = Solution(**payload)
        if solution.id not in app_state.solution_pool:
            app_state.solution_pool[solution.id] = solution
            print(f"💡 New solution received for task '{solution.task_id[:8]}'")
            
            # ثبت رویداد
            app_state.reputation_system.record_event(
                solution.solver_id,
                ReputationEvent.SOLUTION_SUBMITTED,
                {"solution_id": solution.id}
            )

    elif msg_type == 'NEW_BLOCK_ANNOUNCEMENT':
        from src.core.models import KnowledgeBlock
        new_block = KnowledgeBlock(**payload)

        if new_block.index == len(app_state.blockchain.chain):
            if app_state.blockchain.add_block(new_block, app_state.known_authorities):
                print(f"🔗 Block #{new_block.index} added to chain")

                # مشاهده توسط Cognitive Core
                if app_state.cognitive_core:
                    app_state.cognitive_core.observe(new_block)

                # ثبت رویداد برای validator
                if new_block.validator:
                    app_state.reputation_system.record_event(
                        new_block.validator,
                        ReputationEvent.BLOCK_VALIDATED,
                        {"block_index": new_block.index}
                    )

                # حذف تسک و راه‌حل استفاده شده
                if new_block.solution:
                    # ثبت قبولی راه‌حل
                    app_state.reputation_system.record_event(
                        new_block.solution.solver_id,
                        ReputationEvent.SOLUTION_ACCEPTED,
                        {
                            "solution_id": new_block.solution.id,
                            "value": new_block.solution.value_vector.total_value()
                        }
                    )
                    
                    app_state.solution_pool.pop(new_block.solution.id, None)
                    app_state.task_pool.pop(new_block.solution.task_id, None)

    elif msg_type == 'ANNOUNCE_AUTHORITY':
        node_id = payload.get('node_id')
        if node_id and node_id not in app_state.known_authorities:
            app_state.known_authorities.add(node_id)
            print(f"👑 New authority registered: {node_id[:12]}")


# ============================================================================
# API Endpoints - Core
# ============================================================================

@app.get("/")
async def get_node_info():
    """دریافت اطلاعات نود"""
    return app_state.node_info


@app.get("/stats")
async def get_stats():
    """دریافت آمار کامل سیستم"""
    stats = {
        "blockchain": app_state.blockchain.get_chain_stats() if app_state.blockchain else {},
        "cognitive_core": app_state.cognitive_core.get_stats() if app_state.cognitive_core else {},
        "token_economics": app_state.token_economics.get_stats() if app_state.token_economics else {},
        "hash_modernity": app_state.hash_modernity.get_modernity_stats() if app_state.hash_modernity else {},
        "cosmic_simulator": app_state.cosmic_simulator.get_stats() if app_state.cosmic_simulator else {},
        "oracle_manager": app_state.oracle_manager.get_stats() if app_state.oracle_manager else {},
        "reputation_system": app_state.reputation_system.get_stats(),
        "api_manager": app_state.api_manager.get_stats(),
        "task_pool_size": len(app_state.task_pool),
        "solution_pool_size": len(app_state.solution_pool)
    }
    return stats


@app.get("/blockchain")
async def get_blockchain():
    """دریافت اطلاعات بلاک‌چین"""
    if not app_state.blockchain:
        raise HTTPException(status_code=503, detail="Blockchain not initialized")

    return {
        "length": len(app_state.blockchain.chain),
        "last_block_index": app_state.blockchain.last_block.index if app_state.blockchain.last_block else -1,
        "stats": app_state.blockchain.get_chain_stats()
    }


# ============================================================================
# API Endpoints - Tasks & Solutions
# ============================================================================

@app.get("/tasks")
async def get_tasks():
    """دریافت لیست تسک‌ها"""
    return {
        "count": len(app_state.task_pool),
        "tasks": [task.model_dump() for task in app_state.task_pool.values()]
    }


@app.post("/tasks/create", status_code=201)
async def create_task(task_data: dict = Body(...)):
    """ایجاد تسک جدید"""
    try:
        task_id = hashlib.sha256(f"{task_data}{time()}".encode()).hexdigest()

        task = Task(
            id=task_id,
            author_id=app_state.node_info.node_id,
            timestamp=time(),
            **task_data
        )

        app_state.task_pool[task.id] = task

        # ثبت رویداد
        app_state.reputation_system.record_event(
            app_state.node_info.node_id,
            ReputationEvent.TASK_CREATED,
            {"task_id": task_id}
        )

        # انتشار در شبکه
        await app_state.p2p_manager.broadcast({
            "type": "NEW_TASK",
            "payload": task.model_dump()
        })

        print(f"📝 Task created: {task.title}")
        return {"message": "Task created and broadcasted", "task_id": task_id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/solutions/submit", status_code=201)
async def submit_solution(solution_data: dict = Body(...)):
    """ارسال راه‌حل"""
    try:
        task_id = solution_data.get("task_id")
        if not task_id or task_id not in app_state.task_pool:
            raise HTTPException(status_code=404, detail="Task not found")

        task = app_state.task_pool[task_id]
        solution_id = hashlib.sha256(f"{solution_data}{time()}".encode()).hexdigest()

        # ایجاد راه‌حل
        solution = Solution(
            id=solution_id,
            task_id=task_id,
            solver_id=app_state.node_info.node_id,
            content=solution_data.get("content", ""),
            value_vector=ValueVector(),
            timestamp=time()
        )

        # ارزیابی راه‌حل توسط هسته شناختی (فراخوانی ناهمزمان به AI Worker)
        # در این مرحله، ValueVector موقتاً خالی است و بعداً با نتیجه AI به‌روزرسانی می‌شود.
        
        from src.intelligence.ai_worker import process_solution_value_vector
        
        # اجرای ارزیابی در پس‌زمینه (شبیه‌سازی Serverless/Persistent AI)
        asyncio.create_task(
            process_solution_value_vector(solution.model_dump(), task.model_dump())
        )
        
        # مقداردهی اولیه ValueVector برای جلوگیری از خطا
        solution.value_vector = ValueVector()

        # محاسبه Proof of Discovery
        if app_state.hash_modernity:
            solution.proof_of_work = app_state.hash_modernity.compute_proof_of_discovery(
                task, solution, difficulty=4
            )

        app_state.solution_pool[solution.id] = solution

        # ثبت رویداد
        app_state.reputation_system.record_event(
            app_state.node_info.node_id,
            ReputationEvent.SOLUTION_SUBMITTED,
            {"solution_id": solution_id, "task_id": task_id}
        )

        # انتشار در شبکه
        await app_state.p2p_manager.broadcast({
            "type": "NEW_SOLUTION",
            "payload": solution.model_dump()
        })

        print(f"💡 Solution submitted: {solution_id[:8]} with value {solution.value_vector.total_value():.2f}")
        return {
            "message": "Solution submitted and broadcasted",
            "solution_id": solution_id,
            "value": solution.value_vector.to_dict()
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# API Endpoints - Reputation System
# ============================================================================

@app.get("/reputation/{node_id}")
async def get_reputation(node_id: str):
    """دریافت امتیاز اعتبار یک نود"""
    score = app_state.reputation_system.get_reputation(node_id)
    if not score:
        raise HTTPException(status_code=404, detail="Node not found")
    
    return {
        "node_id": node_id,
        "reputation": score.to_dict()
    }


@app.get("/reputation/top/{limit}")
async def get_top_nodes(limit: int = 10):
    """دریافت برترین نودها"""
    top_nodes = app_state.reputation_system.get_top_nodes(limit)
    return {
        "top_nodes": [
            {"node_id": node_id, "score": score}
            for node_id, score in top_nodes
        ]
    }


# ============================================================================
# API Endpoints - External APIs
# ============================================================================

@app.post("/api/query")
async def query_external_api(api_data: dict = Body(...)):
    """پرسش از API های خارجی"""
    try:
        provider = APIProvider(api_data.get("provider"))
        endpoint = api_data.get("endpoint")
        params = api_data.get("params", {})
        
        result = await app_state.api_manager.query_api(provider, endpoint, params)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# API Endpoints - Cognitive Core
# ============================================================================

@app.post("/cognitive/ask")
async def ask_cognitive_core(question_data: dict = Body(...)):
    """پرسیدن سوال از Cognitive Core"""
    if not app_state.cognitive_core:
        raise HTTPException(status_code=503, detail="Cognitive Core not initialized")

    question = question_data.get("question", "")
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    answer = app_state.cognitive_core.ask_question(question)
    return {"question": question, "answer": answer}


@app.post("/cognitive/generate_task")
async def generate_task(task_params: dict = Body(...)):
    """تولید خودکار تسک توسط Cognitive Core"""
    if not app_state.cognitive_core:
        raise HTTPException(status_code=503, detail="Cognitive Core not initialized")

    category = ProblemCategory(task_params.get("category", "scientific"))
    difficulty = float(task_params.get("difficulty", 5.0))

    task_dict = app_state.cognitive_core.generate_task(category, difficulty)
    
    if task_dict:
        return task_dict
    else:
        raise HTTPException(status_code=500, detail="Failed to generate task")


# ============================================================================
# Web Interface
# ============================================================================



@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """سرو رابط کاربری وب (index.html)"""
    ui_file = Path("web/index.html")
    if ui_file.exists():
        return FileResponse(ui_file)
    
    # در صورت عدم وجود index.html، یک پیام خطا برگردان
    return HTMLResponse("<h1>خطا: فایل web/index.html پیدا نشد.</h1>", status_code=500)


@app.get("/api/stats")
async def get_node_stats():
    """دریافت آمار زنده نود برای به‌روزرسانی UI"""
    
    # برای جلوگیری از خطای AttributeError در صورتی که initialize_node هنوز کامل نشده باشد
    if not hasattr(app_state, 'blockchain') or not app_state.blockchain:
        blockchain_stats = {"length": 0, "total_value_created": {"knowledge": 0.0}}
    else:
        blockchain_stats = app_state.blockchain.get_chain_stats()
        
    if not hasattr(app_state, 'p2p_manager') or not app_state.p2p_manager:
        network_stats = {"connected_peers": 0, "tps": 0.0}
    else:
        network_stats = app_state.p2p_manager.get_network_stats()
        
    # اطمینان از اینکه app_state.cognitive_core مقداردهی شده است
    active_tasks = app_state.cognitive_core.get_task_count() if hasattr(app_state, 'cognitive_core') and app_state.cognitive_core else 0
    
    blockchain_data = {
        "chain_length": blockchain_stats.get("length", 0),
        "total_value": blockchain_stats.get("total_value_created", {}).get("knowledge", 0.0), # فقط دانش را برای نمایش می‌گیریم
        "active_tasks": active_tasks,
    }
    network_data = {
        "peer_count": network_stats.get("connected_peers", 0),
        "tps": network_stats.get("tps", 0.0),
    }
    
    node_info = {
        "node_id": app_state.node_info.node_id if app_state.node_info else "N/A",
        "is_authority": app_state.node_info.is_authority if app_state.node_info else False,
        "p2p_port": app_state.p2p_port,
        "api_port": app_state.api_port,
    }
    
    return {
        "blockchain": blockchain_data,
        "network": network_data,
        "node_info": node_info,
    }

# حذف تابع serve_ui قدیمی که داشبورد زنده را تولید می‌کرد
# @app.get("/ui", response_class=HTMLResponse)
# async def serve_live_dashboard():
#     ...)


# ============================================================================
# Initialization
# ============================================================================

async def initialize_node(p2p_port: int, api_port: int, enable_simulation: bool = False):
    """راه‌اندازی نود"""
    print("=" * 60)
    print("🌌 Laniakea Protocol v0.0.1 - Initializing...")
    print("=" * 60)

    # 1. ایجاد کیف پول
    data_dir = f"data_node_{p2p_port}"
    Path(data_dir).mkdir(exist_ok=True)
    
    app_state.wallet = Wallet(data_dir)
    node_id = app_state.wallet.get_address()

    # ثبت نود در سیستم Reputation
    app_state.reputation_system.register_node(node_id)

    # 2. ایجاد اطلاعات نود
    app_state.node_info = NodeInfo(
        node_id=node_id,
        host=HOST,
        p2p_port=p2p_port,
        api_port=api_port,
        is_authority=is_authority(node_id),
        specialties={NodeSpecialty.GENERALIST}
    )

    print(f"📍 Node ID: {node_id[:16]}...")
    print(f"🔑 Authority: {app_state.node_info.is_authority}")

    # 3. راه‌اندازی بلاک‌چین
    app_state.blockchain = LaniakeaChain(app_state.node_info.node_id)
    
    # 4. راه‌اندازی سیستم‌های پیشرفته
    app_state.hash_modernity = HashModernityEngine()
    app_state.token_economics = TokenEconomics()
    app_state.staking_system = StakingSystem(app_state.token_economics)
    app_state.cognitive_core = CognitiveCore()
    app_state.oracle_manager = OracleManager()
    
    if enable_simulation:
        app_state.cosmic_simulator = CosmicSimulator()
    
    # 5. راه‌اندازی شبکه P2P
    bootstrap_nodes = get_bootstrap_nodes()
    app_state.p2p_manager = P2PManager(
        host=HOST,
        port=p2p_port,
        message_handler=handle_p2p_message
    )
    
    await app_state.p2p_manager.start()
    
    for node_addr in bootstrap_nodes:
        await app_state.p2p_manager.connect_to_peer(node_addr)
        
    # 6. فعال‌سازی هوش دائمی (AI Worker)
    from src.intelligence.ai_worker import ai_worker_main_loop
    asyncio.create_task(ai_worker_main_loop())
    
    # 7. اعلام authority
    if app_state.node_info.is_authority:
        app_state.known_authorities.add(node_id)
        await app_state.p2p_manager.broadcast({
            "type": "ANNOUNCE_AUTHORITY",
            "payload": {"node_id": node_id}
        })

    print("=" * 60)
    print("✅ Node initialized successfully!")
    print(f"🌐 API: http://{HOST}:{api_port}")
    print(f"🖥️  UI: http://{HOST}:{api_port}/ui")
    print(f"🔗 P2P: {HOST}:{p2p_port}")
    print("=" * 60)


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Laniakea Protocol Node v5.0")
    parser.add_argument("--p2p-port", type=int, default=5000, help="P2P port")
    parser.add_argument("--api-port", type=int, default=8000, help="API port")
    parser.add_argument("--enable-simulation", action="store_true", help="Enable cosmic simulation")
    
    args = parser.parse_args()

    # راه‌اندازی API server
    # uvicorn.run باید در یک thread جداگانه اجرا شود تا asyncio.run بتواند اجرا شود.
    # اما چون uvicorn خودش یک حلقه رویداد را اجرا می‌کند، باید initialize_node را به صورت async اجرا کنیم.
    
    async def start_node_and_server():
        # 1. راه‌اندازی نود (بخش‌های ناهمزمان)
        await initialize_node(args.p2p_port, args.api_port, args.enable_simulation)
        
        # 2. راه‌اندازی سرور uvicorn
        config = uvicorn.Config(
            app,
            host=HOST,
            port=args.api_port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

    # اجرای کل سیستم در حلقه رویداد
    asyncio.run(start_node_and_server())
if __name__ == "__main__":
    main()
