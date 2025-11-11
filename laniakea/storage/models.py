"""
LaniakeA Protocol - SQLAlchemy ORM Models
Defines the database schema using SQLAlchemy's declarative base.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    Float,
    JSON,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database_setup import Base


class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    block_hash = Column(String(255), unique=True, nullable=False, index=True)
    previous_hash = Column(String(255))
    timestamp = Column(BigInteger, nullable=False)
    nonce = Column(BigInteger)
    difficulty = Column(Float)
    miner_id = Column(String(255))
    transactions_count = Column(Integer)
    data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transactions = relationship("Transaction", back_populates="block")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    tx_hash = Column(String(255), unique=True, nullable=False, index=True)
    block_hash = Column(String(255), ForeignKey("blocks.block_hash"))
    sender = Column(String(255), nullable=False)
    receiver = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    fee = Column(Float)
    timestamp = Column(BigInteger, nullable=False)
    status = Column(String(50))
    data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    block = relationship("Block", back_populates="transactions")


class SmartContract(Base):
    __tablename__ = "smart_contracts"

    id = Column(Integer, primary_key=True, index=True)
    contract_address = Column(String(255), unique=True, nullable=False, index=True)
    owner_address = Column(String(255), nullable=False)
    code = Column(Text)
    state = Column(JSON)
    gas_limit = Column(Integer)
    balance = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    executions = relationship("ContractExecution", back_populates="contract")


class ContractExecution(Base):
    __tablename__ = "contract_executions"

    id = Column(Integer, primary_key=True, index=True)
    contract_address = Column(String(255), ForeignKey("smart_contracts.contract_address"))
    function_name = Column(String(255))
    caller_address = Column(String(255))
    gas_used = Column(Integer)
    result = Column(JSON)
    status = Column(String(50))
    timestamp = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    contract = relationship("SmartContract", back_populates="executions")


class CrossChainBridge(Base):
    __tablename__ = "cross_chain_bridges"

    id = Column(Integer, primary_key=True, index=True)
    bridge_id = Column(String(255), unique=True, nullable=False, index=True)
    from_chain = Column(String(50), nullable=False)
    to_chain = Column(String(50), nullable=False)
    from_address = Column(String(255))
    to_address = Column(String(255))
    amount = Column(Float)
    token_address = Column(String(255))
    status = Column(String(50))
    from_tx_hash = Column(String(255))
    to_tx_hash = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255))
    wallet_address = Column(String(255), unique=True)
    balance = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Analytic(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(255), index=True)
    metric_value = Column(Float)
    timestamp = Column(BigInteger, nullable=False)
    data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
