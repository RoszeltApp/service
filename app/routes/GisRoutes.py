import json
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File

from app.libs.ShapeToGEOJSON import shapeToJSON
from app.libs.jwt import JWTBearer, get_payload
from app.serivces.GISService import GISService

gis_router = APIRouter(prefix='/api/gis', tags=['Размещение компонентов'])


@gis_router.get('/buildings', summary='Получить список помещений')
def get_buildings(auth=Depends(JWTBearer()), gis_service: GISService = Depends()):
    token = auth.credentials
    payload = get_payload(token)
    return gis_service.get_buildings(payload['id'])


@gis_router.get('/get_floors', summary='Получить этажи помещения')
def get_floors(build_id: int, auth=Depends(JWTBearer()), gis_service: GISService = Depends()):
    token = auth.credentials
    payload = get_payload(token)
    return gis_service.get_floors(building_id=build_id)


@gis_router.post('/create_building', summary='Добавить помещение')
def create_building(name: str, address: str, auth=Depends(JWTBearer()), gis_service: GISService = Depends()):
    token = auth.credentials
    payload = get_payload(token)
    return gis_service.upload_building(name=name, address=address, user_id=payload['id'])


@gis_router.post('/upload_plans_floors', summary='Загрузка плана этажа')
def upload_plans(name: str,
                 building_id: int,
                 auditories: UploadFile = File(...),
                 doors: UploadFile = File(...),
                 stairs: UploadFile = File(...),
                 windows: UploadFile = File(...),
                 pol: UploadFile = File(...),
                 foundation: UploadFile = File(...),
                 walls_inter: UploadFile = File(...),
                 walls_outer: UploadFile = File(...),
                 auth=Depends(JWTBearer()),
                 gis_service: GISService = Depends()):
    token = auth.credentials
    payload = get_payload(token)
    return gis_service.upload_floor(name=name, building_id=building_id,
                                    auditories=auditories,
                                    doors=doors,
                                    stairs=stairs,
                                    windows=windows,
                                    pol=pol,
                                    foundation=foundation,
                                    walls_inter=walls_inter,
                                    walls_outer=walls_outer)


@gis_router.post('/place_component', summary='Разместить компонент')
def place_component(floor_id: int, product_id: int, lat: float, long: float, auth=Depends(JWTBearer()),
                    gis_service: GISService = Depends()):
    token = auth.credentials
    payload = get_payload(token)
    return gis_service.add_component(floor_id=floor_id, product_id=product_id, lat=lat, long=long)


@gis_router.delete('/delete_place_component', summary='Удалить размещение')
def delete_place_component(floor_id: int, product_id: int, auth=Depends(JWTBearer()), gis_service: GISService = Depends()):
    token = auth.credentials
    payload = get_payload(token)
    return gis_service.delete_component(floor_id=floor_id, product_id=product_id)


@gis_router.get('/get_layer_components', summary='Слой с компонентами')
def get_layer_components(floor_id: int, auth=Depends(JWTBearer()), gis_service: GISService = Depends()):
    token = auth.credentials
    payload = get_payload(token)
    return gis_service.get_layer(floor_id)

