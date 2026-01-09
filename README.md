# BeArtsy-CaseStudy
 BeArtsy sends users a daily, random time notification, inviting them to the website for a spontaneous pixel art session. 
This repository implements the **BeArtsy backend REST API** using **Flask** and the **Google Cloud Datastore Emulator**, following the provided specification.

Note: Due to time constraints, Auth as well as Art-Gallery relationships were not implemented :(

## Tech Stack

- Python 3.11
- Flask
- Google Cloud Datastore Emulator
- google-cloud-datastore
- python-dotenv

## Project Structure
```
├── app.py # App entry point / blueprint registration
├── config.py # Datastore + environment setup
├── contracts.py # API contract enforcement (Accept, Content-Type, body rules)
├── users/ # Users + Friends endpoints
├── arts/ # Arts endpoints
├── galleries/ # Galleries endpoints
├── utils/ # Shared helpers (time + URL utilities)
├── api-tests.http # VS Code REST Client test file
├── requirements.txt
└── README.md

```
## Setup Instructions

### 1) Create and activate a virtual environment

**Windows (PowerShell):**
```
python -m venv venv
.\venv\Scripts\Activate.ps1
```
**macOS / Linux**
```
python3 -m venv venv
source venv/bin/activate
```

### 2) Install dependencies
```
pip install -r requirements.txt
```

### 3) Configure environment variables
Create a .env file in the project root:
```
DATASTORE_EMULATOR_HOST=localhost:8081
DATASTORE_PROJECT_ID=bearsty-local
```

### 4) Start the Datastore Emulator
```
gcloud beta emulators datastore start --host-port=localhost:8081
```

### 5) Run the API server
```
python app.py
```

The server will run at http://localhost:8080
