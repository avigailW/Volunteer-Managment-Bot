from model import add_request, get_all_open_requests, get_volunteer_areas, get_open_requests_in_area


def add_request_to_db(description, area):
    request_id = add_request(description,area)
    return request_id


def get_all_requests_from_DB():
    all_requests = get_all_open_requests()
    request_list = []
    for request in all_requests:
        extract_request_data = f"#{request['request_id'] } {request['description']}   {request['area']}"
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
    area = update.callback_query.message.text.split(":")[1].strip(" ")
    all_requests.append([(ar['request_id'], ar['description'], ar['area']) for ar in get_open_requests_in_area(area)])
    return all_requests

