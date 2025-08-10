# app/models/blog.py
from sqlalchemy import Column, String, Boolean, TIMESTAMP, Text, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from app.database.db_connect import Base

class Blog(Base):
    __tablename__ = "blog"
    __table_args__ = {'schema': 'blogapp_schema'}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("blogapp_schema.users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    visibility = Column(String, nullable=False, server_default=text("'public'"))
    is_deleted = Column(Boolean, nullable=False, server_default=text("false"))
    main_image_url = Column(String, nullable=True)
    sub_images = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    tags = Column(ARRAY(String), nullable=False, server_default=text("ARRAY[]::text[]"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
