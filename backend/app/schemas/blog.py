# app/schemas/blog.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class BlogCreate(BaseModel):
    title: str
    content: str
    visibility: Optional[str] = "public"
    tags: Optional[List[str]] = []
    main_image_url: Optional[str] = None
    sub_images: Optional[List[str]] = []

class BlogOut(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    content: str
    visibility: str
    is_deleted: bool
    main_image_url: Optional[str]
    sub_images: List[str]
    tags: List[str]
    created_at: datetime

    class Config:
        from_attributes = True
        # orm_mode = True

class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    visibility: Optional[str] = "public"
    tags: Optional[List[str]] = None
    main_image_url: Optional[str] = None
    sub_images: Optional[List[str]] = None