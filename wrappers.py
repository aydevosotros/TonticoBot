import bs4 as bs
import requests

def getSongs():
    header = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; hu-HU; rv:1.7.8) Gecko/20050511 Firefox/1.0.4'}
    canciones = bs.BeautifulSoup(requests.get("http://www.letras.com/", params={"q": quote(message.text)}, headers=header).text).find_all("a", "gs-title")
    # print(requests.get("http://www.letras.com/", params={"q": quote(message.text)}, headers=header).text)
    print(canciones)
    return
    if len(canciones) == 0:
        bot.sendMessage(chat_id=update.message.chat_id, text='Lo siento pero no he encontrado esa canción')
    else:
        titlesButtons = ["{} ({})".format(c["title"], c.find("span").text.lstrip()) for c in canciones][:3]
        bot.sendMessage(chat_id=update.message.chat_id, text="Those are the songs I know", reply_markup=telegram.ReplyKeyboardMarkup([titlesButtons], resize_keyboard=True, one_time_keyboard=True))
        message = getNextMessage(bot, update).message
        s, a = re.search("(.*) \((.*)\)", message.text).groups()
        print("Quieren que cante {} de {}".format(s, a))
        song = [c for c in canciones if c["title"] == s and c.find("span").text.lstrip() == a][0]
        letra = bs.BeautifulSoup(requests.get("http://www.albumcancionyletra.com/{}".format(song["href"])).text).find("div", "letra")
        print(letra)
        print(letra.text.replace("<br>", ""))
