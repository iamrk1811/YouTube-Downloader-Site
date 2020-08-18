from django.shortcuts import render
from pytube import YouTube
from bs4 import BeautifulSoup
import requests
import re
import urllib.parse
from django.http import JsonResponse


# Code for playlist START
def giveMeTheCorrectURL(url_to_be_checked):
    """checking the input url to see either it is playlist link or watch window link
        , if it is a playlist link this function will return watch window link"""

    # regex for match playlist and watch window link
    regex_for_playlist = r"https:\/\/www.youtube.com\/playlist\?list=[a-zA-Z0-9_-]{34}"
    regex_for_playlist_without_www = r"https:\/\/youtube.com\/playlist\?list=[a-zA-Z0-9_-]{34}"
    regex_for_watch_window = r"https:\/\/www.youtube.com\/watch\?v=[0-9A-Za-z-_]+&list=[a-zA-Z0-9_-]{34}"
    regex_for_watch_window_without_www = r"https:\/\/youtube.com\/watch\?v=[0-9A-Za-z-_]+&list=[a-zA-Z0-9_-]{34}"

    test_str = url_to_be_checked

    # Checking for playlist link
    matches_for_playlist = re.finditer(regex_for_playlist, test_str, re.MULTILINE)
    for matchNum, match in enumerate(matches_for_playlist, start=1):
        if matchNum:
            result = "yup this is playlist"
            return result
    # Checking for playlist link without www
    matches_for_playlist_without_www = re.finditer(regex_for_playlist_without_www, test_str, re.MULTILINE)
    for matchNum, match in enumerate(matches_for_playlist_without_www, start=1):
        if matchNum:
            result = "yup this is playlist"
            return result

    # Checking for watch window
    matches_for_watch_window = re.finditer(regex_for_watch_window, test_str, re.MULTILINE)
    for matchNum, match in enumerate(matches_for_watch_window, start=1):
        if matchNum:
            result = "yup this is watch window"
            return result
    # Checking for watch window without www
    matches_for_watch_window_without_www = re.finditer(regex_for_watch_window_without_www, test_str, re.MULTILINE)
    for matchNum, match in enumerate(matches_for_watch_window_without_www, start=1):
        if matchNum:
            result = "yup this is watch window"
            return result

    return "not match found"


def firstVideoLinkFromPlaylist(url):
    """this function will return the first video link with playlist id from playlist web page"""
    playlist_id = url.replace("https://www.youtube.com/playlist?list=", "")
    r = requests.get(url)
    # soup = BeautifulSoup(r.content, 'html.parser')
    
    regex = r"{\"url\":\"/watch\?v=[a-zA-Z0-9_-]{11}"
    
    page_content = r.content.decode('utf-8')

    matches = re.finditer(regex, page_content, re.MULTILINE)

    url = "https://www.youtube.com"

    for matchNum, match in enumerate(matches, start=1):
                if matchNum == 1:
                    url += match.group().replace('''{"url":"''', "")
                    url += "&list=" + playlist_id
                    return url


def giveMeAllVideoList(url):
    """this function will return first video link with playlist id from watch window"""
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    regex = r"/watch\?v=[a-zA-Z0-9-_]{11}\\u0026list=[a-zA-Z0-9-_]{34}\\u0026index=[0-9]+"

    response_script = str(soup.findAll('script')[32])

    matches = re.finditer(regex, response_script, re.MULTILINE)

    videos_list = []
    for matchNum, match in enumerate(matches, start=1):
        videos_list.append(match.group())

    videos_set = set(videos_list)
    
    videos_dict = {}
    for video in videos_set:
        try:
            print(int(str(re.findall(r"index=[0-9]+", video)).replace("index=", "")), 10)
        except Exception as e:
            pass
        videos_dict[str(re.findall(r"index=[0-9]+", video)).replace("index=", "")] = "https://www.youtube.com" + str(re.match(r"/watch\?v=[a-zA-Z0-9-_]{11}", video))

    

    print(videos_dict)

    all_video_list = []
    values = videos_dict.values()
    all_video_list = list(values)

    # for key, video in videos_dict.items():
    #     # all_video_list.append("https://www.youtube.com" + str(re.match(r"/watch\?v=[a-zA-Z0-9-_]{11}", video)))
    #     all_video_list.append(video)
    # print(all_video_list)

    return all_video_list


# Code for playlist END

# Code for single START
def giveMeVideoID(URL):
    # check point for mobile
    regex_for_mobile = r"https://youtu.be/[0-9a-zA-Z-_]{11}"
    regex_for_computer = r"https://www.youtube.com/watch\?v=[0-9a-zA-Z-_]{11}"
    regex_for_computer_without_www = r"https://youtube.com/watch\?v=[0-9a-zA-Z-_]{11}"

    matches_for_mobile = re.finditer(regex_for_mobile, URL, re.MULTILINE)
    matches_for_computer = re.finditer(regex_for_computer, URL, re.MULTILINE)
    matches_for_computer_without_www = re.finditer(regex_for_computer_without_www, URL, re.MULTILINE)

    # for loop to get video id from mobile link
    for matchNum, match in enumerate(matches_for_mobile, start=1):
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
    # for loop to get video from computer link with out www
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
            yt = YouTube("https://www.youtube.com/watch?v=" + single_video_id)
            video_title_url_encoded = "&title=" + urllib.parse.quote(yt.title, safe="")

            seconds = yt.length
            seconds = seconds % (24 * 3600)
            hour = seconds // 3600
            seconds %= 3600
            minutes = seconds // 60
            seconds %= 60
            time = ""
            if not hour == 0:
                time += str(hour) + ":"
            if not minutes == 0:
                time += str(minutes) + ":"
            time += str(seconds)

            dictionary = {'title': yt.title, 'time': time, 'thumbnail': yt.thumbnail_url}
            streams = {}
            if not yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution('720p') is None:
                streams['720p'] = yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution(
                    '720p').url + video_title_url_encoded
            if not yt.streams.get_by_itag(135) is None:
                # you can not get the video url using get_by_resolution() for 480, 240, 144
                # you can get only video not audio by using get_by_itag()
                streams['480p No Audio'] = yt.streams.get_by_itag(135).url + video_title_url_encoded
            if not yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution('360p') is None:
                streams['360p'] = yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution(
                    '360p').url + video_title_url_encoded
            if not yt.streams.get_by_itag(133) is None:
                streams['240p No Audio'] = yt.streams.get_by_itag(133).url + video_title_url_encoded
            if not yt.streams.get_by_itag(160) is None:
                streams['144p No Audio'] = yt.streams.get_by_itag(160).url + video_title_url_encoded
            if not yt.streams.get_by_itag(140) is None:
                streams['Audio 128kb'] = yt.streams.get_by_itag(140).url + video_title_url_encoded

            dictionary['streams'] = streams

            # return render(request, 'home/single.html', dictionary)
            return JsonResponse(dictionary)

        else:
            return render(request, 'home/single.html')
    return render(request, 'home/single.html')


# Handling Playlist page
def homePlaylist(request):
    # checking METHOD is POST or not and URL entered or not
    if request.method == 'POST' and request.POST.get('playlist_link_name'):
        URL = request.POST.get('playlist_link_name')

        # ultimate goal is to get watch window link because we are going to scrape data from watch window
        watch_window_link = ""

        # find out which link user entered real playlist link or watch window link
        if giveMeTheCorrectURL(URL) == 'yup this is playlist':
            watch_window_link = firstVideoLinkFromPlaylist(URL)
        elif giveMeTheCorrectURL(URL) == 'yup this is watch window':
            watch_window_link = URL
        else:
            # handling if user entered wrong url
            return render(request, 'home/playlist.html')

        # if everything goes right then proceed to get all video link from watch window web page
        allVideoList = giveMeAllVideoList(watch_window_link)
        data = {'allVideoList' : allVideoList}
        return JsonResponse(data)

    # return statement for without POST request
    return render(request, 'home/playlist.html')


def playlistAjax(request):
    """This function handle GET AJAX Request and return video number, title, thumbnail, download link"""
    if request.method == 'GET' and request.GET.get('video_link'):
        video_link = request.GET.get('video_link')
        # creating Youtube object using pytube.YouTube
        yt = YouTube(video_link)
        video_title = yt.title
        # making copy of the title because i don't want to prefix the real title with video no
        video_title_copy = video_title
        # getting video thumbnail
        video_thumbnail = yt.thumbnail_url

        # getting video download url
        video_link = ""

        video_quality = request.GET.get('video_quality')

        # handling every resolution
        if video_quality == '720':
            try:
                # execute this code if 720p is selected and if 720 isn't available then go to catch
                # i am handling download link here because user can uncheck reduce quality if not exist
                # in this case output will be blank in text area but title thumbnail will be available but video will be not downloadable
                video_link = yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution('720p').url
            except Exception as e:
                if request.GET.get("reduce") == 'true':
                    video_link = yt.streams.filter(progressive=True, file_extension='mp4').first().url
                else:
                    video_link = ""
        elif video_quality == '480':
            try:
                video_link = yt.streams.get_by_itag(135).url
            except Exception as e:
                if request.GET.get("reduce") == 'true':
                    video_link = yt.streams.filter(progressive=True, file_extension='mp4').first().url
                else:
                    video_link = ""
        elif video_quality == '360':
            try:
                video_link = yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution('360p').url
            except Exception as e:
                if request.GET.get("reduce") == 'true':
                    video_link = yt.streams.filter(progressive=True, file_extension='mp4').first().url
                else:
                    video_link = ""
        elif video_quality == '240':
            try:
                video_link = yt.streams.get_by_itag(133).url
            except Exception as e:
                if request.GET.get("reduce") == 'true':
                    video_link = yt.streams.filter(progressive=True, file_extension='mp4').first().url
                else:
                    video_link = ""
        elif video_quality == '144':
            try:
                video_link = yt.streams.get_by_itag(160).url
            except Exception as e:
                if request.GET.get("reduce") == 'true':
                    video_link = yt.streams.filter(progressive=True, file_extension='mp4').first().url
                else:
                    video_link = ""
        elif video_quality == '128':
            try:
                video_link = yt.streams.get_by_itag(140).url
            except Exception as e:
                video_link = ""

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