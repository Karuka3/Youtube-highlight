from chat import YoutubeChat


def main():
    url = input()
    youchat = YoutubeChat(url)
    youchat.save_data()


if __name__ == "__main__":
    main()
