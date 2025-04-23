from .prepare_podcast_ep import prepare_episode
from fastapi import BackgroundTasks, FastAPI, HTTPException

app = FastAPI()


@app.get("/")
def api_checkk():
    return {"Status": "OK"}


@app.post("/episodes")
async def create_ep(
    video_id: str, start: str, end: str, background_tasks: BackgroundTasks
):
    """"""

    background_tasks.add_task(prepare_episode, video_id, start, end)
    # if not res:
    #     raise HTTPException(status_code=500, detail="Something went wrong")
    return {"message": "Video received for processing"}
