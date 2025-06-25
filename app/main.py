from fastapi import FastAPI
from .db import engine, Base
from . import endpoints


app = FastAPI()

app.include_router(endpoints.router)


@app.on_event("startup")
async def startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
