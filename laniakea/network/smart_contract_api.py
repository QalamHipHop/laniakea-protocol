"""
LaniakeA Protocol - Smart Contract API Endpoints
Provides endpoints for deploying and executing smart contracts.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from laniakea.core.hypercube_blockchain import HypercubeBlockchain, HyperTransaction
from laniakea.core.smart_contract_vm import scvm, ExecutionResult
from laniakea.utils.logger import get_logger

logger = get_logger("SmartContractAPI")
router = APIRouter()

# --- Pydantic Schemas ---

class DeployContractRequest(BaseModel):
    """Schema for deploying a new contract"""
    sender: str = Field(..., description="Address of the contract deployer")
    code: str = Field(..., description="Contract code (simplified as a string)")
    initial_balance: float = Field(0.0, description="Initial balance to fund the contract")

class DeployContractResponse(BaseModel):
    """Schema for deployment response"""
    transaction_id: str
    contract_address: str
    status: str

class ExecuteContractRequest(BaseModel):
    """Schema for executing a contract function"""
    sender: str = Field(..., description="Address of the transaction sender")
    contract_address: str = Field(..., description="Address of the contract to execute")
    function_name: str = Field(..., description="Name of the function to call")
    args: Dict[str, Any] = Field(..., description="Arguments for the function call")
    value: float = Field(0.0, description="Value (in native currency) to send with the transaction")
    gas_limit: int = Field(100000, description="Maximum gas to use for execution")

class ExecuteContractResponse(BaseModel):
    """Schema for execution response"""
    transaction_id: str
    status: str
    
class ContractStateResponse(BaseModel):
    """Schema for contract state"""
    address: str
    owner: str
    balance: float
    storage: Dict[str, Any]
    code_hash: str

# --- API Endpoints ---

@router.post("/deploy", response_model=DeployContractResponse, summary="Deploy a New Smart Contract")
async def deploy_contract(request: DeployContractRequest, blockchain: HypercubeBlockchain = Depends(lambda: HypercubeBlockchain.instance)):
    """
    Creates a transaction to deploy a new smart contract.
    """
    try:
        # Create a deployment transaction
        tx = HyperTransaction(
            sender=request.sender,
            recipient="0-Contract-Deployment", # Placeholder, will be replaced by SCVM
            amount=request.initial_balance,
            metadata={
                "type": "contract_deployment",
                "code": request.code
            }
        )
        
        if blockchain.add_transaction(tx):
            # Contract address is set inside add_transaction by SCVM
            contract_address = tx.metadata.get("contract_address")
            return DeployContractResponse(
                transaction_id=tx.transaction_id,
                contract_address=contract_address,
                status="pending_mining"
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid deployment transaction")
            
    except Exception as e:
        logger.error(f"Error deploying contract: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute", response_model=ExecuteContractResponse, summary="Execute a Smart Contract Function")
async def execute_contract(request: ExecuteContractRequest, blockchain: HypercubeBlockchain = Depends(lambda: HypercubeBlockchain.instance)):
    """
    Creates a transaction to execute a function on a deployed smart contract.
    """
    try:
        # Create an execution transaction
        tx = HyperTransaction(
            sender=request.sender,
            recipient=request.contract_address,
            amount=request.value,
            metadata={
                "type": "contract_execution",
                "function": request.function_name,
                "args": request.args,
                "gas_limit": request.gas_limit
            }
        )
        
        if blockchain.add_transaction(tx):
            return ExecuteContractResponse(
                transaction_id=tx.transaction_id,
                status="pending_mining"
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid execution transaction")
            
    except Exception as e:
        logger.error(f"Error executing contract: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/state/{contract_address}", response_model=ContractStateResponse, summary="Get Contract State")
async def get_contract_state(contract_address: str):
    """
    Retrieves the current state and storage of a deployed smart contract.
    """
    state = scvm.get_contract_state(contract_address)
    if not state:
        raise HTTPException(status_code=404, detail="Contract not found")
    return state

@router.get("/vm_stats", summary="Get SCVM Statistics")
async def get_vm_stats():
    """
    Retrieves statistics about the Smart Contract Virtual Machine.
    """
    return {
        "total_contracts": len(scvm.contracts),
        "implemented_functions": ["set_value", "get_value", "transfer"],
        "gas_system_enabled": True,
        "vm_version": "1.0.0"
    }
