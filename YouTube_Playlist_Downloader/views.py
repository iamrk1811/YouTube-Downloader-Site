from django.shortcuts import render
from pytube import YouTube
from bs4 import BeautifulSoup
import requests
import re
import urllib.parse
from django.http import JsonResponse
import time


# Code for playlist START
def giveMeTheCorrectURL(url_to_be_checked):
    """checking the input url to see either it is playlist link or watch window link
        , if it is a playlist link this function will return watch window link"""

    # regex for match playlist and watch window link
    regex_for_playlist = r"https:\/\/www.youtube.com\/playlist\?list=[a-zA-Z0-9_-]{34}"
    regex_for_watch_window = r"https:\/\/www.youtube.com\/watch\?v=[0-9A-Za-z-_]+&list=[a-zA-Z0-9_-]{34}"

    test_str = url_to_be_checked

    # Checking for playlist link
    matches_for_playlist = re.finditer(regex_for_playlist, test_str, re.MULTILINE)
    for matchNum, match in enumerate(matches_for_playlist, start=1):
        if matchNum:
            result = "yup this is playlist"
            return result

    # Checking for watch window
    matches_for_watch_window = re.finditer(regex_for_watch_window, test_str, re.MULTILINE)
    for matchNum, match in enumerate(matches_for_watch_window, start=1):
        if matchNum:
            result = "yup this is watch window"
            return result

    return "not match found"


def firstVideoLinkFromPlaylist(URL):
    """this function will return the first video link with playlist id from playlist web page"""
    playlist_id = URL.replace("https://www.youtube.com/playlist?list=", "")
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html5lib')
    data = soup.prettify()

    # regex for find out first video
    regex = r"<tr class=\"pl-video yt-uix-tile\" data-set-video-id=\"\" data-title=\"[a-zA-Z0-9 -?\":|}{+_/.,';\][=-~!@#$%^&*()]+ data-video-id=\"[0-9A-Za-z-_]+\">"

    test_str = data

    matches = re.finditer(regex, test_str, re.MULTILINE)
    # loop through matches but return on fist matched condition
    for matchNum, match in enumerate(matches, start=1):
        if matchNum == 1:
            regex_for_data_video_id = r"data-video-id=\"[a-zA-Z0-9-_]+"
            matches_for_video_id = re.finditer(regex_for_data_video_id, test_str, re.MULTILINE)
            for matchNum, match in enumerate(matches_for_video_id, start=1):
                if matchNum == 1:
                    video_id = match.group()
                    video_id = video_id.replace('data-video-id="', "")
                    video_url = "https://www.youtube.com/watch?v=" + video_id + "&list=" + playlist_id
                    return video_url


def giveMeAllVideoList(URL):
    """this function will return first video link with playlist id from watch window"""
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html5lib')
    data = soup.prettify()

    # regex for find out all video from watch window web page
    regex = r"<li class=\"yt-uix-scroller-scroll-unit vve-check(\"|[a-zA-Z, -0-9\"]+)=\"[0-9]+\" data-innertube-clicktracking=\"[0-9a-zA-Z-_]+\" data-thumbnail-url=\"https://i.ytimg.com/vi/[a-zA-Z0-9_-]+/hqdefault.jpg\?sqp=[a-zA-Z0-9-_]+==&amp;rs=[a-zA-Z0-9-_]+\" data-video-id=\"[a-zA-Z0-9 -_]+"
    test_str = data

    matches = re.finditer(regex, test_str, re.MULTILINE)

    # this list will contain all video link
    allVideoList = []

    # looping through matches and add to list
    for matchNum, match in enumerate(matches, start=1):
        regex_for_data_video_id = r"data-video-id=\"[a-zA-Z0-9-_]+"

        matches_for_video_id = re.finditer(regex_for_data_video_id, match.group(), re.MULTILINE)
        for number, matchcase in enumerate(matches_for_video_id, start=1):
            video_id = matchcase.group()
            video_id = video_id.replace('data-video-id="', "")
            video_url = "https://www.youtube.com/watch?v=" + video_id
            allVideoList.append(video_url)

    return allVideoList


# Code for playlist END

# Code for single START
def giveMeVideoID(URL):
    print(URL)
    # check point for mobile
    regex_for_mobile = r"https://youtu.be/[0-9a-zA-Z-_]{11}"
    regex_for_computer = r"https://www.youtube.com/watch\?v=[0-9a-zA-Z-_]{11}"

    matches_for_mobile = re.finditer(regex_for_mobile, URL, re.MULTILINE)
    matches_for_computer = re.finditer(regex_for_computer, URL, re.MULTILINE)

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


# Code for single END

# Handling Single Page
def homeSingle(request):
    if request.method == 'POST' and request.POST.get('single_video_input'):
        URL = request.POST.get('single_video_input')
        single_video_id = giveMeVideoID(URL)
        if not single_video_id is None:
            yt = YouTube("https://www.youtube.com/watch?v=" + single_video_id)
            seven = False
            four = False
            three = False
            two = False
            one = False

            if not yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution('720p') is None:
                seven = True
            if not yt.streams.get_by_itag(135) is None:
                four = True
            if not yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution('360p') is None:
                three = True
            if not yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution('240p') is None:
                two = True
            if not yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution('144p') is None:
                one = True

            dictionary = {}
            dictionary['title'] = yt.title
            dictionary['time'] = yt.length
            dictionary['thumbnail'] = yt.thumbnail_url
            streams = {}
            if seven:
                streams['720p'] = yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution(
                    '720p').url
            if four:
                # you can not get the video url using get_by_resolution() for 480, 240, 144
                # you can get only video not audio by using get_by_itag()
                streams['480p'] = yt.streams.get_by_itag(135).url
            if three:
                streams['360p'] = yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution(
                    '360p').url
            if two:
                streams['240p'] = yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution(
                    '240p').url
            if one:
                streams['144p'] = yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution(
                    '144p').url
            dictionary['streams'] = streams

            # return render(request, 'home/single.html', dictionary)
            return JsonResponse(dictionary)


        else:
            return render(request, 'home/single.html')
    return render(request, 'home/single.html')


# Handling Playlist page
def homePlaylist(request):
    # param dictionary will be send to template within the dictionary
    param = {}
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

        # video_number variable helps to remember current video number
        video_number = 1

        # looping through allVideoList[] and ultimate goal is get video_title, video_thumbnail, video_number, video_download_link
        for item in allVideoList:

            # this list will be set as value of key title, and a single titile will hold [video no, thumbnail, download link]
            value_list = []

            # creating Youtube object using pytube.YouTube
            yt = YouTube(item)
            video_title = yt.streams.filter(progressive=True, file_extension='mp4').order_by(
                'resolution').desc().first().title

            # making copy of the title because i don't want to prefix the real title with video no
            video_title_copy = video_title

            # this variable will hold video link temporary
            video_link = ""
            # this variable will hold title URL encoded value
            video_title_url_encoded = ""
            # this variable will hold final video download link video link + title URL encoded
            video_final_link = ""

            # checking user wants to prefix title with number or not
            if not request.POST.get("prefix") == None:
                video_title = str(video_number) + ". " + video_title + ""

            # getting the quality selected by user in a variable
            video_quality = request.POST.get("playlist_quality")

            # handling every resolution
            if video_quality == '720':
                try:
                    # execute this code if 720p is selected and if 720 isn't available then go to catch
                    # i am handling download link here because user can uncheck reduce quality if not exist
                    # in this case output will be blank in text area but title thumbnail will be available but video will be not downloadable
                    video_link = yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution('720p').url
                    video_title_url_encoded = urllib.parse.quote(video_title, safe="")
                    video_final_link = video_link + "&title=" + video_title_url_encoded
                except Exception as e:
                    if not request.POST.get("reduce") is None:
                        video_link = yt.streams.filter(progressive=True, file_extension='mp4').first().url
                        video_title_url_encoded = urllib.parse.quote(video_title, safe="")
                        video_final_link = video_link + "&title=" + video_title_url_encoded
                    else:
                        video_link = ""
            elif video_quality == '480':
                try:
                    video_link = yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution('480p').url
                    video_title_url_encoded = urllib.parse.quote(video_title, safe="")
                    video_final_link = video_link + "&title=" + video_title_url_encoded
                except Exception as e:
                    if not request.POST.get("reduce") is None:
                        video_link = yt.streams.filter(progressive=True, file_extension='mp4').first().url
                        video_title_url_encoded = urllib.parse.quote(video_title, safe="")
                        video_final_link = video_link + "&title=" + video_title_url_encoded
                    else:
                        video_link = ""
            elif video_quality == '360':
                try:
                    video_link = yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution('360p').url
                    video_title_url_encoded = urllib.parse.quote(video_title, safe="")
                    video_final_link = video_link + "&title=" + video_title_url_encoded
                except Exception as e:
                    if not request.POST.get("reduce") is None:
                        video_link = yt.streams.filter(progressive=True, file_extension='mp4').first().url
                        video_title_url_encoded = urllib.parse.quote(video_title, safe="")
                        video_final_link = video_link + "&title=" + video_title_url_encoded
                    else:
                        video_link = ""
            elif video_quality == '240':
                try:
                    video_link = yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution('240p').url
                    video_title_url_encoded = urllib.parse.quote(video_title, safe="")
                    video_final_link = video_link + "&title=" + video_title_url_encoded
                except Exception as e:
                    if not request.POST.get("reduce") is None:
                        video_link = yt.streams.filter(progressive=True, file_extension='mp4').first().url
                        video_title_url_encoded = urllib.parse.quote(video_title, safe="")
                        video_final_link = video_link + "&title=" + video_title_url_encoded
                    else:
                        video_link = ""
            elif video_quality == '144':
                try:
                    video_link = yt.streams.filter(progressive=True, file_extension='mp4').get_by_resolution('144p').url
                    video_title_url_encoded = urllib.parse.quote(video_title, safe="")
                    video_final_link = video_link + "&title=" + video_title_url_encoded
                except Exception as e:
                    if not request.POST.get("reduce") is None:
                        video_link = yt.streams.filter(progressive=True, file_extension='mp4').first().url
                        video_title_url_encoded = urllib.parse.quote(video_title, safe="")
                        video_final_link = video_link + "&title=" + video_title_url_encoded
                    else:
                        video_link = ""

            # getting video thumbnail
            video_thumbnail = YouTube(item).thumbnail_url
            # creating a list of these data
            value_list.append(video_number)
            value_list.append(video_thumbnail)
            value_list.append(video_final_link)
            print(str(video_number) + " " + video_final_link)
            # creating key value pair { title : [ video_number, video_thumbnail, video_final_link] }
            param[video_title_copy] = value_list
            # increase video number
            video_number += 1
            # if video_number % 50 == 0:
            #     time.sleep(1)

        # this dictionary will be send to template
        # passing a new line char to print after one link is printed
        data_dict = {'dictionary': param, 'new_line': "\n"}
        # finally return
        return render(request, 'home/playlist.html', data_dict)

    # return statement for without POST request
    return render(request, 'home/playlist.html')
