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
import logging
import yaml
import gzip
import json
import datetime
import time
from tempfile import NamedTemporaryFile
from resources import seq2seq_model

# SQLAlchemy stuff
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import *

groupChatId = -216277721
chatCommandLock = Lock()
chatCommand = dict()
allowedLangsSpeech = ["en", "ca", "es"]
chatData = dict()

config = yaml.load(open("config.yaml"))
groupsChatPath = config["others"]["groupsChatPath"]


class TontiBot(object):
    """ Toti bot class """

    def __init__(self, botToken):
        logging.info("Initilizing TontiBot")
        self.botToken = botToken
        self.bot = telegram.Bot(botToken)
        self.updater = Updater(botToken)

        self._suscribeHandlers()
        logging.info("Starting poolling...")
        self.updater.start_polling()
        # self.updater.start_webhook(listen='127.0.0.1', port=5000, url_path='tontibot')
        # self.updater.bot.setWebhook(webhook_url='https://ialab.es/tontibot',
        #                        certificate=open('/home/antonio/keys/cert.pem', 'rb'))
        # logging.info("Setting idle for precissing requets")
        self.updater.idle()


    def _suscribeHandlers(self):
        '''
        It takes the bot updater and suscribe handlers for available
         functionalities
        '''
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(MessageHandler(Filters.text, self.reply_to_query))
        dispatcher.add_handler(CommandHandler('diles', self.sayTo))
        dispatcher.add_handler(CommandHandler('chiste', self.joke))
        logging.debug("All handlers suscribed")

    def _sendVoice(self, idChat, text):
        lang = detect(text)
        if lang not in allowedLangsSpeech:
            lang = "es"
        lang = "es-es" if lang == "es" else lang
        with NamedTemporaryFile() as fp:
            gTTS(text=text, lang=lang).write_to_fp(fp)
            fp.seek(0)
            self.bot.send_voice(idChat, fp)


    def reply_to_query(self, bot, update):
        logging.debug(update.to_dict())
        try:
            chatId = update.message.chat.id
            command = getChatCommand(chatId)
            entry = {
                "timestamp": time.mktime(datetime.datetime.now().timetuple()),
                "userId": update.to_dict()["message"]["from"]["id"],
                "text": update.message.text
            }
            with gzip.open(os.path.join(groupsChatPath, "{}.txt.gz".format(chatId)), "at") as oFile:
                json.dump(entry, oFile)
                oFile.write("\n")
            logging.debug("Gotten a query {}, {}".format(chatId, command))
            if command is None:
            #     bot.sendMessage(chat_id=update.message.chat_id, text='No me has dado ninguna orden, mi am@')
            #     help(bot, update)
                return
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
                        self._sendVoice(groupChatId, text)
                        bot.sendMessage(chat_id=update.message.chat_id, text='😉')
                setChatCommand(chatId, None)
            elif command == "piropo":
                phrases = []
                with open("/home/antonio/piropos.txt") as iFile:
                    for line in iFile:
                        phrases.append(line.rstrip())
                phrase = phrases[randint(0, len(phrases)-1)]
                self._sendVoice(groupChatId, phrase)
                setChatCommand(chatId, None)

        except Exception as ex:
            print("Error on reply text: {}\n{}\n{}".format(ex, bot, update))

    def sayTo(self, bot, update):
        try:
            chatId = update.message.chat.id
            bot.sendMessage(chat_id=update.message.chat_id, text='Vaaale. Qué quieres que le diga? (si me dices "Fuck" lo dejo todo)')
            setChatCommand(chatId, "sayTo")
        except Exception as ex:
            print(ex)

    def joke(self, bot, update):
        joke = bs.BeautifulSoup(
            requests.get("http://www.chistescortos.eu/random", "html.parser").text,
            "lxml").find_all("a", "oldlink")[3].text
        joke += " jejejejejejeje"
        self._sendVoice(groupChatId, joke)

    def registerGroup(self, idGroupChat):
        self.session.add(Group(idGroupChat))


def setChatCommand(chatId, command):
    with chatCommandLock:
        chatCommand[chatId] = command

def getChatCommand(chatId):
    if chatId in chatCommand:
        return chatCommand[chatId]


def saluda(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Hola {}!".format(update.to_dict()["message"]["from"]["first_name"]))


def claratorio():
    bot.sendMessage(chat_id=-172831566, text="Clara... No es la hora de la foto? :wink:")
    # bot.sendMessage(chat_id=166282912, text="Clara, es la hora...")

def piropo(bot, update):
    try:
        chatId = update.message.chat.id
        bot.sendMessage(chat_id=update.message.chat_id, text='Haré lo mejor que pueda... A quién se lo dedico? (si me dices "Fuck" lo dejo todo)')
        setChatCommand(chatId, "piropo")
    except Exception as ex:
        print(ex)


def testButtons(bot, update, update_queue=None):
    try:
        print("Testing buttons")
        bot.sendMessage(chat_id=update.message.chat_id, text="Testing buttons", reply_markup=telegram.ReplyKeyboardMarkup([[KeyboardButton("Ho
