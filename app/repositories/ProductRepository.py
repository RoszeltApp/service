from typing import Optional, List

from sqlalchemy import select, func, literal_column
from sqlalchemy.orm import Session, lazyload, joinedload, load_only, contains_eager, aliased

from app.Models.models import User, Role, Product, TechnicalCharacteristics, UserProductMapping, \
    CommercialCharacteristics, MediaFiles, Class
from app.repositories.BaseRepository import BaseRepository
from app.schemas.Product import ProductFilter, Props


class ProductRepository(BaseRepository):

    def get_catalog(self, _filter: ProductFilter):
        query = self.db.query(Product).join(Product.class_product) \
            .join(Product.mapping) \
            .join(UserProductMapping.stock) \
            .options(contains_eager(Product.mapping).options(contains_eager(UserProductMapping.stock),
                                                             joinedload(UserProductMapping.user)
                                                             .options(load_only(User.name))), contains_eager(Product.class_product))

        if _filter.query_string is not None:
            search = f"%{_filter.query_string}%"
            query = query.where(Product.name.like(search))


        if _filter.price_min is not None:
            query = query.where(_filter.price_min <= CommercialCharacteristics.price)

        if _filter.price_max is not None:
            query = query.filter(CommercialCharacteristics.price <= _filter.price_max)

        if _filter.suppliers is not None:
            print(_filter.suppliers.split(','))
            query = query.filter(UserProductMapping.user_id.in_(_filter.suppliers.split(',')))

        if _filter.category is not None:
            # print(_filter.category.split(','))
            query = query.where(Product.class_id.in_(_filter.category.split(',')))

        count = query.group_by(Product.id).count()

        if _filter.order_by_price is not None:
            if _filter.order_by_price == 'asc':
                query = query.order_by(CommercialCharacteristics.price.asc())
            else:
                query = query.order_by(CommercialCharacteristics.price.desc())

        pp = query.all()
        result = [i.id for i in pp]

        q_offset = self.db.query(Product).where(Product.id.in_(result)).offset(_filter.offset).limit(
            _filter.limit).all()

        result = [i.id for i in q_offset]

        q3 = self.db.query(Product).where(Product.id.in_(result)) \
            .join(Product.mapping).join(UserProductMapping.stock) \
            .options(contains_eager(Product.mapping).options(contains_eager(UserProductMapping.stock),
                                                             joinedload(UserProductMapping.user)
                                                             .options(load_only(User.name))))

        if _filter.price_min is not None:
            q3 = q3.where(_filter.price_min <= CommercialCharacteristics.price)

        if _filter.price_max is not None:
            q3 = q3.filter(CommercialCharacteristics.price <= _filter.price_max)

        if _filter.order_by_price is not None:
            if _filter.order_by_price == 'asc':
                q3 = q3.order_by(CommercialCharacteristics.price.asc())
            else:
                q3 = q3.order_by(CommercialCharacteristics.price.desc())

        return {
            'total_count': count,
            'data': q3.all()
        }

    def get_mapping_table(self, product_id: int, supplier_id: int) -> Optional[UserProductMapping]:
        mapping = self.db.query(UserProductMapping).where(UserProductMapping.user_id == supplier_id,
                                                          UserProductMapping.product_id == product_id).first()

        return mapping

    def add_product(self, product: Product, stock: CommercialCharacteristics, supplier_id: int):
        usr = self.db.query(User).where(User.id == supplier_id).first()
        print(usr.name)
        usr.products.append(product)
        self.db.add(usr)
        self.db.commit()
        print('sasv23')
        mapping = self.db.query(UserProductMapping).where(UserProductMapping.user_id == supplier_id,
                                                          UserProductMapping.product_id == int(product.id)).first()
        print(mapping.id)
        stock.id = mapping.id
        self.db.add(stock)
        self.db.commit()
        return mapping.id

    def update_product_info(self, product: dict):
        prod = self.db.query(Product).where(Product.id == int(product['id']))

        for key, value in product.items():
            if key == 'id':
                continue
            elif value is not None:
                prod.update({key: value})

        self.db.commit()

    def update_product_stock(self, mapping: UserProductMapping, stock: dict):

        for key, value in stock.items():
            if value is not None:
                setattr(mapping.stock, key, value)
        self.db.commit()

    def delete_mapping(self, mapping: UserProductMapping):
        commercy = self.db.query(CommercialCharacteristics). \
            where(CommercialCharacteristics.id == int(mapping.id)).first()

        self.db.delete(commercy)
        self.db.delete(mapping)
        self.db.commit()

    def get_products_for_supplier(self, supplier_id: int, limit: int, offset: int, query_string: str):
        # mappings = self.db.query(UserProductMapping) \
        #     .where(UserProductMapping.user_id == supplier_id) \
        #     .options(joinedload(UserProductMapping.stock), joinedload(UserProductMapping.product))\
        #     .limit(limit).offset(offset).all()

        mappings = self.db.query(UserProductMapping).where(UserProductMapping.user_id == supplier_id). \
            join(UserProductMapping.stock).join(UserProductMapping.product).join(Product.class_product). \
            options(contains_eager(UserProductMapping.stock)).options(contains_eager(UserProductMapping.product)
                                                                      .options(contains_eager(Product.class_product)))

        if query_string is not None:
            query_string = f"%{query_string}%"
            mappings = mappings.where(Product.name.like(query_string))

        count = mappings.count()
        mappings = mappings.limit(limit).offset(offset).all()

        # count = self.db.query(UserProductMapping).where(UserProductMapping.user_id == supplier_id).count()
        return {'total_count': count, 'data': mappings}

    def get_product_card(self, product_id: int):
        return self.db.query(Product) \
            .where(Product.id == product_id) \
            .options(joinedload(Product.mapping)
                     .options(joinedload(UserProductMapping.stock),
                              joinedload(UserProductMapping.props).options(load_only(TechnicalCharacteristics.name,
                                                                                     TechnicalCharacteristics.value)),
                              joinedload(UserProductMapping.media),
                              load_only(UserProductMapping.id, UserProductMapping.image),

                              joinedload(UserProductMapping.user).options(load_only(User.name))
                              )).first()

    def add_props(self, mapping_id: int, props: List[Props]):
        for prop in props:
            data = {
                'user_product_id': mapping_id,
                **prop.dict()
            }
            print(data)
            orm_prop = TechnicalCharacteristics(**data)
            self.db.add(orm_prop)

        self.db.commit()

    def get_product_by_article(self, article: str):
        return self.db.query(Product).where(Product.article == article).first()

    def add_image_for_offer(self, mapping_id: int, image: str):
        query = self.db.query(UserProductMapping).where(UserProductMapping.id == mapping_id).first()
        query.image = image
        self.db.merge(query)
        self.db.commit()

    def add_media(self, mapping_id: int, image: str):
        media = MediaFiles()
        media.path = image
        media.user_product_id = mapping_id

        self.db.add(media)
        self.db.commit()

    def update_mapping(self, mapping: UserProductMapping):
        self.db.merge(mapping)
        self.db.commit()

    def match(self, prod_id: int, user_id: int):
        mapping = UserProductMapping(product_id=prod_id, user_id=user_id)
        self.db.add(mapping)
        self.db.commit()
        return mapping

    def add_stock(self, mapping_id: int, stock: CommercialCharacteristics):
        stock.id = mapping_id
        self.db.add(stock)
        self.db.commit()

    def get_classificator_params(self):
        cls = aliased(Class)
        prod = aliased(Product)
        upm = aliased(UserProductMapping)
        teh = aliased(TechnicalCharacteristics)

        result = self.db.query(
            cls.id,
            cls.name,
            func.string_agg(teh.name, ',')
        ). \
            select_from(cls). \
            outerjoin(prod, cls.id == prod.class_id). \
            outerjoin(upm, upm.product_id == prod.id). \
            outerjoin(teh, teh.user_product_id == upm.id). \
            distinct().\
            group_by(cls.id). \
            all()

        return {'res': [
            {
                'id': i[0],
                'class_name': i[1],
                'params': i[2][:5000]
            }
            for i in result]}

    def get_classes(self):
        return self.db.query(Class).all()
