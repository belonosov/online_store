import random
from datetime import datetime

import databases
import sqlalchemy
from fastapi import FastAPI, HTTPException

from models import UserIn, User, ProductIn, Product, OrderIn, Order

DATABASE_URL = "sqlite://online_shop.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# User table
Users = sqlalchemy.Table(
    "Users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, nullable=False),
    sqlalchemy.Column("first_name", sqlalchemy.String(15), nullable=False),
    sqlalchemy.Column("last_name", sqlalchemy.String(15), nullable=False),
    sqlalchemy.Column("email", sqlalchemy.String(15), unique=True, nullable=False),
    sqlalchemy.Column("password", sqlalchemy.String, nullable=False)
)

# Product table
Products = sqlalchemy.Table(
    "Products",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name_product", sqlalchemy.String(100), nullable=False),
    sqlalchemy.Column("descriptions", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("price", sqlalchemy.Float, nullable=False)
)

# Order table
Orders = sqlalchemy.Table(
    "Orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, nullable=False),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("Users.id")),
    sqlalchemy.Column("product_id", sqlalchemy.ForeignKey("Products.id")),
    sqlalchemy.Column("create_at", sqlalchemy.DateTime, nullable=False, default=datetime.now()),
    sqlalchemy.Column("status", sqlalchemy.String, nullable=False)
)
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

app = FastAPI()


# Function to connect and disconnect from the database

@app.on_event("startup")
async def startup():
    # Creating a connection to the database data when starting the application
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    # Closing a database connection when the application stops
    await database.disconnect()


# Filling tables with fake data

# Populating tables with users
@app.get("/fake_users/{count}")
async def make_fake_users(count: int):
    for i in range(count):
        query = Users.insert().values(
            first_name=f"user{i}",
            last_name=f"surname{i}",
            email=f"mail{i}@mail.ru",
            password=f"Fake_password{i}@#$"
        )
        await database.execute(query)
    return {"message": f"{count} fake users created"}


# Filling tables with products
@app.get("/fake_products/{count}")
async def make_fake_products(count: int):
    for i in range(count):
        query = Products.insert().values(
            name_product=f"Product name {count}",
            descriptions=f"Descriptions text {count}",
            price=i + 10
        )
        await database.execute(query)
    return {"message": f"{count} fake products created"}


# Filling out the orders table
@app.get("/fake_orders/{count}")
async def make_fake_orders(count: int):
    for i in range(count):
        query = Orders.insert().values(
            user_id=random.randint(0, count),
            product_id=random.randint(0, count),
            create_at=datetime.now(),
            status=f"Example status {i}"
        )
        await database.execute(query)
    return {"message": f"{count} fake orders created"}


# Displaying all values from tables (select all)

# Getting all users
@app.get("/all_users/", response_model=list[User])
async def get_all_users():
    query = Users.select()
    return await database.fetch_all(query)


# Getting all products
@app.get("/all_product/", response_model=list[Product])
async def get_all_products():
    query = Products.select()
    return await database.fetch_all(query)


# Getting all orders
@app.get("/all_order/", response_model=list[Order])
async def get_all_orders():
    query = Orders.select()
    return await database.fetch_all(query)


# Getting one instance from the model

# Getting one user by ID
@app.get("/user/{user_id}", response_model=User)
async def fetch_one_user(user_id: int):
    query = Users.select().where(Users.c.id == user_id)
    one_user = await database.fetch_one(query)
    if one_user:
        return one_user
    raise HTTPException(status_code=404, detail="User is not found")


# Getting one product by ID
@app.get("/product/{product_id}", response_model=Product)
async def fetch_one_product(product_id: int):
    query = Products.select().where(Products.c.id == product_id)
    one_product = await database.fetch_one(query)
    if one_product:
        return one_product
    raise HTTPException(status_code=404, detail="Product is not found")


# Getting one order by ID
@app.get("/order/{order_id}", response_model=Order)
async def fetch_one_order(order_id: int):
    query = Orders.select().where(Orders.c.id == order_id)
    one_order = await database.fetch_one(query)
    if one_order:
        return one_order
    raise HTTPException(status_code=404, detail="Order is not found")


# Creating one instance of the model

# Creating a user
@app.post("/users/", response_model=User)
async def create_user(user: UserIn):
    query = Users.insert().values(**user.model_dump())
    write_id = await database.execute(query)
    return {**user.model_dump(), "id": write_id}


# Creating a product
@app.post("/product/", response_model=Product)
async def create_product(product: ProductIn):
    query = Products.insert().values(**product.model_dump())
    write_id = await database.execute(query)
    return {**product.model_dump(), "id": write_id}


# Creating a order
@app.post("/order/", response_model=Order)
async def create_order(order: OrderIn):
    query = Orders.insert().values(**order.model_dump())
    write_id = await database.execute(query)
    return {**order.model_dump(), "id": write_id}


# Changing (updating) the instance model

# Change user
@app.put("/user/{user_id}", response_model=User)
async def update_user(user_id: int, new_user: UserIn):
    query = Users.update().where(Users.c.id == user_id).values(**new_user.model_dump())
    renew_user = await database.execute(query)
    if renew_user:
        return {**new_user.model_dump(), "id": user_id}
    raise HTTPException(status_code=404, detail="User is not found")


# Change product
@app.put("/product/{product_id}", response_model=Product)
async def update_product(product_id: int, new_product: ProductIn):
    query = Products.update().where(Products.c.id == product_id).values(**new_product.model_dump())
    renew_product = await database.execute(query)
    if renew_product:
        return {**new_product.model_dump(), "id": product_id}
    raise HTTPException(status_code=404, detail="Product is not found")


# Change order
@app.put("/order/{}order_id", response_model=Order)
async def update_order(order_id: int, new_order: OrderIn):
    query = Orders.update().where(Orders.c.id == order_id).values(**new_order.model_dump())
    renew_order = await database.execute(query)
    if renew_order:
        return {**new_order.model_dump(), "id": order_id}
    raise HTTPException(status_code=404, detail="Order is not found")


# Deleting a model object (delete)

# Deleting a user
@app.delete("/user/{user_id}")
async def delete_user(user_id: int):
    query = Users.delete().where(Users.c.id == user_id)
    deletion_user = await database.execute(query)
    if deletion_user:
        return {"message": "User deleted"}
    raise HTTPException(status_code=404, detail="User is not found")


# Deleting a product
@app.delete("/product/{product_id}")
async def delete_product(product_id: int):
    query = Products.delete().where(Products.c.id == product_id)
    deletion_product = await database.execute(query)
    if deletion_product:
        return {"message": "Product deleted"}
    raise HTTPException(status_code=404, detail="Product is not found")


# Deleting a order
@app.delete("/order/{order_id}")
async def delete_order(order_id: int):
    query = Orders.delete().where(Orders.c.id == order_id)
    deletion_order = await database.execute(query)
    if deletion_order:
        return {"message": "Order deleted"}
    raise HTTPException(status_code=404, detail="Order is not found")
