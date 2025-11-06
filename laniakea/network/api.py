"""
LaniakeA Protocol - FastAPI Server
RESTful API and WebSocket server for LaniakeA Protocol
Version: 3.0.0
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from pydantic import BaseModel, Field


# Request/Response Models
class TransactionRequest(BaseModel):
    """Transaction request model"""
    sender: str = Field(..., description="Sender address")
    recipient: str = Field(..., description="Recipient address")
    amount: float = Field(..., gt=0, description="Transaction amount")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ThinkRequest(BaseModel):
    """AI thinking request model"""
    problem: str = Field(..., description="Problem or question to think about")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    deep_analysis: bool = Field(default=False, description="Enable deep analysis mode")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: float
    uptime: float


def create_app(
    blockchain,
    brain,
    config: Dict[str, Any],
    logger: logging.Logger,
    dev_mode: bool = False
) -> FastAPI:
    """
    Create and configure FastAPI application
    
    Args:
        blockchain: LaniakeABlockchain instance
        brain: CosmicBrainAI instance
        config: Configuration dictionary
        logger: Logger instance
        dev_mode: Enable developer mode
    
    Returns:
        Configured FastAPI app
    """
    
    # Create FastAPI app
    app = FastAPI(
        title="LaniakeA Protocol API",
        description="Intelligent Blockchain Protocol with AI and Quantum Security",
        version="3.0.0",
        docs_url="/docs" if dev_mode else None,
        redoc_url="/redoc" if dev_mode else None
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.get('security', {}).get('allowed_origins', ['*']),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Store references
    app.state.blockchain = blockchain
    app.state.brain = brain
    app.state.config = config
    app.state.logger = logger
    app.state.dev_mode = dev_mode
    app.state.start_time = time.time()
    app.state.websocket_connections: List[WebSocket] = []
    
    # Health check endpoint
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint"""
        uptime = time.time() - app.state.start_time
        
        return HealthResponse(
            status="healthy",
            version="3.0.0",
            timestamp=time.time(),
            uptime=uptime
        )
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information"""
        return {
            "name": "LaniakeA Protocol",
            "version": "3.0.0",
            "description": "Intelligent Blockchain Protocol with AI and Quantum Security",
            "endpoints": {
                "health": "/health",
                "status": "/api/status",
                "blockchain": "/api/blockchain",
                "transactions": "/api/transactions",
                "ai": "/api/ai/think",
                "docs": "/docs" if dev_mode else "disabled"
            }
        }
    
    # Status endpoint
    @app.get("/api/status")
    async def get_status():
        """Get comprehensive system status"""
        try:
            blockchain_status = app.state.blockchain.get_status()
            ai_status = app.state.brain.get_status() if app.state.brain else {}
            
            uptime = time.time() - app.state.start_time
            
            status = {
                "system": {
                    "version": "3.0.0",
                    "uptime_seconds": round(uptime, 2),
                    "dev_mode": app.state.dev_mode,
                    "timestamp": time.time()
                },
                "blockchain": blockchain_status,
                "ai": ai_status,
                "network": {
                    "websocket_connections": len(app.state.websocket_connections),
                    "status": "active"
                }
            }
            
            return status
            
        except Exception as e:
            app.state.logger.error(f"Error getting status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Blockchain endpoints
    @app.get("/api/blockchain")
    async def get_blockchain():
        """Get full blockchain"""
        try:
            return app.state.blockchain.to_dict()
        except Exception as e:
            app.state.logger.error(f"Error getting blockchain: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/blockchain/blocks/{block_index}")
    async def get_block(block_index: int):
        """Get specific block by index"""
        try:
            if block_index < 0 or block_index >= len(app.state.blockchain.chain):
                raise HTTPException(status_code=404, detail="Block not found")
            
            block = app.state.blockchain.chain[block_index]
            return block.to_dict()
            
        except HTTPException:
            raise
        except Exception as e:
            app.state.logger.error(f"Error getting block: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/blockchain/latest")
    async def get_latest_block():
        """Get latest block"""
        try:
            block = app.state.blockchain.get_latest_block()
            return block.to_dict()
        except Exception as e:
            app.state.logger.error(f"Error getting latest block: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Transaction endpoints
    @app.post("/api/transactions")
    async def create_transaction(transaction: TransactionRequest):
        """Create a new transaction"""
        try:
            from laniakea.core.blockchain import Transaction
            
            tx = Transaction(
                sender=transaction.sender,
                recipient=transaction.recipient,
                amount=transaction.amount,
                metadata=transaction.metadata
            )
            
            success = app.state.blockchain.add_transaction(tx)
            
            if not success:
                raise HTTPException(status_code=400, detail="Invalid transaction")
            
            # Broadcast to WebSocket clients
            await broadcast_message({
                "type": "new_transaction",
                "transaction": tx.to_dict()
            })
            
            return {
                "success": True,
                "transaction_id": tx.transaction_id,
                "message": "Transaction added to pending pool"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            app.state.logger.error(f"Error creating transaction: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/transactions/pending")
    async def get_pending_transactions():
        """Get pending transactions"""
        try:
            return {
                "count": len(app.state.blockchain.pending_transactions),
                "transactions": [tx.to_dict() for tx in app.state.blockchain.pending_transactions]
            }
        except Exception as e:
            app.state.logger.error(f"Error getting pending transactions: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Mining endpoint
    @app.post("/api/mine")
    async def mine_block(miner_address: str):
        """Mine pending transactions"""
        try:
            block = app.state.blockchain.mine_pending_transactions(miner_address)
            
            if not block:
                raise HTTPException(status_code=400, detail="No pending transactions to mine")
            
            # Broadcast to WebSocket clients
            await broadcast_message({
                "type": "new_block",
                "block": block.to_dict()
            })
            
            return {
                "success": True,
                "block_index": block.index,
                "block_hash": block.hash,
                "message": "Block mined successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            app.state.logger.error(f"Error mining block: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Balance endpoint
    @app.get("/api/balance/{address}")
    async def get_balance(address: str):
        """Get balance for an address"""
        try:
            balance = app.state.blockchain.get_balance(address)
            return {
                "address": address,
                "balance": balance
            }
        except Exception as e:
            app.state.logger.error(f"Error getting balance: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # AI endpoints
    @app.post("/api/ai/think")
    async def ai_think(request: ThinkRequest):
        """Ask the AI to think about a problem"""
        if not app.state.brain:
            raise HTTPException(status_code=503, detail="AI brain not available")
        
        try:
            thought = await app.state.brain.think(
                problem=request.problem,
                context=request.context,
                deep_analysis=request.deep_analysis
            )
            
            return {
                "thought_id": thought.thought_id,
                "content": thought.content,
                "creativity_score": thought.creativity_score,
                "confidence": thought.confidence,
                "timestamp": thought.timestamp
            }
            
        except Exception as e:
            app.state.logger.error(f"Error in AI thinking: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/ai/evolve")
    async def ai_evolve():
        """Trigger AI evolution"""
        if not app.state.brain:
            raise HTTPException(status_code=503, detail="AI brain not available")
        
        try:
            result = await app.state.brain.evolve()
            
            return {
                "improvement": result.improvement,
                "new_patterns": result.new_patterns,
                "intelligence_level": result.intelligence_level,
                "metrics": result.metrics
            }
            
        except Exception as e:
            app.state.logger.error(f"Error in AI evolution: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/ai/status")
    async def ai_status():
        """Get AI status"""
        if not app.state.brain:
            raise HTTPException(status_code=503, detail="AI brain not available")
        
        try:
            return app.state.brain.get_status()
        except Exception as e:
            app.state.logger.error(f"Error getting AI status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # WebSocket endpoint
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time updates"""
        await websocket.accept()
        app.state.websocket_connections.append(websocket)
        
        app.state.logger.info(f"WebSocket client connected (total: {len(app.state.websocket_connections)})")
        
        try:
            # Send welcome message
            await websocket.send_json({
                "type": "welcome",
                "message": "Connected to LaniakeA Protocol",
                "version": "3.0.0"
            })
            
            # Keep connection alive
            while True:
                data = await websocket.receive_text()
                
                # Echo back for now
                await websocket.send_json({
                    "type": "echo",
                    "data": data,
                    "timestamp": time.time()
                })
                
        except WebSocketDisconnect:
            app.state.logger.info("WebSocket client disconnected")
        except Exception as e:
            app.state.logger.error(f"WebSocket error: {e}")
        finally:
            if websocket in app.state.websocket_connections:
                app.state.websocket_connections.remove(websocket)
    
    async def broadcast_message(message: Dict[str, Any]):
        """Broadcast message to all WebSocket clients"""
        if not app.state.websocket_connections:
            return
        
        disconnected = []
        
        for websocket in app.state.websocket_connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                app.state.logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.append(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected:
            app.state.websocket_connections.remove(websocket)
    
    # Developer mode endpoints
    if dev_mode:
        @app.get("/dev/logs")
        async def get_logs():
            """Get recent logs (dev mode only)"""
            return {"message": "Logs endpoint - implement log retrieval"}
        
        @app.get("/dev/metrics")
        async def get_metrics():
            """Get performance metrics (dev mode only)"""
            return {
                "uptime": time.time() - app.state.start_time,
                "total_requests": 0,  # Implement request counter
                "websocket_connections": len(app.state.websocket_connections)
            }
    
    return app


def run_server(
    app: FastAPI,
    host: str = "0.0.0.0",
    port: int = 8000,
    workers: int = 4,
    reload: bool = False,
    logger: Optional[logging.Logger] = None
):
    """
    Run the FastAPI server
    
    Args:
        app: FastAPI application
        host: Host address
        port: Port number
        workers: Number of worker processes
        reload: Enable auto-reload
        logger: Logger instance
    """
    if logger:
        logger.info(f"🚀 Starting LaniakeA API server on {host}:{port}")
        logger.info(f"👷 Workers: {workers}")
        logger.info(f"🔄 Auto-reload: {'Enabled' if reload else 'Disabled'}")
    
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=1 if reload else workers,  # Workers=1 when reload is enabled
            reload=reload,
            log_level="info"
        )
    except Exception as e:
        if logger:
            logger.error(f"❌ Server error: {e}")
        raise


# Example usage
if __name__ == '__main__':
    import logging
    from laniakea.core.blockchain import LaniakeABlockchain
    from laniakea.intelligence.brain import CosmicBrainAI
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('laniakea')
    
    # Create blockchain and brain
    blockchain = LaniakeABlockchain('test-node', logger)
    brain = CosmicBrainAI('test-node', logger)
    
    # Create app
    app = create_app(
        blockchain=blockchain,
        brain=brain,
        config={},
        logger=logger,
        dev_mode=True
    )
    
    # Run server
    run_server(app, host="0.0.0.0", port=8000, workers=1, reload=True, logger=logger)
