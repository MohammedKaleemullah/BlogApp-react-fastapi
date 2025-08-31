from dotenv import load_dotenv
import os
import sqlalchemy
from pinecone import Pinecone, ServerlessSpec
from google import genai

# Load environment variables
load_dotenv()

# --------------------
# 1. Database Test
# --------------------
user = os.getenv("db_user")
password = os.getenv("db_password")
host = os.getenv("db_host")
port = os.getenv("db_port")
database_name = os.getenv("db_database")
driver = "psycopg2"

DATABASE_URL = f"postgresql+{driver}://{user}:{password}@{host}:{port}/{database_name}"

try:
    engine = sqlalchemy.create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT version();"))
        version = result.fetchone()[0]
    print(f"✅ PostgreSQL connected! Version: {version}")
except Exception as e:
    print(f"❌ Database connection failed: {e}")

# --------------------
# 2. Pinecone Test
# --------------------
pinecone_api_key = os.getenv("PINECONE_API_KEY")

try:
    # Initialize a Pinecone client with your API key
    pc = Pinecone(api_key=pinecone_api_key)

    # Create a dense index with integrated embedding
    index_name = "quickstart-py"
    if not pc.has_index(index_name):
        pc.create_index_for_model(
            name=index_name,
            cloud="aws",
            region="us-east-1",
            embed={
                "model":"llama-text-embed-v2",
                "field_map":{"text": "chunk_text"}
            }
        )
        print(f"✅ Pinecone index '{index_name}' created successfully.")
    else:
        print(f"✅ Pinecone index '{index_name}' already exists.")
except Exception as e:
    print(f"❌ Pinecone connection failed: {e}")


# --------------------
# 3. Google Gemini Test
# --------------------
try:
    gemini_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=gemini_key)
    
    # quick test: generate a short prompt
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello! Can you respond with 'Connected successfully!'"
    )
    print(f"✅ Gemini API works! Response: {response.candidates[0].content.parts[0].text}")
except Exception as e:
    print(f"❌ Gemini API test failed: {e}")
