"""
Payment Schemas
Pydantic models for payment-related requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OrderCreateRequest(BaseModel):
    complaint_id: str = Field(..., description="Complaint ID for payment")


class OrderResponse(BaseModel):
    order_id: str
    amount: int
    currency: str


class PaymentSuccessRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    complaint_id: str
    amount: int


class PaymentResponse(BaseModel):
    message: str
    payment_id: str


class PaymentDetail(BaseModel):
    id: str
    razorpay_payment_id: str
    razorpay_order_id: str
    amount: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ComplaintPaymentHistory(BaseModel):
    complaint_id: str
    vehicle_type: str
    fine_amount: float
    status: str
    payment: Optional[PaymentDetail] = None
    splits: Optional[dict] = None


class ReporterPaymentItem(BaseModel):
    payment_id: str
    complaint_id: str
    plate_number: Optional[str]
    total_amount: int
    reporter_share: int
    created_at: datetime


class ReporterPaymentHistory(BaseModel):
    reporter_id: str
    total_earnings: int
    wallet_balance: int
    payments: list[ReporterPaymentItem]
    withdrawals: list


class RevenueStats(BaseModel):
    total_fines: int
    govt_revenue: int
    platform_earnings: int
    reporter_rewards: int
