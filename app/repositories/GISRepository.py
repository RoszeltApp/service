from sqlalchemy.orm import contains_eager

from app.Models.models import Buildings, Floors, ComponentsLayer, Product
from app.repositories.BaseRepository import BaseRepository


class GISRepository(BaseRepository):

    def get_buildings(self, user_id: int):
        query = self.db.query(Buildings).where(Buildings.user_id == user_id)
        return query.all()

    def get_floors(self, building_id: int):
        query = self.db.query(Floors).where(Floors.build_id == building_id)
        return query.all()

    def get_layer_components(self, floor_id: int):
        query = self.db.query(ComponentsLayer).join(ComponentsLayer.product).join(Product.class_product).\
            options(contains_eager(ComponentsLayer.product).options(contains_eager(Product.class_product))).\
            where(ComponentsLayer.floor_id == floor_id)

        return query.all()

    def add_component_in_layer(self, floor_id: int, product_id: int, lat: float, long: float):
        mark = ComponentsLayer(floor_id=floor_id, product_id=product_id, lat=lat, long=long)
        self.db.add(mark)
        self.db.commit()

    def delete_component_in_layer(self, floor_id: int, product_id: int):
        mark = self.db.query(ComponentsLayer).\
            where(ComponentsLayer.floor_id == floor_id, ComponentsLayer.product_id == product_id).first()

        self.db.delete(mark)
        self.db.commit()

    def upload_building(self, build: Buildings):
        self.db.add(build)
        self.db.commit()

    def upload_floor(self, floor: Floors):
        self.db.add(floor)
        self.db.commit()
