from http import HTTPStatus
from flask import jsonify, request

from . import app
from .exceptions import APIError
from .models import URLMap


@app.route('/api/id/', methods=['POST'])
def create_short_id():
    """Создает короткую ссылку на основе переданного JSON."""
    data = request.get_json(silent=True)

    if not data:
        raise APIError('Отсутствует тело запроса')

    if 'url' not in data or not data['url']:
        raise APIError('"url" является обязательным полем!')

    try:
        url_map = URLMap.create(
            original=data['url'],
            custom_id=data.get('custom_id')
        )
    except APIError as error:
        raise error
    except Exception as error:
        raise APIError(str(error), HTTPStatus.BAD_REQUEST)

    return jsonify(url_map.to_dict()), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_url(short_id):
    """Возвращает оригинальный URL по короткому идентификатору."""
    url_map = URLMap.get(short_id)

    if not url_map:
        raise APIError('Указанный id не найден', HTTPStatus.NOT_FOUND)

    return jsonify({'url': url_map.original}), HTTPStatus.OK
