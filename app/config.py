import os
from dotenv import load_dotenv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=ROOT / ".env")

MONGO_URL = os.getenv("MONGO_URL", "")
MONGO_DB = os.getenv("MONGO_DB", "chatdb")
