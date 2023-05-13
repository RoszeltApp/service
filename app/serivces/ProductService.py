from typing import List

from fastapi import Depends

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
        success = 0
        for product in products:
            fields_prod = {
                'name': product.name,
                'article': product.article,
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
                else:
                    pass

            except:
                ids.append(product.article)

        return {
            'download_products': success,
            'products_failed': ids
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
