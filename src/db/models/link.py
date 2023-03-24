import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.config import Base


class Link(Base):
    __tablename__ = "link"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    link = Column(Text, nullable=False)
    short_link = Column(String(40), unique=True)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    is_deleted = Column(Boolean, index=True, default=False)
    clicks = relationship("LinkClick",
                          back_populates="link",
                          cascade="delete",
                          passive_deletes=True,
                          )


class LinkClick(Base):
    __tablename__ = "link_click"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    link_id = Column(ForeignKey("link.id"), nullable=False)
    link = relationship("Link", back_populates="clicks")
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    client = Column(String(255))
