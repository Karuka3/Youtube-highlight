from chat import YoutubeLiveChat
from channel import YoutubeChannel
from apiclient.errors import HttpError
from multiprocessing import Pool
import multiprocessing as multi
import itertools
import pandas as pd
import os


def search_channels():
    youchannel = YoutubeChannel()
    try:
        channels = youchannel.get_channelID(query="ホロライブ", max_results=40)
        channels = channels.query(
            'channelTitle.str.contains("Ch")', engine="python").reset_index(drop=True)
        channels.to_csv("data\\channel_infos.csv", index=False)
    except HttpError as e:
        print("An HTTP error {} occurred".format(e.resp.status))


def search_videos():
    youchannel = YoutubeChannel()
    try:
        channel_info = pd.read_csv("data\\channel_infos.csv")
        for id_, title in zip(channel_info["channelId"], channel_info["channelTitle"]):
            videos = youchannel.get_videos(id_)
            videos = videos.sort_values(
                "date", ascending=False).reset_index(drop=True)
            filename = "data\\video_info\\videos_{}.csv".format(title)
            videos.to_csv(filename, index=False)
        print("Finish")
    except HttpError as e:
        print("An HTTP error {} occurred".format(e.resp.status))


def search_livechat(filename):
    youchat = YoutubeLiveChat()
    path = "data\\video_info\\{}".format(filename)
    dir_path = "data\\livechats\\{}".format(filename.rsplit(".", 1)[0])
    videos = pd.read_csv(path)
    for videoId in videos["videoId"]:
        file_ = dir_path + "\\{}.csv".format(videoId)
        if os.path.isfile(file_) == False:
            livechat = youchat.get_livechat(videoId)
            livechat.to_csv(file_, index=False)
        else:
            pass


if __name__ == "__main__":
    path = "data\\video_info"
    files = os.listdir(path)
    filenames = [f for f in files if os.path.isfile(os.path.join(path, f))]
    n_cores = multi.cpu_count()
    with Pool(n_cores) as pool:
        pool.map(search_livechat, filenames)

    # search_channels()
    # search_videos()
    # search_livechat()
