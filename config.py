import os
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import datastore

def init_datastore_client() -> datastore.Client:
    load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

    project_id = os.getenv("DATASTORE_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        project_id = "bearsty-local"

    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
    return datastore.Client(project=project_id)
