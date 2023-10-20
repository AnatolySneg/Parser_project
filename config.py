from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

R_HOST = os.environ.get("R_HOST")

MANAGER_SECRET = os.environ.get("MANAGER_SECRET")

RADIS_HOST = os.environ.get("RADIS_HOST")
RADIS_PORT = os.environ.get("RADIS_PORT")