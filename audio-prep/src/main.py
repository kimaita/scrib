from .prepare_podcast_ep import prepare_episode
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel


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
async def create_ep(video: Video, background_tasks: BackgroundTasks):
    """"""

    background_tasks.add_task(prepare_episode, video)
    # if not res:
    #     raise HTTPException(status_code=500, detail="Something went wrong")
    return {"message": "Video received for processing"}
