from datetime import datetime

from pydantic import BaseModel, Field


# Models of user, product, order without ID

class UserIn(BaseModel):
    first_name: str = Field(..., title="First name", min_length=3, max_length=585)
    last_name: str = Field(..., title="Last name", min_length=3, max_length=58)
    email: str = Field(..., title="Email", min_length=5, max_length=50)
    password: str = Field(..., title="Password", min_length=8, max_length=50)


class ProductIn(BaseModel):
    name_product: str = Field(..., title="Product Name", min_length=10, max_length=50)
    descriptions: str = Field(..., title="Description", min_length=10, max_length=2000)
    price: int = Field(..., title="Price", gt=0, le=10 ** 10)


class OrderIn(BaseModel):
    user_id: int = Field()
    product_id: int = Field()
    create_at: datetime = None
    status: str = Field(..., title="Order status", min_length=10, max_length=50)


# User, product, order models with ID

class User(UserIn):
    id: int


class Product(ProductIn):
    id: int


class Order(OrderIn):
    id: int
