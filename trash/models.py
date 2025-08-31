"""Simple Pydantic models."""

from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3

class QueryResponse(BaseModel):
    query: str
    answer: str
    processing_time: float

class IndexRequest(BaseModel):
    limit: Optional[int] = 50
    chunk_size: Optional[int] = 1000

class HealthResponse(BaseModel):
    status: str
    database: bool
    pinecone: bool
    gemini: bool
