#!/usr/bin/python3

from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
import telegram
from telegram import KeyboardButton
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
import re
from threading import Lock
from langdetect import detect
import wrappers
import tempfile
from pydub import AudioSegment

# SQLAlchemy stuff
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

groupChatId = -172831566
chatCommandLock = Lock()
chatCommand = dict()
allowedLangsSpeech = ["en", "ca", "es"]
chatData = dict()


class TontiBot():
    """ Toti bot class """

    def __init__(self, botToken):
        self.botToken = botToken
        self.bot = telegram.Bot(botToken)

        # Init data persistance if not exists
        self.engine = create_engine('sqlite:///tontiBot.sqlite', echo=True)
        if not os.path.exists("tontiBot.sqlite"):
            Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)

    def registerGroup(self, idGroupChat):
        self.session.add(Group(idGroupChat))


class Group(Base):

    __tablename__ = "groups"

    id = Column(Integer, primary_key)
    name = Column(String)

    def __init__(self, chatId):


    def __repr__(self):
        return "Group: {}".format(name)

def speak(bot, update):
    try:
        print("Testing speak")
        fp = BufferedReader(textToSpeech("Prueba de castellano"))
        bot.send_voice(update.message.chat_id, fp)
    except Exception as ex:
        print(ex)

def getAudioFromText(text):
    lang = detect(text)
    if lang not in allowedLangsSpeech:
        lang = "es"
    i = 0
    filename = "/home/antonio/public/audio{}.mp3".format(i)
    while os.path.exists(filename):
        i += 1
        filename = "/home/antonio/public/audio{}.mp3".format(i)
    gTTS(text=text, lang=lang).save(filename)
    return filename.split("/")[-1]

def setChatCommand(chatId, command):
    with chatCommandLock:
        chatCommand[chatId] = command

def getChatCommand(chatId):
    if chatId in chatCommand:
        return chatCommand[chatId]

def reply_to_query(bot, update):
    try:
        chatId = update.message.chat.id
        command = getChatCommand(chatId)
        print("Gotten a query")
        if command is None:
            bot.sendMessage(chat_id=update.message.chat_id, text='No me has dado ninguna orden, mi am@')
            help()
        elif command == "sayTo":
            message = update.message
            if message.sticker:
                bot.sendSticker(chat_id=groupChatId, sticker=message.sticker.file_id)
            else:
                text = message.text
                if "antonio" in text.lower():
                    text = "Antonio, como me molas"
                if text == "Fuck":
                    bot.sendMessage(chat_id=update.message.chat_id, text='Vaaale, Me callo')
                else:
                    filename = getAudioFromText(text)
                    bot.send_voice(groupChatId, open("/home/antonio/public/{}".format(filename), "rb"))
                    bot.sendMessage(chat_id=update.message.chat_id, text='😉')
            setChatCommand(chatId, None)
        elif command == "sing":
            if chatId not in chatData:
                songList = wrappers.searchInVK(update.message.text)
                replyTextTemplate = "Ok, esto es lo que me se:\n{}\n Dime un número."
                bot.sendMessage(chat_id=update.message.chat_id, text=replyTextTemplate.format("\n".join(["{}. {} ({})".format(i, song["name"], song["artist"]) for i, song in enumerate(songList[:5])])))
                chatData[chatId] = songList
                # bot.send_voice(groupChatId, open("/home/antonio/public/{}".format(filename), "rb"))
                # bot.sendMessage(chat_id=update.message.chat_id, text='😉')
            else:
                try:
                    songId = int(update.message.text)
                except Exception:
                    bot.sendMessage(chat_id=update.message.chat_id, text="No he pillado el número, así que paso de ti")
                    setChatCommand(chatId, None)
                    del chatData[chatId]
                bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.RECORD_AUDIO)
                tFile = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                tFile.close()
                r = requests.get(chatData[chatId][songId]["url"], stream=True)
                if r.status_code == 200:
                    with open(tFile.name, "wb") as f:
                        for chunk in r:
                            f.write(chunk)
                print(tFile.name)
                AudioSegment.from_mp3(tFile.name)[:30000].export(tFile.name, format="mp3")
                bot.send_voice(groupChatId, open(tFile.name, "rb"))
                del chatData[chatId]
                setChatCommand(chatId, None)
        elif command == "piropo":
            phrases = []
            with open("/home/antonio/piropos.txt") as iFile:
                for line in iFile:
                    phrases.append(line.rstrip())
            phrase = phrases[randint(0, len(phrases)-1)]
            try:
                filename = getAudioFromText(phrase.format(update.message.text))
                bot.send_voice(groupChatId, open("/home/antonio/public/{}".format(filename), "rb"))
            except Exception as ex:
                print(ex)
            setChatCommand(chatId, None)

    except Exception as ex:
        print(ex)

def sayTo(bot, update):
    try:
        chatId = update.message.chat.id
        bot.sendMessage(chat_id=update.message.chat_id, text='Vaaale. Qué quieres que le diga? (si me dices "Fuck" lo dejo todo)')
        setChatCommand(chatId, "sayTo")
    except Exception as ex:
        print(ex)

def sing(bot, update):
    try:
        chatId = update.message.chat.id
        bot.sendMessage(chat_id=update.message.chat_id, text='Pero... Venga... Qué quieres que cante (si me dices "Fuck" lo dejo todo)')
        setChatCommand(chatId, "sing")
    except Exception as ex:
        print(ex)


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
        bot.send_voice(groupChatId, open("/home/antonio/public/{}".format(filename), "rb"))
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
    try:
        chatId = update.message.chat.id
        bot.sendMessage(chat_id=update.message.chat_id, text='Haré lo mejor que pueda... A quién se lo dedico? (si me dices "Fuck" lo dejo todo)')
        setChatCommand(chatId, "piropo")
    except Exception as ex:
        print(ex)

def addDefensePhrase(bot, update):
    upDict = update.to_dict()

def audioTest(bot, update, update_queue=None):
    try:
        print("Testing audio files")
        text = " ".join(update.to_dict()["message"]["text"].split(" ")[1:])
        print("testing with {}".format(text))
        filename = getAudioFromText(text)
        print("The file url is: {}".format("/home/antonio/public/{}".format(filename)))
        bot.send_voice(update.message.chat_id, open("/home/antonio/public/{}".format(filename), "rb"))
    except Exception as ex:
        print(ex)

def llora(bot, update):
    try:
        print("llorando")
        bot.send_voice(groupChatId, open("/home/antonio/llanto.mp3", "rb"))
    except Exception as ex:
        print(ex)

def testButtons(bot, update, update_queue=None):
    try:
        print("Testing buttons")
        bot.sendMessage(chat_id=update.message.chat_id, text="Testing buttons", reply_markup=telegram.ReplyKeyboardMarkup([[KeyboardButton("Hola"), KeyboardButton("no")]]))
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
        \t/diles: Me haces decir cosas aunque no esté en absoluto de acuerdo
    """
    bot.sendMessage(chat_id=update.message.chat_id, text=helpText)

def describeMessage(bot, update, update_queue=None):
    bot.sendMessage(chat_id=update.message.chat_id, text="Escribe algo bonito")
    message = update_queue.get().message
    bot.sendMessage(chat_id=update.message.chat_id, text="{}".format(message.to_dict()))

def error(bot, update, err):
    bot.sendMessage(chat_id=update.message.chat_id, text="He petado de mala manera... Si podéis decírselo a Antonio")
    print('Update "%s" caused error "%s"' % (update, err))

start_handler = CommandHandler('start', start1)
dispatcher.add_handler(start_handler)

llora_handler = CommandHandler('llora', llora)
dispatcher.add_handler(llora_handler)

diles_handler = CommandHandler('diles', sayTo)
dispatcher.add_handler(diles_handler)

sing_handler = CommandHandler('sing', sing)
dispatcher.add_handler(sing_handler)

audioTest_handler = CommandHandler('audioTest', audioTest)
dispatcher.add_handler(audioTest_handler)

testButtons_handler = CommandHandler('butons', testButtons)
dispatcher.add_handler(testButtons_handler)

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

describe_handler = CommandHandler('describe', describeMessage)
dispatcher.add_handler(describe_handler)

speak_handler = CommandHandler('speak', speak)
dispatcher.add_handler(speak_handler)

dispatcher.add_handler(MessageHandler([Filters.text], reply_to_query))

# Timers
schedule.every().day.at("11:37").do(claratorio)


updater.start_polling()
print("Tontico is ready :)")
updater.idle()
