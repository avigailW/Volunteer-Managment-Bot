import logging
import requests
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, \
    InlineQueryResultGif, KeyboardButton, ReplyKeyboardMarkup, Location
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, Filters, Updater, CallbackQueryHandler

def set_notification_status(update,context):
    context.user_data["notification"]= not context.user_data["notification"]


def get_notification_status(update,context):
    return context.user_data["notification"]
