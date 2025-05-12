from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .prepare_podcast_ep import prepare_episode
from .queue import create_http_task

load_dotenv()


class Video(BaseModel):
    id: str
    start: str | None = None
    end: str | None = None
    metadata: dict | None = None


app = FastAPI()


@app.get("/")
def api_check():
    return {"Status": "OK"}


@app.post("/enqueue")
def add_to_queue(video: Video):
    """"""
    task = create_http_task(json_payload=video.model_dump())
    if not task.name:
        raise HTTPException(status_code=500, detail="Something went wrong")

    return {"message": "Task added to queue", "details": task.name}


@app.post("/episodes")
async def create_ep(video: Video):
    """"""

    episode = prepare_episode(video)
    if not episode:
        raise HTTPException(status_code=500, detail="Something went wrong")

    return {"message": "Episode prepared", "details": episode}
