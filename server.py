from fastapi import FastAPI
from SQLighter import *
from model import detect_parking

app = FastAPI(title="Hack")


@app.get("/")
async def root():
    print("hello")
    return {"message": "Hello World"}


@app.get("/login/")
async def root(login: str, password: str):
    db_worker = SQLighter("parking.db")
    return {"registred": db_worker.get_user(login, password),
            "is_disabled": db_worker.is_user_disabled(login, password)}


@app.get("/get_house/")
async def read_coords(house_id: int):
    db_worker = SQLighter("parking.db")

    # получаем парковочные места по дому
    house = db_worker.get_parkings_house(house_id)
    house_picture_path = db_worker.get_image_path(house_id)

    coords = {}
    # набиваем словарь UID-координата для модели
    for place in house:
        coords[place[0]] = (place[4], place[5])

    busy_places = detect_parking(house_picture_path, coords)
    free = {}
    busy = {}
    for place in house:
        print(place)
        if place[0] in busy_places:
            busy[place[0]] = {"lat": place[2], "lon": place[3], "disabled": db_worker.is_place_disabled(place[0])}
        else:
            free[place[0]] = {"lat": place[2], "lon": place[3], "disabled": db_worker.is_place_disabled(place[0])}

    db_worker.close()
    return {"free": free, "busy": busy}


@app.get("/get_parking/")
async def read_coords(lat: float, lon: float):
    return lat, lon
