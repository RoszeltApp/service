import base64
import hmac
import json
from datetime import datetime, timedelta
from fastapi import Request
from fastapi.security import HTTPBearer
from starlette.responses import JSONResponse

from app import config


class ValidationError(Exception):
    def __init__(self, status_code: int, msg: str):
        self.status_code = status_code
        self.msg = msg


class Msg:
    INVALID_EMAIL = 'Некорректный формат электронной почты.'
    INVALID_PHONE = 'Некорректный формат номера телефона.'
    INVALID_ACCOUNT = 'Пользователя не существует'
    INVALID_PASSWORD = 'Неверный логин или пароль'
    EMAIL_ALREADY_EXIST = 'Поставщик с указанной электронной почтой уже существует в таблице.'
    PHONE_ALREADY_EXIST = 'Поставщик с указанным номером телефона уже существует в таблице.'
    SUPPLIER_CREATED = 'Поставщик добавлен в таблицу.'
    WRONG_EMAIL_OR_PASSWORD = 'Неверный адрес электронной почты или пароль.'
    UNAUTHORIZED = 'Метод недоступен неавторизованным пользователям.'
    INVALID_TOKEN = 'Токен невалиден или имеет истекший срок действия.'
    INVALID_SUPPLIER_ID = 'Поле supplier_id не может быть отрицательным числом.'
    INVALID_CATEGORY_PID = 'Поле parent_id не может быть отрицательным числом.'

    CATEGORIES_ADDED = 'Категории успешно добавлены.'
    MAPPINGS_ADDED = 'Сопоставления успешно добавлены.'


SECRET_KEY = config.APP_JWT_SECRET
ALGORITHM = 'SHA256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30


def _encode(payload: dict) -> str:
    header = {
        'alg': ALGORITHM,
        'typ': 'JWT'
    }

    header_encoded = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()

    message = f'{header_encoded}.{payload_encoded}'.encode()
    signature = hmac.new(SECRET_KEY.encode(), message, digestmod=ALGORITHM).digest()
    signature_encoded = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()

    jwt_token = f'{header_encoded}.{payload_encoded}.{signature_encoded}'

    return jwt_token


def create_access_token(user_data: dict) -> str:
    """Создание токена доступа"""

    payload = {
        **user_data,
        'type': 'access',
        'exp': (datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).isoformat()
    }

    return _encode(payload)


def create_refresh_token(user_data: dict) -> str:
    """Создание токена обновления"""

    payload = {
        **user_data,
        'type': 'refresh',
        'exp': (datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
    }
    return _encode(payload)


def get_payload(jwt_token: str) -> dict:
    """Получение полей из токена"""

    try:
        header_encoded, payload_encoded, signature_encoded = jwt_token.split('.')
    except ValueError:
        raise ValidationError(status_code=403, msg=Msg.INVALID_TOKEN)

    payload = json.loads(base64.urlsafe_b64decode(payload_encoded + "==="))

    message = f"{header_encoded}.{payload_encoded}".encode()
    expected_signature = hmac.new(SECRET_KEY.encode(), message, digestmod=ALGORITHM).digest()
    actual_signature = base64.urlsafe_b64decode(signature_encoded + "===")
    if expected_signature != actual_signature:
        raise ValidationError(status_code=403, msg=Msg.INVALID_TOKEN)

    if datetime.utcnow() > datetime.fromisoformat(payload['exp']):
        raise ValidationError(status_code=403, msg=Msg.INVALID_TOKEN)

    return payload


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials = await super().__call__(request)

        if not credentials:
            raise ValidationError(status_code=401, msg='Метод недоступен неавторизованным пользователям.')

        if not credentials.scheme == 'Bearer':
            raise ValidationError(status_code=403, msg='Токен невалиден или имеет истекший срок действия.')

        return credentials


