import config
import pandas as pd
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
                channels.append("%s (%s)" % (search_result["snippet"]["title"],
                                             search_result["id"]["channelId"]))
        return channels

    def get_videos(self, channel_id):
        CHANNEL_ID = channel_id
        PAGE_TOKEN = None
        infos = []
        while True:
            if PAGE_TOKEN:
                search_response = self.youtube.search().list(
                    part="id,snippet",
                    channelId=CHANNEL_ID,
                    maxResults=50,
                    order="date",
                    pageToken=PAGE_TOKEN
                ).execute()
            else:
                search_response = self.youtube.search().list(
                    part="id,snippet",
                    channelId=CHANNEL_ID,
                    order="date",
                    maxResults=50
                ).execute()

            for search_result in search_response.get("items", []):
                if search_result["id"]["kind"] == "youtube#video":
                    info = [search_result["snippet"]["channelId"],
                            search_result["snippet"]["title"],
                            search_result["id"]["videoId"]
                            ]
                    infos.append(info)

            if "nextPageToken" in search_response.keys():
                PAGE_TOKEN = search_response["nextPageToken"]
            else:
                print("OK")
                break

        print("Total Video: {}".format(
            search_response["pageInfo"]["totalResults"]))
        videos = pd.DataFrame(
            infos, columns=["channelId", "title", "videoId"])
        return videos

    def get_video_info(self, videoIds: list):
        VIDEO_IDs = videoIds
        infos = []
        video_response = self.youtube.videos().list(
            part="id,snippet,contentDetails,fileDetails,liveStreamingDetails",
            id=VIDEO_IDs
        ).execute()

        for video_result in video_response.get("items", []):
            if video_result["fileDetails"]["fileType"] == "archive":
                info = [video_result["Id"],
                        video_result["snippet"]["title"],
                        video_result["contentDetails"]["duration"],
                        video_result["snippet"]["publishedAt"],
                        video_result["liveStreamingDetails"]["concurrentViewers"],
                        video_result["liveStreamingDetails"]["activeLiveChatId"],
                        ]
                infos.append(info)

        video_info = pd.DataFrame(
            infos, columns=["videoId", "title", "duration", "publishedAt", "concurrentViewers", "activeLiveChatId"])
        return video_info
