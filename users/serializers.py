from google.cloud import datastore
from utils.urls import friend_mini, user_self_url


def user_to_response(user_entity: datastore.Entity) -> dict:
    user_id = user_entity.key.id

    friend_ids = user_entity.get("U_Friends", []) or []
    friends = [friend_mini(fid) for fid in friend_ids]

    return {
        "U_ID": user_id,
        "U_Name": user_entity.get("U_Name", ""),
        "U_Auth_Sub": user_entity.get("U_Auth_Sub", ""),
        "U_Profile": user_entity.get("U_Profile", "Image Path/File"),

        "Arts": user_entity.get("Arts", []) or [],
        "Galleries": user_entity.get("Galleries", []) or [],
        "U_Friends": friends,

        "Pixel_Amount": user_entity.get("Pixel_Amount", 10),
        "Time_Length": user_entity.get("Time_Length", 10),

        "Is_Custom_Time": user_entity.get("Is_Custom_Time", False),
        "Custom_Time_Alarm": user_entity.get("Custom_Time_Alarm", ""),
        "Today_Time": user_entity.get("Today_Time", ""),

        "self": user_self_url(user_id),
    }

def user_mini_response(user_entity: datastore.Entity) -> dict:
    user_id = user_entity.key.id
    return {"U_ID": user_id, "self": user_self_url(user_id)}
