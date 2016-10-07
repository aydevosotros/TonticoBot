#!/usr/bin/python3

from telegram.ext import Updater
from telegram.ext import CommandHandler
import telegram
import time
import requests
import bs4 as bs
import sched
from random import randint
import schedule
from flask import Flask
from urllib.parse import quote
import os
from gtts import gTTS

app = Flask(__name__, static_folder='public', static_url_path='')

updater = Updater("259443067:AAEime5UnPucBBXzt3jll5Oct4CTuHrMbX8")
bot = telegram.Bot("259443067:AAEime5UnPucBBXzt3jll5Oct4CTuHrMbX8")
dispatcher = updater.dispatcher

def getAudioFromText(text):
    language = "es"
    # url = "https://translate.google.com/translate_tts?q=" + quote(text) + "&tl=" + language
    # print(url)
    # headers = { 'User-Agent' :  'vsreality/1.0'}
    # response = requests.get(url, headers=headers, stream=True)
    i = 0
    filename = "/home/antonio/public/audio{}.mp3".format(i)
    while os.path.exists(filename):
        i += 1
        filename = "/home/antonio/public/audio{}.mp3".format(i)
    gTTS(text=text, lang="es").save(filename)
    # with open(filename, 'wb') as f:
    #     for block in response.iter_content(1024):
    #         f.write(block)
    return filename.split("/")[-1]

def start1(bot, update):
    print(update.to_json())
    try:
        t = "I know you 2 {}.".format(update.to_dict()["message"]["from"]["first_name"])
    except Exception as ex:
#         bot.sendMessage(chat_id=update.message.chat_id, text=ex)
        print(ex)
#     if update.chat.id == 166282912:
#         t += " Oh sir Molina, que alegria verle"
    bot.sendMessage(chat_id=update.message.chat_id, text=t)

def saluda(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Hola {}!".format(update.to_dict()["message"]["from"]["first_name"]))

def joke(bot, update):
    try:
        joke = bs.BeautifulSoup(requests.get("http://www.chistescortos.eu/random", "html.parser").text).find_all("a", "oldlink")[3].text
        filename = getAudioFromText(joke + " jejejejejejeje")
        bot.send_audio(update.message.chat_id, "http://137.74.112.195:8111/{}".format(filename))
    except Exception as ex:
        print(ex)

def claratorio():
    bot.sendMessage(chat_id=-172831566, text="Clara... No es la hora de la foto? :wink:")
    # bot.sendMessage(chat_id=166282912, text="Clara, es la hora...")

def defense(bot, update):
    name = update.to_dict()["message"]["text"].split(" ")[1:]
    print(name)
    phrases = []
    with open("/home/antonio/insultos1.txt") as iFile:
        for line in iFile:
            phrases.append(line.rstrip())
    phrase = phrases[randint(0, len(phrases)-1)]
    print("{}, {}".format(name, phrase))
    try:
        bot.sendMessage(chat_id=update.message.chat_id, text="{}, {}".format(" ".join(name), phrase))
    except Exception as ex:
        print(ex)

def piropo(bot, update):
    phrases = []
    with open("/home/antonio/piropos.txt") as iFile:
        for line in iFile:
            phrases.append(line.rstrip())
    phrase = phrases[randint(0, len(phrases)-1)]
    try:
        filename = getAudioFromText(phrase)
        bot.send_audio(update.message.chat_id, "http://137.74.112.195:8111/{}".format(filename))
    except Exception as ex:
        print(ex)

def addDefensePhrase(bot, update):
    upDict = update.to_dict()

def audioTest(bot, update):
    try:
        print("Testing audio files")
        text = " ".join(update.to_dict()["message"]["text"].split(" ")[1:])
        print("testing with {}".format(text))
        filename = getAudioFromText(text)
        bot.send_audio(update.message.chat_id, "http://137.74.112.195:8111/{}".format(filename))
    except Exception as ex:
        print(ex)

def getChatId(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=update.message.chat_id)

def help(bot, update):
    helpText = """
        Para refrescarte la memoria:
        \t/greeting: Te saluda con mucho salero
        \t/chiste: Alegrate el día con un chiste (puede que sea bastante malo)
        \t/meteteCon nombre: Hasta los huevos de alguien del grupo pero sin valor para soltarle una bordería?
        \t/piropo: Qué mejor para alegrarte el día que un piropo con arte?
    """
    bot.sendMessage(chat_id=update.message.chat_id, text=helpText)


start_handler = CommandHandler('start', start1)
dispatcher.add_handler(start_handler)

audioTest_handler = CommandHandler('diles', audioTest)
dispatcher.add_handler(audioTest_handler)

piropo_handler = CommandHandler('piropo', piropo)
dispatcher.add_handler(piropo_handler)

greeting_handler = CommandHandler('greeting', saluda)
dispatcher.add_handler(greeting_handler)

joke_handler = CommandHandler('chiste', joke)
dispatcher.add_handler(joke_handler)

chatId_handler = CommandHandler('giveMeId', getChatId)
dispatcher.add_handler(chatId_handler)

defense_handler = CommandHandler('meteteCon', defense)
dispatcher.add_handler(defense_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

# Timers
schedule.every().day.at("11:37").do(claratorio)


updater.start_polling()

app.run("0.0.0.0", "8111")

print("Tontico is ready :)")
