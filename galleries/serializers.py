from google.cloud import datastore
from flask import request

def gallery_self_url(gallery_id: int) -> str:
    return request.host_url.rstrip("/") + f"/galleries/{gallery_id}"

def gallery_to_response(g: datastore.Entity) -> dict:
    gallery_id = g.key.id
    return {
        "G_ID": gallery_id,
        "Arts": g.get("Arts", []) or [],
        "User": g.get("User", None),
        "G_Name": g.get("G_Name", "Untitled"),
        "G_Creation_Date": g.get("G_Creation_Date", ""),
        "G_Comments": g.get("G_Comments", []) or [],
        "G_Profile": g.get("G_Profile", ""),
        "G_Is_Public": g.get("G_Is_Public", False),
        "self": gallery_self_url(gallery_id),
    }

def gallery_mini_response(g: datastore.Entity) -> dict:
    gallery_id = g.key.id
    return {"G_ID": gallery_id, "self": gallery_self_url(gallery_id)}
