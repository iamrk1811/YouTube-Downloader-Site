import re
import urllib.parse
from django.conf import settings
from googleapiclient.discovery import build
import yt_dlp

# YouTube API client initialization
youtube = build("youtube", "v3", developerKey=settings.API_KEY)

# URL Type Constants
URL_TYPE_NONE = 0
URL_TYPE_PLAYLIST = 1
URL_TYPE_WATCH_WINDOW = 2

# Regex Patterns
YOUTUBE_VIDEO_ID_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})"
)
YOUTUBE_PLAYLIST_ID_REGEX = re.compile(r"list=([a-zA-Z0-9_-]+)")


def extract_video_id(url: str) -> str | None:
    """Extracts the YouTube video ID from a given URL."""
    match = YOUTUBE_VIDEO_ID_REGEX.search(url)
    return match.group(1) if match else None


def extract_playlist_id(url: str) -> str | None:
    """Extracts the YouTube playlist ID from a given URL."""
    match = YOUTUBE_PLAYLIST_ID_REGEX.search(url)
    return match.group(1) if match else None


def format_duration(seconds: int) -> str:
    """Formats duration in seconds to HH:MM:SS or MM:SS."""
    if not seconds:
        return "00:00"
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    return f"{int(minutes):02}:{int(seconds):02}"


def detect_url_type(url: str) -> int:
    """Detects whether the URL is a playlist, watch window with playlist, or a single video."""
    if "/playlist?list=" in url:
        return URL_TYPE_PLAYLIST
    if "list=" in url and "v=" in url:
        return URL_TYPE_WATCH_WINDOW
    return URL_TYPE_NONE


def get_video_info(video_url: str) -> dict | None:
    """
    Fetches video information using yt-dlp.
    Returns a dictionary with title, time, thumbnail, and stream URLs.
    """
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "best",
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info.get("title", "No Title")
            video_title_encoded = "&title=" + urllib.parse.quote(title, safe="")

            streams = {}
            for f in info.get("formats", []):
                # We want mp4 with both audio and video
                if (
                    f.get("ext") == "mp4"
                    and f.get("acodec") != "none"
                    and f.get("vcodec") != "none"
                ):
                    height = f.get("height")
                    if height in [360, 720, 1080]:
                        streams[str(height)] = f.get("url") + video_title_encoded

            # Fallback if preferred resolutions not found
            if not streams:
                for f in info.get("formats", []):
                    if (
                        f.get("ext") == "mp4"
                        and f.get("acodec") != "none"
                        and f.get("vcodec") != "none"
                    ):
                        streams[str(f.get("height"))] = (
                            f.get("url") + video_title_encoded
                        )
                        break

            return {
                "title": title,
                "time": format_duration(info.get("duration", 0)),
                "thumbnail": info.get("thumbnail", ""),
                "streams": streams,
                "error": "",
            }
    except Exception as e:
        print(f"Extraction Error: {e}")
        return None


def get_playlist_video_links(playlist_url: str) -> list[str]:
    """Retrieves all video URLs from a playlist using YouTube API."""
    playlist_id = extract_playlist_id(playlist_url)
    if not playlist_id:
        return []

    video_links = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token,
        )
        response = request.execute()

        for item in response.get("items", []):
            video_id = item["contentDetails"]["videoId"]
            video_links.append(f"https://www.youtube.com/watch?v={video_id}")

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return video_links


def get_playlist_item_download_info(
    video_url: str,
    video_no: int,
    quality: str = "360",
    prefix: bool = False,
    reduce: bool = False,
) -> dict:
    """Fetches download info for a single video in a playlist context."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "best",
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info.get("title", "No Title")
            display_title = f"{video_no + 1}. {title}" if prefix else title
            title_encoded = "&title=" + urllib.parse.quote(display_title, safe="")

            download_url = ""
            target_height = int(quality) if quality.isdigit() else 360

            formats = info.get("formats", [])
            for f in formats:
                if (
                    f.get("ext") == "mp4"
                    and f.get("acodec") != "none"
                    and f.get("vcodec") != "none"
                ):
                    if f.get("height") == target_height:
                        download_url = f.get("url")
                        break

            # Fallback
            if not download_url and reduce:
                for f in formats:
                    if (
                        f.get("ext") == "mp4"
                        and f.get("acodec") != "none"
                        and f.get("vcodec") != "none"
                    ):
                        download_url = f.get("url")
                        break

            return {
                "video_number": video_no + 1,
                "video_title": title,
                "video_thumbnail": info.get("thumbnail", ""),
                "video_download_url": (download_url + title_encoded)
                if download_url
                else "",
            }
    except Exception as e:
        print(f"Playlist Item Error: {e}")
        return {
            "video_number": "-1",
            "video_title": "Video Unavailable",
            "video_thumbnail": "",
            "video_download_url": "",
        }


import concurrent.futures


def get_playlist_full_info(
    playlist_url: str,
    quality: str = "360",
    prefix: bool = False,
    reduce: bool = False,
) -> list[dict]:
    """
    Fetches full information for all videos in a playlist using multi-threading.
    """
    playlist_id = extract_playlist_id(playlist_url)
    if not playlist_id:
        return []

    normalized_url = f"https://www.youtube.com/playlist?list={playlist_id}"

    # Step 1: Extract flat info to get all video headers quickly
    ydl_opts_flat = {
        "quiet": True,
        "extract_flat": True,
        "noplaylist": False,
    }

    entries = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts_flat) as ydl:
            info = ydl.extract_info(normalized_url, download=False)
            entries = info.get("entries", [])
    except Exception as e:
        print(f"Flat Extraction Error: {e}")
        return []

    if not entries:
        return []

    target_height = int(quality) if quality.isdigit() else 360

    def resolve_video_info(index, entry):
        if not entry:
            return None

        video_id = entry.get("id")
        if not video_id:
            return None

        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Aggressively optimized options
        ydl_opts_single = {
            "quiet": True,
            "no_warnings": True,
            "format": f"bestvideo[height<={target_height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={target_height}][ext=mp4]/best",
            "skip_download": True,
            "ignoreerrors": True,
            "no_check_certificate": True,
            "extractor_args": {"youtube": {"skip": ["dash", "hls", "translated_subs"]}},
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts_single) as ydl:
                # We only need the URL and minimal info
                info = ydl.extract_info(video_url, download=False, process=True)
                if not info:
                    return None

                title = info.get("title", entry.get("title", "No Title"))
                display_title = f"{index + 1}. {title}" if prefix else title
                title_encoded = "&title=" + urllib.parse.quote(display_title, safe="")

                download_url = info.get("url", "")

                # If the chosen format doesn't have a URL, fallback
                if not download_url:
                    formats = info.get("formats", [])
                    for f in formats:
                        if (
                            f.get("ext") == "mp4"
                            and f.get("acodec") != "none"
                            and f.get("vcodec") != "none"
                        ):
                            if f.get("height") <= target_height:
                                download_url = f.get("url")
                                break

                return {
                    "video_number": index + 1,
                    "video_title": title,
                    "video_thumbnail": info.get(
                        "thumbnail", entry.get("thumbnail", "")
                    ),
                    "video_download_url": (download_url + title_encoded)
                    if download_url
                    else "",
                }
        except Exception as e:
            print(f"Error resolving video {index + 1}: {e}")
            return {
                "video_number": index + 1,
                "video_title": entry.get("title", "Unavailable"),
                "video_thumbnail": entry.get("thumbnail", ""),
                "video_download_url": "",
            }

    # Step 2: Resolve download links in parallel (increase workers to 20)
    results = [None] * len(entries)
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_index = {
            executor.submit(resolve_video_info, i, entry): i
            for i, entry in enumerate(entries)
        }
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                results[index] = future.result()
            except Exception as e:
                print(f"Future {index} raised exception: {e}")

    return [r for r in results if r is not None]
