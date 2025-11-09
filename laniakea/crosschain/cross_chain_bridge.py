"""
Cross-Chain Bridge API Endpoints
Integrates with the CrossChainManager to provide bridge functionality
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

# Import core components
from laniakea.utils.logger import get_logger
from laniakea.utils.config import get_config
from src.crosschain.cross_chain_manager import (
    cross_chain_manager, ChainType, AssetType, BridgeStatus
)

logger = get_logger("CrossChainBridge")
router = APIRouter()

# --- Pydantic Schemas ---

class BridgeRequestSchema(BaseModel):
    """Schema for a new bridge request"""
    from_chain: ChainType = Field(..., description="Source chain type (e.g., ETHEREUM, LANIAKEA)")
    to_chain: ChainType = Field(..., description="Target chain type")
    asset_type: AssetType = Field(AssetType.NATIVE, description="Asset type (e.g., NATIVE, ERC20)")
    amount: Union[int, float] = Field(..., gt=0, description="Amount of asset to bridge")
    recipient_address: str = Field(..., description="Recipient address on the target chain")
    sender_address: str = Field(..., description="Sender address on the source chain")
    token_address: Optional[str] = Field(None, description="Token contract address for ERC20/ERC721")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

class BridgeStatusResponse(BaseModel):
    """Schema for bridge status response"""
    id: str
    from_chain: str
    to_chain: str
    asset_type: str
    amount: Union[int, float]
    status: str
    created_at: datetime
    transaction_hash: Optional[str]
    bridge_tx_hash: Optional[str]
    confirmations: int
    required_confirmations: int
    fee: Union[int, float]
    error: Optional[str]
    recipient_address: str
    sender_address: str
    metadata: Dict[str, Any]

class ChainConfigResponse(BaseModel):
    """Schema for supported chain configuration"""
    type: str
    name: str
    chain_id: int
    block_time: int
    native_currency: str
    connected: bool
    explorer_url: Optional[str]

class LiquidityInfoResponse(BaseModel):
    """Schema for liquidity information"""
    from_chain: str
    to_chain: str
    token_address: Optional[str]
    total_liquidity: float
    available_liquidity: float
    utilization: float
    fee_rate: float
    max_slippage: float
    min_amount: float
    max_amount: float

# --- API Endpoints ---

@router.on_event("startup")
async def startup_event():
    """Start the cross-chain manager on application startup"""
    logger.info("Starting Cross-Chain Manager...")
    await cross_chain_manager.start()

@router.on_event("shutdown")
async def shutdown_event():
    """Stop the cross-chain manager on application shutdown"""
    logger.info("Stopping Cross-Chain Manager...")
    await cross_chain_manager.stop()

@router.get("/chains", response_model=List[ChainConfigResponse], summary="Get Supported Chains")
async def get_chains():
    """
    Retrieves a list of all supported blockchain networks for cross-chain operations.
    """
    return await cross_chain_manager.get_supported_chains()

@router.get("/liquidity", response_model=LiquidityInfoResponse, summary="Get Bridge Liquidity Info")
async def get_liquidity(from_chain: ChainType, to_chain: ChainType, token_address: Optional[str] = None):
    """
    Retrieves liquidity information for a specific bridge pair.
    """
    try:
        return await cross_chain_manager.get_liquidity_info(from_chain, to_chain, token_address)
    except Exception as e:
        logger.error(f"Error getting liquidity info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/bridge", response_model=Dict[str, str], summary="Create New Cross-Chain Bridge Request")
async def create_bridge(request: BridgeRequestSchema):
    """
    Submits a new request to bridge assets between two chains.
    """
    try:
        bridge_id = await cross_chain_manager.create_bridge_request(
            from_chain=request.from_chain,
            to_chain=request.to_chain,
            asset_type=request.asset_type,
            amount=request.amount,
            recipient_address=request.recipient_address,
            sender_address=request.sender_address,
            token_address=request.token_address,
            metadata=request.metadata
        )
        return {"bridge_id": bridge_id, "status": "pending"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating bridge request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/bridge/{bridge_id}", response_model=BridgeStatusResponse, summary="Get Bridge Status")
async def get_bridge(bridge_id: str):
    """
    Retrieves the current status of a cross-chain bridge request.
    """
    status = await cross_chain_manager.get_bridge_status(bridge_id)
    if not status:
        raise HTTPException(status_code=404, detail="Bridge request not found")
    return status

@router.get("/stats", summary="Get Cross-Chain Bridge Statistics")
async def get_stats():
    """
    Retrieves overall statistics for the cross-chain bridge operations.
    """
    return cross_chain_manager.get_bridge_statistics()
