from django.shortcuts import render
import urllib.parse
from django.http import JsonResponse
from .utils import *
from .pafy_utils import *
import re
from .utils import API_KEY
import pafy

pafy.set_api_key(API_KEY)


# Code for single START
def giveMeVideoID(URL):
    # check point for mobile
    regex_for_mobile = r"https://www.youtu.be/[0-9a-zA-Z-_]{11}"
    regex_for_mobile_without_www = r"https://youtu.be/[0-9a-zA-Z-_]{11}"
    regex_for_computer = r"https://www.youtube.com/watch\?v=[0-9a-zA-Z-_]{11}"
    regex_for_computer_without_www = r"https://youtube.com/watch\?v=[0-9a-zA-Z-_]{11}"


    matches_for_mobile = re.finditer(regex_for_mobile, URL, re.MULTILINE)
    matches_for_mobile_without_www = re.finditer(regex_for_mobile_without_www, URL, re.MULTILINE)
    matches_for_computer = re.finditer(regex_for_computer, URL, re.MULTILINE)
    matches_for_computer_without_www = re.finditer(regex_for_computer_without_www, URL, re.MULTILINE)

    # for loop to get video id from mobile link
    for matchNum, match in enumerate(matches_for_mobile, start=1):
        if matchNum == 1:
            total_match = match.group()
            video_id = total_match.replace("https://www.youtu.be/", "")
            return video_id

    # for loop to get video id from mobile link without www
    for matchNum, match in enumerate(matches_for_mobile_without_www, start=1):
        if matchNum == 1:
            total_match = match.group()
            video_id = total_match.replace("https://youtu.be/", "")
            return video_id
    # for loop to get video id from computer link
    for matchNum, match in enumerate(matches_for_computer, start=1):
        if matchNum == 1:
            total_match = match.group()
            video_id = total_match.replace("https://www.youtube.com/watch?v=", "")
            return video_id
    # for loop to get video from computer link without www
    for matchNum, match in enumerate(matches_for_computer_without_www, start=1):
        if matchNum == 1:
            total_match = match.group()
            video_id = total_match.replace("https://youtube.com/watch?v=", "")
            return video_id


# Code for single END

# Handling Single Page
def homeSingle(request):
    if request.method == 'POST' and request.POST.get('single_video_input'):
        URL = request.POST.get('single_video_input')
        single_video_id = giveMeVideoID(URL)
        if single_video_id is not None:
            video = None
            try:
                video = pafy.new("https://www.youtube.com/watch?v=" + single_video_id)
            except Exception as e:
                err = {
                    "error" : "Something went wrong"
                }
                return JsonResponse(err)

            video_title_url_encoded = "&title=" + urllib.parse.quote(video.title, safe="")

            time = video.duration
            thumbnail = video.thumb
            thumbnail = thumbnail.replace("default", "hqdefault")

            dictionary = {'title': video.title, 'time': time, 'thumbnail': thumbnail}

            all_streams = {}

            for s in video.streams:
                if "720" in s.resolution:
                    all_streams["720"] = s.url + video_title_url_encoded
                if "360" in s.resolution:
                    all_streams["360"] = s.url + video_title_url_encoded

            dictionary['streams'] = all_streams
            dictionary['error'] = ""

            return JsonResponse(dictionary)

        else:
            return render(request, 'home/single.html')
            
    return render(request, 'home/single.html')


# Handling Playlist page
def homePlaylist(request):
    # checking METHOD is POST or not and URL entered or not
    if request.method == 'POST' and request.POST.get('playlist_link_name'):
        URL = request.POST.get('playlist_link_name')

        # check the user input (url type) and according to url type
        # create final URL
        playlist_url = ""

        url_type = giveMeTheCorrectURL(URL)
        print("WORKING")
        if url_type == 'yup this is playlist':
            playlist_url = getPlaylistUrl(URL)
        elif url_type == 'yup this is watch window':
            playlist_url = getPlaylistUrl(URL)
        else:
            # handling if user entered wrong url
            return render(request, 'home/playlist.html')

        # if everything goes right then proceed to get all video link from watch window web page
        allVideoList = getVideoLinks(playlist_url)

        data = {'allVideoList' : allVideoList}
        return JsonResponse(data)

    # return statement for without POST request
    return render(request, 'home/playlist.html')


def playlistAjax(request):
    """This function handle GET AJAX Request and return video number, title, thumbnail, download link"""
    if request.method == 'GET' and request.GET.get('video_link'):
        video_link = request.GET.get('video_link')
        # creating Youtube object using pafy
        video = None
        try:
            video = pafy.new(video_link)
        except Exception as e:
            data = {
                'video_number' : "-1",
                'video_title' : 'Private Video',
                'video_thumbnail' : "",
                'video_download_url' : ""
            }
            return JsonResponse(data)


        video_title = video.title

        # making copy of the title because i don't want to prefix the real title with video no
        video_title_copy = video_title
        # getting video thumbnail
        video_thumbnail = video.thumb

        # getting video download url
        video_link = ""

        video_quality = request.GET.get('video_quality')

        # contains all available streams of a video
        streams = video.streams
        # handling every resolution
        if video_quality == '720':
            for s in streams:
                if "720" in s.resolution:
                    video_link = s.url
            if video_link == "" and request.GET.get("reduce") == 'true':
                for s in streams:
                    video_link = s.url
                    break
        elif video_quality == '360':
            for s in streams:
                if "360" in s.resolution:
                    video_link = s.url
            if video_link == "" and request.GET.get("reduce") == 'true':
                for s in streams:
                    video_link = s.url
                    break
                
        # title prefix if option selected
        if request.GET.get('prefix') == 'true':
            video_title = str(int(request.GET.get('video_no')) + 1) + ". " + video_title
        video_download_url = video_link + "&title=" + urllib.parse.quote(video_title, safe="")

        data = {
            'video_number' : int(request.GET.get('video_no')) + 1,
            'video_title' : video_title_copy,
            'video_thumbnail' : video_thumbnail,
            'video_download_url' : video_download_url
        }
        return JsonResponse(data)


def homeHowToUse(request):
    return render(request, 'home/how-to-use.html')
