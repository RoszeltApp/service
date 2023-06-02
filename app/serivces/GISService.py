import json
from datetime import datetime

from fastapi import Depends, UploadFile
from minio import Minio

from app.Models.models import Buildings, Floors
from app.libs.jwt import ValidationError
from app.repositories.GISRepository import GISRepository


class GISService:
    gis_repository: GISRepository

    def __init__(self, gis_repository: GISRepository = Depends()):
        self.gis_repository = gis_repository

    def get_buildings(self, user_id: int):
        return self.gis_repository.get_buildings(user_id=user_id)

    def get_floors(self, building_id: int):
        return self.gis_repository.get_floors(building_id=building_id)

    def get_layer(self, floor_id: int):
        return self.gis_repository.get_layer_components(floor_id=floor_id)

    def upload_building(self, user_id: int, name: str, address: str):
        build = Buildings(user_id=user_id, name=name, address=address)
        return self.gis_repository.upload_building(build)

    def upload_floor(self, name: str, building_id: int,
                     auditories: UploadFile,
                     doors: UploadFile,
                     stairs: UploadFile,
                     windows: UploadFile,
                     pol: UploadFile,
                     foundation: UploadFile,
                     walls_inter: UploadFile,
                     walls_outer: UploadFile):

        client = Minio(
            "172.19.0.3:9000",
            access_key="minio",
            secret_key="minio124",
            secure=False
        )
        files = [auditories, doors, stairs, windows, pol, foundation, walls_inter, walls_outer]
        names = []
        for file in files:
            file_name = datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S.%f') + file.filename
            file_name = file_name.replace(" ", "")
            result = client.fput_object(
                "testbucket", file_name,
                file.file.fileno(),
                content_type=file.content_type
            )
            names.append(file_name)

        floor = Floors(auditories=names[0],
                       doors=names[1],
                       stairs=names[2],
                       windows=names[3],
                       Pol=names[4],
                       foundation=names[5],
                       walls_inter=names[6],
                       walls_outer=names[7],
                       name=name,
                       build_id=building_id)

        self.gis_repository.upload_floor(floor)

    def add_component(self, floor_id: int, product_offer_id: int, lat: float, long: float):
        return self.gis_repository.add_component_in_layer(floor_id=floor_id, product_offer_id=product_offer_id, lat=lat, long=long)

    def delete_component(self, id: int):
        try:
            self.gis_repository.delete_component_in_layer(id=id)
        except Exception:
            raise ValidationError(status_code=403, msg=f"Ошибка удаления")
