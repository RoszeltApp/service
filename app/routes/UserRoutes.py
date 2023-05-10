from typing import List

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app.libs.jwt import JWTBearer, get_payload
from app.schemas.User import UserCreate, UserLogin, UserSuppliers, UserLK
from app.serivces.UserService import UserService

user_router = APIRouter(prefix='/api/user', tags=['Пользователь'])


@user_router.post('/login', summary='login')
def login(login_form: UserLogin = Depends(UserLogin.as_form), user_service: UserService = Depends()):
    login_data = {
        'name': login_form.name,
        'password': login_form.password
    }

    return user_service.login(login_data)


@user_router.post('/register', summary='Регистрация')
def register(register_form: UserCreate = Depends(UserCreate.as_form), user_service: UserService = Depends()):
    print(register_form.dict())
    result = user_service.register(register_form)

    if result == 'success':
        return JSONResponse(status_code=200, content={
            'message': 'Пользователь зарегистрирован'
        })


@user_router.get('/suppliers', summary='Поставщики', response_model=List[UserSuppliers])
def suppliers(auth=Depends(JWTBearer()), user_service: UserService = Depends()):
    access_token = auth.credentials
    payload = get_payload(access_token)
    print('sup', payload)
    return user_service.suppliers_list()


@user_router.post('/refresh')
async def refresh(auth=Depends(JWTBearer()), user_service: UserService = Depends()):

    refresh_token = auth.credentials
    # print(refresh_token)
    return user_service.refresh_token(refresh_token)


@user_router.post('/lk', response_model=UserLK)
def lk(auth=Depends(JWTBearer()), user_service: UserService = Depends()):
    access_token = auth.credentials
    return user_service.personal_account(access_token)
