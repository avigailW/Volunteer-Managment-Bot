from model import add_request, get_all_open_requests, get_request, get_requests_area, get_notified_volunteers_in_area, \
    update_request_status, get_volunteer_areas, get_open_requests_in_area


def update_request_status_db(request_id,status):
    update_request_status(request_id,status)


def volunteers_to_publish_request(request_id, context):
    description = get_request(request_id)[0]['description']
    request_area = get_requests_area(request_id)
    volunteers = get_notified_volunteers_in_area(request_area)
    return description, volunteers



def add_request_to_db(context):
   description = context.user_data["request_description"]
   area = context.user_data["request_area"]
   request_id = add_request(description,area)
   description, volunteers = volunteers_to_publish_request(request_id, context)
   return request_id, description, volunteers


def get_all_requests_from_DB():
    all_requests = get_all_open_requests()
    request_list = []
    for request in all_requests:
        extract_request_data = f"#{request['request_id'] } \t *{request['description']}*   {request['area']}"
        request_list.append(extract_request_data)
    return request_list

def get_requests_in_volunteer_area(update,context):
    areas = get_volunteer_areas(update.effective_chat.id)
    all_requests = []
    for area in areas:
        all_requests.append([(ar['request_id'],ar['description'], ar['area'])for ar in get_open_requests_in_area(area)])
    return all_requests

def get_requests_in_area(update,context):
    all_requests = []
    area = update.callback_query.message.text.split(":")[1].strip()
    all_requests.append([(ar['request_id'], ar['description'], ar['area']) for ar in get_open_requests_in_area(area)])
    return all_requests