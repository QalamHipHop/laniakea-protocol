"""
LaniakeA Protocol - FastAPI Network Interface
RESTful API for blockchain interactions
Version: 3.0.0
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uvicorn
import uuid
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from src.websocket.websocket_manager import WebSocketManager, ConnectionType
from src.websocket.realtime_updates import RealtimeUpdateSystem, UpdateEvent, UpdateType
from laniakea.intelligence.scda_model import SingleCellDigitalAccount # Import SCDA model

# Import cross-chain bridge router
from src.crosschain.cross_chain_bridge import router as cross_chain_router
    # Import smart contract router
from laniakea.network.llm_api_router import router as llm_router
from laniakea.network.smart_contract_api import router as contract_router

# Request/Response Models
class TransactionRequest(BaseModel):
    sender: str
    recipient: str
    amount: float
    metadata: Dict[str, Any] = {}

class TransactionResponse(BaseModel):
    transaction_id: str
    status: str
    timestamp: float

class StatusResponse(BaseModel):
    chain_length: int
    total_transactions: int
    node_id: str
    status: str

def create_app(
    blockchain,
    brain=None,
    config: Dict[str, Any] = None,
    logger: Optional[logging.Logger] = None,
    dev_mode: bool = False
) -> FastAPI:
    """
    Create FastAPI application
    """
    app = FastAPI(
        title="LaniakeA Protocol API",
        description="8-Dimensional Blockchain with AI Intelligence",
        version="3.0.0",
        docs_url="/docs" if dev_mode else None,
        redoc_url="/redoc" if dev_mode else None
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Store instances
    app.state.blockchain = blockchain
    app.state.brain = brain
    app.state.config = config or {}
    app.state.logger = logger or logging.getLogger('laniakea.api')
    
    # Initialize WebSocket and Realtime Systems
    app.state.websocket_manager = WebSocketManager()
    app.state.realtime_system = RealtimeUpdateSystem(app.state.websocket_manager)
    
    # Placeholder for SCDA Management (Needs proper database integration later)
    # For now, a simple in-memory SCDA store
    app.state.scda_store: Dict[str, SingleCellDigitalAccount] = {}
    
    # Initialize Governance System
    from src.governance.dao import GovernanceSystem
    app.state.governance_system = GovernanceSystem()
    
    # Start Realtime System
    @app.on_event("startup")
    async def startup_event():
        await app.state.realtime_system.start()
        # Create a dummy SCDA for testing
        dummy_scda = SingleCellDigitalAccount(identity="user_123")
        app.state.scda_store[dummy_scda.identity] = dummy_scda
        app.state.logger.info(f"Dummy SCDA {dummy_scda.identity} created.")
        
        # Create a dummy civilization for testing
        try:
            civ_id = app.state.governance_system.create_civilization(leader_id=dummy_scda.identity, name="The Laniakea Core")
            app.state.logger.info(f"Dummy Civilization '{civ_id}' created with leader {dummy_scda.identity}.")
        except Exception as e:
            app.state.logger.error(f"Failed to create dummy civilization: {e}")

    @app.on_event("shutdown")
    async def shutdown_event():
        await app.state.realtime_system.stop()
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "name": "LaniakeA Protocol",
            "version": "3.0.0",
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.get("/api/v1/status", response_model=StatusResponse)
    async def get_status():
        """Get blockchain status"""
        try:
            status = app.state.blockchain.get_status()
            return StatusResponse(
                chain_length=status.get('chain_length', 0),
                total_transactions=status.get('total_transactions', 0),
                node_id=app.state.blockchain.node_id,
                status='operational'
            )
        except Exception as e:
            app.state.logger.error(f"Error getting status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/blockchain")
    async def get_blockchain():
        """Get full blockchain"""
        try:
            return app.state.blockchain.to_dict()
        except Exception as e:
            app.state.logger.error(f"Error getting blockchain: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/transaction", response_model=TransactionResponse)
    async def create_transaction(tx: TransactionRequest):
        """Create new transaction"""
        try:
            from laniakea.core.hypercube_blockchain import HyperTransaction
            
            transaction = HyperTransaction(
                sender=tx.sender,
                recipient=tx.recipient,
                amount=tx.amount,
                metadata=tx.metadata
            )
            
            success = app.state.blockchain.add_transaction(transaction)
            
            if success:
                return TransactionResponse(
                    transaction_id=transaction.transaction_id,
                    status='pending',
                    timestamp=transaction.timestamp
                )
            else:
                raise HTTPException(status_code=400, detail="Invalid transaction")
                
        except Exception as e:
            app.state.logger.error(f"Error creating transaction: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/mine")
    async def mine_block(miner_address: str = "default-miner"):
        """Mine pending transactions"""
        try:
            block = app.state.blockchain.mine_pending_transactions(miner_address)
            
            if block:
                return {
                    "status": "success",
                    "block_index": block.index,
                    "block_hash": block.hash,
                    "transactions": len(block.transactions)
                }
            else:
                return {
                    "status": "no_transactions",
                    "message": "No pending transactions to mine"
                }
                
        except Exception as e:
            app.state.logger.error(f"Error mining block: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/balance/{address}")
    async def get_balance(address: str):
        """Get address balance"""
        try:
            balance = app.state.blockchain.get_balance(address)
            return {
                "address": address,
                "balance": balance
            }
        except Exception as e:
            app.state.logger.error(f"Error getting balance: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # --- Routers ---
    app.include_router(cross_chain_router, prefix="/api/v1/bridge", tags=["Cross-Chain Bridge"])
    app.include_router(contract_router, prefix="/api/v1/contract", tags=["Smart Contracts"])
    app.include_router(llm_router, prefix="/api/v1", tags=["LLM Services"])
    
    # --- SCDA Management Router ---
    scda_router = APIRouter(prefix="/api/v1/scda", tags=["SCDA Management"])
    
    class SCDA_ID_Request(BaseModel):
        scda_id: str
        
    class SCDA_Breed_Request(BaseModel):
        parent1_id: str
        parent2_id: str
        
    class SCDA_Details_Response(BaseModel):
        identity: str
        complexity_index: float
        genetic_diversity: float
        dominant_knowledge_traits: List[str]
        
    @scda_router.get("/{scda_id}", response_model=SCDA_Details_Response)
    async def get_scda_details(scda_id: str):
        """Get SCDA details for Breeding Lab"""
        scda = app.state.scda_store.get(scda_id)
        if not scda:
            # Check if SCDA exists in the SCDA store (in-memory for now)
            # If not, create a new one for demonstration purposes
            new_scda = SingleCellDigitalAccount(identity=scda_id)
            app.state.scda_store[scda_id] = new_scda
            scda = new_scda
            app.state.logger.info(f"New SCDA {scda_id} created on demand for API call.")
    async def get_scda_details(scda_id: str):
        """Get SCDA details for Breeding Lab"""
        scda = app.state.scda_store.get(scda_id)
        if not scda:
            raise HTTPException(status_code=404, detail="SCDA not found")
            
        # Use the SCDA model's new functions
        dominant_traits = scda.dna.get_dominant_genes()
        
        return SCDA_Details_Response(
            identity=scda.identity,
            complexity_index=scda.complexity_index,
            genetic_diversity=scda.dna.calculate_genetic_diversity(),
            dominant_knowledge_traits=[f"{g.domain} ({g.strength:.2f})" for g in dominant_traits]
        )
        
    @scda_router.post("/predict_child")
    async def predict_child(request: SCDA_Breed_Request):
        """Predict child traits based on parents' DNA"""
        parent1 = app.state.scda_store.get(request.parent1_id)
        parent2 = app.state.scda_store.get(request.parent2_id)
        
        if not parent1 or not parent2:
            raise HTTPException(status_code=404, detail="One or both parent SCDAs not found")
            
        from laniakea.intelligence.scda_model import predict_child_traits
        
        prediction = predict_child_traits(parent1, parent2)
        return prediction
        
    @scda_router.post("/breed")
    async def breed_scdas_api(request: SCDA_Breed_Request):
        """Create a new SCDA by breeding two parents"""
        parent1 = app.state.scda_store.get(request.parent1_id)
        parent2 = app.state.scda_store.get(request.parent2_id)
        
        if not parent1 or not parent2:
            raise HTTPException(status_code=404, detail="One or both parent SCDAs not found")
            
        from laniakea.intelligence.scda_model import breed_scdas
        
        child_scda = breed_scdas(parent1, parent2)
        
        # Add child to store (In a real system, this would be a database write)
        app.state.scda_store[child_scda.identity] = child_scda
        
        # Prepare response
        dominant_traits = child_scda.dna.get_dominant_genes()
        
        return {
            "child_id": child_scda.identity,
            "initial_complexity": f"{child_scda.complexity_index:.4f}",
            "genetic_diversity": f"{child_scda.dna.calculate_genetic_diversity():.4f}",
            "dominant_knowledge_traits": [f"{g.domain} ({g.strength:.2f})" for g in dominant_traits]
        }
        
    app.include_router(scda_router)
    
    # --- Civilization Management API Endpoints ---
    
    class Civilization_Create_Request(BaseModel):
        leader_id: str
        name: str
        
    class Civilization_Join_Request(BaseModel):
        scda_id: str
        civ_id: str
        
    class Civilization_Deposit_Request(BaseModel):
        scda_id: str
        amount: float
        
    class Civilization_Proposal_Request(BaseModel):
        proposer_id: str
        title: str
        description: str
        proposal_type: str
        target: str
        action: str
        parameters: Dict = {}
        
    class Civilization_Vote_Request(BaseModel):
        voter_id: str
        proposal_id: str
        vote: bool
        reason: Optional[str] = None
        
    civ_router = APIRouter(prefix="/api/v1/civilization", tags=["Civilization Management"])
    
    @civ_router.post("/create")
    async def create_civilization_api(request: Civilization_Create_Request):
        """Create a new civilization"""
        try:
            civ_id = app.state.governance_system.create_civilization(request.leader_id, request.name)
            return {"status": "success", "civilization_id": civ_id}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
            
    @civ_router.post("/join")
    async def join_civilization_api(request: Civilization_Join_Request):
        """Join an existing civilization"""
        try:
            success = app.state.governance_system.join_civilization(request.scda_id, request.civ_id)
            if not success:
                raise HTTPException(status_code=404, detail="Civilization not found")
            return {"status": "success"}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
            
    @civ_router.get("/{civ_id}")
    async def get_civilization_api(civ_id: str):
        """Get civilization details"""
        data = app.state.governance_system.get_civilization_data(civ_id)
        if not data:
            raise HTTPException(status_code=404, detail="Civilization not found")
        
        # Convert set to list for JSON serialization
        data["members"] = list(data["members"])
        return data
        
    @civ_router.post("/deposit")
    async def deposit_treasury_api(request: Civilization_Deposit_Request):
        """Deposit funds to civilization treasury"""
        success = app.state.governance_system.deposit_to_treasury(request.scda_id, request.amount)
        if not success:
            raise HTTPException(status_code=400, detail="SCDA not in a civilization")
        return {"status": "success"}
        
    @civ_router.post("/proposal")
    async def create_proposal_api(request: Civilization_Proposal_Request):
        """Create a new governance proposal"""
        from src.governance.dao import ProposalType
        try:
            proposal = app.state.governance_system.create_proposal(
                proposer_id=request.proposer_id,
                title=request.title,
                description=request.description,
                proposal_type=ProposalType(request.proposal_type),
                target=request.target,
                action=request.action,
                parameters=request.parameters
            )
            return {"status": "success", "proposal_id": proposal.id}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {e}")
            
    @civ_router.post("/vote")
    async def cast_vote_api(request: Civilization_Vote_Request):
        """Cast a vote on a proposal"""
        # For demonstration, we'll set the voter's stake to their current complexity index
        scda = app.state.scda_store.get(request.voter_id)
        if scda:
            app.state.governance_system.voter_stakes[request.voter_id] = scda.complexity_index
            
        success = app.state.governance_system.cast_vote(
            voter_id=request.voter_id,
            proposal_id=request.proposal_id,
            vote=request.vote,
            reason=request.reason
        )
        if not success:
            raise HTTPException(status_code=400, detail="Vote failed (e.g., proposal not active, already voted)")
        return {"status": "success"}
        
    app.include_router(civ_router)
    
    # --- WebSocket Endpoint for Real-time Collaboration ---
    @app.websocket("/ws/{client_id}/{conn_type}")
    async def websocket_endpoint(websocket: WebSocket, client_id: str, conn_type: str):
        
        # 1. Validate Connection Type
        try:
            connection_type = ConnectionType(conn_type)
        except ValueError:
            await websocket.close(code=1008, reason=f"Invalid connection type: {conn_type}")
            return
            
        # 2. Connect
        connection_id = f"{client_id}_{conn_type}_{str(uuid.uuid4())[:4]}"
        
        # Simple SCDA check (for now, assume client_id is SCDA ID)
        if client_id not in app.state.scda_store:
            # Create a new SCDA if it doesn't exist (for demo purposes)
            new_scda = SingleCellDigitalAccount(identity=client_id)
            app.state.scda_store[client_id] = new_scda
            app.state.logger.info(f"New SCDA {client_id} created for WebSocket connection.")
            
        metadata = {"scda_id": client_id}
        
        success = await app.state.websocket_manager.connect(websocket, connection_id, connection_type, metadata)
        if not success:
            return
            
        try:
            while True:
                # 3. Receive Message
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # 4. Handle Message
                await app.state.websocket_manager.handle_message(connection_id, message_data)
                
        except WebSocketDisconnect:
            # 5. Disconnect
            await app.state.websocket_manager.disconnect(connection_id)
        except Exception as e:
            app.state.logger.error(f"WebSocket error for {connection_id}: {e}")
            await app.state.websocket_manager.disconnect(connection_id)
            
    return app

def run_server(
    app: FastAPI,
    host: str = "0.0.0.0",
    port: int = 8000,
    workers: int = 1,
    reload: bool = False,
    logger: Optional[logging.Logger] = None
):
    """
    Run the FastAPI server
    """
    if logger:
        logger.info(f"🚀 Starting server on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=workers,
        reload=reload,
        log_level="info"
    )
