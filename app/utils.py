from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, delete
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import Union
from . import models, schemas


# Topics
async def create_topic(db: AsyncSession, topic: schemas.Topic) -> models.Topic:
    query = await db.execute(select(models.Topic).where(models.Topic.name == topic.name))
    fetch = query.scalar_one_or_none()
    if fetch:
        topic.id = fetch.id
        topic.msg = f"Topic with ID: {topic.id} and name '{topic.name}' already exists"
        return {**topic.dict()}
    topic_name = models.Topic(name=topic.name)
    db.add(topic_name)
    await db.commit()
    await db.refresh(topic_name)
    return {"detail": f"topic id: {topic_name.id}, topic name: '{topic.name}' create"}

async def update_topic(db: AsyncSession, topic: schemas.Topic) -> models.Topic:
    query = await db.execute(select(models.Topic.name))#.where(models.Topic.name == topic_update.name))
    fetch = query.scalars().all()
    if fetch:
        if topic.name not in fetch:
            topic.msg = f"topic '{topic.name}' not found"
            return topic
        if topic.new_name in fetch:
            topic.msg = f"Topic with name '{topic.new_name}' already exists"
            return topic
        query = await db.execute(select(models.Topic).where(models.Topic.name == topic.name))
        update_topic = query.scalar_one_or_none()
        if update_topic:
            stmt = update(models.Topic).where(models.Topic.name == topic.name).values(name=topic.new_name)
            await db.execute(stmt)
            await db.commit()
            await db.refresh(update_topic)
            return update_topic
        return

async def get_topics(db: AsyncSession):
    query = await db.execute(select(models.Topic))
    topics = query.scalars().all()
    topics_list = []
    for topic in topics:
        topics_list.append({"topic": topic.name})
    return topics_list

async def get_topic_by_post_id(db: AsyncSession, id: int) -> Union[str, bool]:
    query = await db.execute((select(models.Topic).join(models.Post).where(models.Post.id == id)))
    post = query.scalar_one_or_none()
    if post:
        return post.name
    return False

async def delete_topic_by_name(db: AsyncSession, topic: str):
    query = await db.execute(select(models.Topic).where(models.Topic.name == topic))
    topic = query.scalar_one_or_none()
    if topic:
        await db.delete(topic)
        await db.commit()
        return {"detail": f"Topic '{topic.name}' deleted"}
    return False


# Posts
async def create_post(db: AsyncSession, post: schemas.Post) -> models.Post:
    stmt = select(models.Topic).where(models.Topic.name == post.topic)
    query = await db.execute(stmt)
    topic = query.scalar_one_or_none()
    if topic:
        new_post = models.Post(topic_id=topic.id, content=post.content)
        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)
        post.msg =f"new post '{post.content}' id:{new_post.id} successfully added to database\n"
        post.msg += f"Length of parameters to pass to the address bar is {3+len(str(new_post.id))+9+len(new_post.content)}"
        post.id = new_post.id
        return post
    post.id = None
    post.msg = f"topic '{post.topic}' not found"
    return False

async def update_post(db: AsyncSession, post: schemas.Post) -> models.Post:
    query = await db.execute(select(models.Post).where(models.Post.id == post.id))
    post_update = query.scalar_one_or_none()
    if post_update is None:
        return {"detail": f"Post id: '{post.id}' not found"}
    setattr(post_update, "content", post.new_content)
    await db.commit()
    await db.refresh(post_update)
    return jsonable_encoder(post_update)

async def get_posts(db: AsyncSession):
    query = await db.execute(select(models.Topic).options(selectinload(models.Topic.posts).selectinload(models.Post.comments)))
    topics = query.scalars().all()
    posts_by_topic = []
    for topic in topics:
        posts = []
        for post in topic.posts:
            posts.append({
                "post_id": post.id,
                "content": post.content,
                #"comments": [{"comment_id": c.id, "content": c.content} for c in post.comments] if hasattr(post, 'comments') else [],
                "comments": [{"comment_id": c.id, "content": c.content} for c in post.comments],
            })
        posts_by_topic.append({
            "topic": topic.name,
            "posts": posts
        })
    return posts_by_topic

async def get_post_by_id(db: AsyncSession,  id: int) -> schemas.Post:
    result = await db.execute(select(models.Post).where(models.Post.id == id).options(selectinload(models.Post.comments))) # eager load comments
    post = result.scalar_one_or_none()
    return jsonable_encoder(post)

async def delete_post(db: AsyncSession, id: int) -> models.Post:
    query = await db.execute(select(models.Post).where(models.Post.id == id))
    del_post = query.scalar_one_or_none()
    if del_post is None:
        return None
    await db.delete(del_post)
    await db.commit()
    return {"detail": f"Post with ID {del_post.id} was deleted"}


# Comments
async def create_comment(db: AsyncSession, comment: schemas.Comment) -> models.Comment:
    query = await db.execute(select(models.Post).where(models.Post.id == comment.post_id))
    post = query.scalar_one_or_none()
    if post:
        new_comment = models.Comment(content=comment.content, post_id=comment.post_id)
        db.add(new_comment)
        await db.commit()
        await db.refresh(new_comment)
        return jsonable_encoder(new_comment)
    return {"detail": f"Post with ID {comment.post_id} not found"}

async def update_comment(db: AsyncSession, comment: schemas.Comment) -> models.Comment:
    query = await db.execute(select(models.Comment).where(models.Comment.id == comment.id))
    comment_update = query.scalar_one_or_none()
    if comment_update:
        setattr(comment_update, "content", comment.new_content)
        await db.commit()
        await db.refresh(comment_update)
        return jsonable_encoder(comment_update)
    return {"detail": f"Comment with ID {comment.id} not found"}

async def get_comment_by_id(db: AsyncSession, id: int) -> models.Comment:
    query = await db.execute(select(models.Comment).where(models.Comment.id == id))
    comment = query.scalar_one_or_none()
    if comment:
        return comment
    return {"detail": f"Comment with ID: {id} not found"}

async def delete_comment(db: AsyncSession, id: int) -> models.Comment:
    query = await db.execute(select(models.Comment).where(models.Comment.id == id))
    comment = query.scalar_one_or_none()
    if comment:
        await db.delete(comment)
        await db.commit()
        return {"detail": f"Comment with ID {comment.id} was delete"}
    return {"detail": f"Comment with ID {id} not found"}
