from googleapiclient.discovery import build
from django.conf import settings
import re
import requests
from bs4 import BeautifulSoup

youtube = build("youtube", "v3", developerKey=settings.API_KEY)
# URL Type Constants
URL_TYPE_NONE = 0
URL_TYPE_PLAYLIST = 1
URL_TYPE_WATCH_WINDOW = 2


def give_me_video_id(URL):
    # check point for mobile
    regex_for_mobile = r"https://www.youtu.be/[0-9a-zA-Z-_]{11}"
    regex_for_mobile_without_www = r"https://youtu.be/[0-9a-zA-Z-_]{11}"
    regex_for_computer = r"https://www.youtube.com/watch\?v=[0-9a-zA-Z-_]{11}"
    regex_for_computer_without_www = r"https://youtube.com/watch\?v=[0-9a-zA-Z-_]{11}"

    matches_for_mobile = re.finditer(regex_for_mobile, URL, re.MULTILINE)
    matches_for_mobile_without_www = re.finditer(
        regex_for_mobile_without_www, URL, re.MULTILINE
    )
    matches_for_computer = re.finditer(regex_for_computer, URL, re.MULTILINE)
    matches_for_computer_without_www = re.finditer(
        regex_for_computer_without_www, URL, re.MULTILINE
    )

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
    return None


def get_video_links(playlist: str):
    """Accepts playlist id and returns all the videos link"""

    playlist = playlist.replace("https://www.youtube.com/playlist?list=", "")

    request = youtube.playlists().list(
        part="contentDetails", id=playlist, maxResults=50
    )
    response = request.execute()

    total_videos = response["items"][0]["contentDetails"]["itemCount"]

    fetch_till_now = 0

    nextPageToken = ""
    items = {}
    video_number = 0

    while fetch_till_now < total_videos:
        if fetch_till_now == 0:
            request = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=playlist,
                maxResults=50,
            )

            response = request.execute()
            result_fetched = response["pageInfo"]["resultsPerPage"]
            fetch_till_now += result_fetched
            try:
                nextPageToken = response["nextPageToken"]
            except Exception as e:
                pass

            videos = response["items"]
            total_videos_get = len(videos)
            counter = 0

            while counter < total_videos_get:
                items[video_number] = (
                    "https://www.youtube.com/watch?v="
                    + videos[counter]["contentDetails"]["videoId"]
                )
                counter += 1
                video_number += 1

        else:
            request = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=playlist,
                maxResults=50,
                pageToken=nextPageToken,
            )

            response = request.execute()
            result_fetched = response["pageInfo"]["resultsPerPage"]
            fetch_till_now += result_fetched
            try:
                nextPageToken = response["nextPageToken"]
            except Exception as e:
                pass

            videos = response["items"]
            total_videos_get = len(videos)
            counter = 0

            while counter < total_videos_get:
                items[video_number] = (
                    "https://www.youtube.com/watch?v="
                    + videos[counter]["contentDetails"]["videoId"]
                )
                counter += 1
                video_number += 1

    video_list = list(items.values())

    return video_list


def give_me_the_correct_url_type(url_to_be_checked):
    """checking the input url to see either it is playlist link or watch window link
    , if it is a playlist link this function will return watch window link"""

    # regex for match playlist and watch window link
    regex_for_playlist = r"https:\/\/www.youtube.com\/playlist\?list=[a-zA-Z0-9_-]{34}"
    regex_for_playlist_without_www = (
        r"https:\/\/youtube.com\/playlist\?list=[a-zA-Z0-9_-]{34}"
    )
    regex_for_watch_window = (
        r"https:\/\/www.youtube.com\/watch\?v=[0-9A-Za-z-_]+&list=[a-zA-Z0-9_-]{34}"
    )
    regex_for_watch_window_without_www = (
        r"https:\/\/youtube.com\/watch\?v=[0-9A-Za-z-_]+&list=[a-zA-Z0-9_-]{34}"
    )

    test_str = url_to_be_checked

    # Checking for playlist link
    matches_for_playlist = re.finditer(regex_for_playlist, test_str, re.MULTILINE)
    for matchNum, match in enumerate(matches_for_playlist, start=1):
        if matchNum:
            return URL_TYPE_PLAYLIST

    # Checking for playlist link without www
    matches_for_playlist_without_www = re.finditer(
        regex_for_playlist_without_www, test_str, re.MULTILINE
    )
    for matchNum, match in enumerate(matches_for_playlist_without_www, start=1):
        if matchNum:
            return URL_TYPE_PLAYLIST

    # Checking for watch window
    matches_for_watch_window = re.finditer(
        regex_for_watch_window, test_str, re.MULTILINE
    )
    for matchNum, match in enumerate(matches_for_watch_window, start=1):
        if matchNum:
            return URL_TYPE_WATCH_WINDOW

    # Checking for watch window without www
    matches_for_watch_window_without_www = re.finditer(
        regex_for_watch_window_without_www, test_str, re.MULTILINE
    )
    for matchNum, match in enumerate(matches_for_watch_window_without_www, start=1):
        if matchNum:
            return URL_TYPE_WATCH_WINDOW

    return URL_TYPE_NONE


def get_playlist_url(url: str):
    """This function takes URL of watch window and return playlist URL"""

    prefix_url = "https://www.youtube.com/playlist?"

    playlist_id = re.findall(r"list=[a-zA-Z0-9_-]{34}", url)[0]

    return prefix_url + playlist_id


def first_video_link_from_playlist(url):
    """this function will return the first video link with playlist id from playlist web page"""
    playlist_id = url.replace("https://www.youtube.com/playlist?list=", "")
    r = requests.get(url)

    regex = r"{\"url\":\"/watch\?v=[a-zA-Z0-9_-]{11}"

    page_content = r.content.decode("utf-8")

    matches = re.finditer(regex, page_content, re.MULTILINE)

    url = "https://www.youtube.com"

    for matchNum, match in enumerate(matches, start=1):
        if matchNum == 1:
            url += match.group().replace('''{"url":"''', "")
            url += "&list=" + playlist_id
            return url


def give_me_all_video_list(url):
    """this function will return first video link with playlist id from watch window"""
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")

    regex = (
        r"/watch\?v=[a-zA-Z0-9-_]{11}\\u0026list=[a-zA-Z0-9-_]{34}\\u0026index=[0-9]+"
    )

    response_script = str(soup.findAll("script")[32])

    matches = re.finditer(regex, response_script, re.MULTILINE)

    videos_list = []
    for matchNum, match in enumerate(matches, start=1):
        videos_list.append(match.group())

    videos_set = set(videos_list)
    videos_dict = {}
    for video in videos_set:
        try:
            pass
            # print(int(str(re.findall(r"index=[0-9]+", video)).replace("index=", "")), 10)
        except Exception as e:
            pass
        videos_dict[str(re.findall(r"index=[0-9]+", video)).replace("index=", "")] = (
            "https://www.youtube.com"
            + str(re.match(r"/watch\?v=[a-zA-Z0-9-_]{11}", video))
        )

    all_video_list = []
    values = videos_dict.values()
    all_video_list = list(values)

    print(all_video_list)

    return all_video_list
