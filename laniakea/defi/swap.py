# laniakea/defi/swap.py

import time
from typing import Dict, Any

class LiquidityPool:
    """
    A simplified Automated Market Maker (AMM) Liquidity Pool (e.g., Uniswap V2 model).
    Uses the constant product formula: x * y = k
    """
    def __init__(self, token_x: str, token_y: str, initial_x: float, initial_y: float):
        self.token_x = token_x
        self.token_y = token_y
        self.reserve_x = initial_x
        self.reserve_y = initial_y
        self.k = initial_x * initial_y # Constant product
        self.fee = 0.003 # 0.3% trading fee

    def get_price(self, token_in: str) -> float:
        """Returns the current price of token_in in terms of the other token."""
        if token_in == self.token_x:
            return self.reserve_y / self.reserve_x
        elif token_in == self.token_y:
            return self.reserve_x / self.reserve_y
        else:
            raise ValueError("Token not in pool.")

    def swap(self, token_in: str, amount_in: float) -> Dict[str, Any]:
        """
        Simulates a token swap.
        Calculates the amount of token_out received using the constant product formula.
        """
        if token_in == self.token_x:
            reserve_in = self.reserve_x
            reserve_out = self.reserve_y
            token_out = self.token_y
        elif token_in == self.token_y:
            reserve_in = self.reserve_y
            reserve_out = self.reserve_x
            token_out = self.token_x
        else:
            raise ValueError("Token not in pool.")

        # Apply fee to amount_in
        amount_in_after_fee = amount_in * (1 - self.fee)
        
        # Calculate amount_out: amount_out = reserve_out - (k / (reserve_in + amount_in_after_fee))
        new_reserve_in = reserve_in + amount_in_after_fee
        new_reserve_out = self.k / new_reserve_in
        amount_out = reserve_out - new_reserve_out
        
        if amount_out <= 0:
            raise ValueError("Swap amount too small or reserves too low.")

        # Update reserves
        if token_in == self.token_x:
            self.reserve_x = new_reserve_in
            self.reserve_y = new_reserve_out
        else:
            self.reserve_y = new_reserve_in
            self.reserve_x = new_reserve_out
            
        self.k = self.reserve_x * self.reserve_y # Should remain constant (minus fees)

        return {
            "token_in": token_in,
            "amount_in": amount_in,
            "token_out": token_out,
            "amount_out": amount_out,
            "fee_paid": amount_in * self.fee,
            "new_price": self.get_price(token_out)
        }

class DecentralizedExchange:
    """Manages all liquidity pools for the Laniakea Protocol DeFi layer."""
    def __init__(self):
        self.pools: Dict[str, LiquidityPool] = {}
        
        # Initialize a sample pool: LANA/USDC
        self.add_pool("LANA", "USDC", 100000.0, 500000.0) # Initial price: 1 LANA = 5 USDC

    def add_pool(self, token_x: str, token_y: str, initial_x: float, initial_y: float):
        """Adds a new liquidity pool."""
        pool_name = f"{token_x}-{token_y}"
        self.pools[pool_name] = LiquidityPool(token_x, token_y, initial_x, initial_y)
        print(f"Pool {pool_name} created. Initial k: {self.pools[pool_name].k}")

    def get_pool(self, token_a: str, token_b: str) -> LiquidityPool:
        """Retrieves a pool by token pair."""
        pool_name1 = f"{token_a}-{token_b}"
        pool_name2 = f"{token_b}-{token_a}"
        
        if pool_name1 in self.pools:
            return self.pools[pool_name1]
        elif pool_name2 in self.pools:
            return self.pools[pool_name2]
        else:
            raise ValueError(f"Liquidity Pool for {token_a}/{token_b} not found.")

# Example usage
if __name__ == '__main__':
    dex = DecentralizedExchange()
    lana_usdc_pool = dex.get_pool("LANA", "USDC")
    
    print(f"Initial Price (LANA/USDC): {lana_usdc_pool.get_price('LANA'):.4f}")
    
    # Swap 1000 USDC for LANA
    try:
        swap_result = lana_usdc_pool.swap("USDC", 1000.0)
        print("\nSwap Result (USDC -> LANA):")
        print(f"Amount Out: {swap_result['amount_out']:.4f} LANA")
        print(f"New Price (LANA/USDC): {lana_usdc_pool.get_price('LANA'):.4f}")
    except ValueError as e:
        print(f"Swap Error: {e}")
