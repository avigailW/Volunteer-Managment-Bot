from pymongo import MongoClient
import pymongo

client = MongoClient()

db = client.get_database("mechubarim_l'chaim_db")
volunteers = db.get_collection("volunteer")
areas = db.get_collection("areas")
requests_list = db.get_collection("requests")
# requests_list.remove({})

areas.create_index([('name', pymongo.ASCENDING)], unique=True)
volunteers.create_index([('chat_id', pymongo.ASCENDING)], unique=True)
requests_list.create_index([('request_id', pymongo.ASCENDING)], unique=True)

request_id = requests_list.find().count()

#area_info :  {'name'}
#vol_info : {'name': , 'phone': , 'areas': [], 'notify': True , 'chat_id'}
#req_info : {'request_id' ,'description', 'area','status', 'is_done'}


def init_areas():
    area_list = ['jerusalem', 'tel aviv', 'haifa', 'petach tikva', 'bnei brak', 'netanya', 'ashdod']
    for area in area_list:
        info = {'name': area}
        areas.replace_one({'name': area}, info, upsert=True)

def get_all_areas():
    return areas.find({})

def does_area_exist(area):
    return True if areas.find({'name': area.lower()}).count() else False

def get_volunteer_areas(chat_id):
    return  volunteers.find({'chat_id': chat_id})[0]['areas']

def check_if_volunteer_exist(chat_id):
    return volunteers.find({'chat_id': chat_id}).count() >0

# receives one area, returns list of all volunteers whom their notification is on in that area
def get_notified_volunteers_in_area(area):
    return volunteers.find({'areas': area, 'notify': True})

def get_all_open_requests():
    return requests_list.find({'status': 'open'})

# receives one area, returns list of all requests in that area
def get_open_requests_in_area(area):
    return requests_list.find({'area': area, 'status': 'open'})


#name = user_name, my_areas = list of areas, notify = boolean variable
def add_volunteer(name, phone, my_areas, notify, chat_id):
    info = {'name': name, 'phone': phone, 'areas': my_areas, 'notify': notify, 'chat_id': chat_id}
    volunteers.replace_one({'name': name}, info, upsert=True)

def add_request(description, area):
    global request_id
    request_id += 1
    info = {'request_id': request_id, 'description': description, 'area': area, 'status': 'open', 'is_done': False}
    while True:
        try:
            requests_list.replace_one({'description': description}, info, upsert=True)
            break
        except (pymongo.errors.DuplicateKeyError):
            request_id += 1
            info = {'request_id': request_id, 'description': description, 'area': area, 'status': 'open',
                    'is_done': False}
            requests_list.replace_one({'description': description}, info, upsert=True)



    return request_id

def update_volunteer_notification(chat_id):
    volunteers.update_one({'chat_id': chat_id}, {'$set': {'notify': not get_notification_status_from_DB(chat_id)}})

def update_request_status(req_id, staus):
    requests_list.update_one({'request_id': req_id}, {'$set': {'status': staus}})

def update_request_done(req_id):
    requests_list.update_one({'request_id': req_id}, {'$set': {'is_done': True}})

def get_notification_status_from_DB(chat_id):
    return volunteers.find({'chat_id': chat_id})[0]['notify']

def add_area_to_volunteer(chat_id, area):
    volunteers.update_one({'chat_id': chat_id}, {'$push': {'areas': area}})

def delete_area_from_volunteer(chat_id, area):
    volunteers.update_one({'chat_id': chat_id}, {'$pull': {'areas': area}})

def get_requests_area(request_id):
   return requests_list.find({'request_id': request_id})[0]['area']

def get_request(request_id):
   return requests_list.find({'request_id': request_id})


init_areas()