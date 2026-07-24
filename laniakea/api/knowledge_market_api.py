"""Knowledge Market API router.

Exposes the KnowledgeMarketplace over HTTP. The router is intentionally thin:
all business logic lives in :mod:`laniakea.marketplace.knowledge_market`.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from laniakea.marketplace.knowledge_market import (
    KnowledgeAsset,
    KnowledgeMarketplace,
    KnowledgeType,
    get_marketplace,
)


router = APIRouter(prefix="/knowledge-market", tags=["Knowledge Market"])


# --- Pydantic request/response models ---------------------------------------
class TokenizeRequest(BaseModel):
    owner_scda_id: str
    scda_knowledge_vector: List[float]
    complexity_index: float
    knowledge_type: Optional[str] = None


class ListAssetRequest(BaseModel):
    asset_id: str
    price: float


class BuyAssetRequest(BaseModel):
    asset_id: str
    buyer_scda_id: str


# --- Singleton accessor (cached per-process) --------------------------------
_market: Optional[KnowledgeMarketplace] = None


def _get_market() -> KnowledgeMarketplace:
    global _market
    if _market is None:
        _market = get_marketplace()
    return _market


# --- Routes -----------------------------------------------------------------
@router.get("/types", summary="List supported knowledge asset types")
def list_knowledge_types() -> List[Dict[str, str]]:
    return [{"name": t.name, "value": t.value} for t in KnowledgeType]


@router.get("/listed", summary="List assets currently listed for sale")
def list_listed_assets() -> List[Dict[str, Any]]:
    return _get_market().get_listed_assets()


@router.post("/tokenize", summary="Tokenize an SCDA's knowledge vector")
def tokenize_knowledge(req: TokenizeRequest) -> Dict[str, Any]:
    asset: KnowledgeAsset = _get_market().tokenize_knowledge(
        req.owner_scda_id,
        req.scda_knowledge_vector,
        req.complexity_index,
    )
    return {"message": "Knowledge tokenised", "asset": asset.to_dict()}


@router.post("/list", summary="List an asset for sale")
def list_asset(req: ListAssetRequest) -> Dict[str, Any]:
    try:
        asset = _get_market().list_asset(req.asset_id, req.price)
        return {"message": f"Asset {asset.asset_id} listed for {req.price}", "asset": asset.to_dict()}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/buy", summary="Buy a listed knowledge asset")
def buy_asset(req: BuyAssetRequest) -> Dict[str, Any]:
    try:
        tx = _get_market().buy_asset(req.asset_id, req.buyer_scda_id)
        return {
            "message": "Asset purchased",
            "tx_id": tx.tx_id,
            "new_owner": req.buyer_scda_id,
            "tx": {
                "tx_id": tx.tx_id,
                "asset_id": tx.asset_id,
                "seller_scda_id": tx.seller_scda_id,
                "buyer_scda_id": tx.buyer_scda_id,
                "price": tx.price,
                "timestamp": tx.timestamp,
            },
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/asset/{asset_id}", summary="Fetch details of a specific asset")
def get_asset(asset_id: str) -> Dict[str, Any]:
    try:
        return _get_market().get_asset_details(asset_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
