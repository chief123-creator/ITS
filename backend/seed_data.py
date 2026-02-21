"""
Seed script to add dummy data for testing
Run: python seed_data.py
"""
from app.database import SessionLocal
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.models.payment import Payment
from app.models.user import User
from datetime import datetime
import uuid

def seed_data():
    db = SessionLocal()
    
    try:
        print("🌱 Seeding database with test data...")
        
        # Check if user exists
        user = db.query(User).first()
        if not user:
            print("❌ No users found. Please signup first!")
            return
        
        user_id = str(user.id)
        print(f"✅ Found user: {user.email} (ID: {user_id})")
        
        # Create/Update Reporter Wallet
        reporter_wallet = db.query(Wallet).filter(
            Wallet.owner_type == "REPORTER",
            Wallet.owner_id == user_id
        ).first()
        
        if not reporter_wallet:
            reporter_wallet = Wallet(
                owner_type="REPORTER",
                owner_id=user_id,
                balance=50000  # ₹500 in paisa
            )
            db.add(reporter_wallet)
            print(f"✅ Created reporter wallet with ₹500")
        else:
            reporter_wallet.balance += 50000
            print(f"✅ Added ₹500 to existing wallet. New balance: ₹{reporter_wallet.balance/100}")
        
        # Create Government Wallet
        govt_wallet = db.query(Wallet).filter(
            Wallet.owner_type == "GOVT",
            Wallet.owner_id == "GOVT_1"
        ).first()
        
        if not govt_wallet:
            govt_wallet = Wallet(
                owner_type="GOVT",
                owner_id="GOVT_1",
                balance=100000  # ₹1000
            )
            db.add(govt_wallet)
            print(f"✅ Created government wallet with ₹1000")
        
        # Create Platform Wallet
        platform_wallet = db.query(Wallet).filter(
            Wallet.owner_type == "PLATFORM",
            Wallet.owner_id == "PLATFORM_1"
        ).first()
        
        if not platform_wallet:
            platform_wallet = Wallet(
                owner_type="PLATFORM",
                owner_id="PLATFORM_1",
                balance=50000  # ₹500
            )
            db.add(platform_wallet)
            print(f"✅ Created platform wallet with ₹500")
        
        # Create dummy payment
        payment = Payment(
            id=str(uuid.uuid4()),
            complaint_id="test_complaint_1",
            razorpay_payment_id="pay_test_" + str(uuid.uuid4())[:8],
            razorpay_order_id="order_test_" + str(uuid.uuid4())[:8],
            amount=50000,  # ₹500
            status="captured",
            created_at=datetime.utcnow()
        )
        db.add(payment)
        print(f"✅ Created test payment of ₹500")
        
        # Create transactions
        transactions = [
            Transaction(
                payment_id=payment.id,
                receiver_type="REPORTER",
                receiver_id=user_id,
                amount=2500,  # ₹25 (5%)
                created_at=datetime.utcnow()
            ),
            Transaction(
                payment_id=payment.id,
                receiver_type="GOVT",
                receiver_id="GOVT_1",
                amount=45000,  # ₹450 (90%)
                created_at=datetime.utcnow()
            ),
            Transaction(
                payment_id=payment.id,
                receiver_type="PLATFORM",
                receiver_id="PLATFORM_1",
                amount=2500,  # ₹25 (5%)
                created_at=datetime.utcnow()
            )
        ]
        
        for txn in transactions:
            db.add(txn)
        
        print(f"✅ Created 3 test transactions")
        
        db.commit()
        print("\n🎉 Database seeded successfully!")
        print(f"\n📊 Summary:")
        print(f"   Reporter Wallet: ₹{reporter_wallet.balance/100}")
        print(f"   Government Wallet: ₹{govt_wallet.balance/100}")
        print(f"   Platform Wallet: ₹{platform_wallet.balance/100}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
