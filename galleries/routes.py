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

from galleries.repo import create_gallery_entity, get_gallery as repo_get_gallery, list_galleries, delete_gallery as repo_delete_gallery
from galleries.serializers import gallery_to_response, gallery_mini_response
from users.repo import get_user as repo_get_user
from utils.urls import user_self_url


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def create_galleries_blueprint(ds: datastore.Client) -> Blueprint:
    bp = Blueprint("galleries", __name__)

    @bp.post("/galleries")
    @require_accept_json
    @require_content_type_json
    @require_json_body()
    def create_gallery():
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

        gallery = create_gallery_entity(ds, {
            "Arts": [],
            "User": {"U_ID": creator_id, "self": user_self_url(creator_id)},
            "G_Name": body.get("G_Name", "Untitled"),
            "G_Creation_Date": iso_utc_now(),
            "G_Comments": body.get("G_Comments", []) or [],
            "G_Profile": body.get("G_Profile", ""),
            "G_Is_Public": body.get("G_Is_Public", False),
        })

        return jsonify(gallery_to_response(gallery)), 201

    @bp.get("/galleries")
    @require_accept_json
    @reject_body
    def get_galleries():
        limit = request.args.get("limit", default=None, type=int)
        offset = request.args.get("offset", default=0, type=int)

        if offset < 0 or (limit is not None and limit < 0):
            return error_response(400, "Bad Request: limit/offset must be non-negative.")

        galleries = list_galleries(ds, limit=limit, offset=offset)
        return jsonify({"Galleries": [gallery_mini_response(g) for g in galleries]}), 200

    @bp.get("/galleries/<int:gallery_id>")
    @require_accept_json
    @reject_body
    def get_gallery(gallery_id: int):
        gallery = repo_get_gallery(ds, gallery_id)
        if gallery is None:
            return error_response(404, "Not Found")
        return jsonify(gallery_to_response(gallery)), 200
    
    @bp.delete("/galleries/<int:gallery_id>")
    @require_accept_json
    @reject_body
    def delete_gallery(gallery_id: int):
        if not repo_delete_gallery(ds, gallery_id):
            return error_response(404, "Not Found")
        return "", 204

    return bp
