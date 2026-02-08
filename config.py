import os

DB_FILE = os.environ.get("DB_FILE", "/Volumes/SSD_APFS/VoIP_App/Server/Flask_Server/users.db")
FIREBASE_CRED_PATH = os.environ.get("FIREBASE_CRED_PATH", "/Volumes/SSD_APFS/VoIP_App/Server/Flask_Server/secrets/firebase_service_account.json")
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*")
ONLINE_WINDOW_SEC = int(os.environ.get("ONLINE_WINDOW_SEC", "30"))