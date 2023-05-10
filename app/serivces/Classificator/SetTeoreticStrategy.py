from cmath import inf
from typing import List

from app.libs.LevenschteinDistance import calculate_distance


def list_to_str(str_list: List[str]):
    result = ''
    for ss in str_list:
        result += ss
    return result


def algorithm_set_theoretic(product_params: List[str], classes: List[dict]) -> int:
    product_params.sort()
    product_params_str = list_to_str(product_params)

    min_distance = inf
    class_id = -1

    for _class in classes:
        class_params = _class['params'].sort()
        class_params_str = list_to_str(class_params)
        distance = calculate_distance(product_params_str, class_params_str)
        if distance < min_distance:
            min_distance = distance
            class_id = _class['id']

    return class_id
