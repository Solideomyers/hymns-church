from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    hymns = relationship("Hymn", back_populates="category")

class Hymn(Base):
    __tablename__ = 'hymns'
    id = Column(Integer, primary_key=True, index=True)
    hymn_number = Column(Integer, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))

    category = relationship("Category", back_populates="hymns")
    content = relationship("HymnContent", back_populates="hymn", cascade="all, delete-orphan")

class HymnContent(Base):
    __tablename__ = 'hymn_content'
    id = Column(Integer, primary_key=True, index=True)
    hymn_id = Column(Integer, ForeignKey('hymns.id'), nullable=False)
    content_type = Column(String, nullable=False)  # 'estrofa' or 'coro'
    stanza_number = Column(Integer, nullable=True)
    content_order = Column(Integer, nullable=False)

    hymn = relationship("Hymn", back_populates="content")
    lines = relationship("ContentLine", back_populates="hymn_content", cascade="all, delete-orphan")

class ContentLine(Base):
    __tablename__ = 'content_lines'
    id = Column(Integer, primary_key=True, index=True)
    hymn_content_id = Column(Integer, ForeignKey('hymn_content.id'), nullable=False)
    line_text = Column(Text, nullable=False)
    line_order = Column(Integer, nullable=False)

    hymn_content = relationship("HymnContent", back_populates="lines")
