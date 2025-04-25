import logging
import os
import shlex
import subprocess
from datetime import timedelta
from io import BytesIO

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


def generate_summary(file_path) -> str:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    audio_file = client.files.upload(file=file_path)
    with open("sermon_summary_prompt.txt") as f:
        PROMPT = f.read()
    logging.info(f"Generating summary: {file_path}")

    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=[PROMPT, audio_file]
    )
    return response.text


def get_video_info(video_id):
    """"""
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
    """"""
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
    """"""
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
    """"""
    cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1"
    check = subprocess.run(shlex.split(cmd) + [file_name], capture_output=True)
    try:
        actual = float(check.stdout.decode().strip())
        return actual
    except ValueError:
        logging.error(f"Error getting length of {file_name}: {check.stderr.decode()}")
        return 0


def check_length(file_name, expected):
    """"""

    actual = actual_length(file_name)
    ERROR_MARGIN = 2
    logging.debug(
        f"Audio length: {actual} expected: {expected} diff: {abs(actual - expected)}"
    )

    return expected - ERROR_MARGIN <= actual <= expected + ERROR_MARGIN


def create_ytdlp_cmd(video_id, output=False):
    """"""
    cmd = [
        "yt-dlp",
        "-f",
        "ba",
        video_id,
        "--quiet",
        "--no-warnings",
    ]
    if output:
        cmd.extend(["--print", "filename", "-o", "%(id)s.%(ext)s"])
    else:
        cmd.extend(["-o", "-"])

    return cmd


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


def prepare_audio(video_id, start, end, metadata) -> str:
    """"""

    filename = f"{video_id}.mp3"
    thumbnail = f"{video_id}.podcast.jpg"

    info = get_video_info(video_id)
    metadata.update(
        {
            # "album",
            # "title": info.get("title"),
            # "artist",
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

    ytdlp_cmd = create_ytdlp_cmd(video_id, output=True)

    logging.info(f"Downloading audio {video_id}: {ytdlp_cmd} ")
    download = subprocess.Popen(
        ytdlp_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1_000_000,
    )
    downloaded, download_err = download.communicate()
    download_code = download.wait()
    logging.info(f"Downloaded audio {video_id}: {downloaded.decode()}")

    if download_code:
        logging.error(f"Error downloading: {download_err.decode()}")
        return False

    ffmpeg_cmd = create_ffmpeg_cmd(
        input=downloaded.decode(), output=filename, **ffmpeg_args
    )
    logging.info(f"Processing audio {filename}: {ffmpeg_cmd} ")
    audio_process = subprocess.Popen(
        ffmpeg_cmd,
        # stdin=download.stdout,
        stderr=subprocess.PIPE,
    )
    _, processing_err = audio_process.communicate()

    audio_process.wait()

    if audio_process.returncode:
        logging.error(f"Error processing: {processing_err.decode()}")
        return False

    logging.info("Audio processed", filename)
    return filename


def prepare_episode(video_id: str, start, end, metadata=None):
    """"""

    info = get_video_info(video_id)

    thumbnails = info.get("thumbnails")
    thumbnail = thumbnails.get("maxres") or thumbnails.get("standard")
    expected_duration = convert_timestring(end) - convert_timestring(start)
    artwork = prepare_artwork(thumbnail.get("url"), video_id)
    audio = prepare_audio(video_id, start, end, metadata or {})

    if not artwork:
        logging.error("Error processing artwork")
        return False

    if not audio:
        logging.error("Error processing audio file")
        update_video(
            video_id,
            state="FAILED",
        )
        return

    if not check_length(audio, expected_duration):
        logging.error(
            f"Audio length mismatch: {audio} expected: {expected_duration} got: {actual_length(audio)}"
        )
        update_video(
            video_id,
            state="FAILED",
        )
        return

    summary = generate_summary(audio)
    upload_file(artwork, f"processed/{video_id}/{artwork}")
    upload_file(audio, f"processed/{video_id}/{audio}")
    update_video(
        video_id,
        duration=expected_duration,
        state="READY",
        description=summary,
    )

    logging.info(f"Episode prepared: {video_id}")

    return True


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
    """"""
    API_ENDPOINT = "https://scrib-api.childrick.workers.dev/videos"

    r = requests.patch(f"{API_ENDPOINT}/{video_id}", json=kwargs)
    resp = r.json()
    if r.status_code != 200:
        logging.error(f"Error updating video {video_id}: {resp}")
        return False
