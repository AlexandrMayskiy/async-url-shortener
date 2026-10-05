import re
from datetime import datetime, timezone
import random

from flask import url_for

from . import db
from .constants import (
    BASE_CHARACTERS, GENERATE_ATTEMPTS_LIMIT, MAX_SHORT_LENGTH,
    SHORT_ID_LENGTH, SHORT_LINK_REGEX
)
from .exceptions import APIError


class URLMap(db.Model):
    """Модель базы данных для хранения и сопоставления ссылок."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.Text, nullable=False)
    short = db.Column(
        db.String(MAX_SHORT_LENGTH),
        unique=True,
        nullable=False
    )
    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    @staticmethod
    def get_unique_short_id():
        """Генерирует случайный уникальный короткий ID."""
        for _ in range(GENERATE_ATTEMPTS_LIMIT):
            short_id = ''.join(
                random.choice(BASE_CHARACTERS)
                for _ in range(SHORT_ID_LENGTH)
            )
            if not URLMap.get(short_id):
                return short_id
        raise APIError('Превышено количество попыток генерации ID.')

    @classmethod
    def get(cls, short_id):
        """Возвращает объект URLMap по короткому идентификатору."""
        return cls.query.filter_by(short=short_id).first()

    @classmethod
    def create(cls, original, custom_id=None):
        """Валидирует данные, сохраняет в БД и возвращает объект."""
        if custom_id:
            if (len(custom_id) > MAX_SHORT_LENGTH or
                    not re.match(SHORT_LINK_REGEX, custom_id)):
                raise APIError('Указано недопустимое имя для короткой ссылки')

            if cls.get(custom_id):
                raise APIError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
        else:
            custom_id = cls.get_unique_short_id()

        url_map = cls(original=original, short=custom_id)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    def get_short_url(self):
        """Формирует и возвращает полный короткий URL-адрес."""
        return url_for(
            'redirect_view',
            short_id=self.short,
            _external=True
        )

    def to_dict(self):
        """Сериализует объект в словарь с полным URL."""
        return {
            'url': self.original,
            'short_link': self.get_short_url()
        }
