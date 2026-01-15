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

from galleries.repo import create_gallery_entity, get_gallery as repo_get_gallery, list_galleries, delete_gallery as repo_delete_gallery, update_gallery as repo_update_gallery,add_art_to_gallery, remove_art_from_gallery
from galleries.serializers import gallery_to_response, gallery_mini_response
from users.repo import get_user as repo_get_user
from utils.urls import user_self_url
from arts.repo import get_art as repo_get_art, add_gallery_to_art, remove_gallery_from_art
from arts.serializers import art_mini_response


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
    
    @bp.get("/galleries/<int:gallery_id>/arts")
    @require_accept_json
    @reject_body
    def list_gallery_arts(gallery_id: int):
        gallery = repo_get_gallery(ds, gallery_id)
        if gallery is None:
            return error_response(404, "Not Found")

        # Already stored as mini objects
        return jsonify({"Arts": gallery.get("Arts", []) or []}), 200
    
    @bp.put("/galleries/<int:gallery_id>")
    @require_accept_json
    @require_content_type_json
    @require_json_body(required_fields=["G_Name", "G_Is_Public", "G_Comments"])
    def put_gallery(gallery_id: int):
        body = request.parsed_json

        gallery = repo_get_gallery(ds, gallery_id)
        if gallery is None:
            return error_response(404, "Not Found")

        # Disallow changing ownership / relationships via PUT
        if "User" in body or "Arts" in body or "G_ID" in body or "self" in body:
            return error_response(400, "Bad Request")

        updates = {
            "G_Name": body["G_Name"],
            "G_Is_Public": body["G_Is_Public"],
            "G_Comments": body["G_Comments"],
        }

        updated = repo_update_gallery(ds, gallery, updates)
        return jsonify(gallery_to_response(updated)), 200
    
    @bp.patch("/galleries/<int:gallery_id>")
    @require_accept_json
    @require_content_type_json
    @require_json_body(at_least_one_of=["G_Name", "G_Is_Public", "G_Comments"])
    def patch_gallery(gallery_id: int):
        body = request.parsed_json

        gallery = repo_get_gallery(ds, gallery_id)
        if gallery is None:
            return error_response(404, "Not Found")

        # Disallow patching ownership / relationships
        if "User" in body or "Arts" in body or "G_ID" in body or "self" in body:
            return error_response(400, "Bad Request")

        allowed = ["G_Name", "G_Is_Public", "G_Comments"]
        updates = {k: body[k] for k in allowed if k in body}

        updated = repo_update_gallery(ds, gallery, updates)
        return jsonify(gallery_to_response(updated)), 200
    
    @bp.patch("/galleries/<int:gallery_id>/arts/<int:art_id>")
    @require_accept_json
    @reject_body
    def add_art_relationship(gallery_id: int, art_id: int):
        gallery = repo_get_gallery(ds, gallery_id)
        art = repo_get_art(ds, art_id)

        if gallery is None or art is None:
            return error_response(404, "Not Found")

        # prevent duplicates
        existing = gallery.get("Arts", []) or []
        if any(a.get("A_ID") == art_id for a in existing):
            return error_response(403, "The art is already in the gallery")

        # Build minis (absolute self URLs)
        art_mini = art_mini_response(art)
        gallery_mini = gallery_mini_response(gallery)

        # Update both sides
        add_art_to_gallery(ds, gallery, art_mini)
        add_gallery_to_art(ds, art, gallery_mini)

        return jsonify(gallery_to_response(gallery)), 200
    
    @bp.delete("/galleries/<int:gallery_id>/arts/<int:art_id>")
    @require_accept_json
    @reject_body
    def remove_art_relationship(gallery_id: int, art_id: int):
        gallery = repo_get_gallery(ds, gallery_id)
        art = repo_get_art(ds, art_id)

        if gallery is None or art is None:
            return error_response(404, "Not Found")

        existing = gallery.get("Arts", []) or []
        if not any(a.get("A_ID") == art_id for a in existing):
            return error_response(403, "The art is not in the gallery")

        remove_art_from_gallery(ds, gallery, art_id)
        remove_gallery_from_art(ds, art, gallery_id)

        return "", 204

    return bp
