from flask import Blueprint, request, jsonify
from google.cloud import datastore
from datetime import datetime, timezone

from contracts import (
    require_accept_json,
    require_content_type_json,
    reject_body,
    require_json_body,
    error_response,
)

from arts.repo import create_art_entity, get_art as repo_get_art, list_arts, delete_art as repo_delete_art, update_art as repo_update_art
from arts.serializers import art_to_response, art_mini_response
from users.repo import get_user as repo_get_user
from utils.urls import user_self_url 

def iso_utc_now() -> str:
    # Example: 2026-01-09T05:12:34Z
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def create_arts_blueprint(ds: datastore.Client) -> Blueprint:
    bp = Blueprint("arts", __name__)

    @bp.post("/arts")
    @require_accept_json
    @require_content_type_json
    @require_json_body()
    def create_art():
        body = request.parsed_json

        user_obj = body.get("User")
        if not isinstance(user_obj, dict) or "U_ID" not in user_obj:
            return error_response(400, "Bad Request: missing required fields.")

        creator_id = user_obj.get("U_ID")
        if not isinstance(creator_id, int):
            return error_response(400, "Bad Request: invalid User.U_ID.")

        creator = repo_get_user(ds, creator_id)
        if creator is None:
            return error_response(404, "Not Found")

        art = create_art_entity(ds, {
            "A_Image": body.get("A_Image", ""),
            "A_Title": body.get("A_Title", ""),
            "A_Comments": body.get("A_Comments", []) or [],
            "A_Modified_Date": iso_utc_now(),
            "A_Previous": body.get("A_Previous", None),
            "A_Is_Public": body.get("A_Is_Public", False),

            "User": {"U_ID": creator_id, "self": user_self_url(creator_id)},
            "Galleries": [],
        })

        return jsonify(art_to_response(art)), 201

    @bp.get("/arts")
    @require_accept_json
    @reject_body
    def get_arts():
        limit = request.args.get("limit", default=None, type=int)
        offset = request.args.get("offset", default=0, type=int)

        if offset < 0 or (limit is not None and limit < 0):
            return error_response(400, "Bad Request: limit/offset must be non-negative.")

        arts = list_arts(ds, limit=limit, offset=offset)
        return jsonify({"Arts": [art_mini_response(a) for a in arts]}), 200

    @bp.get("/arts/<int:art_id>")
    @require_accept_json
    @reject_body
    def get_art(art_id: int):
        art = repo_get_art(ds, art_id)
        if art is None:
            return error_response(404, "Not Found")
        return jsonify(art_to_response(art)), 200
    
    @bp.delete("/arts/<int:art_id>")
    @require_accept_json
    @reject_body
    def delete_art(art_id: int):
        if not repo_delete_art(ds, art_id):
            return error_response(404, "Not Found")
        return "", 204
    
    @bp.put("/arts/<int:art_id>")
    @require_accept_json
    @require_content_type_json
    @require_json_body(required_fields=["A_Title", "A_Image", "A_Is_Public", "A_Comments"])
    def put_art(art_id: int):
        body = request.parsed_json

        art = repo_get_art(ds, art_id)
        if art is None:
            return error_response(404, "Not Found")

        # Disallow changing ownership / relationships via PUT
        if "User" in body or "Galleries" in body or "A_ID" in body or "self" in body:
            return error_response(400, "Bad Request")

        updates = {
            "A_Title": body["A_Title"],
            "A_Image": body["A_Image"],
            "A_Is_Public": body["A_Is_Public"],
            "A_Comments": body["A_Comments"],
        }

        updated = repo_update_art(ds, art, updates)
        return jsonify(art_to_response(updated)), 200
    
    @bp.patch("/arts/<int:art_id>")
    @require_accept_json
    @require_content_type_json
    @require_json_body(at_least_one_of=["A_Title", "A_Image", "A_Is_Public", "A_Comments"])
    def patch_art(art_id: int):
        body = request.parsed_json

        art = repo_get_art(ds, art_id)
        if art is None:
            return error_response(404, "Not Found")

        # Disallow patching ownership / relationships
        if "User" in body or "Galleries" in body or "A_ID" in body or "self" in body:
            return error_response(400, "Bad Request")

        allowed = ["A_Title", "A_Image", "A_Is_Public", "A_Comments"]
        updates = {k: body[k] for k in allowed if k in body}

        updated = repo_update_art(ds, art, updates)
        return jsonify(art_to_response(updated)), 200


    
    @bp.get("/arts/<int:art_id>/galleries")
    @require_accept_json
    @reject_body
    def list_art_galleries(art_id: int):
        art = repo_get_art(ds, art_id)
        if art is None:
            return error_response(404, "Not Found")

        return jsonify({"Galleries": art.get("Galleries", []) or []}), 200

    return bp
