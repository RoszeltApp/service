import datetime

from sqlalchemy.orm import relationship, backref

from app.database.database import Base
from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    UniqueConstraint,
    func
)


class Role(Base):
    __tablename__ = 'Role'
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(256), nullable=False, unique=True)

    users = relationship('User', back_populates='role')


class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False, unique=True)
    mail = Column(String(256), nullable=False, unique=True)
    password = Column(String(256), nullable=False)
    phone = Column(String(256), unique=True, nullable=False)
    company_name = Column(String(256), nullable=False)
    mail_confirmed = Column(Boolean, default=False)
    date_reg = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)
    refresh_token = Column(String, nullable=True, unique=False)

    role_code = Column(Integer, ForeignKey(Role.id, ondelete='CASCADE', onupdate='CASCADE'))
    role = relationship('Role', back_populates='users')

    products = relationship('Product', secondary='UserProductMapping', back_populates='users')
    mapping = relationship('UserProductMapping', back_populates='user')


class Class(Base):
    __tablename__ = 'Class'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False, unique=True)
    class_params = Column(JSON, nullable=True, unique=False)
    # is_leaf = Column(Boolean, nullable=False, default=False)
    class_icon = Column(String(256), nullable=True, unique=False)
    # parent_id = Column(Integer, ForeignKey('Class.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=True)
    # children = relationship('Class', backref=backref('parent', remote_side=[id]))
    product = relationship('Product', back_populates='class_product')


class Product(Base):
    __tablename__ = 'Product'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False, unique=True)
    article = Column(String(256), nullable=False, unique=True)
    brand = Column(String(256), nullable=True, unique=False)

    class_id = Column(Integer, ForeignKey('Class.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=True)
    users = relationship('User', secondary='UserProductMapping', back_populates='products')
    class_product = relationship('Class', back_populates='product')

    mapping = relationship('UserProductMapping', back_populates='product')


class UserProductMapping(Base):
    __tablename__ = 'UserProductMapping'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('User.id', onupdate='CASCADE', ondelete='CASCADE'))
    product_id = Column(Integer, ForeignKey('Product.id', onupdate='CASCADE', ondelete='CASCADE'))

    image = Column(String, nullable=True, unique=False)

    props = relationship('TechnicalCharacteristics', back_populates='product')
    stock = relationship('CommercialCharacteristics', back_populates="mapping", uselist=False)
    product = relationship('Product', back_populates='mapping')
    user = relationship('User', back_populates='mapping')
    media = relationship('MediaFiles', back_populates='mapping')


class TechnicalCharacteristics(Base):
    __tablename__ = 'TechnicalCharacteristics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False, unique=False)
    value = Column(String(256), nullable=True, unique=False)

    user_product_id = Column(Integer, ForeignKey('UserProductMapping.id', onupdate='CASCADE', ondelete='CASCADE'))
    product = relationship('UserProductMapping', back_populates='props')


class CommercialCharacteristics(Base):
    __tablename__ = 'CommercialCharacteristics'
    id = Column(Integer, ForeignKey('UserProductMapping.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    quantity = Column(Integer, nullable=True)
    price = Column(Integer, nullable=True)

    mapping = relationship('UserProductMapping', back_populates='stock')


class MediaFiles(Base):
    __tablename__ = 'MediaFiles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(300), nullable=False, unique=False)

    user_product_id = Column(Integer, ForeignKey('UserProductMapping.id', onupdate='CASCADE', ondelete='CASCADE'))
    mapping = relationship('UserProductMapping', back_populates='media')
