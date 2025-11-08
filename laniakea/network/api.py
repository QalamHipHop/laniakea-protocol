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
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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
