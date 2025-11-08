"""
LaniakeA Protocol - Smart Contract Virtual Machine (SCVM)
Handles execution of smart contracts and manages gas system.
"""

import logging
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field

logger = logging.getLogger("SCVM")

@dataclass
class ContractState:
    """Represents the persistent state of a smart contract"""
    storage: Dict[str, Any] = field(default_factory=dict)
    balance: float = 0.0
    code: str = ""
    owner: str = ""

@dataclass
class ExecutionResult:
    """Result of a contract execution"""
    success: bool
    gas_used: int
    return_value: Optional[Any] = None
    error: Optional[str] = None
    logs: List[str] = field(default_factory=list)

class GasSystem:
    """Manages gas consumption for contract execution"""
    
    def __init__(self, initial_gas: int):
        self.gas_limit = initial_gas
        self.gas_remaining = initial_gas
        self.gas_used = 0
        
    def consume_gas(self, amount: int) -> bool:
        """Consumes a specified amount of gas"""
        if self.gas_remaining >= amount:
            self.gas_remaining -= amount
            self.gas_used += amount
            return True
        return False
    
    def refund_gas(self, amount: int):
        """Refunds unused gas"""
        self.gas_remaining += amount
        
    def get_gas_used(self) -> int:
        """Returns the total gas used"""
        return self.gas_used

class SmartContractVM:
    """
    LaniakeA Smart Contract Virtual Machine (SCVM)
    A simplified, high-level VM for demonstration.
    """
    
    def __init__(self):
        self.contracts: Dict[str, ContractState] = {}
        self.logger = logging.getLogger("SCVM")
        self.logger.info("Smart Contract VM initialized")
        
    def deploy_contract(self, code: str, owner: str, initial_balance: float = 0.0) -> str:
        """Deploys a new smart contract"""
        contract_address = self._generate_contract_address(code, owner)
        
        if contract_address in self.contracts:
            raise ValueError("Contract already deployed at this address")
            
        self.contracts[contract_address] = ContractState(
            code=code,
            owner=owner,
            balance=initial_balance
        )
        self.logger.info(f"Contract deployed at: {contract_address}")
        return contract_address
        
    def execute_contract(self, 
                         contract_address: str, 
                         function_name: str, 
                         args: Dict[str, Any], 
                         sender: str, 
                         value: float = 0.0,
                         gas_limit: int = 100000) -> ExecutionResult:
        """Executes a function on a deployed smart contract"""
        
        if contract_address not in self.contracts:
            return ExecutionResult(False, 0, error="Contract not found")
            
        state = self.contracts[contract_address]
        gas_system = GasSystem(gas_limit)
        
        # Simulate value transfer
        if value > 0:
            # In a real system, this would involve updating the sender's balance
            state.balance += value
            gas_system.consume_gas(500) # Gas for value transfer
        
        # Simple execution simulation based on function name
        try:
            gas_system.consume_gas(1000) # Base execution cost
            
            if function_name == "set_value":
                key = args.get("key")
                value_to_set = args.get("value")
                if key is None or value_to_set is None:
                    raise ValueError("Missing key or value for set_value")
                
                state.storage[key] = value_to_set
                gas_system.consume_gas(5000) # Gas for storage write
                result = ExecutionResult(True, gas_system.get_gas_used(), return_value=True, logs=[f"Set {key} to {value_to_set}"])
                
            elif function_name == "get_value":
                key = args.get("key")
                if key is None:
                    raise ValueError("Missing key for get_value")
                
                value_retrieved = state.storage.get(key)
                gas_system.consume_gas(500) # Gas for storage read
                result = ExecutionResult(True, gas_system.get_gas_used(), return_value=value_retrieved)
                
            elif function_name == "transfer":
                to = args.get("to")
                amount = args.get("amount")
                if to is None or amount is None:
                    raise ValueError("Missing recipient or amount for transfer")
                
                # Simulate transfer logic
                gas_system.consume_gas(10000) # Gas for complex operation
                result = ExecutionResult(True, gas_system.get_gas_used(), return_value=True, logs=[f"Transferred {amount} to {to}"])
                
            else:
                raise NotImplementedError(f"Function {function_name} not implemented in SCVM")
                
            # Check for out of gas
            if gas_system.gas_remaining < 0:
                raise Exception("Out of Gas")
                
            return result
            
        except Exception as e:
            self.logger.error(f"Contract execution failed: {e}")
            return ExecutionResult(False, gas_limit, error=str(e)) # All gas consumed on failure
            
    def get_contract_state(self, contract_address: str) -> Optional[Dict[str, Any]]:
        """Retrieves the current state of a contract"""
        state = self.contracts.get(contract_address)
        if state:
            return {
                "address": contract_address,
                "owner": state.owner,
                "balance": state.balance,
                "storage": state.storage,
                "code_hash": self._hash_code(state.code)
            }
        return None
        
    def _generate_contract_address(self, code: str, owner: str) -> str:
        """Generates a unique contract address (simplified)"""
        import hashlib
        data = f"{code}{owner}{len(self.contracts)}"
        return "0x" + hashlib.sha256(data.encode()).hexdigest()[:40]
        
    def _hash_code(self, code: str) -> str:
        """Hashes the contract code"""
        import hashlib
        return hashlib.sha256(code.encode()).hexdigest()

# Global SCVM instance
scvm = SmartContractVM()
