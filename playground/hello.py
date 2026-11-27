from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Hello API")


@app.get("/")
def hello():
    return {"message": "backend journey begins"}


@app.get("/greet/{name}")
def greet(name: str, excited: bool = False):
    text = f"Hello, {name} {'!' if excited else '.'}"
    print(text)
    return {"greeting": text}


@app.get("/add")
def add(a: int, b: int):
    return {"result": a + b}


class Item(BaseModel):
    name: str
    price: float


@app.post("/items", status_code=201)
def create_item(item: Item):
    return {
        "received": item.model_dump(),
        "price_with_tax": round(item.price * 1.18, 2),
    }
