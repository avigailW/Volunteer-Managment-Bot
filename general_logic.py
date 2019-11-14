from model import get_all_areas, init_areas

def get_all_areas_from_DB():
    list_areas_dict=get_all_areas()
    list_areas=[area['name'] for area in list_areas_dict]
    return list_areas

def add_area_to_list(update,context,text):
    context.user_data["areas_list"].append(text)

