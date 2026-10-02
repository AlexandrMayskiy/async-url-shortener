import re

from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from .constants import (
    FORBIDDEN_SHORT_NAMES, MAX_SHORT_LENGTH, SHORT_LINK_REGEX
)
from .models import URLMap


class URLMapForm(FlaskForm):
    """Форма для сокращения длинных ссылок на главной странице."""

    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле')]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[Length(max=MAX_SHORT_LENGTH), Optional()]
    )
    submit = SubmitField('Создать')

    def validate_custom_id(self, field):
        """Валидация кастомного идентификатора короткой ссылки."""
        if field.data:
            if field.data in FORBIDDEN_SHORT_NAMES:
                raise ValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
            if not re.match(SHORT_LINK_REGEX, field.data):
                raise ValidationError(
                    'Указано недопустимое имя для короткой ссылки'
                )
            if URLMap.query.filter_by(short=field.data).first():
                raise ValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )


class FileUploadForm(FlaskForm):
    """Форма для загрузки файлов на Яндекс Диск по стандартам Практикума."""

    files = MultipleFileField('Выберите файлы')
    submit = SubmitField('Загрузить')
