import os
from pathlib import Path

from flask import Flask, request, jsonify
from google.cloud import datastore
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

app = Flask(__name__)

# Prefer emulator project id, fall back to GOOGLE_CLOUD_PROJECT
project_id = os.getenv("DATASTORE_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
if not project_id:
    project_id = "bearsty-local"  # safe default for local dev/interview

# Ensure google-cloud libraries see a project consistently
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)

ds = datastore.Client(project=project_id)

USER_KIND = "User"

def user_to_response(user_entity: datastore.Entity) -> dict:
    """Convert a Datastore entity into the JSON response we send back."""
    user_id = user_entity.key.id 
    return {
        "U_ID": user_id,
        "U_Name": user_entity.get("U_Name", ""),
        "U_Auth_Sub": user_entity.get("U_Auth_Sub", ""),
        "U_Profile": user_entity.get("U_Profile", ""),
        "self": f"/users/{user_id}",
    }


@app.get("/")
def health_check():
    return {"status": "ok"}, 200

# CREATE
@app.post("/users")
def create_user():
    body = request.get_json(silent=True) or {}

    key = ds.key(USER_KIND)
    user = datastore.Entity(key=key)

    user.update({
        "U_Name": body.get("U_Name", ""),
        "U_Auth_Sub": body.get("U_Auth_Sub", ""),
        "U_Profile": body.get("U_Profile", ""),
    })

    ds.put(user) 

    return jsonify(user_to_response(user)), 201


# READ
@app.get("/users/<int:user_id>")
def get_user(user_id: int):
    key = ds.key(USER_KIND, user_id)
    user = ds.get(key)

    if user is None:
        return jsonify({"error": "Not Found"}), 404

    return jsonify(user_to_response(user)), 200


# UPDATE
@app.put("/users/<int:user_id>")
def update_user(user_id: int):
    key = ds.key(USER_KIND, user_id)
    user = ds.get(key)

    if user is None:
        return jsonify({"error": "Not Found"}), 404

    body = request.get_json(silent=True) or {}

    user.update({
        "U_Name": body.get("U_Name", user.get("U_Name", "")),
        "U_Auth_Sub": body.get("U_Auth_Sub", user.get("U_Auth_Sub", "")),
        "U_Profile": body.get("U_Profile", user.get("U_Profile", "")),
    })

    ds.put(user)

    return jsonify(user_to_response(user)), 200


# DELETE
@app.delete("/users/<int:user_id>")
def delete_user(user_id: int):
    key = ds.key(USER_KIND, user_id)
    user = ds.get(key)

    if user is None:
        return jsonify({"error": "Not Found"}), 404

    ds.delete(key)

    return "", 204


if __name__ == "__main__":
    app.run(port=8080, debug=True)
