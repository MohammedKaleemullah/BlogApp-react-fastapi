from sqlalchemy.orm import Session
from app.models.blog import Blog
from app.schemas.blog import BlogCreate, BlogOut, BlogUpdate
from typing import List, Optional
import uuid

from sqlalchemy import cast, String
from sqlalchemy.dialects.postgresql import array

from app.core.sanitizer import sanitize_html

from sqlalchemy import desc


def is_valid_image_url(url: Optional[str]) -> bool:
    if url is None:
        return True
    return url.startswith("/uploads/")


def create_blog(db: Session, blog_data: BlogCreate, user_id: uuid.UUID) -> Blog:

    clean_content = sanitize_html(blog_data.content)
    # print("SEEEEE HEREEEE")
    # print(blog_data.main_image_url)
    # exit()
    if not is_valid_image_url(blog_data.main_image_url):

        raise ValueError("Invalid main image URL")

    if blog_data.sub_images:
        for url in blog_data.sub_images:
            if not is_valid_image_url(url):
                raise ValueError("Invalid sub image URL")
            

    blog = Blog(
        user_id=user_id,
        title=blog_data.title,
        content=clean_content,
        visibility=blog_data.visibility,
        main_image_url=blog_data.main_image_url,
        sub_images=blog_data.sub_images or [],
        tags=blog_data.tags or []
    )
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog

def get_blogs(
    db: Session,
    limit: int = 10,
    offset: int = 0,
    tags: Optional[list[str]] = None,
    visibility: Optional[str] = "public"
) -> List[Blog]:
    query = db.query(Blog).filter(Blog.is_deleted == False)

    if visibility:
        query = query.filter(Blog.visibility == visibility)

    if tags:
        query = query.filter(Blog.tags.overlap(array(tags, type_=String)))

    query = query.order_by(desc(Blog.created_at))

    return query.offset(offset).limit(limit).all()

def get_blog(db: Session, blog_id: uuid.UUID) -> Blog:
    return db.query(Blog).filter(Blog.id == blog_id, Blog.is_deleted == False).first()

def soft_delete_blog(db: Session, blog_id: uuid.UUID) -> bool:
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        return False
    blog.is_deleted = True
    db.commit()
    return True

def update_blog(db: Session, blog_id: uuid.UUID, blog_data: BlogUpdate) -> Blog:
    blog = db.query(Blog).filter(Blog.id == blog_id, Blog.is_deleted == False).first()
    if not blog:
        return None
    
    if 'content' in blog_data.model_dump(exclude_unset=True):
        blog_data.content = sanitize_html(blog_data.content)

    for field, value in blog_data.model_dump(exclude_unset=True).items():
        setattr(blog, field, value)

    db.commit()
    db.refresh(blog)
    return blog
