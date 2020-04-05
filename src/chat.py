import requests
import itertools
import pandas as pd
from bs4 import BeautifulSoup


class YoutubeLiveChat:
    def __init__(self):
        pass

    def get_livechat(self, videoId):
        livechat_data = []
        target_url = "https://www.youtube.com/watch?v=" + videoId
        session = requests.Session()
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"}

        html = requests.get(target_url)
        soup = BeautifulSoup(html.text, "html.parser")

        for iframe in soup.find_all("iframe"):
            if("live_chat_replay" in iframe["src"]):
                next_url = iframe["src"]
                break
        while True:
            html = session.get(next_url, headers=headers)
            soup = BeautifulSoup(html.text, 'lxml')
            for scrp in soup.find_all("script"):
                if "window[\"ytInitialData\"]" in scrp.text:
                    dict_str = scrp.text.split(" = ", 1)[1]

            dict_str = dict_str.replace("false", "False")
            dict_str = dict_str.replace("true", "True")
            dict_str = dict_str.rstrip("  \n;")
            dics = eval(dict_str)
            try:
                continuation = dics["continuationContents"]["liveChatContinuation"][
                    "continuations"][0]["liveChatReplayContinuationData"]["continuation"]
                continue_url = "https://www.youtube.com/live_chat_replay?continuation=" + continuation
                next_url = continue_url
            except Exception:
                print("Finish")
                break
            livechat_data.append(self.get_data(dics))
        livechat_data = list(itertools.chain.from_iterable(livechat_data))
        livechat_data = pd.json_normalize(livechat_data)
        return livechat_data

    def get_data(self, dics):
        chat = []
        for sample in dics['continuationContents']['liveChatContinuation']['actions'][1:]:
            d = {}
            try:
                sample = sample['replayChatItemAction']['actions'][0]['addChatItemAction']['item']
                chat_type = list(sample.keys())[0]
                if 'liveChatTextMessageRenderer' == chat_type:  # 通常チャットの処理
                    if 'simpleText' in sample['liveChatTextMessageRenderer']['message']:
                        d['message'] = sample['liveChatTextMessageRenderer']['message']['simpleText']
                    else:
                        d['message'] = ''
                        for elem in sample['liveChatTextMessageRenderer']['message']['runs']:
                            if 'text' in elem:
                                d['message'] += elem['text']
                            else:
                                d['message'] += elem['emoji']['shortcuts'][0]
                    t = sample['liveChatTextMessageRenderer']['timestampText']['simpleText']
                    d['timestamp'] = self.convert_time(t)
                    d['id'] = sample['liveChatTextMessageRenderer']['authorExternalChannelId']
                elif 'liveChatPaidMessageRenderer' == chat_type:  # スパチャの処理
                    if 'simpleText' in sample['liveChatPaidMessageRenderer']['message']:
                        d['message'] = sample['liveChatPaidMessageRenderer']['message']['simpleText']
                    else:
                        d['message'] = ''
                        for elem in sample['liveChatPaidMessageRenderer']['message']['runs']:
                            if 'text' in elem:
                                d['message'] += elem['text']
                            else:
                                d['message'] += elem['emoji']['shortcuts'][0]
                    t = sample['liveChatPaidMessageRenderer']['timestampText']['simpleText']
                    d['timestamp'] = self.convert_time(t)
                    d['id'] = sample['liveChatPaidMessageRenderer']['authorExternalChannelId']
                elif 'liveChatPaidStickerRenderer' == chat_type:  # コメントなしスパチャ
                    continue
                elif 'liveChatLegacyPaidMessageRenderer' == chat_type:  # 新規メンバーメッセージ
                    continue
                elif 'liveChatPlaceholderItemRenderer' == chat_type:
                    continue
                elif "liveChatMembershipItemRenderer" == chat_type:
                    continue
                else:
                    print('知らないチャットの種類' + chat_type)
                    continue
            except Exception:
                continue
            chat.append(d)
        return chat

    def convert_time(self, input_t):
        if input_t[0] == '-':
            return 0
        t = list(map(int, input_t.split(':')))
        if len(t) == 2:
            return 60 * t[0] + t[1]
        else:
            return 60 * 60 * t[0] + 60 * t[1] + t[2]
