"""
Laniakea Protocol - Main Entry Point
نقطه ورود اصلی پروتوکل Laniakea
"""

import asyncio
import argparse
import uvicorn
import hashlib
from time import time
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import JSONResponse

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
from src.marketplace.nft_knowledge import get_marketplace, NFTMetadata, KnowledgeType


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

        # سیستم‌های جدید v0.0.1
        self.metrics_collector = get_metrics_collector()
        self.predictive_engine = get_predictive_engine()
        self.nft_marketplace = get_marketplace()
        self.evolution_engine: Optional[SelfEvolutionEngine] = None

        # استخرها
        self.task_pool: Dict[str, Task] = {}
        self.solution_pool: Dict[str, Solution] = {}
        self.known_authorities: set = set()


# ایجاد instance های global
app_state = AppState()
app = FastAPI(
    title="Laniakea Protocol Node",
    version="3.0.0",
    description="A cosmic computational organism for universal problem-solving"
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

    elif msg_type == 'NEW_SOLUTION':
        solution = Solution(**payload)
        if solution.id not in app_state.solution_pool:
            app_state.solution_pool[solution.id] = solution
            print(f"💡 New solution received for task '{solution.task_id[:8]}'")

    elif msg_type == 'NEW_BLOCK_ANNOUNCEMENT':
        from src.core.models import KnowledgeBlock
        new_block = KnowledgeBlock(**payload)

        if new_block.index == len(app_state.blockchain.chain):
            if app_state.blockchain.add_block(new_block, app_state.known_authorities):
                print(f"🔗 Block #{new_block.index} added to chain")

                # مشاهده توسط Cognitive Core
                if app_state.cognitive_core:
                    app_state.cognitive_core.observe(new_block)

                # حذف تسک و راه‌حل استفاده شده
                if new_block.solution:
                    app_state.solution_pool.pop(new_block.solution.id, None)
                    app_state.task_pool.pop(new_block.solution.task_id, None)

    elif msg_type == 'ANNOUNCE_AUTHORITY':
        node_id = payload.get('node_id')
        if node_id and node_id not in app_state.known_authorities:
            app_state.known_authorities.add(node_id)
            print(f"👑 New authority registered: {node_id[:12]}")


# ============================================================================
# API Endpoints
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

        # ایجاد راه‌حل با ارزش‌گذاری اولیه
        solution = Solution(
            id=solution_id,
            task_id=task_id,
            solver_id=app_state.node_info.node_id,
            content=solution_data.get("content", ""),
            value_vector=ValueVector(),  # خالی
            timestamp=time()
        )

        # ارزیابی توسط Cognitive Core
        if app_state.cognitive_core:
            solution.value_vector = app_state.cognitive_core.analyze_solution(solution, task)
        else:
            # ارزش‌گذاری پیش‌فرض
            solution.value_vector = ValueVector(
                knowledge=float(solution_data.get("knowledge", 10.0)),
                computation=float(solution_data.get("computation", 5.0)),
                originality=float(solution_data.get("originality", 5.0))
            )

        # محاسبه Proof of Discovery
        if app_state.hash_modernity:
            solution.proof_of_work = app_state.hash_modernity.compute_proof_of_discovery(
                task, solution, difficulty=4
            )

        app_state.solution_pool[solution.id] = solution

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


@app.get("/balance/{node_id}")
async def get_balance(node_id: str):
    """دریافت موجودی یک نود"""
    if not app_state.blockchain:
        raise HTTPException(status_code=503, detail="Blockchain not initialized")

    balance = app_state.blockchain.get_total_balance(node_id)
    return {"node_id": node_id, "balance": balance.to_dict()}


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

    task = app_state.cognitive_core.generate_task(category, difficulty)

    if task:
        app_state.task_pool[task.id] = task
        await app_state.p2p_manager.broadcast({
            "type": "NEW_TASK",
            "payload": task.model_dump()
        })
        return {"message": "Task generated", "task": task.model_dump()}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate task")


@app.post("/oracle/query")
async def query_oracle(query_data: dict = Body(...)):
    """پرس‌وجو از اوراکل"""
    if not app_state.oracle_manager:
        raise HTTPException(status_code=503, detail="Oracle Manager not initialized")

    oracle_type = query_data.get("oracle_type", "")
    params = query_data.get("params", {})

    result = await app_state.oracle_manager.query(oracle_type, params)
    return result


@app.get("/simulation/status")
async def get_simulation_status():
    """دریافت وضعیت شبیه‌سازی"""
    if not app_state.cosmic_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")

    return app_state.cosmic_simulator.get_stats()


@app.get("/simulation/visualize")
async def visualize_simulation():
    """نمایش وضعیت شبیه‌سازی"""
    if not app_state.cosmic_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")

    visualization = app_state.cosmic_simulator.visualize_state()
    return {"visualization": visualization}


# ============================================================================
# New Features v0.0.1
# ============================================================================

@app.get("/dashboard")
async def get_dashboard():
    """دریافت داشبورد زنده"""
    from fastapi.responses import HTMLResponse
    
    blockchain_data = {
        'chain_length': len(app_state.blockchain.chain) if app_state.blockchain else 0,
        'total_value': sum(
            block.solution.value_vector.total_value() if block.solution else 0
            for block in (app_state.blockchain.chain if app_state.blockchain else [])
        ),
        'active_tasks': len(app_state.task_pool)
    }
    
    network_data = {
        'peer_count': len(app_state.p2p_manager.peers) if app_state.p2p_manager else 0,
        'tps': 0.0  # محاسبه بعداً
    }
    
    # ثبت متریک‌ها
    app_state.metrics_collector.record('blockchain', blockchain_data)
    app_state.metrics_collector.record('network', network_data)
    
    html = generate_dashboard(blockchain_data, network_data)
    return HTMLResponse(content=html)


@app.get("/analytics/predict")
async def get_predictions():
    """دریافت پیش‌بینی‌های آینده"""
    blockchain_data = {
        'chain_length': len(app_state.blockchain.chain) if app_state.blockchain else 0,
        'total_value': sum(
            block.solution.value_vector.total_value() if block.solution else 0
            for block in (app_state.blockchain.chain if app_state.blockchain else [])
        )
    }
    
    network_data = {
        'peer_count': len(app_state.p2p_manager.peers) if app_state.p2p_manager else 0
    }
    
    predictions = await app_state.predictive_engine.analyze_blockchain_future(
        blockchain_data,
        network_data
    )
    
    return predictions


@app.post("/nft/mint")
async def mint_knowledge_nft(nft_data: dict = Body(...)):
    """ضرب NFT دانش"""
    try:
        metadata = NFTMetadata(
            name=nft_data.get('name'),
            description=nft_data.get('description'),
            knowledge_type=KnowledgeType(nft_data.get('knowledge_type', 'scientific')),
            creator=nft_data.get('creator'),
            knowledge_value=float(nft_data.get('knowledge_value', 0)),
            computation_value=float(nft_data.get('computation_value', 0)),
            originality_score=float(nft_data.get('originality_score', 0))
        )
        
        nft = app_state.nft_marketplace.mint_nft(
            content=nft_data.get('content', ''),
            metadata=metadata,
            creator=nft_data.get('creator')
        )
        
        return {
            'message': 'NFT minted successfully',
            'token_id': nft.token_id,
            'nft': nft.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/nft/marketplace")
async def get_marketplace_listings():
    """دریافت لیست فروش"""
    return {
        'listings': list(app_state.nft_marketplace.listings.values()),
        'stats': app_state.nft_marketplace.get_stats()
    }


@app.get("/nft/trending")
async def get_trending_nfts():
    """دریافت NFT های ترند"""
    trending = app_state.nft_marketplace.get_trending(limit=10)
    return {'trending': [nft.model_dump() for nft in trending]}


@app.post("/evolution/analyze")
async def analyze_code_evolution(params: dict = Body(...)):
    """تحلیل و پیشنهاد بهبودها"""
    if not app_state.evolution_engine:
        app_state.evolution_engine = SelfEvolutionEngine('.')
    
    auto_apply = params.get('auto_apply', False)
    result = await app_state.evolution_engine.evolve(auto_apply=auto_apply)
    
    return {
        'message': 'Evolution analysis complete',
        'summary': {
            'files_analyzed': result['project_stats']['total_files'],
            'suggestions_count': len(result['suggestions']),
            'improvements_applied': len(result['applied_improvements'])
        },
        'report_path': 'EVOLUTION_REPORT.json'
    }


# ============================================================================
# Background Tasks
# ============================================================================

async def authority_mining_process():
    """فرآیند استخراج برای نودهای authority"""
    while True:
        await asyncio.sleep(BLOCK_TIME)

        if not is_authority() or app_state.node_info.node_id not in app_state.known_authorities:
            continue

        print(f"⛏️ Mining new block...")

        # انتخاب راه‌حل از استخر
        solution_to_include = None
        if app_state.solution_pool:
            solution_id = next(iter(app_state.solution_pool))
            solution_to_include = app_state.solution_pool.pop(solution_id)
            print(f"💰 Including solution '{solution_to_include.id[:8]}' in block")

        # ایجاد بلاک جدید
        last_block = app_state.blockchain.last_block
        new_block = app_state.blockchain.new_block(
            transactions=[],
            solution=solution_to_include,
            previous_hash=LaniakeaChain.hash(last_block)
        )

        # امضای بلاک
        hash_payload = LaniakeaChain.get_block_hash_payload(new_block)
        new_block.signature = app_state.wallet.sign(hash_payload)

        # افزودن به زنجیره
        if app_state.blockchain.add_block(new_block, app_state.known_authorities):
            # مشاهده توسط Cognitive Core
            if app_state.cognitive_core:
                app_state.cognitive_core.observe(new_block)

            # انتشار در شبکه
            await app_state.p2p_manager.broadcast({
                "type": "NEW_BLOCK_ANNOUNCEMENT",
                "payload": new_block.model_dump()
            })

            print(f"✅ Forged and broadcasted block #{new_block.index}")


async def cognitive_evolution_process():
    """فرآیند تکامل Cognitive Core"""
    while True:
        await asyncio.sleep(60)  # هر 60 ثانیه

        if app_state.cognitive_core and len(app_state.cognitive_core.observations) >= 20:
            # پیشنهاد بهبود پروتوکل
            proposal = app_state.cognitive_core.propose_protocol_improvement()
            if proposal:
                print(f"📜 Cognitive Core proposed: {proposal.title}")


async def simulation_process():
    """فرآیند شبیه‌سازی کیهانی"""
    while True:
        await asyncio.sleep(1)  # هر ثانیه

        if app_state.cosmic_simulator:
            app_state.cosmic_simulator.step()


# ============================================================================
# Main Initialization
# ============================================================================

async def main():
    """تابع اصلی"""
    parser = argparse.ArgumentParser(description="Laniakea Protocol Node")
    parser.add_argument('--p2p-port', type=int, required=True, help="P2P port")
    parser.add_argument('--api-port', type=int, required=True, help="API port")
    parser.add_argument('--enable-simulation', action='store_true', help="Enable cosmic simulation")
    args = parser.parse_args()

    print("=" * 70)
    print("🌌 LANIAKEA PROTOCOL v3.0 - The Cosmic Computational Organism")
    print("=" * 70)

    # ایجاد wallet
    app_state.wallet = Wallet(f"data_node_{args.p2p_port}")
    node_id = app_state.wallet.node_id

    # تنظیم authority
    if is_authority():
        AUTHORITY_NODES.add(node_id)
        app_state.known_authorities.add(node_id)
        print(f"👑 This node is an AUTHORITY node")

    # ایجاد node info
    app_state.node_info = NodeInfo(
        node_id=node_id,
        host=HOST,
        p2p_port=args.p2p_port,
        api_port=args.api_port,
        specialties={NodeSpecialty.MINING, NodeSpecialty.SOLVING, NodeSpecialty.AI_INFERENCE}
    )

    # ایجاد blockchain
    app_state.blockchain = LaniakeaChain(node_id)
    app_state.blockchain.create_genesis_block()

    # ایجاد P2P manager
    app_state.p2p_manager = P2PManager(HOST, args.p2p_port, handle_p2p_message)

    # ایجاد سیستم‌های پیشرفته
    print("\n🚀 Initializing advanced systems...")

    app_state.cognitive_core = CognitiveCore(model="gpt-4.1-mini")
    app_state.oracle_manager = OracleManager()
    app_state.hash_modernity = HashModernityEngine()
    app_state.token_economics = TokenEconomics()
    app_state.staking_system = StakingSystem(app_state.token_economics)

    if args.enable_simulation:
        app_state.cosmic_simulator = CosmicSimulator()
        app_state.cosmic_simulator.create_genesis_cell()
        print("🌱 Cosmic simulation enabled")

    # انتشار authority
    if is_authority():
        await app_state.p2p_manager.broadcast({
            "type": "ANNOUNCE_AUTHORITY",
            "payload": {"node_id": node_id}
        })

    print(f"\n✨ Node initialized: {node_id[:12]}...")
    print(f"🔗 P2P: ws://{HOST}:{args.p2p_port}")
    print(f"🌐 API: http://{HOST}:{args.api_port}")
    print("=" * 70)

    # ایجاد task های background
    tasks = [
        asyncio.create_task(app_state.p2p_manager.start()),
        asyncio.create_task(
            uvicorn.Server(
                uvicorn.Config(app, host=HOST, port=args.api_port, log_level="warning")
            ).serve()
        ),
        asyncio.create_task(cognitive_evolution_process())
    ]

    if is_authority():
        tasks.append(asyncio.create_task(authority_mining_process()))

    if args.enable_simulation:
        tasks.append(asyncio.create_task(simulation_process()))

    # اجرا
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Laniakea Protocol...")
        print("💫 The cosmic journey continues...")
