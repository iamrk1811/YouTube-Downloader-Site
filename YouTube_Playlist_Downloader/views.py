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

        url_type = youtube_utils.detect_url_type(url)
        if url_type in [
            youtube_utils.URL_TYPE_PLAYLIST,
            youtube_utils.URL_TYPE_WATCH_WINDOW,
        ]:
            video_links = youtube_utils.get_playlist_video_links(url)
            if video_links:
                return JsonResponse({"allVideoList": video_links})

        return render(request, "home/playlist.html")

    return render(request, "home/playlist.html")


def playlist_ajax(request):
    """Handles AJAX requests for individual video details within a playlist."""
    if request.method == "GET" and request.GET.get("video_link"):
        video_link = request.GET.get("video_link")
        video_no = int(request.GET.get("video_no", 0))
        quality = request.GET.get("video_quality", "360")
        prefix = request.GET.get("prefix") == "true"
        reduce = request.GET.get("reduce") == "true"

        data = youtube_utils.get_playlist_item_download_info(
            video_link, video_no, quality=quality, prefix=prefix, reduce=reduce
        )
        return JsonResponse(data)

    return JsonResponse({"error": "Invalid request"}, status=400)


def home_how_to_use(request):
    """Renders the how-to-use page."""
    return render(request, "home/how-to-use.html")
