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
import time
import uuid
from fastapi import FastAPI, HTTPException, Depends, Request, status
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
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
from laniakea.external_apis.integrations import ExternalAPIIntegrator
from laniakea.network.smart_contract_api import router as contract_router

# Security Imports
from laniakea.security.auth import get_current_user, User, Token, create_access_token, oauth2_scheme
from datetime import timedelta
from redis import asyncio as aioredis
from fastapi_limiter import FastAPILimiter

# New SQLAlchemy Imports
from laniakea.storage.database_setup import init_db, get_db, Base 
from laniakea.storage.database import DatabaseConnection, BlockchainDatabase # Assuming these are still needed for legacy parts
from laniakea.monitoring.metrics import get_metrics_response, API_REQUESTS_TOTAL, API_REQUEST_LATENCY, REGISTRY # New metrics imports

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
    
    # Initialize Redis for Rate Limiting
    @app.on_event("startup")
    async def startup_event_redis():
        redis_host = Config.get("REDIS_HOST", "redis")
        redis_port = Config.get("REDIS_PORT", 6379)
        redis = aioredis.from_url(f"redis://{redis_host}:{redis_port}", encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis)
        app.state.logger.info("✅ FastAPILimiter initialized with Redis.")
    app.state.brain = brain
    app.state.config = config or {}
    app.state.logger = logger or logging.getLogger('laniakea.api')

    # Middleware for Prometheus metrics
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start_time = time.time()
        endpoint = request.url.path
        method = request.method
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise e
        finally:
            process_time = time.time() - start_time
            
            # Record request total
            API_REQUESTS_TOTAL.labels(endpoint=endpoint, method=method, status=status_code).inc()
            
            # Record request latency
            API_REQUEST_LATENCY.labels(endpoint=endpoint, method=method).observe(process_time)
            
        return response
    
    # Initialize WebSocket and Realtime Systems
    app.state.websocket_manager = WebSocketManager()
    app.state.realtime_system = RealtimeUpdateSystem(app.state.websocket_manager)
    
    # Placeholder for SCDA Management (Needs proper database integration later)
    # For now, a simple in-memory SCDA store
    app.state.scda_store: Dict[str, SingleCellDigitalAccount] = {}

    # Initialize SQLAlchemy ORM Database
    from laniakea.utils.config import Config
    db_url = Config.get("DATABASE_URL")
    if db_url:
        try:
            init_db(db_url)
            app.state.logger.info("SQLAlchemy ORM initialized successfully.")
        except Exception as e:
            app.state.logger.error(f"Failed to initialize SQLAlchemy ORM: {e}")
    else:
        app.state.logger.error("DATABASE_URL not found in configuration. SQLAlchemy ORM not initialized.")

    # Initialize Legacy Database (keep for compatibility if other parts rely on it)
    db_conn = DatabaseConnection(
        host=Config.get("POSTGRES_HOST", "db"), # Use 'db' as host for Docker Compose
        port=Config.get("POSTGRES_PORT", 5432),
        database=Config.get("POSTGRES_DB", "laniakea_db"),
        user=Config.get("POSTGRES_USER", "laniakea_user"),
        password=Config.get("POSTGRES_PASSWORD", "laniakea_password")
    )
    if db_conn.connect():
        app.state.blockchain_db = BlockchainDatabase(db_conn)
    else:
        app.state.logger.error("Failed to connect to the legacy database.")
    
    # Initialize Governance System
    from src.governance.dao import GovernanceSystem
    from src.governance.diplomacy_system import get_diplomacy_system
    app.state.governance_system = GovernanceSystem()
    app.state.diplomacy_system = get_diplomacy_system()
    
    # Initialize External API Integrator
    app.state.external_api_integrator = ExternalAPIIntegrator()
    
    # Start Realtime System
    @app.on_event("startup")
    async def startup_event_laniakea():
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
    
    @app.get("/", dependencies=[Depends(get_current_user)]) # Protect root endpoint for demonstration
    async def root(current_user: User = Depends(get_current_user)):
        """Root endpoint"""
        return {
            "name": "LaniakeA Protocol",
            "version": "3.0.0",
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint"""
        return Response(content=get_metrics_response(), media_type="text/plain")

    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.get("/api/v1/status", response_model=StatusResponse, dependencies=[Depends(get_current_user)])
    async def get_status(current_user: User = Depends(get_current_user)):
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
    
    @app.get("/api/v1/blockchain", dependencies=[Depends(get_current_user)])
    async def get_blockchain(current_user: User = Depends(get_current_user)):
        """Get full blockchain"""
        try:
            return app.state.blockchain.to_dict()
        except Exception as e:
            app.state.logger.error(f"Error getting blockchain: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/transaction", response_model=TransactionResponse, dependencies=[Depends(get_current_user)])
    async def create_transaction(tx: TransactionRequest, current_user: User = Depends(get_current_user)):
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
    
    @app.post("/api/v1/mine", dependencies=[Depends(get_current_user)])
    async def mine_block(miner_address: str = "default-miner", current_user: User = Depends(get_current_user)):
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
    
    @app.get("/api/v1/balance/{address}", dependencies=[Depends(get_current_user)])
    async def get_balance(address: str, current_user: User = Depends(get_current_user)):
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
    
    # --- External API Router ---
    external_api_router = APIRouter(prefix="/api/v1/external", tags=["External APIs"], dependencies=[Depends(get_current_user)])
    
    @external_api_router.get("/coingecko/price/{coin_id}")
    async def get_coin_price(coin_id: str):
        price = app.state.external_api_integrator.get_token_price(coin_id)
        if price is None:
            raise HTTPException(status_code=404, detail=f"Price for {coin_id} not found or API error.")
        return {"coin_id": coin_id, "price_usd": price}

    @external_api_router.get("/arxiv/search")
    async def search_arxiv_papers(query: str):
        results = app.state.external_api_integrator.search_arxiv(query)
        return {"query": query, "results": results}

    @external_api_router.get("/nasa/apod")
    async def get_nasa_picture():
        apod = app.state.external_api_integrator.get_nasa_apod()
        if apod is None:
            raise HTTPException(status_code=500, detail="Failed to fetch NASA APOD.")
        return apod
        
    app.include_router(external_api_router)
    
    # --- Authentication Endpoint ---
    @app.post("/token", response_model=Token)
    async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
        # In a real app, you would verify the user/password against the database
        # For this example, we'll use a simple mock check
        if form_data.username != "testuser" or form_data.password != "testpass":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=Config.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
        access_token = create_access_token(
            data={"sub": form_data.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    # --- SCDA Management Router ---
    scda_router = APIRouter(prefix="/api/v1/scda", tags=["SCDA Management"], dependencies=[Depends(get_current_user)])
    
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
    
    # --- Diplomacy Management Router ---
    diplomacy_router = APIRouter(prefix="/api/v1/diplomacy", tags=["Diplomacy Management"])
    
    class SetRelationRequest(BaseModel):
        scda1_id: str
        scda2_id: str
        relation: str
        
    class ProposeTreatyRequest(BaseModel):
        parties: List[str]
        treaty_type: str
        duration: float
        terms: Dict[str, Any] = {}
        
    class DissolveTreatyRequest(BaseModel):
        treaty_id: str
        reason: str
        
    @diplomacy_router.post("/set_relation")
    async def set_relation_api(request: SetRelationRequest):
        """Set a diplomatic relation between two SCDAs"""
        from src.governance.diplomacy_system import RelationType
        try:
            relation_type = RelationType(request.relation)
            app.state.diplomacy_system.set_relation(request.scda1_id, request.scda2_id, relation_type)
            return {"status": "success", "relation": relation_type.value}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid relation type: {e}")
            
    @diplomacy_router.get("/relation/{scda1_id}/{scda2_id}")
    async def get_relation_api(scda1_id: str, scda2_id: str):
        """Get the diplomatic relation between two SCDAs"""
        relation = app.state.diplomacy_system.get_relation(scda1_id, scda2_id)
        return {"scda1": scda1_id, "scda2": scda2_id, "relation": relation.value}

    @diplomacy_router.post("/propose_treaty")
    async def propose_treaty_api(request: ProposeTreatyRequest):
        """Propose and sign a new diplomatic treaty"""
        from src.governance.diplomacy_system import TreatyType
        try:
            treaty_type = TreatyType(request.treaty_type)
            treaty = app.state.diplomacy_system.propose_treaty(
                request.parties, treaty_type, request.duration, request.terms
            )
            return {"status": "success", "treaty_id": treaty.treaty_id, "treaty_info": treaty.to_dict()}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
            
    @diplomacy_router.post("/dissolve_treaty")
    async def dissolve_treaty_api(request: DissolveTreatyRequest):
        """Dissolve an active diplomatic treaty"""
        success = app.state.diplomacy_system.dissolve_treaty(request.treaty_id, request.reason)
        if not success:
            raise HTTPException(status_code=404, detail="Treaty not found or already dissolved")
        return {"status": "success"}

    @diplomacy_router.get("/summary/{scda_id}")
    async def get_diplomacy_summary_api(scda_id: str):
        """Get the diplomatic summary for a single SCDA"""
        summary = app.state.diplomacy_system.get_scda_diplomacy_summary(scda_id)
        return summary
        
    app.include_router(diplomacy_router)
    
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
