import re

from flask import jsonify, request, url_for

from . import app, db
from .constants import MAX_SHORT_LENGTH, SHORT_LINK_REGEX
from .models import URLMap
from .views import get_unique_short_id


class APIError(Exception):
    """Кастомный класс исключения для ошибок API."""

    def __init__(self, message, status_code=400):
        super().__init__()
        self.message = message
        self.status_code = status_code


@app.errorhandler(APIError)
def handle_invalid_usage(error):
    """Глобальный обработчик кастомных ошибок APIError."""
    return jsonify({'message': error.message}), error.status_code


@app.route('/api/id/', methods=['POST'])
def create_short_id():
    """Создает короткую ссылку на основе переданного JSON."""
    data = request.get_json(silent=True)

    if not data:
        raise APIError('Отсутствует тело запроса')

    if 'url' not in data or not data['url']:
        raise APIError('"url" является обязательным полем!')

    custom_id = data.get('custom_id')

    if custom_id:
        if (len(custom_id) > MAX_SHORT_LENGTH or
                not re.match(SHORT_LINK_REGEX, custom_id)):
            raise APIError('Указано недопустимое имя для короткой ссылки')

        if URLMap.query.filter_by(short=custom_id).first():
            raise APIError(
                'Предложенный вариант короткой ссылки уже существует.'
            )
    else:
        custom_id = get_unique_short_id()

    url_map = URLMap(original=data['url'], short=custom_id)
    db.session.add(url_map)
    db.session.commit()

    response_data = url_map.to_dict()
    response_data['short_link'] = url_for(
        'redirect_view',
        short_id=custom_id,
        _external=True
    )
    return jsonify(response_data), 201


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_url(short_id):
    """Возвращает оригинальный URL по короткому идентификатору."""
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        raise APIError('Указанный id не найден', 404)

    return jsonify({'url': url_map.original}), 200
