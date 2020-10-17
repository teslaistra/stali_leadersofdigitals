from fastapi import FastAPI
from SQLighter import *
from model import detect_parking
import geocoder
import scipy.spatial as spatial
from math import radians, cos, sin, asin, sqrt
import time

app = FastAPI(title="Hack")


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return c * r


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/login/")
async def login(login: str, password: str):
    db_worker = SQLighter("parking.db")

    is_registred, house_id = db_worker.get_user(login, password)

    result = {"registred": is_registred,
              "is_disabled": db_worker.is_user_disabled(login, password) if is_registred else "false",
              "home_id": house_id}
    db_worker.close()
    return result


@app.get("/get_house/")
async def read_coords(house_id: int):
    start_time = time.time()

    db_worker = SQLighter("parking.db")

    # получаем парковочные места по дому
    house = db_worker.get_parkings_house(house_id)
    house_picture_path = db_worker.get_image_path(house_id)

    coords = {}
    # набиваем словарь UID-координата для модели
    for place in house:
        coords[place[0]] = (place[4], place[5])

    # получаем занятые парковки
    busy_places = detect_parking(house_picture_path, coords)
    free = {}
    busy = {}

    # адрес и координаты первой парковки
    lat_last = float(house[0][2])
    lon_last = float(house[0][3])
    g = geocoder.osm([float(place[2]), float(place[3])], method='reverse')

    for place in house:

        # будем искать новый адрес только если точка далее 50 метров предыдущей
        # это помогает сократить время исполнения запроса
        print("--- %s seconds ---" % (time.time() - start_time))
        if haversine(float(place[2]), float(place[3]), lat_last, lon_last) * 1000 > 50:
            g = geocoder.osm([float(place[2]), float(place[3])], method='reverse')
        print("--- %s seconds ---" % (time.time() - start_time))
        print("____________")
        address = g[0].json['raw']['address']['road']
        if place[0] in busy_places:
            busy[place[0]] = {"lat": place[2], "lon": place[3], "disabled": db_worker.is_place_disabled(place[0]),
                              "address": address}
        else:
            free[place[0]] = {"lat": place[2], "lon": place[3], "disabled": db_worker.is_place_disabled(place[0]),
                              "address": address}
    db_worker.close()
    print("--- %s seconds ---" % (time.time() - start_time))
    return {"free": free, "busy": busy}


@app.get("/get_parking/")
async def read_coords(lat: float, lon: float):
    return lat, lon
