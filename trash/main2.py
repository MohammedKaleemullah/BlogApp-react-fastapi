"""Simple FastAPI RAG Server."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
from models import QueryRequest, QueryResponse, HealthResponse, IndexRequest
from services import ServiceManager

app = FastAPI(title="Simple RAG API", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
service_manager = ServiceManager()

@app.on_event("startup")
async def startup():
    """Initialize all services on startup."""
    success = service_manager.initialize_all()
    if not success:
        raise RuntimeError("Failed to initialize services")

@app.on_event("shutdown") 
async def shutdown():
    """Cleanup on shutdown."""
    service_manager.cleanup()

@app.get("/")
async def root():
    return {"message": "Simple RAG API", "docs": "/docs"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if all services are working."""
    db_ok = service_manager.test_database()
    pinecone_ok = service_manager.test_pinecone()
    gemini_ok = service_manager.test_gemini()
    
    return HealthResponse(
        status="healthy" if all([db_ok, pinecone_ok, gemini_ok]) else "unhealthy",
        database=db_ok,
        pinecone=pinecone_ok,
        gemini=gemini_ok
    )

@app.post("/index")
async def index_blogs(request: IndexRequest):
    """Index blogs for RAG."""
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main2:app", host="0.0.0.0", port=8020, reload=True)
