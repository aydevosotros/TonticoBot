#!/usr/bin/python3
# -*- coding: utf8 -*-
import argparse
import sys
import os
import yaml
import logging

from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
import telegram


# Getting the logger instance
logger = logging.getLogger()
logger.setLevel(logging.INFO)
if not os.path.isdir(os.path.expanduser("~/log")):
    os.mkdir(os.path.expanduser("~/log"))
logPath = os.path.expanduser("~/log/TonticoHooker.log")
fileHandler = logging.FileHandler(logPath)
fileHandler.setFormatter(logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s'))
logger.addHandler(fileHandler)


updater = Updater("259443067:AAEime5UnPucBBXzt3jll5Oct4CTuHrMbX8")
bot = telegram.Bot("259443067:AAEime5UnPucBBXzt3jll5Oct4CTuHrMbX8")

def main():
    # Getting arguments and options
    parser = argparse.ArgumentParser()
    parser.add_argument("--logStdout", help="Active flag for getting the log in the standard output", action="store_true")
    parser.add_argument("--configFile", help="Select the file for configuration stuff", default="config.yaml")

    args = parser.parse_args()

    if args.logStdout:
        logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    config = yaml.load(open(args.configFile))
    print(bot.getChat(-172831566))

    updater = Updater(config["bot"]["token"])

    tontiBot = tontiBot.TontiBot(config["bot"]["token"])

    # Event suscription:
    dispatcher = updater.dispatcher

    # start_handler = CommandHandler('start', tontiBot.start)
    # dispatcher.add_handler(start_handler)
    #
    # llora_handler = CommandHandler('llora', tontiBot.llora)
    # dispatcher.add_handler(llora_handler)
    #
    # diles_handler = CommandHandler('diles', tontiBot.sayTo)
    # dispatcher.add_handler(diles_handler)
    #
    # sing_handler = CommandHandler('sing', tontiBot.sing)
    # dispatcher.add_handler(sing_handler)
    #
    # audioTest_handler = CommandHandler('audioTest', tontiBot.audioTest)
    # dispatcher.add_handler(audioTest_handler)
    #
    # testButtons_handler = CommandHandler('butons', tontiBot.testButtons)
    # dispatcher.add_handler(testButtons_handler)
    #
    # piropo_handler = CommandHandler('piropo', tontiBot.piropo)
    # dispatcher.add_handler(piropo_handler)
    #
    # greeting_handler = CommandHandler('greeting', tontiBot.saluda)
    # dispatcher.add_handler(greeting_handler)
    #
    # joke_handler = CommandHandler('chiste', tontiBot.joke)
    # dispatcher.add_handler(joke_handler)
    #
    # chatId_handler = CommandHandler('giveMeId', tontiBot.getChatId)
    # dispatcher.add_handler(chatId_handler)
    #
    # defense_handler = CommandHandler('meteteCon', tontiBot.defense)
    # dispatcher.add_handler(defense_handler)
    #
    # help_handler = CommandHandler('help', tontiBot.help)
    # dispatcher.add_handler(help_handler)
    #
    # describe_handler = CommandHandler('describe', tontiBot.describeMessage)
    # dispatcher.add_handler(describe_handler)
    #
    # speak_handler = CommandHandler('speak', tontiBot.speak)
    # dispatcher.add_handler(speak_handler)

    # updater.start_webhook(listen='127.0.0.1', port=5000, url_path='TOKEN1')
    # updater.bot.setWebhook(url='https://ialab.es/tontiBot',
    #                        certificate=open('cert.pem', 'rb'))

if __name__ == '__main__':
    main()
