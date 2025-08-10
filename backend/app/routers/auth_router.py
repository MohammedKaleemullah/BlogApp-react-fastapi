# app/routers/auth_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db_connect import SessionLocal
from app.schemas.auth import Token
from app.schemas.user import UserLogin
from app.services import user_service
from app.core.security import verify_password, create_access_token
from datetime import timedelta
from app.core.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # user = user_service.get_user_by_email(db, user_data.username)
    user = user_service.get_user_by_username(db, user_data.username)
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid USERNAME or password")
    access_token = create_access_token({"sub": str(user.id)}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}
