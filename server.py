from fastapi import FastAPI
from SQLighter import *
from model import detect_parking
import geocoder
from math import radians, cos, sin, asin, sqrt
from datetime import *
from sklearn.neighbors import BallTree, DistanceMetric
import numpy as np

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
    db_worker = SQLighter("parking.db")

    # получаем парковочные места по дому
    house = db_worker.get_parkings_house(house_id)
    house_picture_path = db_worker.get_image_path(house_id)

    coords = {}
    # набиваем словарь UID-координата для модели
    for place in house:
        coords[place[0]] = (place[4], place[5])

    # считаем разницу во времени между текущим запросом и предыдущим обновлением этого дома
    last_time_update_obj = datetime.strptime(db_worker.get_last_time_update(house_id), '%Y-%m-%d %H:%M:%S')
    now_time_obj = datetime.now(tz=None).replace(microsecond=0)
    difference = now_time_obj - last_time_update_obj

    # если данные устаревшие, то используем нейронную сеть
    if difference.seconds / 60 > 5:
        # получаем занятые парковки
        busy_places = detect_parking(house_picture_path, coords)
        # обновляем время получения последних данных по этой камере
        db_worker.update_last_time(house_id)
        # проходимся по всем парковкам в доме, обновляя статус каждой
        for place in house:
            if place[0] in busy_places:
                db_worker.set_to_busy_place(place[0])
            else:
                db_worker.set_to_free_place(place[0])

    free = {}
    busy = {}

    # адрес и координаты первой парковки
    lat_last = float(house[0][2])
    lon_last = float(house[0][3])
    g = geocoder.osm([float(place[2]), float(place[3])], method='reverse')

    for place in house:

        # будем искать новый адрес только если точка далее 50 метров предыдущей
        # это помогает сократить время исполнения запроса
        if haversine(float(place[2]), float(place[3]), lat_last, lon_last) * 1000 > 50:
            g = geocoder.osm([float(place[2]), float(place[3])], method='reverse')

        address = g[0].json['raw']['address']['road']
        if db_worker.is_busy_place(place[0]):
            busy[place[0]] = {"lat": place[2], "lon": place[3], "disabled": db_worker.is_place_disabled(place[0]),
                              "address": address}
        else:
            free[place[0]] = {"lat": place[2], "lon": place[3], "disabled": db_worker.is_place_disabled(place[0]),
                              "address": address}
    db_worker.close()
    return {"free": free, "busy": busy}


@app.get("/get_parking/")
async def read_coords(lat: float, lon: float):
    return lat, lon


@app.get("/feedback/")
async def read_coords(user_id: int, text: str):
    db_worker = SQLighter("parking.db")
    db_worker.insert_feedback(user_id, text)
    db_worker.close()


@app.get("/get_in_radius/")
async def read_coords(address: str, radius: int):
    db_worker = SQLighter("parking.db")
    coords = db_worker.get_points_numpy()

    if address == "debug":
        house = db_worker.get_all_places()
        lat_last = float(house[0][2])
        lon_last = float(house[0][3])
        g = geocoder.osm([lat_last, lon_last], method='reverse')
        free = {}
        busy = {}
        for place in house:
            address = g[0].json['raw']['address']['road']
            if db_worker.is_busy_place(place[0]):
                busy[place[0]] = {"lat": place[2], "lon": place[3], "disabled": db_worker.is_place_disabled(place[0]),
                                  "address": address}
            else:
                free[place[0]] = {"lat": place[2], "lon": place[3], "disabled": db_worker.is_place_disabled(place[0]),
                                  "address": address}
        return {"free": free, "busy": busy}


    db_worker = SQLighter("parking.db")
    coords = db_worker.get_points_numpy()
    coords = [[55.892242, 37.542604]]
    coords_radian = []
    for coord in coords:
        lat = float(coord[0])
        lon = float(coord[1])
        coords_radian.append([radians(lat), radians(lon)])

    tree = BallTree(np.array(coords_radian), leaf_size=3, metric=DistanceMetric.get_metric("haversine"))

    g = geocoder.yandex('Moscow Russia')
    sci_radius = radius / 1000 / 6371

    print(g.json)
    object_idxs = tree.query_radius([[radians(g.osm['y']), radians(g.osm['x'])]], r=sci_radius, return_distance=True)


    print(object_idxs)
    db_worker.close()

    return {"еще не": "сделал"}
