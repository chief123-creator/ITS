"""
Payment Routes
Handles payment-related API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.complaint import Complaint
from app.models.payment import Payment
from app.models.transaction import Transaction
from app.schemas.payment import (
    OrderCreateRequest, OrderResponse, PaymentSuccessRequest,
    PaymentResponse, ComplaintPaymentHistory, ReporterPaymentHistory,
    RevenueStats, PaymentDetail, ReporterPaymentItem
)
from app.services.razorpay_service import RazorpayService
from app.services.wallet_service import WalletService
from app.services.split_service import SplitService
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/payments", tags=["payments"])


def get_razorpay_service():
    """Get Razorpay service instance"""
    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")
    if not key_id or not key_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Razorpay credentials not configured"
        )
    return RazorpayService(key_id, key_secret)


@router.post("/create-order", response_model=OrderResponse)
async def create_payment_order(
    request: OrderCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create Razorpay order for complaint payment"""
    try:
        # Fetch complaint
        complaint = db.query(Complaint).filter(
            Complaint.id == request.complaint_id
        ).first()
        
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found"
            )
        
        # Check if already paid
        existing_payment = db.query(Payment).filter(
            Payment.complaint_id == request.complaint_id
        ).first()
        
        if existing_payment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Complaint is already paid"
            )
        
        # Get fine amount in paisa
        amount = int(complaint.fine_amount * 100)
        
        # Create Razorpay order
        razorpay_service = get_razorpay_service()
        receipt = f"complaint_{request.complaint_id}"
        order = razorpay_service.create_order(
            amount=amount,
            currency='INR',
            receipt=receipt
        )
        
        logger.info(f"✓ Order created - Complaint: {request.complaint_id}, Order ID: {order['id']}")
        
        return OrderResponse(
            order_id=order['id'],
            amount=order['amount'],
            currency=order['currency']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error creating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order"
        )


@router.post("/payment-success", response_model=PaymentResponse)
async def process_payment_success(
    request: PaymentSuccessRequest,
    db: Session = Depends(get_db)
):
    """Process successful payment callback from Razorpay"""
    try:
        # Fetch complaint and reporter_id
        complaint = db.query(Complaint).filter(
            Complaint.id == request.complaint_id
        ).first()
        
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found"
            )
        
        reporter_id = complaint.user_id
        
        # Verify signature
        razorpay_service = get_razorpay_service()
        is_valid = razorpay_service.verify_signature(
            order_id=request.razorpay_order_id,
            payment_id=request.razorpay_payment_id,
            signature=request.razorpay_signature
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )
        
        # Check for duplicate payment
        existing_payment = db.query(Payment).filter(
            Payment.razorpay_payment_id == request.razorpay_payment_id
        ).first()
        
        if existing_payment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already processed"
            )
        
        # Create payment record
        payment = Payment(
            complaint_id=request.complaint_id,
            razorpay_payment_id=request.razorpay_payment_id,
            razorpay_order_id=request.razorpay_order_id,
            amount=request.amount,
            status='SUCCESS'
        )
        db.add(payment)
        db.flush()
        
        logger.info(f"✓ Payment recorded - ID: {payment.id}, Complaint: {request.complaint_id}")
        
        # Calculate splits
        split_service = SplitService()
        splits = split_service.calculate_splits(request.amount)
        
        # Credit wallets
        wallet_service = WalletService(db)
        wallet_service.credit_wallet('GOVT', WalletService.GOVT_ID, splits['govt'])
        wallet_service.credit_wallet('REPORTER', reporter_id, splits['reporter'])
        wallet_service.credit_wallet('PLATFORM', WalletService.PLATFORM_ID, splits['platform'])
        
        # Log transactions
        transactions = [
            Transaction(payment_id=payment.id, receiver_type='GOVT', receiver_id=WalletService.GOVT_ID, amount=splits['govt']),
            Transaction(payment_id=payment.id, receiver_type='REPORTER', receiver_id=reporter_id, amount=splits['reporter']),
            Transaction(payment_id=payment.id, receiver_type='PLATFORM', receiver_id=WalletService.PLATFORM_ID, amount=splits['platform'])
        ]
        db.add_all(transactions)
        
        db.commit()
        
        logger.info(f"✓ Payment processing complete - Payment ID: {payment.id}")
        
        return PaymentResponse(
            message="Payment processed successfully",
            payment_id=payment.id
        )
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error processing payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process payment"
        )


@router.get("/complaint/{complaint_id}", response_model=ComplaintPaymentHistory)
async def get_complaint_payment_history(
    complaint_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment history for a specific complaint"""
    try:
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found"
            )
        
        payment = db.query(Payment).filter(Payment.complaint_id == complaint_id).first()
        
        response = ComplaintPaymentHistory(
            complaint_id=complaint.id,
            vehicle_type=complaint.vehicle_type.value,
            fine_amount=complaint.fine_amount,
            status=complaint.status.value,
            payment=None,
            splits=None
        )
        
        if payment:
            split_service = SplitService()
            splits = split_service.calculate_splits(payment.amount)
            
            response.payment = PaymentDetail(
                id=payment.id,
                razorpay_payment_id=payment.razorpay_payment_id,
                razorpay_order_id=payment.razorpay_order_id,
                amount=payment.amount,
                status=payment.status,
                created_at=payment.created_at
            )
            response.splits = splits
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error fetching complaint payment history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment history"
        )


@router.get("/reporter/{reporter_id}", response_model=ReporterPaymentHistory)
async def get_reporter_payment_history(
    reporter_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment history for a reporter"""
    try:
        # Authorization check
        if current_user.id != reporter_id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this data"
            )
        
        # Get all payments for reporter's complaints
        payments = db.query(Payment, Complaint).join(
            Complaint, Payment.complaint_id == Complaint.id
        ).filter(Complaint.user_id == reporter_id).all()
        
        total_earnings = 0
        payment_list = []
        
        for payment, complaint in payments:
            reporter_share = int(payment.amount * 0.05)
            total_earnings += reporter_share
            
            payment_list.append(ReporterPaymentItem(
                payment_id=payment.id,
                complaint_id=complaint.id,
                plate_number=complaint.plate_number,
                total_amount=payment.amount,
                reporter_share=reporter_share,
                created_at=payment.created_at
            ))
        
        # Get wallet balance
        wallet_service = WalletService(db)
        wallet_balance = wallet_service.get_balance('REPORTER', reporter_id)
        
        # Get withdrawal history (placeholder for now)
        withdrawals = []
        
        return ReporterPaymentHistory(
            reporter_id=reporter_id,
            total_earnings=total_earnings,
            wallet_balance=wallet_balance,
            payments=payment_list,
            withdrawals=withdrawals
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error fetching reporter payment history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment history"
        )


@router.post("/test-payment")
async def simulate_test_payment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    TEST ENDPOINT: Simulate a payment for testing wallet functionality
    This creates a fake payment and credits wallets with 90/5/5 split
    """
    try:
        import uuid
        from datetime import datetime
        
        # Create test payment
        test_amount = 50000  # ₹500 in paisa
        
        payment = Payment(
            complaint_id=f"test_complaint_{uuid.uuid4().hex[:8]}",
            razorpay_payment_id=f"pay_test_{uuid.uuid4().hex[:8]}",
            razorpay_order_id=f"order_test_{uuid.uuid4().hex[:8]}",
            amount=test_amount,
            status='SUCCESS'
        )
        db.add(payment)
        db.flush()
        
        # Calculate splits
        split_service = SplitService()
        splits = split_service.calculate_splits(test_amount)
        
        # Credit wallets
        wallet_service = WalletService(db)
        wallet_service.credit_wallet('GOVT', WalletService.GOVT_ID, splits['govt'])
        wallet_service.credit_wallet('REPORTER', current_user.id, splits['reporter'])
        wallet_service.credit_wallet('PLATFORM', WalletService.PLATFORM_ID, splits['platform'])
        
        # Log transactions
        transactions = [
            Transaction(payment_id=payment.id, receiver_type='GOVT', receiver_id=WalletService.GOVT_ID, amount=splits['govt']),
            Transaction(payment_id=payment.id, receiver_type='REPORTER', receiver_id=current_user.id, amount=splits['reporter']),
            Transaction(payment_id=payment.id, receiver_type='PLATFORM', receiver_id=WalletService.PLATFORM_ID, amount=splits['platform'])
        ]
        db.add_all(transactions)
        
        db.commit()
        
        return {
            "message": "Test payment processed successfully",
            "payment_id": payment.id,
            "amount": test_amount,
            "splits": {
                "govt": f"₹{splits['govt']/100}",
                "reporter": f"₹{splits['reporter']/100}",
                "platform": f"₹{splits['platform']/100}"
            },
            "your_wallet_credited": f"₹{splits['reporter']/100}"
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error in test payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test payment failed: {str(e)}"
        )

