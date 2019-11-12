import secret_settings
import general_logic
import logging
import requests
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, \
    InlineQueryResultGif, KeyboardButton, ReplyKeyboardMarkup, Location, CallbackQuery
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, Filters, Updater, CallbackQueryHandler, \
    ConversationHandler

from model import does_area_exist, add_volunteer, get_all_areas, init_areas
from request_logic import get_all_requests_from_DB, add_request_to_db
from volunteer_logic import get_notification_status, create_new_volunteer, \
    get_areas_of_volunteers, update_notification_status, delete_area_from_volunteer_DB, add_area_to_volunteer_DB

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
    request_keyboard = telegram.KeyboardButton(text="Open new request")
    volunteer_keyboard = telegram.KeyboardButton(text="Volunteer")
    custom_keyboard = [[request_keyboard, volunteer_keyboard]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True,one_time_keyboard=False)
    context.bot.send_message(chat_id=chat_id,
                             text=f"""Welcome!
/volunteer - to volunteer, 
/request_help - to open a request help,
/show_all_areas - to show all our areas,
/show_all_open_requests - to show all the open requests""",
                             reply_markup=reply_markup)
    create_new_volunteer(update, context)



def volunteer(update: Update, context: CallbackContext):
    #TODO: check if volunteer exist. if he exist-
    chat_id = update.effective_chat.id
    logger.info(f"> Volunteer chat #{chat_id}")

    all_areas_list=[ar['name'] for ar in get_all_areas()]
    areas_of_volunteers=get_areas_of_volunteers(update,context)
    number_areas=len(areas_of_volunteers)
    notification_bottun_status = get_notification_status(update, context)
    keyboard_status = "Disable" if notification_bottun_status else "Enable"
    message_status = "are" if notification_bottun_status else "are not"
    keyboard_areas=[]
    keyboard_line = []
    for i, area in enumerate(all_areas_list,1):
        check_sign = "✔" if area in areas_of_volunteers else "⭕"  ##TODO: change list
        keyboard_line.append(InlineKeyboardButton(f"{check_sign} {area.capitalize()}", callback_data=f'area_{i}'))
        if i%3==0 :
            keyboard_areas.append(keyboard_line)
            keyboard_line=[]

    keyboard_areas.append([InlineKeyboardButton(f"{keyboard_status} notifications", callback_data='change_notification_status')])
    reply_markup_areas = InlineKeyboardMarkup(keyboard_areas)
    message_volunteer = context.bot.send_message(chat_id=chat_id,text=f"""{number_areas} areas selected. You {message_status} receiving notifications.""",
                                       reply_markup=reply_markup_areas)
    context.user_data["volunteer_message_id"] = message_volunteer.message_id


def request_help(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Open new request chat #{chat_id}")
    context.bot.send_message(chat_id=chat_id, text=f"""Enter your request description + contact info.""")


def show_notification_message(update, context):
    chat_id = update.effective_chat.id

    areas_of_volunteers = get_areas_of_volunteers(update, context)
    number_areas = len(areas_of_volunteers)
    all_areas_list=[ar['name'] for ar in get_all_areas()]
    notification_bottun_status = get_notification_status(update, context)
    keyboard_status = "Disable" if notification_bottun_status else "Enable"
    message_status = "are" if notification_bottun_status else "are not"
    keyboard_areas=[]
    keyboard_line = []
    for i, area in enumerate(all_areas_list, 1):
        check_sign = "✔" if area in areas_of_volunteers else "⭕"  ##TODO: change list
        keyboard_line.append(InlineKeyboardButton(f"{check_sign} {area.capitalize()}", callback_data=f'area_{i}'))
        if i % 3 == 0:
            keyboard_areas.append(keyboard_line)
            keyboard_line = []
    keyboard_areas.append([InlineKeyboardButton(f"{keyboard_status} notifications", callback_data='change_notification_status')])

    reply_markup_areas = InlineKeyboardMarkup(keyboard_areas)
    context.bot.editMessageReplyMarkup(chat_id=chat_id, message_id=context.user_data["volunteer_message_id"],
                                          reply_markup=reply_markup_areas)
    context.bot.editMessageText(chat_id=chat_id, message_id=context.user_data["volunteer_message_id"],
                                  text=f"""{number_areas} areas selected. You {message_status} receiving notifications.""",
                                       reply_markup=reply_markup_areas)




def callback_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if update.callback_query.data == "change_notification_status":
        update_notification_status(update, context)
        show_notification_message(update,context)
    if update.callback_query.data[:5]=="area_":
        index_button=int(update.callback_query.data[5:])-1
        all_areas_list = [ar['name'] for ar in get_all_areas()]
        areas_of_volunteer = get_areas_of_volunteers(update, context)
        area_name=all_areas_list[index_button]
        if area_name in areas_of_volunteer: #remove area
            delete_area_from_volunteer_DB(update,context,area_name)
        else: ## add area
            add_area_to_volunteer_DB(update,context,area_name)
        show_notification_message(update, context)


def show_all_areas(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Show all areas chat #{chat_id}")
    list_all_area= general_logic.get_all_areas_from_DB()
    str_all_areas=""
    for i,area in enumerate(list_all_area):
        str_all_areas+=f"{i+1}. {area.capitalize()}\n"
    context.bot.send_message(chat_id=chat_id, text=str_all_areas)




def show_all_requests(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Show all requests chat #{chat_id}")
    list_all_requests = get_all_requests_from_DB()
    str_all_requests = ""
    for i, request in enumerate(list_all_requests,1):
        str_all_requests += f"{request}\n"
    context.bot.send_message(chat_id=chat_id, text=str_all_requests)


def command_handler_buttons(update: Update, context: CallbackContext):
    if update.message.text == "Volunteer":
        volunteer(update, context)
    elif update.message.text == "Open new request":
        request_help(update, context)
    else:  # entered a description
        request = update.message.text
        context.bot.send_message(chat_id=update.message.chat_id, text=f'You have opened new request:'
                                                                      f' {request}\n'
                                                                      f'To approve, specify where the collect area is:')
        #######
        context.bot.send_message(chat_id=update.message.chat_id, text=add_request_to_db(update))

def main():
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('volunteer', volunteer))
    dispatcher.add_handler(CommandHandler('request_help', request_help))
    dispatcher.add_handler(CommandHandler('show_all_areas', show_all_areas))
    dispatcher.add_handler(CommandHandler('show_all_open_requests', show_all_requests))

    dispatcher.add_handler(CallbackQueryHandler(callback_handler, pass_chat_data=True))
    dispatcher.add_handler(MessageHandler(Filters.text, command_handler_buttons))

    logger.info("* Start polling...")
    updater.start_polling()  # Starts polling in a background thread.
    updater.idle()  # Wait until Ctrl+C is pressed
    logger.info("* Bye!")


if __name__ == '__main__':
    main()
