from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .prepare_podcast_ep import prepare_episode


class Video(BaseModel):
    id: str
    start: str | None = None
    end: str | None = None
    metadata: dict | None = None


app = FastAPI()


@app.get("/")
def api_checkk():
    return {"Status": "OK"}


@app.post("/episodes")
async def create_ep(video: Video):
    """"""

    episode = prepare_episode(video)
    if not episode:
        raise HTTPException(status_code=500, detail="Something went wrong")

    return {"message": "Episode prepared", "details": episode}
