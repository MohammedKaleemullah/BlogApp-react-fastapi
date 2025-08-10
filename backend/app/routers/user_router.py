from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.db_connect import SessionLocal
from app.schemas.user import UserCreate, UserOut
from app.services import user_service
import uuid
from app.core.dependencies import get_db


router = APIRouter(prefix="/users", tags=["Users"])

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

@router.post("/", response_model=UserOut)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user_data)

@router.get("/", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    return user_service.get_users(db)

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}")
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    deleted = user_service.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
