# laniakea/api/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

# Import core components
from laniakea.core.config import settings
from laniakea.utils.logger import setup_logger

# Import recovered modules
from laniakea.blockchain.core import Blockchain
from laniakea.consensus.poa import ProofOfAuthority
from laniakea.crosschain.bridge import Bridge
from laniakea.quantum.processor import QuantumProcessor, QuantumCircuit
from laniakea.governance.dao import DAO
from laniakea.marketplace.nft import Marketplace
from laniakea.simulation.cosmic import CosmicSimulator, CosmicEntity
from laniakea.dashboard.metrics import ProtocolMetrics
from laniakea.achievements.system import AchievementSystem
from laniakea.ai.model import AIModel
from laniakea.defi.swap import DecentralizedExchange, LiquidityPool

# --- Initialization ---
logger = setup_logger("laniakea.api")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="The unified API for the Laniakea Protocol, integrating all core modules.",
    version=settings.PROJECT_VERSION
)

# Global instances of the core systems, initialized from config
laniakea_chain = Blockchain()
laniakea_consensus = ProofOfAuthority(settings.AUTHORITIES)
laniakea_bridge = Bridge(supported_chains=settings.SUPPORTED_CHAINS)
laniakea_quantum = QuantumProcessor(max_qubits=settings.MAX_QUBITS)
laniakea_dao = DAO(total_supply=settings.TOTAL_TOKEN_SUPPLY)
laniakea_marketplace = Marketplace()
laniakea_simulator = CosmicSimulator(time_step=settings.SIMULATION_TIME_STEP)
laniakea_metrics = ProtocolMetrics()
laniakea_achievements = AchievementSystem()
laniakea_ai = AIModel("LANA_KE_001")
laniakea_dex = DecentralizedExchange()

# Initialize simulator with some entities
import numpy as np
laniakea_simulator.add_entity(CosmicEntity("Laniakea_Core", "Galaxy", [0.0, 0.0, 0.0], 1.0e42))
laniakea_simulator.add_entity(CosmicEntity("Milky_Way", "Galaxy", [1.0e22, 0.0, 0.0], 1.5e42))

# Add AI and DeFi endpoints to the logger info
logger.info("Laniakea Protocol components initialized, including AI and DeFi.")



# --- Pydantic Models for API ---

class Transaction(BaseModel):
    sender: str
    recipient: str
    amount: float

class BlockResponse(BaseModel):
    index: int
    timestamp: float
    transactions: List[Dict[str, Any]]
    proof: Any
    previous_hash: str

class BridgeTransfer(BaseModel):
    source_chain: str
    target_chain: str
    asset: str
    amount: float
    sender: str
    recipient: str

class AIQuery(BaseModel):
    prompt: str

class SwapRequest(BaseModel):
    token_in: str
    token_out: str
    amount_in: float

class QuantumJob(BaseModel):
    num_qubits: int
    gates: List[Dict[str, Any]] # e.g., [{"type": "H", "target": 0}, {"type": "X", "target": 1}]

# --- API Endpoints ---

@app.get("/", tags=["System"])
def read_root():
    logger.info("Root endpoint accessed.")
    return {"message": f"Welcome to the {settings.PROJECT_NAME} Unified API"}

# --- Blockchain Endpoints ---

@app.get("/blockchain/chain", response_model=List[BlockResponse], tags=["Blockchain"])
def full_chain():
    return [block.to_dict() for block in laniakea_chain.chain]

@app.post("/blockchain/transactions/new", tags=["Blockchain"])
def new_transaction(tx: Transaction):
    index = laniakea_chain.new_transaction(tx.sender, tx.recipient, tx.amount)
    logger.info(f"New transaction from {tx.sender} to {tx.recipient} queued for block {index}.")
    return {"message": f"Transaction will be added to Block {index}"}

@app.post("/blockchain/mine", tags=["Blockchain"])
def mine_block(authority_address: str = settings.AUTHORITIES[0]):
    if authority_address not in settings.AUTHORITIES:
        logger.warning(f"Unauthorized mine attempt by {authority_address}.")
        raise HTTPException(status_code=403, detail="Not a recognized authority.")
        
    new_block = laniakea_consensus.sign_block(laniakea_chain, authority_address)
    logger.info(f"New block {new_block.index} forged by {authority_address}.")
    
    # Update metrics
    laniakea_metrics.update_metric("latest_block_height", new_block.index)
    laniakea_metrics.update_metric("total_transactions", laniakea_metrics.metrics["total_transactions"] + len(new_block.transactions))
    laniakea_achievements.update_user_progress(authority_address, "blockchain.blocks_mined", new_block.index)
    
    return {
        "message": "New Block Forged",
        "block": new_block.to_dict()
    }

# --- Cross-Chain Endpoints ---

@app.post("/crosschain/transfer/initiate", tags=["Cross-Chain"])
def initiate_cross_chain_transfer(transfer: BridgeTransfer):
    try:
        tx = laniakea_bridge.initiate_transfer(
            transfer.source_chain, transfer.target_chain, transfer.asset, 
            transfer.amount, transfer.sender, transfer.recipient
        )
        logger.info(f"Cross-chain transfer initiated: {tx.tx_id}")
        laniakea_achievements.update_user_progress(transfer.sender, "crosschain.transfers_completed", len(laniakea_bridge.completed_transactions) + 1)
        return {"message": "Transfer initiated successfully", "tx_id": tx.tx_id}
    except ValueError as e:
        logger.error(f"Cross-chain initiation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/crosschain/transfer/complete/{tx_id}", tags=["Cross-Chain"])
def complete_cross_chain_transfer(tx_id: str):
    try:
        tx = laniakea_bridge.complete_transfer(tx_id)
        logger.info(f"Cross-chain transfer completed: {tx.tx_id}")
        return {"message": "Transfer completed successfully", "tx": tx.to_dict()}
    except ValueError as e:
        logger.error(f"Cross-chain completion failed for {tx_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))

# --- Quantum Endpoints ---

@app.post("/quantum/job/submit", tags=["Quantum"])
def submit_quantum_job(job: QuantumJob):
    try:
        qc = laniakea_quantum.create_circuit(job.num_qubits)
        for gate in job.gates:
            if gate["type"].lower() == "h":
                qc.h_gate(gate["target"])
            elif gate["type"].lower() == "x":
                qc.x_gate(gate["target"])
        
        laniakea_quantum.submit_job(qc)
        laniakea_metrics.update_metric("quantum_job_queue_size", len(laniakea_quantum.job_queue))
        laniakea_achievements.update_user_progress("System", "quantum.jobs_submitted", len(laniakea_quantum.job_queue))
        logger.info(f"Quantum job submitted with {job.num_qubits} qubits.")
        return {"message": "Quantum job submitted", "queue_size": len(laniakea_quantum.job_queue)}
    except ValueError as e:
        logger.error(f"Quantum job submission failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/quantum/job/process", tags=["Quantum"])
def process_quantum_job():
    result = laniakea_quantum.process_next_job()
    laniakea_metrics.update_metric("quantum_job_queue_size", len(laniakea_quantum.job_queue))
    if result is None:
        logger.info("No pending quantum jobs to process.")
        return {"message": "No pending quantum jobs"}
    logger.info(f"Quantum job processed. Result: {result}")
    return {"message": "Quantum job processed", "result": result}

# --- Governance Endpoints ---

class ProposalCreate(BaseModel):
    title: str
    description: str
    proposer: str

class VoteCast(BaseModel):
    voter_address: str
    vote_type: str # "for" or "against"

@app.post("/governance/proposals/new", tags=["Governance"])
def create_proposal(prop: ProposalCreate):
    proposal = laniakea_dao.create_proposal(prop.title, prop.description, prop.proposer)
    logger.info(f"New DAO proposal created by {prop.proposer}: {prop.title}")
    return {"message": "Proposal created", "proposal_id": proposal.proposal_id}

@app.post("/governance/proposals/{proposal_id}/vote", tags=["Governance"])
def cast_vote(proposal_id: int, vote: VoteCast):
    try:
        laniakea_dao.vote(proposal_id, vote.voter_address, vote.vote_type)
        laniakea_achievements.update_user_progress(vote.voter_address, "governance.votes_cast", len(laniakea_dao.proposals[proposal_id].voters))
        logger.info(f"Vote cast by {vote.voter_address} on proposal {proposal_id}.")
        return {"message": "Vote cast successfully"}
    except ValueError as e:
        logger.error(f"Vote failed on proposal {proposal_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/governance/proposals/{proposal_id}/finalize", tags=["Governance"])
def finalize_proposal(proposal_id: int):
    try:
        laniakea_dao.finalize_proposal(proposal_id)
        logger.info(f"Proposal {proposal_id} finalized with status: {laniakea_dao.proposals[proposal_id].status}")
        return {"message": f"Proposal {proposal_id} finalized", "status": laniakea_dao.proposals[proposal_id].status}
    except ValueError as e:
        logger.error(f"Finalization failed for proposal {proposal_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))

# --- Marketplace Endpoints ---

class NFTMint(BaseModel):
    owner: str
    metadata_uri: str
    asset_type: str

@app.post("/marketplace/nft/mint", tags=["Marketplace"])
def mint_nft(nft_data: NFTMint):
    nft = laniakea_marketplace.mint_nft(nft_data.owner, nft_data.metadata_uri, nft_data.asset_type)
    logger.info(f"NFT {nft.token_id} minted for {nft_data.owner}.")
    return {"message": "NFT minted successfully", "token_id": nft.token_id}

@app.post("/marketplace/nft/{token_id}/list", tags=["Marketplace"])
def list_nft(token_id: str, price: float):
    try:
        laniakea_marketplace.list_nft(token_id, price)
        logger.info(f"NFT {token_id} listed for sale at {price} LANA.")
        return {"message": f"NFT {token_id} listed for {price}"}
    except ValueError as e:
        logger.error(f"NFT listing failed for {token_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/marketplace/nft/{token_id}/buy", tags=["Marketplace"])
def buy_nft(token_id: str, buyer: str):
    try:
        nft = laniakea_marketplace.buy_nft(token_id, buyer)
        logger.info(f"NFT {token_id} purchased by {buyer}.")
        return {"message": f"NFT {token_id} purchased by {buyer}", "new_owner": nft.owner}
    except ValueError as e:
        logger.error(f"NFT purchase failed for {token_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# --- Simulation Endpoints ---

@app.post("/simulation/step", tags=["Simulation"])
def step_simulation():
    laniakea_simulator.step_simulation()
    laniakea_achievements.update_user_progress("System", "simulation.steps_run", int(laniakea_simulator.current_time / laniakea_simulator.time_step))
    logger.info(f"Cosmic simulation stepped. Current time: {laniakea_simulator.current_time}")
    return {"message": "Simulation advanced one step", "current_time": laniakea_simulator.current_time}

@app.get("/simulation/entities", tags=["Simulation"])
def get_simulation_entities():
    return [entity.to_dict() for entity in laniakea_simulator.entities]

# --- Dashboard/Metrics Endpoints ---

@app.get("/dashboard/metrics", tags=["Dashboard"])
def get_metrics():
    return laniakea_metrics.get_all_metrics()

@app.get("/dashboard/history/{key}", tags=["Dashboard"])
def get_metric_history(key: str):
    history = laniakea_metrics.get_metric_history(key)
    if not history:
        raise HTTPException(status_code=404, detail="Metric history not found.")
    return history

# --- Achievements Endpoints ---

@app.get("/achievements/all", tags=["Achievements"])
def get_all_achievements():
    return [ach.to_dict() for ach in laniakea_achievements.achievements.values()]

@app.get("/achievements/user/{user_id}", tags=["Achievements"])
def get_user_achievements(user_id: str):
    progress = laniakea_achievements.user_progress.get(user_id, {})
    if not progress:
        raise HTTPException(status_code=404, detail="User not found or no progress recorded.")
    return progress

# --- Core/Utils Endpoints ---

@app.get("/core/status", tags=["Core"])
def core_status():
    return {
        "status": "Operational",
        "protocol_version": settings.PROJECT_VERSION,
        "chain_length": len(laniakea_chain.chain),
        "dao_proposals": len(laniakea_dao.proposals),
        "quantum_queue": len(laniakea_quantum.job_queue),
        "ai_model_version": laniakea_ai.version,
        "dex_pools": len(laniakea_dex.pools)
    }

# --- AI Endpoints ---

@app.post("/ai/query", tags=["AI"])
def query_ai_model(query: AIQuery):
    result = laniakea_ai.query(query.prompt)
    logger.info(f"AI Model queried. Confidence: {result['confidence']:.2f}")
    return result

@app.post("/ai/train", tags=["AI"])
def train_ai_model(data_size: int):
    laniakea_ai.train(data_size)
    logger.info(f"AI Model trained with {data_size} data units.")
    return {"message": "AI Model training simulated successfully", "new_score": laniakea_ai.performance_score}

# --- DeFi Endpoints ---

@app.get("/defi/pools", tags=["DeFi"])
def get_all_pools():
    return {name: {"reserve_x": pool.reserve_x, "reserve_y": pool.reserve_y, "token_x": pool.token_x, "token_y": pool.token_y} for name, pool in laniakea_dex.pools.items()}

@app.post("/defi/swap", tags=["DeFi"])
def perform_swap(swap_request: SwapRequest):
    try:
        pool = laniakea_dex.get_pool(swap_request.token_in, swap_request.token_out)
        result = pool.swap(swap_request.token_in, swap_request.amount_in)
        logger.info(f"Swap performed: {swap_request.amount_in} {swap_request.token_in} -> {result['amount_out']:.4f} {swap_request.token_out}")
        return result
    except ValueError as e:
        logger.error(f"Swap failed: {e}")
        raise HTTPException(status_code=400, detail=str(e)}],path:
def core_status():
    return {
        "status": "Operational",
        "protocol_version": settings.PROJECT_VERSION,
        "chain_length": len(laniakea_chain.chain),
        "dao_proposals": len(laniakea_dao.proposals),
        "quantum_queue": len(laniakea_quantum.job_queue)
    }
