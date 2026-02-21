# Payment System Integration Guide

## ✅ Integration Complete!

Payment system successfully integrated into the ITS application. All Flask-based payment code has been converted to FastAPI and connected to the frontend.

## 🎯 What's Implemented

### Backend (FastAPI)

#### 1. Database Models (SQLAlchemy)
- ✅ `Payment` - Razorpay payment records
- ✅ `Wallet` - Balance management (Govt/Reporter/Platform)
- ✅ `Transaction` - Transaction audit trail
- ✅ `WithdrawalRequest` - Withdrawal management
- ✅ `PaymentMethod` - UPI/Bank account storage

#### 2. API Endpoints

**Payments** (`/api/payments`)
- `POST /create-order` - Create Razorpay order for complaint payment
- `POST /payment-success` - Process payment callback from Razorpay
- `GET /complaint/{complaint_id}` - Get payment history for complaint
- `GET /reporter/{reporter_id}` - Get reporter's payment history

**Wallets** (`/api/wallets`)
- `GET /balance` - Get current user's wallet balance
- `GET /transactions` - Get transaction history

**Withdrawals** (`/api/withdrawals`)
- `POST /` - Create withdrawal request
- `GET /` - Get user's withdrawal requests
- `POST /{id}/approve` - Approve withdrawal (admin only)
- `POST /{id}/reject` - Reject withdrawal (admin only)

**Payment Methods** (`/api/payment-methods`)
- `POST /` - Add UPI or Bank account
- `GET /` - Get user's payment methods
- `DELETE /{id}` - Delete payment method
- `POST /{id}/set-primary` - Set as primary method

#### 3. Services
- ✅ `RazorpayService` - Payment gateway integration
- ✅ `WalletService` - Wallet operations (credit/debit/balance)
- ✅ `SplitService` - Revenue split (90% Govt, 5% Reporter, 5% Platform)

### Frontend (React/TypeScript)

#### 1. API Client (`lib/api.ts`)
- ✅ Payment order creation
- ✅ Payment success processing
- ✅ Wallet balance and transactions
- ✅ Withdrawal requests
- ✅ Payment methods management

#### 2. Components
- ✅ `WalletPage` - Connected to backend API
  - Real-time balance display
  - Transaction history
  - Withdrawal request submission
- ✅ `RewardsPage` - Ready for backend integration

## 🚀 Setup Instructions

### 1. Backend Setup

#### Install Dependencies
```bash
cd ITS/backend
pip install razorpay
```

#### Configure Razorpay
Edit `ITS/backend/.env`:
```env
RAZORPAY_KEY_ID=your_actual_key_id
RAZORPAY_KEY_SECRET=your_actual_key_secret
```

**Get Razorpay Credentials:**
1. Sign up at https://razorpay.com/
2. Go to Settings → API Keys
3. Generate Test/Live keys
4. Copy Key ID and Key Secret to `.env`

#### Run Database Migration
```bash
cd ITS/backend
python run.py
```

This will automatically create all payment tables on first run.

### 2. Frontend Setup

```bash
cd ITS/frontend
npm install
npm run dev
```

Frontend is already configured to connect to `http://localhost:8000`

## 🧪 Testing Guide

### 1. Start Backend
```bash
cd ITS/backend
python run.py
```

Backend will run on: `http://localhost:8000`

### 2. Start Frontend
```bash
cd ITS/frontend
npm run dev
```

Frontend will run on: `http://localhost:8080`

### 3. Test Payment Flow

#### A. Create a Complaint
1. Login to the app
2. Record a video complaint
3. Submit complaint with fine amount

#### B. Create Payment Order
```bash
curl -X POST http://localhost:8000/api/payments/create-order \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"complaint_id": "complaint_id_here"}'
```

Response:
```json
{
  "order_id": "order_xxx",
  "amount": 50000,
  "currency": "INR"
}
```

#### C. Test Wallet Balance
```bash
curl http://localhost:8000/api/wallets/balance \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "balance": 2500,
  "owner_type": "REPORTER",
  "owner_id": "user_id"
}
```

#### D. Test Withdrawal Request
```bash
curl -X POST http://localhost:8000/api/withdrawals \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"amount": 1000}'
```

### 4. Test Frontend Integration

1. **Login** to the app
2. **Go to Wallet page** (`/wallet`)
   - Should show real balance from backend
   - Should show transaction history
3. **Request Withdrawal**
   - Enter amount
   - Click "Withdraw"
   - Should create withdrawal request
4. **Check Transactions**
   - Should display all credit/debit transactions

## 📊 Database Schema

### Tables Created

1. **payments**
   - id, complaint_id, razorpay_payment_id, razorpay_order_id
   - amount, status, created_at

2. **wallets**
   - id, owner_type, owner_id, balance
   - created_at, updated_at
   - Constraints: unique(owner_type, owner_id), balance >= 0

3. **transactions**
   - id, payment_id, receiver_type, receiver_id
   - amount, created_at

4. **withdraw_requests**
   - id, user_id, amount, status
   - created_at, updated_at

5. **user_payment_methods**
   - id, user_id, method_type, upi_id
   - account_holder_name, account_number, ifsc_code, bank_name
   - is_primary, is_verified, created_at, updated_at

## 🔐 Security Features

- ✅ JWT authentication on all endpoints
- ✅ Razorpay signature verification
- ✅ User authorization checks
- ✅ Admin-only endpoints for withdrawals
- ✅ Account number masking in responses
- ✅ Balance validation before withdrawal

## 💰 Revenue Split Logic

For every payment:
- **90%** → Government wallet
- **5%** → Reporter wallet (who reported the violation)
- **5%** → Platform wallet

Example: ₹500 fine
- Government: ₹450
- Reporter: ₹25
- Platform: ₹25

## 🐛 Troubleshooting

### Backend Issues

**Error: "Razorpay credentials not configured"**
- Solution: Add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to `.env`

**Error: "Table doesn't exist"**
- Solution: Restart backend to trigger table creation

**Error: "Invalid signature"**
- Solution: Check Razorpay key secret is correct

### Frontend Issues

**Error: "Failed to fetch"**
- Solution: Ensure backend is running on port 8000
- Check CORS is enabled in backend

**Balance shows 0**
- Solution: Check if wallet exists in database
- Verify authentication token is valid

## 📝 API Documentation

Once backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🎉 Next Steps

1. **Test with real Razorpay account**
   - Switch from test keys to live keys
   - Test actual payment flow

2. **Add SMS notifications**
   - Configure SMS service
   - Send notifications on payment/withdrawal

3. **Add payment method verification**
   - Verify UPI IDs
   - Verify bank accounts

4. **Add admin dashboard**
   - View all payments
   - Manage withdrawals
   - View revenue statistics

## 📞 Support

For issues or questions:
1. Check logs in backend console
2. Check browser console for frontend errors
3. Verify all environment variables are set
4. Ensure database tables are created

---

**Status**: ✅ Ready for Testing
**Last Updated**: Now
