from google.cloud import datastore
from flask import request

def art_self_url(art_id: int) -> str:
    return request.host_url.rstrip("/") + f"/arts/{art_id}"

def art_to_response(art: datastore.Entity) -> dict:
    art_id = art.key.id
    return {
        "A_ID": art_id,
        "A_Image": art.get("A_Image", ""),
        "A_Title": art.get("A_Title", ""),
        "A_Comments": art.get("A_Comments", []) or [],
        "A_Modified_Date": art.get("A_Modified_Date", ""),
        "A_Previous": art.get("A_Previous", None),
        "A_Is_Public": art.get("A_Is_Public", False),
        "User": art.get("User", None),
        "Galleries": art.get("Galleries", []) or [],
        "self": art_self_url(art_id),
    }

def art_mini_response(art: datastore.Entity) -> dict:
    art_id = art.key.id
    return {"A_ID": art_id, "self": art_self_url(art_id)}
