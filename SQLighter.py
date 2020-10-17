import sqlite3
import random
import datetime


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_image_path(self, house_id):
        obj = self.cursor.execute(f'SELECT PATH_TO_IMAGE FROM pictures WHERE HOUSE_ID = {house_id}')
        return obj.fetchall()[0][0]

    def get_last_time_update(self, house_id):
        obj = self.cursor.execute(f'SELECT UPDATE_DATE FROM pictures WHERE HOUSE_ID = {house_id}')
        return obj.fetchall()[0][0]

    def update_last_time(self, house_id):
        self.cursor.execute(
            f"UPDATE pictures SET UPDATE_DATE = '{datetime.datetime.now().replace(microsecond=0)}' where HOUSE_ID = {house_id}")
        self.connection.commit()

    def set_to_busy_place(self, place_id):
        self.cursor.execute(
            f"UPDATE parking_places SET BUSY = 'TRUE' where UID = {place_id}")
        self.connection.commit()

    def set_to_free_place(self, place_id):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", place_id)

        self.cursor.execute(f"UPDATE parking_places SET BUSY = 'FALSE' where UID = {place_id}")
        self.connection.commit()

    def is_busy_place(self, place_id):
        obj = self.cursor.execute(f'SELECT BUSY FROM parking_places WHERE UID = {place_id}')
        if obj.fetchall()[0][0] == "TRUE":
            return True
        else:
            return False

    def get_parkings_house(self, house_id):
        obj = self.cursor.execute(f'SELECT * FROM parking_places WHERE HOUSE_ID = {house_id}')
        return obj.fetchall()

    def get_user(self, login, password):
        obj = self.cursor.execute(f"SELECT HOUSE_ID FROM users WHERE LOGIN = '{login}' AND PASSWORD = '{password}'")

        if len(obj.fetchall()) == 0:
            return False, 0
        else:
            obj = self.cursor.execute(f"SELECT HOUSE_ID FROM users WHERE LOGIN = '{login}' AND PASSWORD = '{password}'")
            house_id = obj.fetchall()[0][0]
            return True, house_id

    def get_user_home(self, login, password):
        obj = self.cursor.execute(f"SELECT HOUSE_ID FROM users WHERE LOGIN = '{login}' AND PASSWORD = '{password}'")
        if len(obj.fetchall()) == 0:
            return False
        else:
            return True

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
