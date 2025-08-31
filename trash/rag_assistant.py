# rag_assistant.py
import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import text
from pinecone import Pinecone, ServerlessSpec
from google import genai
from langchain_text_splitters import RecursiveCharacterTextSplitter

# -----------------------------
# 1. Load Environment Variables
# -----------------------------
load_dotenv()

DB_USER = os.getenv("db_user")
DB_PASSWORD = os.getenv("db_password")
DB_HOST = os.getenv("db_host")
DB_PORT = os.getenv("db_port")
DB_NAME = os.getenv("db_database")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# -----------------------------
# 2. PostgreSQL Connection
# -----------------------------
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?client_encoding=utf8"

try:
    engine = sqlalchemy.create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print(f"✅ PostgreSQL connected! Version: {result.fetchone()[0]}")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit(1)

# -----------------------------
# 3. Pinecone Initialization
# -----------------------------
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    INDEX_NAME = "blogs-rag"
    existing_indexes = [index.name for index in pc.list_indexes()]


    if INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=INDEX_NAME,
            dimension=768,  # text-embedding-004 dimension
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print(f"✅ Pinecone index '{INDEX_NAME}' created.")
    else:
        print(f"✅ Pinecone index '{INDEX_NAME}' already exists.")
except Exception as e:
    print(f"❌ Pinecone connection failed: {e}")
    exit(1)

# -----------------------------
# 4. Gemini API Test
# -----------------------------
try:
    test_resp = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello! Test connection."
    )
    print(f"✅ Gemini API works! Response: {test_resp.candidates[0].content.parts[0].text}")
except Exception as e:
    print(f"❌ Gemini API failed: {e}")
    exit(1)

# -----------------------------
# 5. Fetch Blogs
# -----------------------------
def fetch_blogs(limit=50):
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT id, title, content FROM blogapp_schema.blog LIMIT {limit}"))
        blogs = [
            {
                "id": row[0],
                "title": row[1],
                "content": row[2] if row[2] is not None else ""
            }
            for row in result.fetchall()
        ]
    return blogs

# -----------------------------
# 6. Chunking Function
# -----------------------------
def chunk_blog_content(blogs, chunk_size=1000, overlap=200):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    all_chunks = []
    for blog in blogs:
        if blog["content"]:  # Only process non-empty content
            chunks = splitter.split_text(blog["content"])
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    "blog_id": blog["id"],
                    "chunk_id": i,
                    "text": chunk
                })
    return all_chunks

def embed_text(text):
    """
    Generates embeddings using Gemini API.
    Returns a list of floats.
    """
    try:
        response = gemini_client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        return response.embeddings[0].values
    except Exception as e:
        print(f"❌ Embedding failed for text: {text[:50]}... Error: {e}")
        return None

# -----------------------------
# 8. Index Chunks in Pinecone
# -----------------------------
def index_chunks(chunks, batch_size=50):
    index = pc.Index(INDEX_NAME)
    vectors = []

    for chunk in chunks:
        embedding = embed_text(chunk["text"])
        if embedding:  # Only add if embedding was successful
            vectors.append({
                "id": f"{chunk['blog_id']}_{chunk['chunk_id']}",
                "values": embedding,
                "metadata": {"text": chunk["text"]}
            })

            if len(vectors) >= batch_size:
                try:
                    index.upsert(vectors=vectors)
                    vectors = []
                except Exception as e:
                    print(f"❌ Batch upsert failed: {e}")

    if vectors:
        try:
            index.upsert(vectors=vectors)
        except Exception as e:
            print(f"❌ Final batch upsert failed: {e}")

    print(f"✅ {len(chunks)} chunks processed for indexing in Pinecone.")

# -----------------------------
# 9. Retrieve Chunks
# -----------------------------
def retrieve_chunks(query, top_k=3):
    query_embedding = embed_text(query)
    if not query_embedding:
        return []
        
    index = pc.Index(INDEX_NAME)

    try:
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        return [match["metadata"]["text"] for match in results["matches"]]
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return []

# -----------------------------
# 10. Generate Answer
# -----------------------------
def generate_answer(context_chunks, user_query):
    if not context_chunks:
        return "Sorry, I couldn't find relevant information to answer your query."
        
    context_text = "\n\n".join(context_chunks)
    prompt = f"""
    You are a helpful assistant. Use the following blog content to answer the user's query.

    {context_text}

    Question: {user_query}
    Answer in concise and clear language.
    """
    
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "temperature": 0.2, 
                "max_output_tokens": 2048  # ✅ Increased from 512 to 2048
            }
        )
        
        # ✅ Handle different response states
        if not response or not hasattr(response, 'candidates') or not response.candidates:
            return "Sorry, I received an empty response from the AI."
        
        candidate = response.candidates[0]
        
        # ✅ Check for MAX_TOKENS finish reason
        if hasattr(candidate, 'finish_reason') and str(candidate.finish_reason) == 'FinishReason.MAX_TOKENS':
            print("⚠️ Response was truncated due to token limit")
        
        # ✅ Safe access to content
        if (hasattr(candidate, 'content') and 
            candidate.content and 
            hasattr(candidate.content, 'parts') and 
            candidate.content.parts and 
            len(candidate.content.parts) > 0 and 
            hasattr(candidate.content.parts[0], 'text')):
            
            return candidate.content.parts[0].text
        else:
            print("❌ Response content parts are empty or malformed")
            print(f"Candidate: {candidate}")
            return "Sorry, the AI response was incomplete or malformed."
            
    except Exception as e:
        print(f"❌ Answer generation failed: {e}")
        return "Sorry, I encountered an error while generating the response."

# -----------------------------
# 11. Main
# -----------------------------
if __name__ == "__main__":
    print("Starting RAG Assistant Setup...")
    blogs = fetch_blogs()
    print(f"Fetched {len(blogs)} blogs from database.")

    chunks = chunk_blog_content(blogs)
    print(f"Created {len(chunks)} chunks from blogs.")

    index_chunks(chunks)
    print("Setup complete. You can now query the RAG assistant.")

    # Example query
    user_query = "Summarize recent pokemon blogs for me"
    relevant_chunks = retrieve_chunks(user_query)
    answer = generate_answer(relevant_chunks, user_query)
    print("\n--- RAG Assistant Response ---")
    print(answer)
