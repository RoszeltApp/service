import datetime

from fastapi import Form
from pydantic import BaseModel


class Role(BaseModel):
    id: int
    role_name: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    name: str


class UserLK(UserBase):
    mail: str
    company_name: str
    phone: str
    role: Role


class UserSuppliers(UserBase):
    id: int


class UserCreate(UserBase):
    phone: str
    mail: str
    password: str
    company_name: str
    role_code: int

    @classmethod
    def as_form(cls, mail: str = Form(...), password: str = Form(...), company_name: str = Form(...),
                name: str = Form(...), phone: str = Form(...), role_code: int = Form(...)):

        return cls(mail=mail, password=password, company_name=company_name, name=name, phone=phone, role_code=role_code)

    class Config:
        orm_mode = True


class UserLogin(UserBase):
    password: str

    @classmethod
    def as_form(cls, name: str = Form(...), password: str = Form(...)):
        return cls(name=name, password=password)