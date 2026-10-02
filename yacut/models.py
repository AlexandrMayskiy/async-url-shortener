from datetime import datetime, timezone

from . import db


class URLMap(db.Model):
    """Модель базы данных для хранения и сопоставления ссылок."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.Text, nullable=False)
    short = db.Column(db.String(16), unique=True, nullable=False)
    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    def to_dict(self):
        """Сериализует объект модели в словарь для ответов API."""
        return {
            'url': self.original,
            'short_link': self.short
        }

    def from_dict(self, data):
        """Десериализует данные из JSON-запроса API в поля объекта."""
        if 'url' in data:
            self.original = data['url']
        if 'custom_id' in data:
            self.short = data['custom_id']
