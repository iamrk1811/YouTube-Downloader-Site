from googleapiclient.discovery import build
from django.conf import settings

youtube = build('youtube', 'v3', developerKey=settings.API_KEY)


def getVideoLinks(playlist : str):
    """Accepts playlist id and returns all the videos link"""

    
    playlist = playlist.replace("https://www.youtube.com/playlist?list=", "")

    request = youtube.playlists().list(
        part="contentDetails",
        id=playlist,
        maxResults=50
    )
    response = request.execute()

    total_videos = response['items'][0]['contentDetails']['itemCount']

    fetch_till_now = 0

    nextPageToken = ''
    items = {}
    video_number = 0

    streams = None

    while fetch_till_now < total_videos:
        if fetch_till_now == 0:
            request = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=playlist,
                maxResults=50,
            )

            response = request.execute()
            result_fetched = response['pageInfo']['resultsPerPage']
            fetch_till_now += result_fetched
            try:
                nextPageToken = response['nextPageToken']
            except Exception as e:
                pass

            videos = response['items']
            total_videos_get = len(videos)
            counter = 0

            while counter < total_videos_get:
                items[video_number] = "https://www.youtube.com/watch?v=" + videos[counter]['contentDetails']['videoId']
                counter += 1
                video_number += 1
                
        else:
            request = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=playlist,
                maxResults=50,
                pageToken=nextPageToken
            )

            response = request.execute()
            result_fetched = response['pageInfo']['resultsPerPage']
            fetch_till_now += result_fetched
            try:
                nextPageToken = response['nextPageToken']
            except Exception as e:
                pass

            videos = response['items']
            total_videos_get = len(videos)
            counter = 0

            while counter < total_videos_get:
                items[video_number] = "https://www.youtube.com/watch?v=" + videos[counter]['contentDetails']['videoId']
                counter += 1
                video_number += 1
    

    video_list = list(items.values())

    return video_list





