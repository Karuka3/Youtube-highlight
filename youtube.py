import sys
import requests
import itertools
import pandas as pd
from bs4 import BeautifulSoup


class YoutubeChat:
    def __init__(self, url=''):
        self.chat_data = self.get_chat_data(url)

    def get_html(self, url):
        try:
            html = requests.get(url)
        except Exception as E:
            print(E)
            sys.exit()
        return html

    def js2py(self, dict_str):
        dict_str = dict_str.replace('false', 'False')
        dict_str = dict_str.replace('true', 'True')
        return dict_str

    def convert2dict(self, dict_str, soup):
        try:
            dics = eval(dict_str)
        except Exception:
            with open('error_dict_str.txt', 'w') as f:
                f.write(dict_str)
            with open('error_soup.txt', 'w') as f:
                f.write(str(soup))
            print("Failed to convert the text into dict")
            print(sys.exc_info()[0])
            sys.exit()
        return dics

    def get_chat(self, dics):
        chat = []
        for sample in dics['continuationContents']['liveChatContinuation']['actions'][1:]:
            d = {}
            try:
                sample = sample['replayChatItemAction']['actions'][0]['addChatItemAction']['item']
                chat_type = list(sample.keys())[0]
                if 'liveChatTextMessageRenderer' == chat_type:
                    # 通常チャットの処理
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
                elif 'liveChatPaidMessageRenderer' == chat_type:
                    # スパチャの処理
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
                elif 'liveChatPaidStickerRenderer' == chat_type:
                    # コメントなしスパチャ
                    continue
                elif 'liveChatLegacyPaidMessageRenderer' == chat_type:
                    # 新規メンバーメッセージ
                    continue
                elif 'liveChatPlaceholderItemRenderer' == chat_type:
                    continue
                else:
                    print('知らないチャットの種類' + chat_type)
                    continue
            except Exception:
                continue
            chat.append(d)
        return chat

    def get_chat_data(self, url):
        chat_data = []
        dict_str = ''
        next_url = ''
        session = requests.Session()
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}

        html = self.get_html(url)
        soup = BeautifulSoup(html.text, 'lxml')

        for iframe in soup.find_all('iframe'):
            if 'live_chat_replay' in iframe['src']:
                next_url = iframe['src']

        while True:
            html = session.get(next_url, headers=headers)
            soup = BeautifulSoup(html.text, 'lxml')

            for scrp in soup.find_all('script'):
                if 'window["ytInitialData"]' in scrp.text:
                    dict_str = scrp.text.split(' = ', 1)[1]

            dict_str = self.js2py(dict_str)
            dict_str = dict_str.rstrip('  \n;')

            dics = self.convert2dict(dict_str, soup)

            try:
                continue_url = dics['continuationContents']['liveChatContinuation'][
                    'continuations'][0]['liveChatReplayContinuationData']['continuation']
            except Exception:
                break
            next_url = 'https://www.youtube.com/live_chat_replay?continuation=' + continue_url
            chat_data.append(self.get_chat(dics))
        chat_data = list(itertools.chain.from_iterable(chat_data))
        return chat_data

    def save_data(self):
        df = pd.json_normalize(self.chat_data)
        df.to_csv('youtube_chat_data.csv')

    def convert_time(self, input_t):
        if input_t[0] == '-':
            return 0
        t = list(map(int, input_t.split(':')))
        if len(t) == 2:
            t = 60 * t[0] + t[1]
        else:
            t = 60 * 60 * t[0] + 60 * t[1] + t[2]
        return t
