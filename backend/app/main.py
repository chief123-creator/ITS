from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import auth, users, complaints, payments, wallets, withdrawals, payment_methods
from app.database import engine, Base
from app.models import user, otp, payment, wallet, transaction, withdrawal, payment_method  # noqa
from app.config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = [
    "http://localhost:8080",
]
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory to serve videos. This is for uploadin videos and serving them back. In production, consider using a proper file storage solution.
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(complaints.router)
app.include_router(payments.router)
app.include_router(wallets.router)
app.include_router(withdrawals.router)
app.include_router(payment_methods.router)

@app.get("/")
def root():
    return {"message": "Welcome to TMS API", "status": "running"}