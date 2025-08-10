# app/scripts/test_db.py
from app.database.db_connect import SessionLocal
from app.models.user import User
from app.models.blog import Blog

def test():
    db = SessionLocal()
    try:
        print("Users count:", db.query(User).count())
        print("Blogs count:", db.query(Blog).count())
    finally:
        db.close()

if __name__ == "__main__":
    test()
