"""
Withdrawal Schemas
Pydantic models for withdrawal-related requests and responses
"""
from pydantic import BaseModel, Field
from datetime import datetime


class WithdrawalCreate(BaseModel):
    amount: int = Field(..., gt=0, description="Amount to withdraw in paisa")


class WithdrawalResponse(BaseModel):
    id: str
    user_id: str
    amount: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class WithdrawalListResponse(BaseModel):
    user_id: str
    withdrawals: list[WithdrawalResponse]
