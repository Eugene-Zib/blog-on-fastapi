from pydantic import BaseModel, ConfigDict, validator, Field
from typing import List, Optional, TYPE_CHECKING

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
from . import db, utils


if TYPE_CHECKING:
    from .schemas import Comment as comment_schema
else:
    comment_schema = None

class Topic(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., max_length=47)
    new_name: Optional[str] = Field(None, max_length=47)
    msg: Optional[str] = None
    class Config:
        from_attributes = True

class GetTopic:
    def __init__(self, id: str) -> None:
        self.id = id
    async def __call__(self, request: Request, db: AsyncSession=Depends(db.get_db)) -> Union[str]:
        id = request.query_params.get(self.id)
        topic = await utils.get_topic_by_post_id(db, id)
        return topic if topic else None

class Post(BaseModel):
    id: Optional[int] = None
    topic: str
    content: Optional[str] = Field(None, max_length=200)
    new_content: Optional[str] = Field(None, max_length=200)
    comments: List[comment_schema] = []
    msg: Optional[str] = None
    class Config:
        orm_mode = True

class Comment(BaseModel):
    id: Optional[int] = None
    post_id: Optional[int] = None
    content: Optional[str] = None
    new_content: Optional[str] = None
    class Config:
        orm_mode = True
