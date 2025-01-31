import datetime
import io
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile

from fastapi import APIRouter, Depends
from minio import Minio

from app.libs.jwt import JWTBearer, get_payload
from app.schemas.Product import ProductFilter, ProductBase, ProductTest, Stock, MyProductsFilter
from app.serivces.ProductService import ProductService

product_router = APIRouter(prefix='/api/product', tags=['Товары'])


@product_router.get('/catalog', summary='Каталог товаров')
def catalog(_filter: ProductFilter = Depends(), product_service: ProductService = Depends()):
    return product_service.catalog(_filter)


@product_router.get('/my_list', summary='Мои товары')
def my_products(_filter: MyProductsFilter = Depends(),
                auth=Depends(JWTBearer()), product_service: ProductService = Depends()):

    token = auth.credentials
    payload = get_payload(token)
    return product_service.my_products(supplier_id=payload['id'], limit=_filter.limit, offset=_filter.offset,
                                       query_string=_filter.query_string)


@product_router.post('/upload_products', summary='Загрузка товаров')
def upload_products(data: List[ProductBase], auth=Depends(JWTBearer()), product_service: ProductService = Depends()):
    token = auth.credentials
    payload = get_payload(token)

    return product_service.add_products(data, payload['id'])


@product_router.post('/update_products', summary='Обновление товаров')
def update_products(product: ProductTest = Depends(), stock: Stock = Depends(), auth=Depends(JWTBearer()),
                    product_service: ProductService = Depends()):
    token = auth.credentials
    payload = get_payload(token)
    product_service.update_product(product=product, stock=stock, supplier_id=payload['id'])

    pass


@product_router.delete('/delete_products', summary='Удаление товаров')
def delete_products(id: int, auth=Depends(JWTBearer()), product_service: ProductService = Depends()):
    token = auth.credentials
    payload = get_payload(token)
    product_service.delete_product(product_id=id, supplier_id=payload['id'])


@product_router.get('/card', summary='Карточка товара')
def product_card(product_id: int, product_service: ProductService = Depends()):
    return product_service.get_card(product_id=product_id)


@product_router.post('/upload_gallery', summary='Загрузка картинок')
def upload_gallery(product_id: int, upload_file: List[UploadFile] = File(...), auth=Depends(JWTBearer()),
                   product_service: ProductService = Depends()):
    token = auth.credentials
    payload = get_payload(token)

    product_service.add_gallery(product_id=product_id, supplier_id=payload['id'], files=upload_file)

    pass


@product_router.post('/upload_main_image', summary='Загрузка превью')
def upload_main_image(product_id: int, upload_file: UploadFile = File(...), auth=Depends(JWTBearer()),
                      product_service: ProductService = Depends()):
    token = auth.credentials
    payload = get_payload(token)

    product_service.upload_main_image(product_id=product_id, supplier_id=payload['id'], file=upload_file)


@product_router.get('/test', summary='test')
def test(product_service: ProductService = Depends()):
    return product_service.productRepository.get_classificator_params()


@product_router.get('/classes', summary='Классы')
def classes(product_service: ProductService = Depends()):
    return product_service.classes()
