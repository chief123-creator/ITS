"""
Wallet Schemas
Pydantic models for wallet-related requests and responses
"""
from pydantic import BaseModel
from datetime import datetime


class WalletResponse(BaseModel):
    balance: int
    owner_type: str
    owner_id: str

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    id: str
    amount: int
    receiver_type: str
    created_at: datetime
    description: str

    class Config:
        from_attributes = True
