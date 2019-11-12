import secret_settings
import logging
import requests
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, \
    InlineQueryResultGif, KeyboardButton, ReplyKeyboardMarkup, Location
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, Filters, Updater, CallbackQueryHandler

import volunteer_logic as vl

logging.basicConfig(
    format='[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

updater = Updater(token=secret_settings.BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Start chat #{chat_id}")
    request_keyboard = telegram.KeyboardButton(text="request_help")
    volunteer_keyboard = telegram.KeyboardButton(text="volunteer")
    custom_keyboard = [[request_keyboard, volunteer_keyboard]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    context.bot.send_message(chat_id=chat_id,
                             text=f"""Welcome! if you are new volunteer: volunteer, to request help: request_help""",
                             reply_markup=reply_markup)
    vl.create_new_volunteer(update, context)

def register_volunteer(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Volunteer chat #{chat_id}")
    context.user_data["notification"] = False
    keyboard = [[InlineKeyboardButton(f"Enable notifications", callback_data='change_notification_status')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message=context.bot.send_message(chat_id=chat_id,
                             text="""You are not receiving notifications.""",
                             reply_markup=reply_markup)
    context.user_data["notification_message_id"] = message.message_id

def request_help(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Volunteer chat #{chat_id}")
    context.bot.send_message(chat_id=chat_id, text=f"""Enter your request description + contact info.""")
    

def show_notification_message(update, context):
    chat_id = update.effective_chat.id
    notification_bottun_status = vl.get_notification_status(update, context)
    keyboard_status = "Disable" if notification_bottun_status else "Enable"
    message_status = "are" if notification_bottun_status else "are not"
    keyboard = [[InlineKeyboardButton(f"{keyboard_status} notifications", callback_data='change_notification_status')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_reply_markup(chat_id=chat_id,message_id=context.user_data["notification_message_id"],
                             reply_markup=reply_markup)
    context.bot.edit_message_text(chat_id=chat_id, message_id=context.user_data["notification_message_id"],
                                          text=f"""You {message_status} receiving notifications.""",reply_markup=reply_markup)

def callback_handler(update: Update, context: CallbackContext):
    if update.callback_query.data == "change_notification_status":
        vl.set_notification_status(update, context)
        show_notification_message(update,context)

def command_handler_buttons(update: Update, context: CallbackContext):

    if update.message['text'] == "volunteer":
        register_volunteer(update, context)
    elif update.message['text'] == "request_help":
        request_help(update, context)

def main():
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('volunteer', register_volunteer))
    dispatcher.add_handler(CommandHandler('request_help', request_help))
    dispatcher.add_handler(CallbackQueryHandler(callback_handler, pass_chat_data=True))
    dispatcher.add_handler(MessageHandler(Filters.text, command_handler_buttons))
    logger.info("* Start polling...")
    updater.start_polling()  # Starts polling in a background thread.
    updater.idle()  # Wait until Ctrl+C is pressed
    logger.info("* Bye!")


if __name__ == '__main__':
    main()
