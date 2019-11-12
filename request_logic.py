from model import add_request, get_all_open_requests


def add_request_to_db(update):
    request_id = add_request(update.message.text,"jerusalem")
    return f'Your request has been saved. Case #{request_id} for follow up.'

def get_all_requests_from_DB():
    all_requests = get_all_open_requests()
    request_list = []
    for request in all_requests:
        extract_request_data = f"#{request['request_id'] } {request['description']}   {request['area']}"
        request_list.append(extract_request_data)
    return request_list
