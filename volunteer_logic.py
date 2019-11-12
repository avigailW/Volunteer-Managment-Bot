import logging
import requests
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, \
    InlineQueryResultGif, KeyboardButton, ReplyKeyboardMarkup, Location
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, Filters, Updater, CallbackQueryHandler

from model import update_volunteer_notification, add_volunteer, get_notification_status_from_DB, get_volunteer_areas


def set_notification_status(update,context):
    chat_id = update.effective_chat.id
    update_volunteer_notification(chat_id)

def get_notification_status(update,context):
    chat_id = update.effective_chat.id
    return get_notification_status_from_DB(chat_id)

def create_new_volunteer(update,context):
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    id = update.effective_chat.id
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
    add_volunteer(name, " ", [] , False,id)

def get_areas_of_volunteers(update,context):
    chat_id = update.effective_chat.id
    return get_volunteer_areas(chat_id)