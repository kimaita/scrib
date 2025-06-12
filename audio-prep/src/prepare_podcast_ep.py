import logging
import os
import shlex
import subprocess
from datetime import timedelta
from io import BytesIO
from pathlib import Path

import boto3
import requests
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from google import genai
from PIL import Image, ImageOps

from .youtube_api import YouTube

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(levelname)s:%(asctime)s:%(message)s",
    encoding="utf-8",
    level=logging.INFO,
)


def upload_file(file_name, object_name=None):
    """Upload a file to R2 Storage

    :param file_name: File to upload
    :param object_name: Storage object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    if object_name is None:
        object_name = os.path.basename(file_name)

    print("Uploading to R2:", file_name)
    s3 = boto3.client(
        service_name="s3",
        endpoint_url=f"https://{os.getenv('ACCOUNT_ID')}.r2.cloudflarestorage.com",
        aws_access_key_id=os.getenv("ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
        region_name=os.getenv("REGION"),
    )

    try:
        s3.upload_file(
            file_name,
            os.getenv("BUCKET_NAME"),
            object_name,
        )
    except ClientError as e:
        logging.error(e)
        return False
    return True


def update_video(video_id, **kwargs):
    """Update video attributes"""
    API_ENDPOINT = f"{os.getenv('SCRIB_API_URL')}/videos"

    r = requests.patch(f"{API_ENDPOINT}/{video_id}", json=kwargs)
    resp = r.json()
    if r.status_code != 200:
        logging.error(f"Error updating video {video_id}: {resp}")
        return False

    return resp


def generate_summary(file_path) -> str:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    audio_file = client.files.upload(file=file_path)
    with open("/app/sermon_summary_prompt.txt") as f:
        PROMPT = f.read()
    logging.info(f"Generating summary: {file_path}")

    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=[PROMPT, audio_file]
    )
    return response.text


def get_video_info(video_id):
    """Fetch video details from the Youtube API"""
    res = YouTube().get("video", video_id)
    try:
        return res[0]
    except Exception:
        return None


def get_pad_color(img):
    colors = img.getcolors(2**20)
    if colors:
        return sorted(colors, key=lambda p: p[0], reverse=True)[0][1]
    get_pad_color(img.crop((32, 0, (img.width) - 32, img.height)))


def resize(img):
    """Resize image to suitable artwork size"""
    size = (1400, 1400)

    asp_ratio = img.width / img.height
    new_height = img.height + ((size[0] - img.width) * (1 / asp_ratio))
    strip_height = int((size[1] - new_height) / 2)

    strip_size = 8
    top_strip = img.crop((0, 0, img.width, 0 + strip_size))

    padding = Image.new("RGB", (size[0], strip_height), color=get_pad_color(top_strip))

    thmb = ImageOps.pad(img, size)
    thmb.paste(padding, (0, 0))
    thmb.paste(padding, (0, int(new_height) + strip_height))

    return thmb


def prepare_artwork(thumbnail_url, id):
    filename = f"{id}.podcast.jpg"
    res = requests.get(thumbnail_url)
    thumbnail = Image.open(BytesIO(res.content))
    logging.info(f"Resizing image {filename}")

    try:
        artwork = resize(thumbnail)
        artwork.save(filename)
        return filename
    except Exception as e:
        logging.error(f"Error processing thumhnail {e}")
        return False


def convert_timestring(timestring):
    """Convert a string timestamp to seconds"""
    parts = timestring.split(":")
    if len(parts) > 3:
        raise ValueError("Invalid time")

    if len(parts) == 3:
        tdelta = timedelta(
            hours=int(parts[0]), minutes=int(parts[1]), seconds=float(parts[2])
        )
    else:
        tdelta = timedelta(minutes=int(parts[0]), seconds=float(parts[1]))

    return tdelta.total_seconds()


def actual_length(file_name):
    """Get audio/video file length"""
    cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1"
    check = subprocess.run(shlex.split(cmd) + [file_name], capture_output=True)
    try:
        actual = float(check.stdout.decode().strip())
        return actual
    except ValueError:
        logging.error(f"Error getting length of {file_name}: {check.stderr.decode()}")
        return 0


def check_length(file_name, expected):
    """Check whether the sermon's lenth is within accepted range"""

    actual = actual_length(file_name)
    ERROR_MARGIN = 2
    logging.debug(
        f"Audio length: {actual} expected: {expected} diff: {abs(actual - expected)}"
    )

    return expected - ERROR_MARGIN <= actual <= expected + ERROR_MARGIN


def create_ffmpeg_cmd(input=None, output=None, **kwargs):
    ffmpeg_cmd = ["ffmpeg", "-hide_banner", "-loglevel", "10"]
    BITRATE = "128k"

    if "start" in kwargs:
        ffmpeg_cmd.extend(("-ss", kwargs["start"]))
    if "end" in kwargs:
        ffmpeg_cmd.extend(("-to", kwargs["end"]))

    ffmpeg_cmd.extend(("-i", input or "pipe:"))
    if "thumbnail" in kwargs:
        ffmpeg_cmd.extend(("-i", kwargs["thumbnail"]))

    if "metadata" in kwargs:
        for k, v in kwargs["metadata"].items():
            ffmpeg_cmd.extend(("-metadata", f"{k}={v}"))

    ffmpeg_cmd.extend(
        [
            "-map",
            "0:a",
            "-c:a",
            "libmp3lame",
            "-b:a",
            BITRATE,
            "-af",
            "afftdn",
            "-map",
            "1",
            "-y",
            output or "pipe:",
        ]
    )

    return ffmpeg_cmd


def download_audio(video_id: str) -> str | None:
    """"""
    resp = requests.post(
        f"{os.getenv('DOWNLOADER_API')}/download",
        json={"id": video_id},
    )

    resp_json = resp.json()

    if resp.status_code != 200:
        logging.error(f"Error downloading {video_id}: {resp_json}")
        return None

    file_path = resp_json.get("path")
    logging.info(f"File downloaded at {file_path}")
    return file_path


def prepare_audio(video_id, start, end, metadata) -> str:
    """Process a sermon audio recording"""

    filename = f"{video_id}.mp3"
    thumbnail = f"{video_id}.podcast.jpg"

    info = get_video_info(video_id)
    if "description" in metadata:
        del metadata["description"]

    metadata.update(
        {
            "publisher": info.get("channel"),
            "date": info.get("publish_date"),
            "language": info.get("language") or "en",
        }
    )
    ffmpeg_args = {
        "start": start,
        "end": end,
        "thumbnail": thumbnail,
        "metadata": metadata,
    }

    logging.info(f"Downloading audio {video_id}")
    downloaded = download_audio(video_id)
    if not downloaded:
        return False

    download_path = Path("/downloads/unprocessed")
    processed_path = Path("/downloads/processed")

    filepath = os.path.join(download_path, Path(downloaded).name)
    if os.path.isfile(filepath):
        logging.info(f"Downloaded audio {video_id}: {filepath}")

    audiofile = os.path.join(processed_path, filename)
    ffmpeg_cmd = create_ffmpeg_cmd(
        input=filepath,
        output=audiofile,
        **ffmpeg_args,
    )
    logging.info(f"Processing audio {filename}: {ffmpeg_cmd} ")
    audio_process = subprocess.Popen(
        ffmpeg_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    ff_logs, ff_error = audio_process.communicate()

    logging.info(f"Processing logs: {ff_logs}")

    if audio_process.returncode:
        logging.error(f"Processing failed: {ff_error}")
        return False

    logging.info(f"Audio {filename} processed: {audiofile} ")
    return audiofile


def prepare_episode(video):
    """Prepares sermon for hosting"""

    info = get_video_info(video.id)

    thumbnails = info.get("thumbnails")
    thumbnail = thumbnails.get("maxres") or thumbnails.get("standard")
    expected_duration = convert_timestring(video.end) - convert_timestring(video.start)
    artwork = prepare_artwork(thumbnail.get("url"), video.id)

    if not artwork:
        logging.error("Error processing artwork")
    else:
        artwork_upload = upload_file(artwork, f"processed/{video.id}/{artwork}")

    audio = prepare_audio(video.id, video.start, video.end, video.metadata or {})
    if not audio:
        logging.error("Error processing audio file")
        update_video(video.id, state="FAILED")
        return

    audio_length = actual_length(audio)
    if not check_length(audio, expected_duration):
        logging.error(
            f"Audio length mismatch: {audio} expected: {expected_duration} got: {audio_length}"
        )
        update_video(video.id, state="FAILED")
        return

    summary = video.metadata.get("description") or generate_summary(audio)

    episode_upload = upload_file(audio, f"processed/{video.id}/{audio}")
    if episode_upload:
        Path(audio).unlink(missing_ok=True)
        Path(artwork).unlink(missing_ok=True)

    if not episode_upload and artwork_upload:
        update_video(video.id, state="FAILED")
        return

    update_req = update_video(
        video.id,
        duration=int(audio_length),
        state="READY",
        description=summary,
    )
    logging.info(f"Episode prepared: {video.id} - {update_req}")

    return update_req
