from django.shortcuts import render
import urllib.parse
from django.http import JsonResponse
from .youtube_utils import give_me_video_id, get_video_links, give_me_the_correct_url_type, get_playlist_url, URL_TYPE_PLAYLIST, URL_TYPE_WATCH_WINDOW
import yt_dlp

YOUTUBE_VIDEO_URL_PREFIX = "https://www.youtube.com/watch?v="


# Handling Single Page
def homeSingle(request):
    if request.method == "POST" and request.POST.get("single_video_input"):
        URL = request.POST.get("single_video_input")
        single_video_id = give_me_video_id(URL)
        if single_video_id is not None:
            video_url = YOUTUBE_VIDEO_URL_PREFIX + single_video_id
            try:
                ydl_opts = {
                    "quiet": True,
                    "no_warnings": True,
                    "format": "best",
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)

                    title = info.get("title", "No Title")
                    video_title_url_encoded = "&title=" + urllib.parse.quote(
                        title, safe=""
                    )

                    # duration is in seconds
                    duration_seconds = info.get("duration", 0)
                    hours, remainder = divmod(duration_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    time = (
                        f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
                        if hours > 0
                        else f"{int(minutes):02}:{int(seconds):02}"
                    )

                    thumbnail = info.get("thumbnail", "")

                    dictionary = {"title": title, "time": time, "thumbnail": thumbnail}
                    all_streams = {}

                    formats = info.get("formats", [])
                    for f in formats:
                        # Extracting 720p and 360p mp4 streams with audio
                        ext = f.get("ext")
                        height = f.get("height")
                        acodec = f.get("acodec")
                        vcodec = f.get("vcodec")

                        if ext == "mp4" and acodec != "none" and vcodec != "none":
                            if height == 720:
                                all_streams["720"] = (
                                    f.get("url") + video_title_url_encoded
                                )
                            elif height == 360:
                                all_streams["360"] = (
                                    f.get("url") + video_title_url_encoded
                                )
                            elif height == 1080:
                                all_streams["1080"] = (
                                    f.get("url") + video_title_url_encoded
                                )

                    # Fallback if specific heights not found
                    if not all_streams:
                        # try to find any mp4 with audio
                        for f in formats:
                            if (
                                f.get("ext") == "mp4"
                                and f.get("acodec") != "none"
                                and f.get("vcodec") != "none"
                            ):
                                res = str(f.get("height"))
                                all_streams[res] = (
                                    f.get("url") + video_title_url_encoded
                                )
                                break

                    dictionary["streams"] = all_streams
                    dictionary["error"] = ""
                    return JsonResponse(dictionary)
            except Exception as e:
                print(f"Error: {e}")
                err = {"error": "Something went wrong"}
                return JsonResponse(err)

        else:
            return render(request, "home/single.html")

    return render(request, "home/single.html")


# Handling Playlist page
def homePlaylist(request):
    # checking METHOD is POST or not and URL entered or not
    if request.method == "POST" and request.POST.get("playlist_link_name"):
        URL = request.POST.get("playlist_link_name")

        # check the user input (url type) and according to url type
        # create final URL
        playlist_url = ""

        url_type = give_me_the_correct_url_type(URL)
        if url_type == URL_TYPE_PLAYLIST or url_type == URL_TYPE_WATCH_WINDOW:
            playlist_url = get_playlist_url(URL)
        else:
            # handling if user entered wrong url
            return render(request, "home/playlist.html")

        # if everything goes right then proceed to get all video link from watch window web page
        allVideoList = get_video_links(playlist_url)

        data = {"allVideoList": allVideoList}
        return JsonResponse(data)

    # return statement for without POST request
    return render(request, "home/playlist.html")


def playlistAjax(request):
    """This function handle GET AJAX Request and return video number, title, thumbnail, download link"""
    if request.method == "GET" and request.GET.get("video_link"):
        video_link = request.GET.get("video_link")
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "format": "best",
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_link, download=False)

                video_title = info.get("title", "No Title")
                video_title_copy = video_title
                video_thumbnail = info.get("thumbnail", "")

                video_quality = request.GET.get("video_quality")
                download_url = ""

                formats = info.get("formats", [])
                target_height = int(video_quality) if video_quality else 360

                # Try to find exactly what user requested
                for f in formats:
                    if (
                        f.get("ext") == "mp4"
                        and f.get("acodec") != "none"
                        and f.get("vcodec") != "none"
                    ):
                        if f.get("height") == target_height:
                            download_url = f.get("url")
                            break

                # Fallback if not found
                if download_url == "" and request.GET.get("reduce") == "true":
                    for f in formats:
                        if (
                            f.get("ext") == "mp4"
                            and f.get("acodec") != "none"
                            and f.get("vcodec") != "none"
                        ):
                            download_url = f.get("url")
                            break

                if request.GET.get("prefix") == "true":
                    video_title = (
                        str(int(request.GET.get("video_no")) + 1) + ". " + video_title
                    )

                video_download_url = (
                    download_url + "&title=" + urllib.parse.quote(video_title, safe="")
                )

                data = {
                    "video_number": int(request.GET.get("video_no")) + 1,
                    "video_title": video_title_copy,
                    "video_thumbnail": video_thumbnail,
                    "video_download_url": video_download_url,
                }
                return JsonResponse(data)
        except Exception as e:
            print(f"Error in playlistAjax: {e}")
            data = {
                "video_number": "-1",
                "video_title": "Private Video or Error",
                "video_thumbnail": "",
                "video_download_url": "",
            }
            return JsonResponse(data)


def homeHowToUse(request):
    return render(request, "home/how-to-use.html")
