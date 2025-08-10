from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from typing import List
import uuid

from app.core.security import hash_password

def create_user(db: Session, user_data: UserCreate) -> User:
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    ) 
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_users(db: Session) -> List[User]:
    return db.query(User).all()

def get_user(db: Session, user_id: uuid.UUID) -> User:
    return db.query(User).filter(User.id == user_id).first()

def delete_user(db: Session, user_id: uuid.UUID) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True

def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()
