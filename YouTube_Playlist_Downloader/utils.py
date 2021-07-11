from os import pipe
import re
import requests
from bs4 import BeautifulSoup



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



def getPlaylistUrl(url : str):
    """This function takes URL of watch window and return playlist URL"""
    
    prefix_url = "https://www.youtube.com/playlist?"

    playlist_id = re.findall(r"list=[a-zA-Z0-9_-]{34}", url)[0]
    
    return prefix_url + playlist_id


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
            pass
            # print(int(str(re.findall(r"index=[0-9]+", video)).replace("index=", "")), 10)
        except Exception as e:
            pass
        videos_dict[str(re.findall(r"index=[0-9]+", video)).replace("index=", "")] = "https://www.youtube.com" + str(re.match(r"/watch\?v=[a-zA-Z0-9-_]{11}", video))

    all_video_list = []
    values = videos_dict.values()
    all_video_list = list(values)

    print(all_video_list)

    return all_video_list