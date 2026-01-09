from flask import request

def user_self_url(user_id: int) -> str:
    return request.host_url.rstrip("/") + f"/users/{user_id}"

def friend_mini(user_id: int) -> dict:
    return {"U_ID": user_id, "self": user_self_url(user_id)}
