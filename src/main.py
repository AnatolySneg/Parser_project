from typing import Union, Annotated

import httpx
import uvicorn
import telebot

import asyncio
from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel, EmailStr, json
from starlette import status, requests

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []


@app.get("/")
async def root():
    return {"message": "Hello_world"}


# @app.get("/items/{item_id}")
# async def reed_items(item_id: int):
#     return {"item_id": item_id}


# @app.post("/items/")
# async def create_item(item: Item) -> Item:
#     return item


@app.get("/items/")
async def reed_items() -> list[Item]:
    return [
        Item(name="Portal Gun", price=42.0),
        Item(name="Portal Gun", price=42.0, tax=10.0, description="Some description"),
    ]


class BaseItem(BaseModel):
    description: str
    type: str


class CarItem(BaseItem):
    type: str = "car"


class PlaneItem(BaseItem):
    type: str = "plane"
    size: int


items = {
    "item1": {"description": "All my friends drive a low rider", "type": "car"},
    "item2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        "type": "plane",
        "size": 5,
    },
}


@app.get("/items/{item_id}", response_model=Union[PlaneItem, CarItem])
async def read_item(item_id: str):
    return items[item_id]


@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(name: str):
    return {"name": name}


@app.post("/files/")
async def create_file(
        file: Annotated[bytes, File()],
        fileb: Annotated[UploadFile, File()],
        token: Annotated[str, Form()],
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }


BOT_TOKEN = "6406909658:AAEeFz40BapS4_SvHRQJGmqNyFQFpD3CYCo"
PRIVATBANK_API_URL = "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11"
BOT_NAME = "CurrencyParsingBot"


@app.get('/get_exchange_course')
async def get_exchange_course():
    client = httpx.AsyncClient()
    response = await client.get(PRIVATBANK_API_URL)
    return response.json()


bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["hello"])
def handle(message):
    user = message
    x = 5 + 3
    x = 5 + 3
    x = 5 + 3
    exchange_course = get_exchange_course()
    bot.send_message(chat_id=message.chat.id, text=f"Hi to {message.chat.username}, from Fastapi")
    get_course(chat_id=message.chat.id)


def get_course(chat_id):
    response = get_exchange_course()
    text_response = response
    bot.send_message(chat_id=chat_id, text=f"result: {str(text_response)}")


@bot.message_handler(commands=["get_course"])
def course_handle(message):
    bot.send_message(message.chat.id, "chose command from list:\n"
                                      "/help - get list of commands,\n"
                                      "/get_exchange_course - get actual exchange course from all banks")


# bot.polling()

if __name__ == "__main__":
    # uvicorn.run(app="main:app", reload=True)
    uvicorn.run(app="main:app", port=8888, reload=True)

    """
    From command line$ uvicorn main:app --host 192.168.0.165 --port 8000 --reload
    or
    $ uvicorn main:app  --reload
    """
