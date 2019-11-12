import logging
import requests
import telegram

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, \
    InlineQueryResultGif, KeyboardButton, ReplyKeyboardMarkup, Location
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, Filters, Updater, CallbackQueryHandler

import model


def set_notification_status(update,context):
    context.user_data["notification"]= not context.user_data["notification"]


def get_notification_status(update,context):
    return context.user_data["notification"]

def create_new_volunteer(update,context):
    #message1 = update.message.chat
    message = update['message']
    chat = message['chat']
    id = chat['id']
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    name = ""
    try:
         name = first_name + " "
    except:
        first_name = "@"
        name = first_name + " "
    try:
        name += last_name
    except:
        last_name = "@"
        name += last_name
    model.add_volunteer(name, " ", [] , False,id)
