from http import HTTPStatus
from flask import jsonify, render_template

from . import app, db
from .exceptions import APIError


@app.errorhandler(APIError)
def handle_api_error(error):
    """Возвращает ошибку API в формате JSON."""
    return jsonify({'message': error.message}), error.status_code


@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(error):
    """Отображает кастомную HTML-страницу при ошибке 404."""
    return render_template('404.html'), HTTPStatus.NOT_FOUND


@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_error(error):
    """Откатывает транзакции БД и возвращает HTML ошибки 500."""
    db.session.rollback()
    return (
        render_template('500.html'),
        HTTPStatus.INTERNAL_SERVER_ERROR
    )
