#!/usr/bin/python3
# -*- coding: utf8 -*-
import argparse
import sys
import os
import yaml
import logging
from tonticobot import TontiBot

from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
import telegram

from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)


# Getting the logger instance
logger = logging.getLogger()
logger.setLevel(logging.INFO)
if not os.path.isdir(os.path.expanduser("~/log")):
    os.mkdir(os.path.expanduser("~/log"))
logPath = os.path.expanduser("~/log/TonticoHooker.log")
fileHandler = logging.FileHandler(logPath)
fileHandler.setFormatter(logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s'))
logger.addHandler(fileHandler)


def status_update(bot, update):
    logger.info("Gotten update")
    logger.info(update.to_dict())

def describeMessage(bot, update):
    print("Hola")
    logger.info(update.to_dict())

def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        # remove update.message.chat_id from conversation list
        print(error)
    except BadRequest:
        # handle malformed requests - read more below!
        print(error)
    except TimedOut:
        # handle slow connection problems
        print(error)
    except NetworkError:
        # handle other connection problems
        print(error)
    except ChatMigrated as e:
        # the chat_id of a group has changed, use e.new_chat_id instead
        print(error)
    except TelegramError:
        # handle all other telegram related errors
        print(error)

def main():
    # Getting arguments and options
    parser = argparse.ArgumentParser()
    parser.add_argument("--logStdout", help="Active flag for getting the log in the standard output", action="store_true")
    parser.add_argument("--configFile", help="Select the file for configuration stuff", default="config.yaml")

    args = parser.parse_args()

    if args.logStdout:
        logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    config = yaml.load(open(args.configFile))

    updater = Updater(config["bot"]["token"])
    logger.info("Starting bot")
    tBot = TontiBot(config["bot"]["token"])
    # print(tBot.getChat(-172831566))

    groupsChatPath = config["others"]["groupsChatPath"]
    if not os.path.exists(groupsChatPath):
        os.makedirs(groupsChatPath)

    logger.info("Starting bot")
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler([Filters.text], tontiBot.reply_to_query))
    diles_handler = CommandHandler('diles', tontiBot.sayTo)
    dispatcher.add_handler(diles_handler)

    joke_handler = CommandHandler('chiste', tontiBot.joke)
    dispatcher.add_handler(joke_handler)

    logger.info("Starting server")
    updater.start_polling()
