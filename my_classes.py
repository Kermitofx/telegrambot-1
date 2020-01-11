import requests,json,re
from bs4 import BeautifulSoup
from db import SearchData,loadSession
from sqlalchemy import desc

BOTURL_MES = 'https://api.telegram.org/bot928105941:AAHXNyGre-Wi6tRExNFCw5VsKjuJApByXjI/sendMessage'
BOTURL_AUDIO = 'https://api.telegram.org/bot928105941:AAHXNyGre-Wi6tRExNFCw5VsKjuJApByXjI/sendAudio'
GREETINGS = """Hello,I am musicbot. I will help you search and download some music. Just enter your search request.
Здравствуйте,я - музыкальный бот. Я помогу Вам найти и скачать музыку. Просто введите свой поисковый запрос."""
UNKNOWN="Sorry.This command doesn't exist"
APPROVE="Send search request?"
SITE_SEARCH_URL='http://myzcloud.me/search?searchText='
SITE_URL='http://myzcloud.me'
NO_RESULT="Can't find anything.Please,try different search request."
REQUEST_FAIL="Sorry.Something went wrong.Please,try again later"
FILE_NOTFOUND="Sorry. This file does not exist"


class Update:
    def __init__(self,MsgUpdate):
        self.chat_id=MsgUpdate['message']['chat']['id']
        self.mes_text=MsgUpdate['message']['text']
        self.mes_id=MsgUpdate['message']['message_id']

    def main(self):
        if re.match('\/\d+$',self.mes_text):
            self.sendFile()
        elif self.mes_text == '/start':
            self.sendHello()
        elif re.match('\/.*\D+',self.mes_text):
            self.sendUnknownCommand()
        else:
            self.sendApprove()

    def sendFile(self):
        session=loadSession()

        link = session.query(SearchData).filter(SearchData.song_link.ilike('%' + self.mes_text+ '%')).order_by(
            desc(SearchData.id)).first().song_link
        payload = {'chat_id': self.chat_id, 'audio': link}
        self.sendTgrmRequest(BOTURL_AUDIO,payload)

    def sendTgrmRequest(self,url,payload):
        try:
            res=requests.post(url,json=payload)
            #print (res.url)
            #print(payload)
        except (requests.exceptions.ConnectionError ,requests.exceptions.ConnectTimeout) as e:
            self.sendReqNotOk()
        else:
            resp=json.loads(res.text)
            #print(resp)
            if (resp.get('error_code') == 400) and (resp.get('description') == 'Bad Request: failed to get HTTP URL content'):
                self.sendNotFound()

    def sendNotFound(self):
        payload = {'chat_id': self.chat_id}
        payload['text'] = FILE_NOTFOUND
        self.sendTgrmRequest(BOTURL_MES, payload)

    def sendReqNotOk(self):
        payload = {'chat_id': self.chat_id}
        payload['text'] = REQUEST_FAIL
        self.sendTgrmRequest(BOTURL_MES, payload)

    def sendHello(self):
        payload = {'chat_id': self.chat_id}
        payload['text'] = GREETINGS
        self.sendTgrmRequest(BOTURL_MES, payload)

    def sendUnknownCommand(self):
        payload = {'chat_id': self.chat_id}
        payload['text'] = UNKNOWN
        self.sendTgrmRequest(BOTURL_MES, payload)

    def sendApprove(self):
        payload = {'chat_id': self.chat_id}
        payload['text'] = APPROVE
        payload['reply_to_message_id'] = self.mes_id
        payload['reply_markup'] = {'inline_keyboard': [[{'text': 'Yes', 'callback_data': 'agreed'},
                                                        {'text': 'No', 'callback_data': 'nope'}]]}
        self.sendTgrmRequest(BOTURL_MES, payload)

class Callback(Update):
    def __init__(self, MsgUpdate):
        self.mes_id = MsgUpdate['callback_query']['message']['reply_to_message']['message_id']
        self.chat_id = MsgUpdate['callback_query']['message']['chat']['id']
        self.button = MsgUpdate['callback_query']['data']
        self.search_text = MsgUpdate['callback_query']['message']['reply_to_message']['text']

    def main(self):
        if self.button == 'agreed':
            soup = self.site_request(SITE_SEARCH_URL + self.search_text)
            if soup is not None:    # если есть ответ от сервера сайта
                playlist = soup.find("div", "playlist--hover")
                if playlist:
                    self.makeResults(playlist)
                    self.sendResults()
                else:
                    self.sendNoResult()
            else:
                self.sendReqNotOk()

    def makeResults(self, data):
        self.search_result = data.find_all(class_='playlist__item', limit=5)
        self.reslist = []
        for x in self.search_result:  # наполнение массива словарями  песен
            curdict = {}
            curdict['song'] = x.attrs['data-name']
            curdict['author'] = x.attrs['data-artist']
            curdict['link'] = x.find("a", class_="dl-song")['href']
            curdict['info'] = []
            for c in x.find_all("span", class_="text-muted"):
                curdict['info'].append(c.get_text())
            self.reslist.append(curdict)

        for y in self.reslist:  # получаем полные ссылки на песни
            result = self.site_request(SITE_URL + y['link'])

            div = result.find("div", "playlist__actions")

            resultRef = div.find("a", class_="no-ajaxy yaBrowser")
            if resultRef is None: #если на целевой странице нет ссылки на песню
                y['filelink']='empty'
                continue
            resultRef = resultRef['href']
            y['filelink'] = SITE_URL + str(resultRef)
            session=loadSession()
            new_searchData=SearchData(song_short=y['link'],song_link=y['filelink'])
            session.add(new_searchData)
            session.commit()
        self.res_text = ""
        for a in self.reslist:
            if a['filelink']!='empty': # не обрабатываем песню без ссылки
                a['mod_link'] = re.sub(r'^.*?\/.*?(\/.*?)\/.*$', r'\1', a['link'])
                self.res_text += '<b>' + a['author'] + '</b>' + '\n'
                self.res_text += a['song'] + '\n'
                self.res_text += a['info'][0] + '  ' + '<i>' + a['info'][1] + '</i>' + '\n'
                self.res_text += '<i>Download:</i>' + a['mod_link'] + '\n\n'

    def sendResults(self):
        payload = {'chat_id': self.chat_id}
        payload['reply_to_message_id'] = self.mes_id
        payload['parse_mode'] = 'HTML'
        payload['text'] = self.res_text
        self.sendTgrmRequest(BOTURL_MES, payload)

    def site_request(self, url):
        headers = {
            'Referer': "ya.ru",
            'User-Agent': "Mozilla/5.0"
        }
        try:
            r = requests.get(url, headers=headers, timeout=30)
        except requests.exceptions.RequestException:
            return None
        # print(r.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup

    def sendNoResult(self):
        payload = {'chat_id': self.chat_id}
        payload['text'] = NO_RESULT
        payload['reply_to_message_id'] = self.mes_id
        self.sendTgrmRequest(BOTURL_MES, payload)
