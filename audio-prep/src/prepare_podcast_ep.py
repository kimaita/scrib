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


def generate_summary(file_path) -> str:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    audio_file = client.files.upload(file=file_path)
    with open("sermon_summary_prompt.txt") as f:
        PROMPT = f.read()
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

    try:
        artwork = resize(thumbnail)
        artwork.save(filename)
        return filename
    except Exception as e:
        logging.error(e)
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


def check_length(file_name, expected):
    """"""
    cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1"
    ERROR_MARGIN = 2

    check = subprocess.run(shlex.split(cmd) + [file_name], capture_output=True)
    actual = float(check.stdout.decode().strip())

    return expected - ERROR_MARGIN <= actual <= expected + ERROR_MARGIN


def create_ytdlp_cmd(video_id, output=None):
    """"""
    return [
        "yt-dlp",
        "-f",
        "ba",
        video_id,
        "--quiet",
        "--no-warnings",
        "--output",
        output or "-",
    ]


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


def prepare_audio(video_id, start, end, metadata={}) -> str:
    """"""

    filename = f"{video_id}.mp3"
    thumbnail = f"{video_id}.podcast.jpg"

    download_err = open("download.err.txt", "a")
    ffmpeg_err = open("ffmpeg.err.txt", "a")

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

    ytdlp_cmd = create_ytdlp_cmd(video_id)
    ffmpeg_cmd = create_ffmpeg_cmd(output=filename, **ffmpeg_args)

    print("Processing audio...", filename)
    download = subprocess.Popen(
        ytdlp_cmd,
        stdout=subprocess.PIPE,
        stderr=download_err,
        bufsize=1_000_000,
    )
    audio_process = subprocess.Popen(
        ffmpeg_cmd,
        stdin=download.stdout,
        stderr=ffmpeg_err,
    )
    _, err = audio_process.communicate()

    if err or audio_process.returncode:
        print(f"Error processing: {err}")
        return False

    return filename


def prepare_episode(video_id: str, start, end):
    """"""

    info = get_video_info(video_id)

    thumbnails = info.get("thumbnails")
    thumbnail = thumbnails.get("maxres") or thumbnails.get("standard")
    artwork = prepare_artwork(thumbnail.get("url"), video_id)
    audio = prepare_audio(video_id, start, end)
    summary = generate_summary(audio)
    expected_duration = convert_timestring(end) - convert_timestring(start)

    if not artwork:
        print("Error processing artwork")
        return False

    if not (audio and check_length(audio, expected_duration)):
        print("Error processing audio file")
        update_video(
            video_id,
            state="FAILED",
        )
        return False

    upload_file(artwork, f"processed/{video_id}/{artwork}")
    upload_file(audio, f"processed/{video_id}/{audio}")
    update_video(
        video_id,
        duration=expected_duration,
        state="READY",
        description=summary,
    )

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
