from model import add_request


def add_request_to_db(update, context):
    request_id = add_request(update.message.text,"jerusalem")
    return f'Your request has been saved. Case #{request_id} for follow up.'