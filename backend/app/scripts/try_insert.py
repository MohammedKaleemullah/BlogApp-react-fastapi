from sqlalchemy.orm import Session
from app.database.db_connect import SessionLocal
from app.models.user import User

def insert_sample_user():
    db: Session = SessionLocal()
    try:
        new_user = User(
            username="john_doe",
            email="john@example.com",
            password_hash="hashed_password_123"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"Inserted user: {new_user.id} - {new_user.username}")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    insert_sample_user()
