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
        obj = self.cursor.execute(f'SELECT * FROM users WHERE LOGIN = {login} AND PASSWORD = {password}')
        return bool(len(obj.fetchall()))


        #self.cursor.execute(f"INSERT INTO wait (chat_id) VALUES({str(chat_id)})")
        #self.connection.commit()

    def is_waiting(self, chat_id):
        with self.connection:
            obj = self.cursor.execute(f'SELECT * FROM wait WHERE chat_id = {chat_id}')
            return bool(len(obj.fetchall()))

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()
