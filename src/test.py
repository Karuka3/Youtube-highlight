from channel import YoutubeChannel
import pandas as pd


def main():
    you = YoutubeChannel()
    #videos = you.get_videos(channel_id="UCCzUftO8KOVkV4wQG1vkUvg")
    # videos.to_csv("data\\test.csv")

    video_info = you.get_video_info(videoId="5Nr41M9zk2c,YSx-pfTthBA")
    video_info.to_csv("data\\test_info.csv")


if __name__ == "__main__":
    main()
