import concurrent.futures
import csv
import os
from datetime import datetime
from typing import Callable

import requests
from dotenv import load_dotenv

load_dotenv()


def make_request(sess, endpoint, req_params):
    resp = sess.get(endpoint, params=req_params)
    try:
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"!!Something went wrong fetching {endpoint}!!", e)
        return None


class YouTube:
    """"""

    _session: requests.Session = None
    _base_params = {
        "maxResults": 50,
        "key": os.getenv("YT_API_KEY"),
    }

    def __init__(self):
        if self._session is None:
            sess = requests.Session()
            sess.params = self._base_params
            type(self)._session = sess

    def get(self, resource, id):
        """Fetch Youtube resource"""
        match resource:
            case "uploads":
                params = {"playlistId": id, "part": ["snippet", "contentDetails"]}
                return self._fetch_youtube_data("playlistItems", params, process_upload)
            case "video":
                params = {"id": id, "part": ["snippet", "liveStreamingDetails"]}
                return self._fetch_youtube_data("videos", params, process_video)
            case "playlists":
                params = {"channelId": id, "part": ["id", "snippet", "contentDetails"]}
                return self._fetch_youtube_data("playlists", params, process_playlist)
            case "playlist_videos":
                params = {"playlistId": id, "part": ["snippet", "contentDetails"]}
                return self._fetch_youtube_data(
                    "playlistItems", params, process_playlist_video
                )
            case _:
                raise ValueError(
                    "Invalid resourcse type. Must be one of: 'video', 'playlists', 'playlist_videos'"
                )

    def _fetch_youtube_data(
        self, endpoint: str, params: dict, processor: Callable
    ) -> list:
        """Query Youtube Data API

        Args:
            endpoint (str): endpoint to query - channel, videos, playlistItem, playlist
            params (dict): request specific params to pass to the api - id, part
            processor (Callable): function to apply to response to select specific fields

        Returns:
            list: processed results
        """

        API = "https://youtube.googleapis.com/youtube/v3/"

        results = []
        next_page = True

        while next_page:
            resp = make_request(self._session, f"{API}{endpoint}", req_params=params)
            if not resp:
                next_page = False
            results.extend([processor(item) for item in resp.get("items")])
            next_page = resp.get("nextPageToken")
            params.update({"pageToken": next_page})
        return results


def process_video(item):
    snippet = item.get("snippet")
    livestream = item.get("liveStreamingDetails")

    if livestream:
        publish_date = livestream.get("actualStartTime") or livestream.get(
            "scheduledStartTime"
        )
    else:
        publish_date = snippet["publishedAt"]

    return {
        "title": snippet["title"],
        "publish_date": datetime.fromisoformat(publish_date),
        "description": snippet.get("description"),
        "channel": snippet.get("channelTitle"),
        "thumbnails": snippet.get("thumbnails"),
    }


def process_playlist(item):
    snippet = item.get("snippet")
    return {
        "id": item.get("id"),
        "title": snippet["title"],
        "description": snippet.get("description"),
        "publish_date": datetime.fromisoformat(snippet["publishedAt"]),
        "thumbnails": snippet.get("thumbnails"),
        "video_count": item.get("contentDetails").get("itemCount"),
    }


def process_playlist_video(item):
    snippet = item.get("snippet")
    details = item.get("contentDetails")
    data = {
        "id": details.get("videoId"),
        "playlist": snippet.get("playlistId"),
        "title": snippet.get("title"),
        "added_on": datetime.fromisoformat(snippet.get("publishedAt")),
        "position": snippet.get("position"),
    }
    return data


def process_upload(item):
    snippet = item.get("snippet")
    details = item.get("contentDetails")
    return {
        "id": details.get("videoId"),
        "title": snippet.get("title"),
        "published_on": datetime.fromisoformat(details.get("videoPublishedAt")),
        "thumbnails": snippet.get("thumbnails"),
        "description": snippet.get("description"),
    }


def process_search_item(item):
    snippet = item.get("snippet")
    data = {
        "title": snippet["title"],
        "publish_date": datetime.fromisoformat(snippet["publishedAt"]),
    }

    item_type = item.get("id").get("kind").split("#")[1]
    if item_type == "video":
        data["id"] = item.get("id").get("videoId")
    elif item_type == "playlist":
        data["id"] = item.get("id").get("playlistId")
    else:
        print("skipped:", item)
    return data
