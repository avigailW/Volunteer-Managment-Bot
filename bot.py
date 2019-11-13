import secret_settings
import general_logic
import logging
from termcolor import colored
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, \
    InlineQueryResultGif, KeyboardButton, ReplyKeyboardMarkup, Location, CallbackQuery
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, Filters, Updater, CallbackQueryHandler, \
    ConversationHandler
from settings import colors
from model import does_area_exist, add_volunteer, get_all_areas, init_areas, get_request
from request_logic import get_all_requests_from_DB, add_request_to_db, update_request_status_db, \
    get_requests_in_volunteer_area
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
    context.user_data["request_status"] = "no status"
    request_keyboard = telegram.KeyboardButton(text="Open new request")
    volunteer_keyboard = telegram.KeyboardButton(text="Volunteer")
    custom_keyboard = [[request_keyboard, volunteer_keyboard]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=False)
    # context.bot.setChatPhoto(chat_id=chat_id, photo=open(r"C:\Users\efrat2\Hackaton\xt-bareket-bot-hackathon-efrat_avigail_esti\images\logo.png", 'rb'))
    context.bot.sendPhoto(chat_id=chat_id,photo=open(r"C:\Users\efrat2\Hackaton\xt-bareket-bot-hackathon-efrat_avigail_esti\images\immage2.jpg",'rb'),
                            caption=f"""Welcome to our project bot!
                            
For using the bot: 

/volunteer - to volunteer,
/request_help - to open a request help,
/show_all_areas - to show all our areas,
/show_all_open_requests - to show all the open requests,
/requests_in_my_areas - to show all opened requests in your selected areas,
/requests_by_area - to show all opened requests in a selected area,
/about_us - about "connected to life" """,
                             reply_markup=reply_markup)
    create_new_volunteer(update, context)


def volunteer(update: Update, context: CallbackContext):
    # TODO: check if volunteer exist. if he exist-
    chat_id = update.effective_chat.id
    logger.info(f"> Volunteer chat #{chat_id}")

    all_areas_list = [ar['name'] for ar in get_all_areas()]
    areas_of_volunteers = get_areas_of_volunteers(update, context)
    number_areas = len(areas_of_volunteers)
    notification_bottun_status = get_notification_status(update, context)
    keyboard_status = "Disable" if notification_bottun_status else "Enable"
    message_status = "are" if notification_bottun_status else "are not"
    keyboard_areas = []
    keyboard_line = []
    for i, area in enumerate(all_areas_list, 1):
        check_sign = "✔" if area in areas_of_volunteers else "⭕"  ##TODO: change list
        keyboard_line.append(InlineKeyboardButton(f"{check_sign} {area.capitalize()}", callback_data=f'area_{i}'))
        if i % 3 == 0:
            keyboard_areas.append(keyboard_line)
            keyboard_line = []

    keyboard_areas.append(
        [InlineKeyboardButton(f"{keyboard_status} notifications", callback_data='change_notification_status')])
    reply_markup_areas = InlineKeyboardMarkup(keyboard_areas)
    message_volunteer = context.bot.send_message(chat_id=chat_id,
                                                 text=f"""{number_areas} areas selected. You {message_status} receiving notifications.""",
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
    all_areas_list = [ar['name'] for ar in get_all_areas()]
    notification_bottun_status = get_notification_status(update, context)
    keyboard_status = "Disable" if notification_bottun_status else "Enable"
    message_status = "are" if notification_bottun_status else "are not"
    keyboard_areas = []
    keyboard_line = []
    for i, area in enumerate(all_areas_list, 1):
        check_sign = "✔" if area in areas_of_volunteers else "⭕"  ##TODO: change list
        keyboard_line.append(InlineKeyboardButton(f"{check_sign} {area.capitalize()}", callback_data=f'area_{i}'))
        if i % 3 == 0:
            keyboard_areas.append(keyboard_line)
            keyboard_line = []
    keyboard_areas.append(
        [InlineKeyboardButton(f"{keyboard_status} notifications", callback_data='change_notification_status')])

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
        show_notification_message(update, context)
    if update.callback_query.data[:5] == "area_":
        index_button = int(update.callback_query.data[5:]) - 1
        all_areas_list = [ar['name'] for ar in get_all_areas()]
        areas_of_volunteer = get_areas_of_volunteers(update, context)
        area_name = all_areas_list[index_button]
        if area_name in areas_of_volunteer:  # remove area
            delete_area_from_volunteer_DB(update, context, area_name)
        else:  ## add area
            add_area_to_volunteer_DB(update, context, area_name)
        show_notification_message(update, context)
    if update.callback_query.data[:7]=="r_area_":
        for row in update.callback_query.message.reply_markup.inline_keyboard:
            for btn in row:
                if btn["callback_data"]==update.callback_query.data:
                    context.user_data["request_area"]=btn["text"][2:].lower()
        update_areas_for_request(update, context)

    if update.callback_query.data=="confirm_area_for_request":
        request_id, description, volunteers = add_request_to_db(context)
        context.user_data["message_accept_chat_message_id"]=[]
        context.bot.send_message(chat_id=update.callback_query.message.chat.id,text=f'Your request has been saved. Your case is #{request_id} for follow up.')
        for vol in volunteers:
           reply_markup_areas = InlineKeyboardMarkup([[InlineKeyboardButton(f"🖐 accept", callback_data=f'accept_request')]])
           message_accept = context.bot.send_message(chat_id=vol['chat_id'], text=f'NOTIFICATION!\ncase #{request_id}: {description}.',
                                              reply_markup=reply_markup_areas)
           context.user_data["message_accept_chat_message_id"].append((vol['chat_id'],message_accept.message_id,request_id))

    if update.callback_query.data=="accept_request":
        for user_d in context.user_data["message_accept_chat_message_id"]:
            context.bot.editMessageText(f"case #{user_d[2]} was taken.",chat_id=user_d[0],message_id=user_d[1])
            update_request_status_db(user_d[2],'accepted')



def show_all_areas(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Show all areas chat #{chat_id}")
    list_all_area = general_logic.get_all_areas_from_DB()
    str_all_areas = ""
    for i, area in enumerate(list_all_area):
        str_all_areas += f"{i + 1}. {area.capitalize()}\n"
    context.bot.send_message(chat_id=chat_id, text=str_all_areas)


def show_all_requests(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Show all requests chat #{chat_id}")
    list_all_requests = get_all_requests_from_DB()
    str_all_requests = ""
    for i, request in enumerate(list_all_requests, 1):
        str_all_requests += f"{request}\n"
    context.bot.send_message(chat_id=chat_id, text=str_all_requests)

def update_areas_for_request(update, context):
    chat_id = update.effective_chat.id
    all_areas_list = [ar['name'] for ar in get_all_areas()]
    keyboard_areas = []
    keyboard_line = []
    for i, area in enumerate(all_areas_list, 1):
        sign_check= '✔' if (area==context.user_data["request_area"]) else '⭕'
        keyboard_line.append(InlineKeyboardButton(f"{sign_check} {area.capitalize()}", callback_data=f'r_area_{i}'))
        if i % 3 == 0:
            keyboard_areas.append(keyboard_line)
            keyboard_line = []
    keyboard_areas.append(
        [InlineKeyboardButton(f"confirm area", callback_data=f'confirm_area_for_request')])  # TODO::bold
    reply_markup_areas = InlineKeyboardMarkup(keyboard_areas)

    context.bot.editMessageReplyMarkup(chat_id=chat_id, message_id=context.user_data["message_area_request"],
                                       reply_markup=reply_markup_areas)
    context.bot.editMessageText(chat_id=chat_id, message_id=context.user_data["message_area_request"],
                                text=f'You have opened new request:\n'
                                     f'{context.user_data["request_description"]}\n'
                                     f'Your request area is : '
                                     f'{context.user_data["request_area"]}',
                                     reply_markup=reply_markup_areas)




def command_handler_buttons(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if update.message.text == "Volunteer":
        volunteer(update, context)

    elif update.message.text == "Open new request":
        request_help(update, context)
        context.user_data["request_status"] = "Open new request"

    elif context.user_data["request_status"] == "Open new request":  # entered a description
        request_description = update.message.text
        context.user_data["request_description"]=request_description
        context.user_data["request_status"] = "no status"

        all_areas_list = [ar['name'] for ar in get_all_areas()]
        keyboard_areas = []
        keyboard_line = []
        for i, area in enumerate(all_areas_list, 1):
            keyboard_line.append(InlineKeyboardButton(f"⭕ {area.capitalize()}", callback_data=f'r_area_{i}'))
            if i % 3 == 0:
                keyboard_areas.append(keyboard_line)
                keyboard_line = []
        keyboard_areas.append([InlineKeyboardButton(f"confirm area", callback_data=f'confirm_area_for_request')])#TODO::bold
        reply_markup_areas = InlineKeyboardMarkup(keyboard_areas)

        message=context.bot.send_message(chat_id=chat_id,text=f'You have opened new request:\n'
                                                                      f'{request_description}\n'
                                                                      f'To approve, specify where the collect area is:',
                                 reply_markup=reply_markup_areas)
        context.user_data["message_area_request"]=message.message_id


def requests_in_wanted_areas(update: Update, context: CallbackContext):

    chat_id = update.effective_chat.id
    logger.info(f"> requests_in_wanted_areas #{chat_id} ")

    list_requests = get_requests_in_volunteer_area(update,context)
    str_all_requests = ""
    for request in list_requests:
        for r in request:
            str_all_requests += f"#{r[0] } : {r[1]}  {r[2]}\n"
    context.bot.send_message(chat_id=chat_id, text=str_all_requests)
    update_areas_for_request(update, context,'confirm_area_for_request','r_area_')


def requests_by_area(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> requests_by_area #{chat_id} ")

    ###TODO CODE SHOLED BE IN A FUNCTION
    all_areas_list = [ar['name'] for ar in get_all_areas()]
    keyboard_areas = []
    keyboard_line = []
    for i, area in enumerate(all_areas_list, 1):
        keyboard_line.append(InlineKeyboardButton(f"⭕ {area.capitalize()}", callback_data=f'r_A_area_{i}'))
        if i % 3 == 0:
            keyboard_areas.append(keyboard_line)
            keyboard_line = []
    keyboard_areas.append(
        [InlineKeyboardButton(f"confirm area", callback_data=f'confirm_area_for_search')])
    reply_markup_areas = InlineKeyboardMarkup(keyboard_areas)

    message = context.bot.send_message(chat_id=chat_id, text=f'Select an area to show requests in that area:',reply_markup=reply_markup_areas)
    context.user_data["message_area_request"] = message.message_id


def about_us(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> about us #{chat_id} ")
    context.bot.send_message(chat_id=chat_id, text=f'about us')


def main():
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('volunteer', volunteer))
    dispatcher.add_handler(CommandHandler('request_help', request_help))
    dispatcher.add_handler(CommandHandler('show_all_areas', show_all_areas))
    dispatcher.add_handler(CommandHandler('show_all_open_requests', show_all_requests))
    dispatcher.add_handler(CommandHandler('requests_in_my_areas', requests_in_wanted_areas))
    dispatcher.add_handler(CommandHandler('requests_by_area', requests_by_area))
    dispatcher.add_handler(CommandHandler('about_us', about_us))

    dispatcher.add_handler(CallbackQueryHandler(callback_handler, pass_chat_data=True))
    dispatcher.add_handler(MessageHandler(Filters.text, command_handler_buttons))




    logger.info("* Start polling...")
    updater.start_polling()  # Starts polling in a background thread.
    updater.idle()  # Wait until Ctrl+C is pressed
    logger.info("* Bye!")


if __name__ == '__main__':
    main()
