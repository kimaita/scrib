import logging
from pathlib import PosixPath

from yt_dlp import YoutubeDL


def download_audio(video_id: str) -> str:
    """Downloads an audio file from YouTube
    :param video_id
    """
    downloaded = check_downloaded(video_id)
    if downloaded:
        logging.info(f"Audio {video_id} already downloaded")
        return downloaded

    ydl_opts = {
        "format": "bestaudio",
        "paths": {
            "home": str(PosixPath("~/downloads")),
            "temp": str(PosixPath("/tmp/audiostore")),
        },
        "outtmpl": "%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "forceprint": "filename",
    }
    with YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(video_id)

    if error_code:
        logging.error(f"Error downloading {video_id}: {error_code}")
        return False

    return check_downloaded(video_id)


def check_downloaded(video_id: str) -> bool | str:
    """Checks if an audio file was already downloaded"""
    downloads = PosixPath("~/downloads").expanduser()
    rel_path = sorted(downloads.glob(f"{video_id}.*"))
    if rel_path:
        return rel_path[0]

    return False
