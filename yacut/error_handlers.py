from flask import jsonify, render_template

from . import app, db
from .api_views import APIError


@app.errorhandler(APIError)
def handle_api_error(error):
    """Возвращает ошибку API в формате JSON."""
    return jsonify({'message': error.message}), error.status_code


@app.errorhandler(404)
def page_not_found(error):
    """Отображает кастомную HTML-страницу при ошибке 404."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Откатывает транзакции БД и возвращает HTML ошибки 500."""
    db.session.rollback()
    return render_template('500.html'), 500
