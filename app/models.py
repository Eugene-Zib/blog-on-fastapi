
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base


class Topic(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    posts = relationship("Post", back_populates="topic", cascade="all, delete-orphan")

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    topic_id = Column(Integer, ForeignKey('topics.id'))
    topic = relationship("Topic", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    post_id = Column(Integer, ForeignKey('posts.id'))
    post = relationship("Post", back_populates="comments")
