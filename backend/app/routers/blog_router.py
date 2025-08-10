# app/routers/blog_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.db_connect import SessionLocal
from app.schemas.blog import BlogCreate, BlogOut
from app.services import blog_service
import uuid

from app.core.dependencies import get_current_user
from app.core.dependencies import get_db
from fastapi import Query
from app.schemas.blog import BlogUpdate

router = APIRouter(prefix="/blogs", tags=["Blogs"])

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

@router.post("/", response_model=BlogOut)
def create_blog(blog_data: BlogCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return blog_service.create_blog(db, blog_data, current_user.id)

@router.get("/", response_model=List[BlogOut])
def get_blogs(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tags: Optional[List[str]] = Query(None),
    visibility: Optional[str] = Query("public")
):
    return blog_service.get_blogs(db, limit=limit, offset=offset, tags=tags, visibility=visibility)

@router.get("/{blog_id}", response_model=BlogOut)
def get_blog(blog_id: uuid.UUID, db: Session = Depends(get_db)):
    blog = blog_service.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog

@router.delete("/{blog_id}")
def delete_blog(
    blog_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    blog = blog_service.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    if blog.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this blog")
    deleted = blog_service.soft_delete_blog(db, blog_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete blog")
    return {"message": "Blog soft deleted successfully"}

@router.put("/{blog_id}", response_model=BlogOut)
def update_blog(
    blog_id: uuid.UUID,
    blog_data: BlogUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    blog = blog_service.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    if blog.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this blog")
    updated_blog = blog_service.update_blog(db, blog_id, blog_data)
    if not updated_blog:
        raise HTTPException(status_code=500, detail="Failed to update blog")
    return updated_blog

