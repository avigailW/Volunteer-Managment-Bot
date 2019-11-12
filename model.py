
from pymongo import MongoClient
import pymongo

client = MongoClient()

db = client.get_database("mechubarim_l'chaim_db")
volunteers = db.get_collection("volunteer")
areas = db.get_collection("areas")
requests_list = db.get_collection("requests")

areas.create_index([('name', pymongo.ASCENDING)], unique=True)
volunteers.create_index([('name', pymongo.ASCENDING)], unique=True)
requests_list.create_index([('request_id', pymongo.ASCENDING)], unique=True)

request_id = 0

#area_info :  {'name'}
#vol_info : {'name': , 'phone': , 'areas': [], 'notify': True , 'chat_id'}
#req_info : {'request_id' ,'description', 'area','status', 'is_done'}


def init_areas():
    area_list = ['Jerusalem', 'Tel Aviv', 'Haifa', 'Petach Tikva', 'Bnei Brak', 'Netanya', 'Ashdod']
    for area in area_list:
        info = {'name': area}
        areas.replace_one({'name': area}, info, upsert=True)

def get_all_areas():
    return areas.find()

def does_area_exist(area):
    return True if areas.find({'name': area}) else False

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
    info = {'request_id': request_id, 'description': description, 'area': area, 'status': 'open', 'is_done': False}
    request_id += 1
    requests_list.replace_one({'description': description}, info, upsert=True)

def update_volunteer_notification(name, notify):
    volunteers.update_one({'name': name}, {'$set': {'notify': notify}})

def update_request_status(req_id, staus):
    requests_list.update_one({'request_id': req_id}, {'$set': {'status': staus}})

def update_request_done(req_id):
    requests_list.update_one({'request_id': req_id}, {'$set': {'is_done': True}})

