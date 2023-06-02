import datetime
from typing import List

from fastapi import Depends, UploadFile
from minio import Minio

from app.Models.models import Product, CommercialCharacteristics
from app.libs.jwt import ValidationError
from app.repositories.ProductRepository import ProductRepository
from app.schemas.Product import ProductBase, ProductUpdate, ProductTest, Stock, ProductFilter
from app.serivces.Classificator.Classificator import Classificator
from app.serivces.Classificator.SetTeoreticStrategy import algorithm_set_theoretic


class ProductService:
    productRepository: ProductRepository
    classificator: Classificator

    def __init__(self, product_repository: ProductRepository = Depends()):
        self.productRepository = product_repository
        self.classificator = Classificator(algorithm_set_theoretic) # Classificator(neuro_network)

    def add_products(self, products: List[ProductBase], supplier_id):
        ids = []
        success_products = []
        success = 0
        for product in products:
            fields_prod = {
                'name': product.name,
                'article': product.article,
                'brand': product.brand,
                'class_id': None
            }
            fields_stock = {
                'quantity': product.quantity,
                'price': product.price
            }
            try:
                prod = Product(**fields_prod)

                mapping_product = self.productRepository.get_product_by_article(product.article)

                if mapping_product is None:
                    # prod.class_id = self.classificator.classify()
                    stock = CommercialCharacteristics(**fields_stock)
                    id_mapping = self.productRepository.add_product(prod, stock, supplier_id)
                    self.productRepository.add_props(id_mapping, product.props)

                    success += 1
                    print(prod.id)
                    success_products.append({'article': prod.article, 'id': prod.id})
                else:
                    print('test')
                    created_mapping = self.productRepository.match(mapping_product.id, supplier_id)
                    stock = CommercialCharacteristics(**fields_stock)
                    self.productRepository.add_props(created_mapping.id, product.props)
                    self.productRepository.add_stock(created_mapping.id, stock)
                    print('stop test')
                    success += 1
                    success_products.append({'article': prod.article, 'id': mapping_product.id})

            except:
                ids.append(product.article)

        return {
            'download_products': success,
            'products_failed': ids,
            'success_products': success_products
        }

    def update_product(self, product: ProductTest, stock: Stock, supplier_id: int):
        mapping = self.productRepository.get_mapping_table(product_id=product.id, supplier_id=supplier_id)

        if mapping is not None:
            self.productRepository.update_product_info(product.dict())
            self.productRepository.update_product_stock(mapping=mapping, stock=stock.dict())
        else:
            raise ValidationError(status_code=403, msg=f"У пользователя не существует товара с id={product.id}")

    def delete_product(self, product_id: int, supplier_id: int):
        mapping = self.productRepository.get_mapping_table(product_id=product_id, supplier_id=supplier_id)
        if mapping is not None:
            self.productRepository.delete_mapping(mapping)
        else:
            raise ValidationError(status_code=403, msg=f"У пользователя не существует товара с id={product_id}")

    def my_products(self, supplier_id: int, limit: int, offset: int, query_string: str):
        return self.productRepository.get_products_for_supplier(supplier_id=supplier_id, limit=limit, offset=offset,
                                                                query_string=query_string)

    def catalog(self, _filter: ProductFilter):
        return self.productRepository.get_catalog(_filter)

    def get_card(self, product_id: int):
        return self.productRepository.get_product_card(product_id)

    def add_gallery(self, product_id: int, supplier_id: int, files: List[UploadFile]):

        client = Minio(
            "172.20.0.2:9000",
            access_key="minio",
            secret_key="minio124",
            secure=False
        )
        mapping = self.productRepository.get_mapping_table(product_id=product_id, supplier_id=supplier_id)

        if mapping is None:
            raise ValidationError(status_code=403, msg=f"У пользователя не существует товара с id={product_id}")

        for file in files:
            file_name = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S.%f') + file.filename
            file_name = file_name.replace(" ", "")

            result = client.fput_object(
                "testbucket", file_name,
                file.file.fileno(),
                content_type=file.content_type
            )
            self.productRepository.add_media(mapping.id, file_name)

    def upload_main_image(self, product_id: int, supplier_id: int, file: UploadFile):
        mapping = self.productRepository.get_mapping_table(product_id=product_id, supplier_id=supplier_id)
        if mapping is None:
            raise ValidationError(status_code=403, msg=f"У пользователя не существует товара с id={product_id}")

        client = Minio(
            "172.20.0.2:9000",
            access_key="minio",
            secret_key="minio124",
            secure=False
        )
        file_name = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S.%f') + file.filename
        file_name = file_name.replace(" ", "")

        mapping.image = file_name
        result = client.fput_object(
            "testbucket", file_name,
            file.file.fileno(),
            content_type=file.content_type
        )
        self.productRepository.update_mapping(mapping)

