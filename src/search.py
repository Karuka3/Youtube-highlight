from chat import YoutubeLiveChat
from channel import YoutubeChannel
from apiclient.errors import HttpError
import itertools
import pandas as pd
import os


def search_channels():
    youchannel = YoutubeChannel()
    try:
        channels = youchannel.get_channelID(query="ホロライブ", max_results=40)
        channels = channels.query(
            'channelTitle.str.contains("Ch")', engine="python").reset_index(drop=True)
        channels.to_csv("data\\channel_infos.csv")
    except HttpError as e:
        print("An HTTP error {} occurred".format(e.resp.status))


def search_videos():
    youchannel = YoutubeChannel()
    try:
        channel_info = pd.read_csv("data\\channel_infos.csv")
        for id, title in zip(channel_info["channelId"], channel_info["channelTitle"]):
            videos = youchannel.get_videos(id)
            videos = videos.sort_values(
                "date", ascending=False).reset_index(drop=True)
            filename = "data\\video_info\\videos_{}.csv".format(title)
            videos.to_csv(filename)
        print("Finish")
    except HttpError as e:
        print("An HTTP error {} occurred".format(e.resp.status))


def search_livechat():
    youchat = YoutubeLiveChat()
    path = "data\\video_info"
    files = os.listdir(path)
    filenames = [f for f in files if os.path.isfile(os.path.join(path, f))]
    for name in filenames:
        path = "data\\video_info\\{}".format(name)
        videos = pd.read_csv(path)
        videoIds = videos["videoId"]
        for videoId in videoIds:
            livechat = youchat.get_livechat(videoId)
            dir_path = "data\\livechats\\{}".format(name.rsplit(".", 1)[0])
            if os.path.exists(dir_path) == False:
                os.mkdir(dir_path)
            livechat.to_csv(dir_path + "\\{}.csv".format(videoId))


if __name__ == "__main__":
    # search_channels()
    # search_videos()
    # search_livechat()
