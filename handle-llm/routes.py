import time
from uuid import uuid4
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from models import *
from image_utils import make_pollinations_prompt, generate_image
from config import UPLOAD_DIR, ALLOWED_EXTENSIONS

router = APIRouter()
service_manager = None

def set_service_manager(sm):
    global service_manager
    service_manager = sm

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
    
@router.post("/update-blog/{blog_id}")
async def update_blog_in_index(blog_id: str, chunk_size: int = 1000):
    """Update a specific blog in the RAG index."""
    if not service_manager or not service_manager.services_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    try:
        start_time = time.time()
        result = service_manager.update_blog_in_index(blog_id, chunk_size)
        processing_time = time.time() - start_time
        
        return {
            "message": f"Blog {blog_id} updated in index",
            "chunks_created": result.get("chunks_count", 0),
            "processing_time": round(processing_time, 2),
            "updated": result.get("updated", True)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.delete("/delete-blog/{blog_id}")
async def delete_blog_from_index(blog_id: str):
    """Remove a blog from the RAG index."""
    if not service_manager or not service_manager.services_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    try:
        result = service_manager.handle_blog_deletion(blog_id)
        return {
            "message": f"Blog {blog_id} removed from index",
            "deleted": result["deleted"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

@router.post("/refresh-index")
async def refresh_entire_index():
    """Refresh the entire RAG index (re-index all blogs)."""
    if not service_manager or not service_manager.services_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    try:
        start_time = time.time()

        index = service_manager.pinecone_client.Index(service_manager.index_name)
        index.delete(delete_all=True)
        print("🗑️ Cleared entire index")

        time.sleep(5)

        result = service_manager.index_blogs(limit=100, chunk_size=1000)
        processing_time = time.time() - start_time
        
        return {
            "message": "Index refreshed successfully",
            "blogs_processed": result["blogs_count"],
            "chunks_created": result["chunks_count"],
            "processing_time": round(processing_time, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")

