import sqlite3
import random


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_image_path(self, house_id):
        obj = self.cursor.execute(f'SELECT PATH_TO_IMAGE FROM pictures WHERE HOUSE_ID = {house_id}')
        return obj.fetchall()[0][0]

    def get_parkings_house(self, house_id):
        obj = self.cursor.execute(f'SELECT * FROM parking_places WHERE HOUSE_ID = {house_id}')
        return obj.fetchall()

    def get_user(self, login, password):
        obj = self.cursor.execute(f"SELECT * FROM users WHERE LOGIN = '{login}' AND PASSWORD = '{password}'")
        return bool(len(obj.fetchall()))

    def is_user_disabled(self, login, password):
        obj = self.cursor.execute(f"SELECT IS_DISABLED FROM users WHERE LOGIN = '{login}' AND PASSWORD = '{password}'")
        return obj.fetchall()[0][0]

    def is_place_disabled(self, parking_id):
        obj = self.cursor.execute(
            f"SELECT IS_DISABLED FROM parking_places WHERE UID = {parking_id}")
        return obj.fetchall()[0][0]


        # self.cursor.execute(f"INSERT INTO wait (chat_id) VALUES({str(chat_id)})")
        # self.connection.commit()

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()
