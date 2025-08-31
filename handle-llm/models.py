"""Pydantic models for API requests and responses."""

from pydantic import BaseModel

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
