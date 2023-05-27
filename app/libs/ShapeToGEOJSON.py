from typing import List

import geopandas as gpd
from fastapi import UploadFile


def shapeToJSON(files: List[UploadFile]):
    res = ''
    for file in files:
        file_location = f"files/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
            if '.shp' in file.filename:
                res = file_location

    data = gpd.read_file(res)
    return data.to_json()

