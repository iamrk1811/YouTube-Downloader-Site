from django.shortcuts import render
from django.http import JsonResponse
from . import youtube_utils


def home_single(request):
    """Handles requests for single video information."""
    if request.method == "POST" and request.POST.get("single_video_input"):
        url = request.POST.get("single_video_input")
        video_id = youtube_utils.extract_video_id(url)

        if video_id:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            info = youtube_utils.get_video_info(video_url)
            if info:
                return JsonResponse(info)
            return JsonResponse({"error": "Failed to extract video information"})

        return render(request, "home/single.html")

    return render(request, "home/single.html")


def home_playlist(request):
    """Handles requests for playlist information."""
    if request.method == "POST" and request.POST.get("playlist_link_name"):
        url = request.POST.get("playlist_link_name")
        quality = request.POST.get("video_quality", "360")
        prefix = request.POST.get("prefix") == "true"
        reduce = request.POST.get("reduce") == "true"

        url_type = youtube_utils.detect_url_type(url)
        if url_type in [
            youtube_utils.URL_TYPE_PLAYLIST,
            youtube_utils.URL_TYPE_WATCH_WINDOW,
        ]:
            # Use the optimized full info extraction
            video_data = youtube_utils.get_playlist_full_info(
                url, quality=quality, prefix=prefix, reduce=reduce
            )
            if video_data:
                return JsonResponse({"allVideoData": video_data})
            return JsonResponse(
                {
                    "error": "Failed to extract playlist information or playlist is empty."
                }
            )

        return JsonResponse({"error": "Invalid YouTube Playlist URL."})

    return render(request, "home/playlist.html")


def home_how_to_use(request):
    """Renders the how-to-use page."""
    return render(request, "home/how-to-use.html")
