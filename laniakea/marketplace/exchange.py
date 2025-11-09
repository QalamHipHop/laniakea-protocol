"""
Laniakea Protocol - Marketplace & Exchange
سیستم بازار و معاملات
"""

import hashlib
from time import time
from typing import Dict, List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field
from collections import defaultdict


class OrderType(str, Enum):
    """نوع سفارش"""

    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    """وضعیت سفارش"""

    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"


class Order(BaseModel):
    """سفارش خرید/فروش"""

    id: str
    trader_id: str
    order_type: OrderType
    from_dimension: str  # بُعد فروش
    to_dimension: str  # بُعد خرید
    amount: float  # مقدار
    price: float  # قیمت (نرخ تبدیل)
    filled_amount: float = 0.0
    status: OrderStatus = OrderStatus.OPEN
    timestamp: float
    expires_at: Optional[float] = None


class Trade(BaseModel):
    """معامله انجام شده"""

    id: str
    buy_order_id: str
    sell_order_id: str
    buyer_id: str
    seller_id: str
    dimension: str
    amount: float
    price: float
    timestamp: float


class OrderBook:
    """
    دفتر سفارشات

    نگهداری و مدیریت سفارشات خرید و فروش
    """

    def __init__(self, dimension: str):
        """
        Args:
            dimension: بُعد ارزشی
        """
        self.dimension = dimension
        self.buy_orders: List[Order] = []  # مرتب شده از بالا به پایین
        self.sell_orders: List[Order] = []  # مرتب شده از پایین به بالا

    def add_order(self, order: Order):
        """افزودن سفارش"""
        if order.order_type == OrderType.BUY:
            self.buy_orders.append(order)
            self.buy_orders.sort(key=lambda o: o.price, reverse=True)
        else:
            self.sell_orders.append(order)
            self.sell_orders.sort(key=lambda o: o.price)

    def remove_order(self, order_id: str):
        """حذف سفارش"""
        self.buy_orders = [o for o in self.buy_orders if o.id != order_id]
        self.sell_orders = [o for o in self.sell_orders if o.id != order_id]

    def get_best_bid(self) -> Optional[Order]:
        """بهترین قیمت خرید"""
        return self.buy_orders[0] if self.buy_orders else None

    def get_best_ask(self) -> Optional[Order]:
        """بهترین قیمت فروش"""
        return self.sell_orders[0] if self.sell_orders else None

    def get_spread(self) -> Optional[float]:
        """اختلاف قیمت خرید و فروش"""
        bid = self.get_best_bid()
        ask = self.get_best_ask()
        if bid and ask:
            return ask.price - bid.price
        return None

    def get_depth(self, levels: int = 5) -> Dict:
        """عمق بازار"""
        return {
            "bids": [(o.price, o.amount - o.filled_amount) for o in self.buy_orders[:levels]],
            "asks": [(o.price, o.amount - o.filled_amount) for o in self.sell_orders[:levels]],
        }


class Exchange:
    """
    صرافی غیرمتمرکز

    معاملات بین ابعاد ارزشی مختلف
    """

    def __init__(self):
        # دفتر سفارشات برای هر جفت
        self.order_books: Dict[str, OrderBook] = {}

        # تمام سفارشات
        self.orders: Dict[str, Order] = {}

        # معاملات انجام شده
        self.trades: List[Trade] = []

        # موجودی کاربران
        self.balances: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

        # کارمزد
        self.fee_rate = 0.001  # 0.1%

        print("💱 Exchange initialized")

    def _get_pair_key(self, from_dim: str, to_dim: str) -> str:
        """کلید جفت ارز"""
        return f"{from_dim}/{to_dim}"

    def _get_order_book(self, from_dim: str, to_dim: str) -> OrderBook:
        """دریافت یا ایجاد order book"""
        key = self._get_pair_key(from_dim, to_dim)
        if key not in self.order_books:
            self.order_books[key] = OrderBook(key)
        return self.order_books[key]

    def deposit(self, user_id: str, dimension: str, amount: float):
        """واریز به صرافی"""
        self.balances[user_id][dimension] += amount
        print(f"💰 Deposit: {user_id[:12]} deposited {amount:.2f} {dimension}")

    def withdraw(self, user_id: str, dimension: str, amount: float) -> bool:
        """برداشت از صرافی"""
        if self.balances[user_id][dimension] >= amount:
            self.balances[user_id][dimension] -= amount
            print(f"💸 Withdraw: {user_id[:12]} withdrew {amount:.2f} {dimension}")
            return True
        return False

    def place_order(
        self,
        trader_id: str,
        order_type: OrderType,
        from_dimension: str,
        to_dimension: str,
        amount: float,
        price: float,
        expires_in: Optional[float] = None,
    ) -> Optional[Order]:
        """
        ثبت سفارش

        Args:
            trader_id: شناسه معامله‌گر
            order_type: نوع سفارش
            from_dimension: بُعد فروش
            to_dimension: بُعد خرید
            amount: مقدار
            price: قیمت
            expires_in: زمان انقضا (ثانیه)

        Returns:
            سفارش ایجاد شده
        """
        # بررسی موجودی
        required_amount = amount if order_type == OrderType.SELL else amount * price
        required_dim = from_dimension if order_type == OrderType.SELL else to_dimension

        if self.balances[trader_id][required_dim] < required_amount:
            print(f"❌ Insufficient balance for order")
            return None

        # ایجاد سفارش
        order_id = hashlib.sha256(f"{trader_id}{time()}".encode()).hexdigest()

        order = Order(
            id=order_id,
            trader_id=trader_id,
            order_type=order_type,
            from_dimension=from_dimension,
            to_dimension=to_dimension,
            amount=amount,
            price=price,
            timestamp=time(),
            expires_at=time() + expires_in if expires_in else None,
        )

        # قفل کردن موجودی
        self.balances[trader_id][required_dim] -= required_amount

        # افزودن به order book
        order_book = self._get_order_book(from_dimension, to_dimension)
        order_book.add_order(order)
        self.orders[order_id] = order

        # تلاش برای match
        self._match_orders(order_book, order)

        print(f"📝 Order placed: {order_type.value} {amount:.2f} {from_dimension} @ {price:.4f}")
        return order

    def _match_orders(self, order_book: OrderBook, new_order: Order):
        """تطبیق سفارشات"""
        if new_order.status == OrderStatus.FILLED:
            return

        # سفارشات مقابل
        opposite_orders = (
            order_book.sell_orders
            if new_order.order_type == OrderType.BUY
            else order_book.buy_orders
        )

        for opposite_order in opposite_orders[:]:
            if new_order.status == OrderStatus.FILLED:
                break

            # بررسی قیمت
            if new_order.order_type == OrderType.BUY:
                if new_order.price < opposite_order.price:
                    break
            else:
                if new_order.price > opposite_order.price:
                    break

            # محاسبه مقدار معامله
            remaining_new = new_order.amount - new_order.filled_amount
            remaining_opposite = opposite_order.amount - opposite_order.filled_amount
            trade_amount = min(remaining_new, remaining_opposite)

            # اجرای معامله
            self._execute_trade(new_order, opposite_order, trade_amount)

    def _execute_trade(self, order1: Order, order2: Order, amount: float):
        """اجرای معامله"""
        # تعیین خریدار و فروشنده
        if order1.order_type == OrderType.BUY:
            buy_order, sell_order = order1, order2
        else:
            buy_order, sell_order = order2, order1

        # قیمت معامله (قیمت سفارش قدیمی‌تر)
        trade_price = sell_order.price

        # محاسبه کارمزد
        fee = amount * trade_price * self.fee_rate

        # انتقال دارایی
        # فروشنده دارایی می‌فروشد
        self.balances[sell_order.trader_id][sell_order.to_dimension] += amount * trade_price - fee

        # خریدار دارایی می‌خرد
        self.balances[buy_order.trader_id][buy_order.from_dimension] += amount - fee

        # به‌روزرسانی سفارشات
        buy_order.filled_amount += amount
        sell_order.filled_amount += amount

        if buy_order.filled_amount >= buy_order.amount:
            buy_order.status = OrderStatus.FILLED
        else:
            buy_order.status = OrderStatus.PARTIALLY_FILLED

        if sell_order.filled_amount >= sell_order.amount:
            sell_order.status = OrderStatus.FILLED
        else:
            sell_order.status = OrderStatus.PARTIALLY_FILLED

        # ثبت معامله
        trade_id = hashlib.sha256(f"{buy_order.id}{sell_order.id}{time()}".encode()).hexdigest()
        trade = Trade(
            id=trade_id,
            buy_order_id=buy_order.id,
            sell_order_id=sell_order.id,
            buyer_id=buy_order.trader_id,
            seller_id=sell_order.trader_id,
            dimension=buy_order.from_dimension,
            amount=amount,
            price=trade_price,
            timestamp=time(),
        )
        self.trades.append(trade)

        print(f"✅ Trade executed: {amount:.2f} @ {trade_price:.4f}")

    def cancel_order(self, order_id: str, user_id: str) -> bool:
        """لغو سفارش"""
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]

        if order.trader_id != user_id:
            return False

        if order.status == OrderStatus.FILLED:
            return False

        # بازگرداندن موجودی
        remaining = order.amount - order.filled_amount
        if order.order_type == OrderType.SELL:
            self.balances[user_id][order.from_dimension] += remaining
        else:
            self.balances[user_id][order.to_dimension] += remaining * order.price

        # حذف از order book
        order_book = self._get_order_book(order.from_dimension, order.to_dimension)
        order_book.remove_order(order_id)

        order.status = OrderStatus.CANCELLED

        print(f"🚫 Order cancelled: {order_id[:12]}")
        return True

    def get_market_price(self, from_dim: str, to_dim: str) -> Optional[float]:
        """دریافت قیمت بازار"""
        order_book = self._get_order_book(from_dim, to_dim)

        bid = order_book.get_best_bid()
        ask = order_book.get_best_ask()

        if bid and ask:
            return (bid.price + ask.price) / 2
        elif bid:
            return bid.price
        elif ask:
            return ask.price

        return None

    def get_order_book_depth(self, from_dim: str, to_dim: str) -> Dict:
        """دریافت عمق بازار"""
        order_book = self._get_order_book(from_dim, to_dim)
        return order_book.get_depth()

    def get_recent_trades(self, limit: int = 10) -> List[Trade]:
        """دریافت معاملات اخیر"""
        return self.trades[-limit:]

    def get_user_orders(self, user_id: str) -> List[Order]:
        """دریافت سفارشات کاربر"""
        return [o for o in self.orders.values() if o.trader_id == user_id]

    def get_stats(self) -> Dict:
        """آمار صرافی"""
        return {
            "total_orders": len(self.orders),
            "open_orders": len([o for o in self.orders.values() if o.status == OrderStatus.OPEN]),
            "total_trades": len(self.trades),
            "total_volume": sum(t.amount * t.price for t in self.trades),
            "active_traders": len(self.balances),
            "order_books": len(self.order_books),
        }


class LiquidityPool:
    """
    استخر نقدینگی (AMM)

    مدل Automated Market Maker برای نقدینگی
    """

    def __init__(self, dimension_a: str, dimension_b: str):
        """
        Args:
            dimension_a: بُعد اول
            dimension_b: بُعد دوم
        """
        self.dimension_a = dimension_a
        self.dimension_b = dimension_b

        self.reserve_a = 0.0
        self.reserve_b = 0.0

        self.total_shares = 0.0
        self.shares: Dict[str, float] = defaultdict(float)

        self.fee_rate = 0.003  # 0.3%

        print(f"💧 Liquidity Pool created: {dimension_a}/{dimension_b}")

    def add_liquidity(self, provider_id: str, amount_a: float, amount_b: float) -> float:
        """
        افزودن نقدینگی

        Args:
            provider_id: شناسه تأمین‌کننده
            amount_a: مقدار A
            amount_b: مقدار B

        Returns:
            سهم دریافتی
        """
        if self.total_shares == 0:
            # اولین نقدینگی
            shares = (amount_a * amount_b) ** 0.5
        else:
            # محاسبه سهم بر اساس نسبت
            shares_a = self.total_shares * amount_a / self.reserve_a
            shares_b = self.total_shares * amount_b / self.reserve_b
            shares = min(shares_a, shares_b)

        self.reserve_a += amount_a
        self.reserve_b += amount_b
        self.total_shares += shares
        self.shares[provider_id] += shares

        print(
            f"➕ Liquidity added: {amount_a:.2f} {self.dimension_a}, {amount_b:.2f} {self.dimension_b}"
        )
        return shares

    def remove_liquidity(self, provider_id: str, shares: float) -> Tuple[float, float]:
        """
        برداشت نقدینگی

        Args:
            provider_id: شناسه تأمین‌کننده
            shares: مقدار سهم

        Returns:
            (amount_a, amount_b)
        """
        if self.shares[provider_id] < shares:
            return (0.0, 0.0)

        # محاسبه مقدار بازگشتی
        amount_a = self.reserve_a * shares / self.total_shares
        amount_b = self.reserve_b * shares / self.total_shares

        self.reserve_a -= amount_a
        self.reserve_b -= amount_b
        self.total_shares -= shares
        self.shares[provider_id] -= shares

        print(
            f"➖ Liquidity removed: {amount_a:.2f} {self.dimension_a}, {amount_b:.2f} {self.dimension_b}"
        )
        return (amount_a, amount_b)

    def swap(self, from_dimension: str, amount_in: float) -> float:
        """
        مبادله (swap)

        Args:
            from_dimension: بُعد ورودی
            amount_in: مقدار ورودی

        Returns:
            مقدار خروجی
        """
        # تعیین ذخایر
        if from_dimension == self.dimension_a:
            reserve_in = self.reserve_a
            reserve_out = self.reserve_b
        else:
            reserve_in = self.reserve_b
            reserve_out = self.reserve_a

        # محاسبه با فرمول x * y = k
        amount_in_with_fee = amount_in * (1 - self.fee_rate)
        amount_out = (reserve_out * amount_in_with_fee) / (reserve_in + amount_in_with_fee)

        # به‌روزرسانی ذخایر
        if from_dimension == self.dimension_a:
            self.reserve_a += amount_in
            self.reserve_b -= amount_out
        else:
            self.reserve_b += amount_in
            self.reserve_a -= amount_out

        print(f"🔄 Swap: {amount_in:.2f} -> {amount_out:.2f}")
        return amount_out

    def get_price(self, from_dimension: str) -> float:
        """دریافت قیمت"""
        if from_dimension == self.dimension_a:
            return self.reserve_b / self.reserve_a if self.reserve_a > 0 else 0
        else:
            return self.reserve_a / self.reserve_b if self.reserve_b > 0 else 0

    def get_stats(self) -> Dict:
        """آمار استخر"""
        return {
            "reserve_a": self.reserve_a,
            "reserve_b": self.reserve_b,
            "total_shares": self.total_shares,
            "price_a_to_b": self.get_price(self.dimension_a),
            "price_b_to_a": self.get_price(self.dimension_b),
            "providers": len([p for p, s in self.shares.items() if s > 0]),
        }
