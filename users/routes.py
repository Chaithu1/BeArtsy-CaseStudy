from flask import Blueprint, request, jsonify
from google.cloud import datastore

from contracts import (
    require_accept_json,
    require_content_type_json,
    reject_body,
    require_json_body,
    error_response,
)

from utils.time_utils import random_time_today_gmt
from users.repo import create_user_entity, get_user as repo_get_user, delete_user as repo_delete_user, list_users, add_friend as repo_add_friend, remove_friend as repo_remove_friend
from users.serializers import user_to_response, user_mini_response

def create_users_blueprint(ds: datastore.Client) -> Blueprint:
    bp = Blueprint("users", __name__)

    @bp.post("/users")
    @require_accept_json
    @require_content_type_json
    @require_json_body()
    def create_user():
        body = request.parsed_json
        userinfo = body.get("userinfo")

        if not isinstance(userinfo, dict):
            return error_response(400, "The request object is missing the required userinfo attribute")

        user = create_user_entity(ds, {
            "U_Name": userinfo.get("email") or userinfo.get("name") or "",
            "U_Auth_Sub": userinfo.get("sub") or "",
            "U_Profile": userinfo.get("picture") or "Image Path/File",

            "Arts": [],
            "Galleries": [],
            "U_Friends": [],
            "Pixel_Amount": 10,
            "Time_Length": 10,
            "Is_Custom_Time": False,
            "Custom_Time_Alarm": random_time_today_gmt(),
            "Today_Time": random_time_today_gmt(),
        })

        return jsonify(user_to_response(user)), 201

    @bp.get("/users/<int:user_id>")
    @require_accept_json
    @reject_body
    def get_user(user_id: int):
        user = repo_get_user(ds, user_id)
        if user is None:
            return error_response(404, "Not Found")
        return jsonify(user_to_response(user)), 200

    @bp.delete("/users/<int:user_id>")
    @require_accept_json
    @reject_body
    def delete_user(user_id: int):
        if not repo_delete_user(ds, user_id):
            return error_response(404, "Not Found")
        return "", 204

    @bp.get("/users")
    @require_accept_json
    @reject_body
    def get_all_users():
        users = list_users(ds)
        return jsonify({"Users": [user_mini_response(u) for u in users]}), 200

    @bp.patch("/users")
    @require_accept_json
    @require_content_type_json
    @require_json_body(required_fields=["request_method"])
    def patch_all_users():
        body = request.parsed_json
        if body.get("request_method") != "automatically":
            return error_response(400, "BadRequest:Should not be triggered manually")

        users = list_users(ds)
        for u in users:
            u["Today_Time"] = random_time_today_gmt()
            ds.put(u)

        return jsonify(user_to_response(users[0])) if users else jsonify({}), 200
    
    @bp.patch("/users/<int:user_id1>/users/<int:user_id2>")
    @require_accept_json
    @reject_body
    def add_friend(user_id1: int, user_id2: int):
        if user_id1 == user_id2:
            return error_response(403, "You cannot add yourself as a friend")

        user1 = repo_get_user(ds, user_id1)
        user2 = repo_get_user(ds, user_id2)

        if user1 is None or user2 is None:
            return error_response(404, "Not Found")

        friends1 = user1.get("U_Friends", []) or []
        if user_id2 in friends1:
            return error_response(403, "The user is already a friend")

        repo_add_friend(ds, user1, user_id2)

        return jsonify(user_to_response(user1)), 200
    
    @bp.delete("/users/<int:user_id1>/users/<int:user_id2>")
    @require_accept_json
    @reject_body
    def remove_friend(user_id1: int, user_id2: int):
        if user_id1 == user_id2:
            return error_response(403, "You cannot remove yourself as a friend")

        user1 = repo_get_user(ds, user_id1)
        user2 = repo_get_user(ds, user_id2)

        if user1 is None or user2 is None:
            return error_response(404, "Not Found")

        friends1 = user1.get("U_Friends", []) or []
        if user_id2 not in friends1:
            return error_response(403, "The user is not a friend")

        repo_remove_friend(ds, user1, user_id2)
        return "", 204

    return bp
