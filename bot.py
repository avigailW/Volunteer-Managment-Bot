import secret_settings
import general_logic
import logging
import requests
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, \
    InlineQueryResultGif, KeyboardButton, ReplyKeyboardMarkup, Location
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, Filters, Updater, CallbackQueryHandler, \
    ConversationHandler

from model import does_area_exist, add_volunteer, get_all_areas
from volunteer_logic import get_notification_status, set_notification_status

logging.basicConfig(
    format='[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

updater = Updater(token=secret_settings.BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher


def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Start chat #{chat_id}")
    context.user_data["notification"]=False
    request_keyboard = telegram.KeyboardButton(text="/request_help")
    volunteer_keyboard = telegram.KeyboardButton(text="/volunteer")
    custom_keyboard = [[request_keyboard, volunteer_keyboard]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    context.bot.send_message(chat_id=chat_id,
                             text=f"""Welcome!
/volunteer - to volunteer, 
/request_help - to open a request help,
/show_all_areas - to show all our areas""",
                             reply_markup=reply_markup)



def volunteer(update: Update, context: CallbackContext):
    #TODO: check if volunteer exist. if he exist-
    chat_id = update.effective_chat.id
    logger.info(f"> Volunteer chat #{chat_id}")
    # context.user_data["notification"] = get_notification_status(update,context)

    # context.user_data["status_process"]="volunteer"
#     keyboard = [[InlineKeyboardButton(f"Enable notifications", callback_data='change_notification_status')]]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     message=context.bot.send_message(chat_id=chat_id,
#                              text=f"""In which areas do you want to volunteer?
# No areas selected.
# You are not receiving notifications.""",
#                              reply_markup=reply_markup)
#     context.user_data["notification_message_id"]=message.message_id

    all_areas_list=get_all_areas()
    keyboard_areas=[[ InlineKeyboardButton(f"⭕ {i} {ar['name']}", callback_data=f'area_{i}')]for i,ar in enumerate(all_areas_list)]
    reply_markup_areas = InlineKeyboardMarkup(keyboard_areas)
    message_area = context.bot.send_message(chat_id=chat_id,text=f"""0 areas selected.""",
                                       reply_markup=reply_markup_areas)
    context.user_data["areas_volunteer_message_id"] = message_area.message_id


def request_help(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Volunteer chat #{chat_id}")
    context.bot.send_message(chat_id=chat_id, text=f"""Enter your request description + contact info.""")


def show_notification_message(update, context):
    chat_id = update.effective_chat.id
    # number_selected_areas = get_list_areas_by_volunteer()
    context.user_data["areas_list"]=[]
    notification_bottun_status = get_notification_status(update, context)
    keyboard_status = "Disable" if notification_bottun_status else "Enable"
    message_status = "are" if notification_bottun_status else "are not"
    keyboard = [[InlineKeyboardButton(f"{keyboard_status} notifications", callback_data='change_notification_status')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_reply_markup(chat_id=chat_id,message_id=context.user_data["notification_message_id"],
                             reply_markup=reply_markup)
    context.bot.edit_message_text(chat_id=chat_id, message_id=context.user_data["notification_message_id"],
                                          text=f"""In which areas do you want to volunteer?
No areas selected.
You {message_status} receiving notifications.""",reply_markup=reply_markup)



def callback_handler(update: Update, context: CallbackContext):
    if update.callback_query.data == "change_notification_status":
        set_notification_status(update, context)
        show_notification_message(update,context)

def show_all_areas(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Show all areas chat #{chat_id}")
    list_all_area= general_logic.get_all_areas_from_DB()
    str_all_areas=""
    for i,area in enumerate(list_all_area):
        str_all_areas+=f"{i+1}. {area.capitalize()}\n"
    context.bot.send_message(chat_id=chat_id, text=str_all_areas)


def text_hendler(update: Update, context: CallbackContext):
    text = update.message.text
    chat_id = update.effective_chat.id
    if context.user_data["status_process"]=="volunteer":
        areas_list=[]
        for ar in text.split(','):
            if not does_area_exist(ar.strip()):
                context.bot.send_message(chat_id=chat_id, text=f"{ar.strip()} is not exist area, please enter again all your areas.")
            else:
                areas_list.append(ar.strip())
        areas_list=list(set(areas_list))

        logger.info(f" Add areas {areas_list} to volunteer #{chat_id}")
    if context.user_data["status_process"] == "request_help":
        area_for_help=text


def main():
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('volunteer', volunteer))
    dispatcher.add_handler(CommandHandler('request_help', request_help))
    dispatcher.add_handler(CommandHandler('show_all_areas', show_all_areas))
    dispatcher.add_handler(CallbackQueryHandler(callback_handler, pass_chat_data=True))
    dispatcher.add_handler(MessageHandler(Filters.text, text_hendler))

    logger.info("* Start polling...")
    updater.start_polling()  # Starts polling in a background thread.
    updater.idle()  # Wait until Ctrl+C is pressed
    logger.info("* Bye!")


if __name__ == '__main__':
    main()
