from fastapi import APIRouter, Depends, Request, HTTPException, Body, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlencode
from typing import List, Dict, Union
from . import utils, schemas, db


router = APIRouter()

# Topics
@router.get("/topics/")
async def get_topics(db: AsyncSession = Depends(db.get_db)) -> List[Dict]:
    return await utils.get_topics(db)

@router.post("/create-topic/")
async def create_topic(topic: schemas.Topic, db: AsyncSession = Depends(db.get_db)) -> Dict:
    return await utils.create_topic(db, topic)

@router.put("/update-topic/", response_model=schemas.Topic)
async def update_topic(topic: schemas.Topic, db: AsyncSession = Depends(db.get_db)) -> Dict:
    try:
        return await utils.update_topic(db, topic)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) # HTTP 400 Bad Request

@router.delete("/delete-topic/")
async def delete_topic(request: Request, name: str, db: AsyncSession = Depends(db.get_db)) -> None:
    topic = await utils.delete_topic_by_name(db, name)
    return topic if topic else {"detail": f"Topic '{request.query_params["name"]}' not found"}


# Posts
@router.get("/posts/")
async def get_posts(db: AsyncSession = Depends(db.get_db)) -> List[Dict]:
    return await utils.get_posts(db)

@router.get("/get-post/", response_class=RedirectResponse)
async def get_post(request: Request, topic: str = Depends(schemas.GetTopic("post_id")), post_id: int = Query(default=0)) -> Dict:
    if topic:
        return RedirectResponse(url=f"/post/{topic}/?id={post_id}", status_code=303) # 303 See Other
    raise HTTPException(status_code=404, detail=f"Post id: {post_id} not found") # HTTP 404 Non Found

#from fastapi.encoders import jsonable_encoder
@router.post("/create-post/", response_model=schemas.Post)
async def create_post(post: schemas.Post, db: AsyncSession = Depends(db.get_db)) -> Union[Dict, bool]:
    try:
        new_post = await utils.create_post(db, post)
        #new_post = jsonable_encoder(await utils.create_post(db, post))
        print(new_post)
        #params = urlencode({"id": new_post["id"], "content": new_post["content"]})
        params = urlencode({"id": new_post.id, "content": new_post.content})
        return RedirectResponse(url=f"/post/{post.topic}/?{params}", status_code=303) # 303 See Other
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) # HTTP 400 Bad Request
    except:
        raise HTTPException(status_code=404, detail=f"Topic '{post.topic}' not found") # HTTP 404 Not Found

@router.put("/update-post/")
async def update_post(post: schemas.Post, db: AsyncSession = Depends(db.get_db)) -> Dict:
    try:
        return await utils.update_post(db, post)
        params = urlencode({"id": update.id, "content": update.new_content})
        return RedirectResponse(url=f"/post/{update.topic}/?{params}", status_code=303) # 303 See Other
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) # HTTP 400 Bad Request
    except:
        raise HTTPException(status_code=404, detail=f"Post id: '{post.id}' not found") # HTTP 404 Not Found

@router.get("/post/{topic}/")
async def get_post(request: Request, db: AsyncSession = Depends(db.get_db)) -> Union[Dict, List[Dict]]:
    params = request.query_params
    if "content" in params:
        return {"content": params["content"]}
    if "id" in params:
        post = await utils.get_post_by_id(db, params["id"])
        print(post)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found") # HTTP 404 Not Found
        return post
        return {"content": post.content}
    return {"detail": "Unknown error"}

@router.delete("/delete-post/")
async def delete_post(request: Request, post_id: int, db: AsyncSession = Depends(db.get_db)) -> None:
    post = await utils.delete_post(db, post_id)
    return post if post else {"detail": f"Post id: {request.query_params["post_id"]} not found"}


# Comments
@router.post("/create-comment/")
async def create_comment(comment: schemas.Comment, db: AsyncSession = Depends(db.get_db)) -> Dict:
    try:
        return await utils.create_comment(db, comment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) # HTTP 400 Bad Request

@router.put("/update-comment/")
async def update_comment(comment: schemas.Comment, db: AsyncSession = Depends(db.get_db)) -> Dict:
    try:
        return await utils.update_comment(db, comment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) # HTTP 400 Bad Request

@router.get("/get-comment/", response_model=schemas.Comment)
async def get_comment_by_id(comment_id: int, db: AsyncSession = Depends(db.get_db)) -> Dict:
    return await utils.get_comment_by_id(db, comment_id)

@router.delete("/delete-comment/")
async def delete_comment(comment_id: int, db: AsyncSession = Depends(db.get_db)) -> None:
    return await utils.delete_comment(db, comment_id)
