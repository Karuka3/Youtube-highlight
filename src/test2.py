from chat import YoutubeLiveChat


def main():
    youchat = YoutubeLiveChat()
    df = youchat.get_livechat("xfs3P8mIAIw")
    df.to_csv("data\\test.csv", index=False)


if __name__ == "__main__":
    main()
