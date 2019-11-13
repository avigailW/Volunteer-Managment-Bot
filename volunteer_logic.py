import logging
import requests
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, \
    InlineQueryResultGif, KeyboardButton, ReplyKeyboardMarkup, Location
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, Filters, Updater, CallbackQueryHandler

from model import update_volunteer_notification, add_volunteer, get_notification_status_from_DB, get_volunteer_areas, \
    add_area_to_volunteer, delete_area_from_volunteer, check_if_volunteer_exist


def update_notification_status(update,context):
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
    if not check_if_volunteer_exist(update.effective_chat.id):
        add_volunteer(name, " ", [] , False,id)

def get_areas_of_volunteers(update,context):
    chat_id = update.effective_chat.id
    return get_volunteer_areas(chat_id)

def add_area_to_volunteer_DB(update,context, area):
    chat_id = update.effective_chat.id
    add_area_to_volunteer(chat_id,area)

def delete_area_from_volunteer_DB(update,context, area):
    chat_id = update.effective_chat.id
    delete_area_from_volunteer(chat_id, area)