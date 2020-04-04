import config
import pandas as pd
import itertools
from apiclient.discovery import build


class YoutubeChannel:
    def __init__(self):
        self.youtube = build(config.YOUTUBE_API_SERVICE_NAME,
                             config.API_VERSION, developerKey=config.YOUTUBE_API_TOKEN)

    def get_channelID(self, query, max_results=50):
        search_response = self.youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=max_results,
            type="channel"
        ).execute()

        channels = []

        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#channel":
                info = [search_result["snippet"]["title"],
                        search_result["id"]["channelId"]]
                channels.append(info)
        channels = pd.DataFrame(
            channels, columns=["channelTitle", "channelId"])
        return channels

    def get_videos(self, channel_id, pageToken=""):
        infos = []
        while True:
            search_response = self.youtube.search().list(
                part="id,snippet",
                channelId=channel_id,
                maxResults=50,
                order="date",
                pageToken=pageToken
            ).execute()

            for search_result in search_response.get("items", []):
                if search_result["id"]["kind"] == "youtube#video":
                    info = [search_result["snippet"]["channelId"],
                            search_result["snippet"]["title"],
                            search_result["id"]["videoId"],
                            search_result["snippet"]["publishedAt"]
                            ]
                    infos.append(info)
            if "nextPageToken" in search_response.keys():
                pageToken = search_response["nextPageToken"]
            else:
                break
        print("Total Video: {}".format(
            search_response["pageInfo"]["totalResults"]))
        videos = pd.DataFrame(
            infos, columns=["channelId", "title", "videoId", "date"])
        return videos

    def get_video_info(self, videoId):
        infos = []
        video_response = self.youtube.videos().list(
            part="id, snippet, contentDetails",
            id=videoId
        ).execute()

        for video_result in video_response.get("items", []):
            info = [video_result["id"],
                    video_result["snippet"]["title"],
                    video_result["contentDetails"]["duration"],
                    video_result["snippet"]["publishedAt"],
                    ]
            infos.append(info)

        video_info = pd.DataFrame(
            infos, columns=["videoId", "title", "duration", "publishedAt"])
        return video_info
