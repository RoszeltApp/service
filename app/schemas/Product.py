from typing import Optional, List

from pydantic import BaseModel


class ProductFilter(BaseModel):
    limit: int = 20
    offset: int = 0
    query_string: Optional[str]
    suppliers: Optional[str]
    price_min: Optional[int]
    price_max: Optional[int]
    category: Optional[int]
    order_by_price: Optional[str]


class Props(BaseModel):
    name: str
    value: str


class ProductBase(BaseModel):
    name: str
    article: str
    price: float
    quantity: int
    brand: str
    class_id: Optional[int]
    props: List[Props]


class ProductUpdate(BaseModel):
    id: int
    name: Optional[str]
    article: Optional[str]
    price: Optional[float]
    quantity: Optional[int]

    class Config:
        orm_mode = True


class ProductTest(BaseModel):
    id: int
    name: Optional[str] = None
    article: Optional[str] = None

    # class_id: Optional[int]

    class Config:
        orm_mode = True


class Stock(BaseModel):
    price: Optional[float]
    quantity: Optional[int]


class MyProductsFilter(BaseModel):
    limit: int
    offset: int
    query_string: Optional[str]
