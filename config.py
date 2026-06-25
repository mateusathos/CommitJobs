import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")
    CRON_SECRET = os.getenv("CRON_SECRET")