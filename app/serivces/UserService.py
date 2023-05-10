import sqlalchemy
from fastapi import Depends

from app.Models.models import User
from app.libs.jwt import get_payload, create_access_token, create_refresh_token, ValidationError, Msg
from app.libs.verify_password import verify_password, get_password_hash
from app.repositories.UserRepository import UserRepository
from app.schemas.User import UserLK, UserCreate


def create_user_data(user: User):
    return {
        'id': user.id,
        'name': user.name,
        'company_name': user.company_name,
        'mail': user.mail,
        'phone': user.phone,
        'role': {
            'id': user.role_code,
            'role_name': user.role.role_name
        }
    }


class UserService:
    userRepository: UserRepository

    def __init__(self, user_repository: UserRepository = Depends()):
        self.userRepository = user_repository

    def register(self, reg_form: UserCreate):
        if self.userRepository.check_user(reg_form.name) is None:
            new_user = User(**reg_form.dict())
            new_user.password = get_password_hash(new_user.password)
            try:
                self.userRepository.add_user(new_user)
                return 'success'
            except sqlalchemy.exc.IntegrityError as e:
                raise ValidationError(status_code=403, msg='Почта или телефон уже используются другим пользователем')
        else:
            raise ValidationError(status_code=403, msg='Пользователь c таким именем существует')

    def login(self, login_data: dict):
        user = self.userRepository.check_user(name=login_data['name'])
        if user is not None:
            account = self.userRepository.personal_account(id=user.id)
            if verify_password(login_data['password'], account.password):

                user_data = create_user_data(account)

                access_token = create_access_token(user_data)
                refresh_token = create_refresh_token(user_data)

                self.userRepository.update_token(user_id=account.id, new_token=refresh_token)

                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                }
            else:
                raise ValidationError(status_code=403, msg=Msg.INVALID_PASSWORD)
        else:
            raise ValidationError(status_code=403, msg=Msg.INVALID_PASSWORD)

    def refresh_token(self, refresh_token):
        print(refresh_token)
        payload = get_payload(refresh_token)
        print(payload)
        user = self.userRepository.check_user(name=payload['name'])
        if user is not None:
            account = self.userRepository.personal_account(id=user.id)
            if refresh_token == account.refresh_token and payload['type'] == 'refresh':
                user_data = create_user_data(account)
                access_token = create_access_token(user_data)
                refresh_token = create_refresh_token(user_data)

                self.userRepository.update_token(user_id=account.id, new_token=refresh_token)
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                }
            else:
                raise ValidationError(status_code=403, msg=Msg.INVALID_TOKEN)
        else:
            raise ValidationError(status_code=403, msg=Msg.INVALID_TOKEN)

    def suppliers_list(self):
        return self.userRepository.suppliers_list()

    def personal_account(self, access_token):
        payload = get_payload(access_token)

        if self.userRepository.check_user(name=payload['name']) is not None and payload['type'] == 'access':
            account = self.userRepository.personal_account(id=payload['id'])
            return create_user_data(account)
        else:
            raise ValidationError(status_code=403, msg=Msg.INVALID_TOKEN)

