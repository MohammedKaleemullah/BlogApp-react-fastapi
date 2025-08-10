from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.data_config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()



# from sqlalchemy import create_engine, Column, Integer, String
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import create_engine
# from dotenv import load_dotenv
# import os
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy import TIMESTAMP, text


# load_dotenv()

# print ("hello")

# user = os.getenv("db_user")
# password = os.getenv("db_password")
# host = os.getenv("db_host")
# port = os.getenv("db_port")
# database_name = os.getenv("db_database")
# driver = "psycopg2"

# engine = create_engine(f"postgresql+{driver}://{user}:{password}@{host}:{port}/{database_name}")

# print("connected ")
# Session = sessionmaker(bind=engine)
# session = Session()
# print("session created")

# Base = declarative_base()

# class User(Base):
#     __tablename__ = 'users'
#     __table_args__ = {'schema': 'blogapp_schema'}
#     id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
#     username = Column(String, unique=True, nullable=False)
#     email = Column(String, unique=True, nullable=False)
#     password_hash = Column(String, nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)


# users = session.query(User).all()
# for u in users:
#     print(u.id, u.username, u.email, u.created_at)

# print("done")