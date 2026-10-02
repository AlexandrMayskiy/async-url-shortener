import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Базовый класс конфигурации приложения."""

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        'sqlite:///db.sqlite3'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-yacut-key')
    DISK_TOKEN = os.getenv('DISK_TOKEN')
    YADISK_API_BASE_URL = os.getenv(
        'YADISK_API_BASE_URL',
        'https://cloud-api.yandex.net'
    )
