import os
import time
import urllib.parse
import requests
import json
import re
from uuid import uuid4
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

# RAG imports
import sqlalchemy
from sqlalchemy import text
from pinecone import Pinecone, ServerlessSpec
from google import genai as genai_client
from langchain_text_splitters import RecursiveCharacterTextSplitter

# -----------------------------
# Setup
# -----------------------------

app = FastAPI(title="Combined RAG + Image API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Image generation setup
UPLOAD_DIR = Path("../backend/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg"}

load_dotenv()

# Configure Gemini for image generation
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    print("✅ Gemini configured for image generation")
except Exception as e:
    print(f"⚠️ Gemini image generation setup failed: {e}")
    gemini_model = None

# Pollinations models priority
MODELS = ["turbo", "flux", "kontext"]

# -----------------------------
# Pydantic Models
# -----------------------------

# RAG Models
class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

class QueryResponse(BaseModel):
    query: str
    answer: str
    processing_time: float

class IndexRequest(BaseModel):
    limit: int = 50
    chunk_size: int = 1000

class HealthResponse(BaseModel):
    status: str
    database: bool
    pinecone: bool
    gemini: bool

# Image Generation Models
class PromptRequest(BaseModel):
    user_input: str
    width: int = 1024
    height: int = 1024
    seed: int = 42

class PromptResponse(BaseModel):
    summary: str
    image_file: str
    image_url: str

# -----------------------------
# Service Manager
# -----------------------------

class ServiceManager:
    """Manages all services in one class."""
    
    def __init__(self):
        # Database
        self.db_engine = None
        
        # Pinecone
        self.pinecone_client = None
        self.index_name = "rag-index-v1"
        
        # Gemini for RAG
        self.gemini_client = None
        
        # Service status
        self.services_initialized = False
        self.index_populated = False
        
    def initialize_all(self) -> bool:
        """Initialize all services with detailed logging."""
        print("🚀 Starting service initialization...")
        
        try:
            # Database
            print("🔗 Connecting to database...")
            db_url = f"postgresql+psycopg2://{os.getenv('db_user')}:{os.getenv('db_password')}@{os.getenv('db_host')}:{os.getenv('db_port')}/{os.getenv('db_database')}"
            self.db_engine = sqlalchemy.create_engine(db_url)
            
            # Test database
            with self.db_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database connected")
            
            # Pinecone
            print("🔗 Connecting to Pinecone...")
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            existing_indexes = [index.name for index in pc.list_indexes()]

            index_created = False
            if self.index_name not in existing_indexes:
                print(f"Creating new Pinecone index: {self.index_name}")
                pc.create_index(
                    name=self.index_name,
                    dimension=768,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1")
                )
                print(f"✅ Created Pinecone index: {self.index_name}")
                index_created = True
                
                # Wait for index to be ready
                print("⏳ Waiting for index to be ready...")
                time.sleep(10)
            else:
                print(f"✅ Pinecone index exists: {self.index_name}")
                
            self.pinecone_client = pc
            
            # Gemini for RAG
            print("🔗 Connecting to Gemini...")
            self.gemini_client = genai_client.Client(api_key=os.getenv("GEMINI_API_KEY"))
            
            # Test Gemini
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents="Say 'OK'"
            )
            print("✅ Gemini connected")
            
            self.services_initialized = True
            
            # ✅ AUTO-INDEX BLOGS DURING STARTUP
            if index_created or not self.is_index_populated():
                print("🔄 Auto-indexing blogs during startup...")
                try:
                    result = self.index_blogs(limit=20, chunk_size=1000)
                    print(f"✅ Auto-indexed {result['blogs_count']} blogs with {result['chunks_count']} chunks")
                    self.index_populated = True
                except Exception as e:
                    print(f"⚠️ Auto-indexing failed: {e}")
                    print("You can manually index blogs using the /index endpoint")
            else:
                print("✅ Index already has data, skipping auto-indexing")
                self.index_populated = True
            
            print("🎉 All services initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Service initialization failed: {e}")
            self.services_initialized = False
            return False
    
    def is_index_populated(self) -> bool:
        """Check if the Pinecone index has data."""
        try:
            index = self.pinecone_client.Index(self.index_name)
            stats = index.describe_index_stats()
            total_vectors = stats.get('total_vector_count', 0)
            print(f"📊 Index has {total_vectors} vectors")
            return total_vectors > 0
        except Exception as e:
            print(f"⚠️ Could not check index stats: {e}")
            return False
    
    def test_database(self) -> bool:
        """Test database connection."""
        if not self.db_engine:
            return False
        try:
            with self.db_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except:
            return False
    
    def test_pinecone(self) -> bool:
        """Test Pinecone connection."""
        if not self.pinecone_client:
            return False
        try:
            self.pinecone_client.Index(self.index_name).describe_index_stats()
            return True
        except:
            return False
    
    def test_gemini(self) -> bool:
        """Test Gemini connection."""
        if not self.gemini_client:
            return False
        try:
            self.gemini_client.models.generate_content(
                model="gemini-2.5-flash", 
                contents="test"
            )
            return True
        except:
            return False
    
    def fetch_blogs(self, limit: int = 50):
        """Fetch blogs from database."""
        if not self.db_engine:
            raise RuntimeError("Database not connected")
            
        with self.db_engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, title, content FROM blogapp_schema.blog WHERE content IS NOT NULL AND content != '' LIMIT :limit"),
                {"limit": limit}
            )
            blogs = [
                {"id": row[0], "title": row[1], "content": row[2]}
                for row in result.fetchall()
                if row[2] and len(row[2].strip()) > 50  # Only blogs with substantial content
            ]
            print(f"📚 Fetched {len(blogs)} blogs with content")
            return blogs
    
    def embed_text(self, text: str):
        """Generate embedding for text."""
        if not self.gemini_client:
            raise RuntimeError("Gemini client not connected")
            
        # Clean and truncate text for embedding
        clean_text = text.strip()[:8000]  # Limit text length for embedding
        
        response = self.gemini_client.models.embed_content(
            model="text-embedding-004",
            contents=clean_text
        )
        return response.embeddings[0].values
    
    def chunk_text(self, text: str, chunk_size: int = 1000):
        """Split text into chunks."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=200
        )
        return splitter.split_text(text)
    
    def index_blogs(self, limit: int = 50, chunk_size: int = 1000):
        """Index blogs into Pinecone."""
        if not self.services_initialized:
            raise RuntimeError("Services not initialized")
            
        print(f"🔄 Starting indexing process for {limit} blogs...")
        
        # Fetch blogs
        blogs = self.fetch_blogs(limit)
        
        if not blogs:
            print("⚠️ No blogs found with content to index")
            return {"blogs_count": 0, "chunks_count": 0}
        
        # Create chunks and vectors
        vectors = []
        chunks_count = 0
        
        for blog in blogs:
            if not blog["content"] or len(blog["content"].strip()) < 50:
                continue
                
            print(f"📝 Processing blog {blog['id']}: {blog['title'][:50]}...")
            
            # Combine title and content for better context
            full_content = f"Title: {blog['title']}\n\nContent: {blog['content']}"
            chunks = self.chunk_text(full_content, chunk_size)
            
            for i, chunk in enumerate(chunks):
                try:
                    embedding = self.embed_text(chunk)
                    vectors.append({
                        "id": f"blog_{blog['id']}_chunk_{i}",
                        "values": embedding,
                        "metadata": {
                            "text": chunk,
                            "blog_id": str(blog['id']),
                            "blog_title": blog['title'],
                            "chunk_index": i
                        }
                    })
                    chunks_count += 1
                    
                    if len(vectors) % 10 == 0:
                        print(f"  📊 Processed {len(vectors)} chunks...")
                        
                except Exception as e:
                    print(f"⚠️ Failed to embed chunk {i} from blog {blog['id']}: {e}")
                    continue
        
        # Upsert to Pinecone
        if vectors:
            print(f"🚀 Upserting {len(vectors)} vectors to Pinecone...")
            index = self.pinecone_client.Index(self.index_name)
            
            # Batch upsert
            batch_size = 50
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                try:
                    index.upsert(vectors=batch)
                    print(f"  ✅ Upserted batch {i//batch_size + 1}/{(len(vectors) + batch_size - 1)//batch_size}")
                except Exception as e:
                    print(f"⚠️ Failed to upsert batch {i//batch_size + 1}: {e}")
            
            # Verify indexing
            time.sleep(2)  # Wait for indexing to complete
            stats = index.describe_index_stats()
            total_vectors = stats.get('total_vector_count', 0)
            print(f"📊 Index now has {total_vectors} total vectors")
        
        result = {
            "blogs_count": len(blogs),
            "chunks_count": chunks_count
        }
        
        print(f"✅ Indexing completed: {result}")
        return result
    
    def process_query(self, query: str, top_k: int = 3):
        """Process a RAG query with friendly system prompt."""
        if not self.services_initialized:
            raise RuntimeError("Services not initialized")
        
        print(f"🔍 Processing query: '{query}'")
        
        # Check if index has data
        if not self.is_index_populated():
            return """I don't have any blog content indexed yet! 😔 

Here are a few options:
1. Use the /index endpoint to index some blogs first
2. Ask an admin to run the indexing process
3. Try again in a few minutes if indexing is in progress

I'd love to help once we have some content to search through! 🤖"""
        
        # Get query embedding
        query_embedding = self.embed_text(query)
        
        # Search Pinecone
        index = self.pinecone_client.Index(self.index_name)
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        print(f"📊 Found {len(results.get('matches', []))} matches")
        
        # Get relevant chunks
        chunks = []
        for match in results.get('matches', []):
            if match.get('score', 0) > 0.1:  # Only include relevant matches
                chunks.append(match["metadata"]["text"])
        
        if not chunks:
            return f"""I couldn't find specific information about "{query}" in our blog database. 🤔

This could mean:
- The topic isn't covered in our current blogs
- Try rephrasing your question differently
- Ask about related topics

Is there something else I can help you with? I'm here to assist! 😊"""
        
        # ✅ FRIENDLY SYSTEM PROMPT
        system_prompt = """You are a friendly, helpful, and knowledgeable blog assistant. Your personality traits:

🎯 **Role**: You help users find information from our blog database
😊 **Tone**: Warm, conversational, and enthusiastic  
🧠 **Style**: Clear, concise, but engaging explanations
✨ **Approach**: Always try to be helpful and provide actionable insights
🤝 **Interaction**: Use emojis sparingly but appropriately, ask follow-up questions when helpful

**Guidelines**:
- Base your answers ONLY on the provided blog content
- If information is limited, acknowledge it honestly
- Structure your responses with clear points when appropriate  
- Add personal touches like "Hope this helps!" or "Let me know if you'd like to know more!"
- If you can't fully answer, suggest related topics or ask clarifying questions"""

        # Generate answer
        context = "\n\n".join(chunks)
        user_prompt = f"""**Blog Content:**
{context}

**User Question:** {query}

Please provide a helpful, friendly response based on the blog content above. If you can partially answer, do so and mention what additional information might be helpful."""

        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        response = self.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
            config={
                "temperature": 0.2,  # Slightly higher for more personality
                "max_output_tokens": 2048
            }
        )
        
        if (response and response.candidates and 
            response.candidates[0].content and
            response.candidates[0].content.parts):
            return response.candidates[0].content.parts[0].text
        else:
            return "I'm having trouble generating a response right now. Please try again! 🤖"
    
    def cleanup(self):
        """Cleanup resources."""
        if self.db_engine:
            self.db_engine.dispose()
        print("✅ Services cleaned up")

# -----------------------------
# Image Generation Helpers
# -----------------------------

def make_pollinations_prompt(user_input: str) -> tuple[str, str]:
    """Use Gemini to generate Pollinations prompt + summary, with fallback."""
    if not gemini_model:
        return user_input[:50], user_input
        
    system_instruction = """
    You are a prompt generator for Pollinations.ai.
    The user will describe an image.
    You will:
    1. Create a short 5-word summary.
    2. Expand the description into a Pollinations prompt using this format:
       {sceneDetailed}, {adjective1}, {charactersDetailed}, {adjective2}, 
       {visualStyle1}, {visualStyle2}, {visualStyle3}, {genre}, {artistReference}
    Return in JSON:
    {"summary": "...", "prompt": "..."}
    """

    try:
        response = gemini_model.generate_content(
            system_instruction + f"\nUser description: {user_input}"
        )
        raw_text = response.text.strip()
        print("🔎 Gemini raw output:", raw_text)

        # Try strict JSON parse
        try:
            result = json.loads(raw_text)
            if "summary" in result and "prompt" in result:
                return result["summary"], result["prompt"]
        except json.JSONDecodeError:
            # Try regex to extract JSON block
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                result = json.loads(match.group())
                if "summary" in result and "prompt" in result:
                    return result["summary"], result["prompt"]

        # As fallback, just return raw input
        print("⚠️ Gemini failed to produce JSON, falling back to raw input.")
        return user_input[:50], user_input

    except Exception as e:
        print(f"❌ Gemini error: {e}, falling back to raw input.")
        return user_input[:50], user_input

def generate_image(prompt: str, width: int, height: int, seed: int, retries: int = 5) -> str:
    """Try Pollinations models in order, retrying each if needed."""
    encoded_prompt = urllib.parse.quote(prompt)

    for model in MODELS:
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model={model}&width={width}&height={height}&seed={seed}"
        print(f"🔄 Trying model: {model} -> {url}")

        for attempt in range(retries):
            try:
                resp = requests.get(url, timeout=30)
                if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
                    filename = f"{uuid4().hex}_{model}.webp"
                    filepath = UPLOAD_DIR / filename
                    with open(filepath, "wb") as f:
                        f.write(resp.content)
                    print(f"✅ Success with {model}, saved {filepath}")
                    return f"/uploads/{filename}"
                else:
                    print(f"⚠️ {model} returned non-image, retrying ({attempt+1}/{retries})...")
            except Exception as e:
                print(f"❌ {model} error: {e}, retrying ({attempt+1}/{retries})...")
            time.sleep(2)

    raise HTTPException(status_code=500, detail="All Pollinations models failed.")

# -----------------------------
# Initialize Services
# -----------------------------

service_manager = ServiceManager()

# Non-blocking initialization
@app.on_event("startup")
async def startup():
    """Initialize all services on startup - non-blocking."""
    print("🚀 FastAPI server starting...")
    
    try:
        # Try to initialize services but don't block if it fails
        success = service_manager.initialize_all()
        if success:
            print("✅ All services ready!")
        else:
            print("⚠️ Some services failed to initialize - continuing with limited functionality")
    except Exception as e:
        print(f"⚠️ Service initialization error: {e}")
        print("Continuing with basic server functionality...")

@app.on_event("shutdown") 
async def shutdown():
    """Cleanup on shutdown."""
    service_manager.cleanup()

# -----------------------------
# Routes - Always Available
# -----------------------------

@app.get("/")
async def root():
    return {
        "message": "Combined RAG + Image Generation API", 
        "version": "1.0.0",
        "status": "online",
        "services_initialized": service_manager.services_initialized,
        "index_populated": service_manager.index_populated,
        "endpoints": {
            "health": "/health",
            "rag": ["/index", "/query"],
            "images": ["/generate", "/upload"],
            "docs": "/docs"
        }
    }

@app.get("/test")
async def test():
    """Simple test endpoint - always works."""
    return {
        "status": "working",
        "message": "Basic routing works",
        "timestamp": time.time()
    }

# RAG Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if all services are working."""
    db_ok = service_manager.test_database()
    pinecone_ok = service_manager.test_pinecone()
    gemini_ok = service_manager.test_gemini()
    
    return HealthResponse(
        status="healthy" if all([db_ok, pinecone_ok, gemini_ok]) else "degraded",
        database=db_ok,
        pinecone=pinecone_ok,
        gemini=gemini_ok
    )

@app.get("/index-status")
async def index_status():
    """Check RAG index status."""
    if not service_manager.services_initialized:
        return {"status": "services_not_ready"}
    
    try:
        index = service_manager.pinecone_client.Index(service_manager.index_name)
        stats = index.describe_index_stats()
        return {
            "status": "ready",
            "total_vectors": stats.get('total_vector_count', 0),
            "index_populated": service_manager.index_populated
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/index")
async def index_blogs(request: IndexRequest):
    """Index blogs for RAG."""
    if not service_manager.services_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized")
        
    try:
        start_time = time.time()
        
        # Fetch and process blogs
        result = service_manager.index_blogs(
            limit=request.limit,
            chunk_size=request.chunk_size
        )
        
        processing_time = time.time() - start_time
        
        return {
            "message": "Indexing completed",
            "blogs_processed": result["blogs_count"],
            "chunks_created": result["chunks_count"],
            "processing_time": round(processing_time, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Query the RAG system."""
    if not service_manager.services_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized")
        
    try:
        start_time = time.time()
        
        # Process query
        answer = service_manager.process_query(request.query, request.top_k)
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            query=request.query,
            answer=answer,
            processing_time=round(processing_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

# Image Generation Endpoints
@app.post("/generate", response_model=PromptResponse)
async def generate(req: PromptRequest):
    """Generate image using Pollinations AI."""
    try:
        summary, pollinations_prompt = make_pollinations_prompt(req.user_input)

        # Generate image and get relative URL
        image_file = generate_image(
            prompt=pollinations_prompt,
            width=req.width,
            height=req.height,
            seed=req.seed
        )

        return PromptResponse(
            summary=summary,
            image_file=image_file,
            image_url=image_file
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload an image and store it in /uploads."""
    try:
        if not file.filename or "." not in file.filename:
            raise HTTPException(status_code=400, detail="Invalid file")

        file_extension = file.filename.rsplit(".", 1)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Invalid file type")

        unique_filename = f"{uuid4()}.{file_extension}"
        file_path = UPLOAD_DIR / unique_filename

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        return JSONResponse(content={"url": f"/uploads/{unique_filename}"})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# ✅ Always run on port 8005
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting server on port 8005...")
    uvicorn.run("everything:app", host="0.0.0.0", port=8005, reload=True)
