"""
Payment Method Schemas
Pydantic models for payment method requests and responses
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re


class PaymentMethodCreate(BaseModel):
    method_type: str = Field(..., description="UPI or BANK_ACCOUNT")
    upi_id: Optional[str] = None
    account_holder_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    bank_name: Optional[str] = None
    is_primary: bool = False

    @validator('method_type')
    def validate_method_type(cls, v):
        if v not in ['UPI', 'BANK_ACCOUNT']:
            raise ValueError('method_type must be UPI or BANK_ACCOUNT')
        return v

    @validator('upi_id')
    def validate_upi_id(cls, v, values):
        if values.get('method_type') == 'UPI' and v:
            pattern = r'^[\w\.\-]+@[\w]+$'
            if not re.match(pattern, v):
                raise ValueError('Invalid UPI ID format')
        return v

    @validator('ifsc_code')
    def validate_ifsc_code(cls, v, values):
        if values.get('method_type') == 'BANK_ACCOUNT' and v:
            pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
            if not re.match(pattern, v.upper()):
                raise ValueError('Invalid IFSC code format')
        return v.upper() if v else v


class PaymentMethodResponse(BaseModel):
    id: str
    method_type: str
    upi_id: Optional[str] = None
    account_holder_name: Optional[str] = None
    account_number: Optional[str] = None  # Will be masked
    ifsc_code: Optional[str] = None
    bank_name: Optional[str] = None
    is_primary: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
