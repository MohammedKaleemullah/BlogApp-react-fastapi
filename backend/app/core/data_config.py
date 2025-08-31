# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os


load_dotenv()

user = os.getenv("db_user")
password = os.getenv("db_password")
host = os.getenv("db_host")
port = os.getenv("db_port")
database_name = os.getenv("db_database")
driver = "psycopg2"

DATABASE_URL = f"postgresql+{driver}://{user}:{password}@{host}:{port}/{database_name}"

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(bind=engine)
# Base = declarative_base()
