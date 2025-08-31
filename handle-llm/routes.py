"""API routes for the RAG + Image generation service."""

import time
from uuid import uuid4
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from models import *
from image_utils import make_pollinations_prompt, generate_image
from config import UPLOAD_DIR, ALLOWED_EXTENSIONS

# Create router
router = APIRouter()

# Global service manager (will be set from main.py)
service_manager = None

def set_service_manager(sm):
    """Set the service manager instance."""
    global service_manager
    service_manager = sm

# Basic endpoints
@router.get("/")
async def root():
    return {
        "message": "Combined RAG + Image Generation API", 
        "version": "1.0.0",
        "status": "online",
        "services_initialized": service_manager.services_initialized if service_manager else False,
        "index_populated": service_manager.index_populated if service_manager else False,
        "endpoints": {
            "health": "/health",
            "rag": ["/index", "/query"],
            "images": ["/generate", "/upload"],
            "docs": "/docs"
        }
    }

@router.get("/test")
async def test():
    return {
        "status": "working",
        "message": "Basic routing works",
        "timestamp": time.time()
    }

# RAG Endpoints
@router.get("/health", response_model=HealthResponse)
async def health_check():
    if not service_manager:
        return HealthResponse(status="error", database=False, pinecone=False, gemini=False)
    
    db_ok = service_manager.test_database()
    pinecone_ok = service_manager.test_pinecone()
    gemini_ok = service_manager.test_gemini()
    
    return HealthResponse(
        status="healthy" if all([db_ok, pinecone_ok, gemini_ok]) else "degraded",
        database=db_ok,
        pinecone=pinecone_ok,
        gemini=gemini_ok
    )

@router.get("/index-status")
async def index_status():
    if not service_manager or not service_manager.services_initialized:
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

@router.post("/index")
async def index_blogs(request: IndexRequest):
    if not service_manager or not service_manager.services_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized")
        
    try:
        start_time = time.time()
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

@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    if not service_manager or not service_manager.services_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized")
        
    try:
        start_time = time.time()
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
@router.post("/generate", response_model=PromptResponse)
async def generate(req: PromptRequest):
    try:
        summary, pollinations_prompt = make_pollinations_prompt(req.user_input)
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

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
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
