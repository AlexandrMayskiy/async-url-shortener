"""Глобальные константы проекта YaCut."""

import string

SHORT_ID_LENGTH = 6
MAX_SHORT_LENGTH = 16
SHORT_LINK_REGEX = rf'^[A-Za-z0-9]{{1,{MAX_SHORT_LENGTH}}}$'
FORBIDDEN_SHORT_NAMES = ('files', 'api', 'static')
DEFAULT_API_URL = 'https://yandex.net'
BASE_CHARACTERS = string.ascii_letters + string.digits
GENERATE_ATTEMPTS_LIMIT = 10
