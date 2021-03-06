import requests
import json
import time
import datetime
import os


class YDiskError(Exception):

    def __init__(self, status_code, error_code, msg):
        self.status_code = status_code
        self.error_code = error_code
        self.message = msg


class YDiskUnauthorizedError(YDiskError):

    def __init__(self, access_token):
        self.access_token = access_token
        self.status_code = 401
        self.message = 'Ошибка авторизации пользователя по токену доступа'


class YDiskPathNotFoundError(YDiskError):

    def __init__(self, path=''):
        self.message = 'Не удалось найти запрошенный ресурс.'
        self.status_code = 404
        self.path = path


class YDiskOperationHandler:
    def __init__(self, ydisk_client, name, info):
        """target - экземпляр класса"""
        self.ydisk = ydisk_client
        self.name = name
        self.url = info['href']
        self.status = 'undefined'
        self.check_datetime = None
        self.check_count = 0

    def check_status(self):
        if self.check_count > 0:
            if (datetime.datetime.now() - self.check_datetime).seconds < 3:
                return  # с момента последней проверки прошло менее 3 секунд

        self.check_datetime = datetime.datetime.now()
        self.check_count += 1
        print(f'Проверка {self.check_count} статуса операции {self.name}: ', end='')
        response = requests.get(self.url, headers=self.ydisk.headers)
        info = self.ydisk.check_response(response)
        self.status = info['status']
        if self.status == 'success':
            print("операция успешно завершена")
        else:
            print(self.status)


class YDiskClient:
    """
    Обеспечивает взаимодействие с YandexDisk API
    """
    API_URL = 'https://cloud-api.yandex.net:443/v1/disk'

    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {
            "Authorization": "OAuth " + self.access_token
        }

    def check_response(self, response) -> map:

        ok_codes = (200, 201, 202, 204)
        if response.text.strip():
            info = json.loads(response.text.strip())
        elif response.status_code in ok_codes:
            info = {'error': '', 'message': 'OK'}
        else:
            info = {'error': response.status_code, 'message': ''}

        if response.status_code in ok_codes:
            return info

        if response.status_code == 401:
            raise YDiskUnauthorizedError(self.access_token)
        elif response.status_code == 404:
            raise YDiskPathNotFoundError()
        else:
            raise YDiskError(response.status_code, info['error'], info['message'])

    def path_exists(self, path: str) -> map:
        href = f'{YDiskClient.API_URL}/resources'
        response = requests.get(href, params={'path': path, 'limit': 0}, headers=self.headers)

        try:
            self.check_response(response)
        except YDiskPathNotFoundError:
            return False
        else:
            return True


    def delete_file(self, file_path):
        href = f'{YDiskClient.API_URL}/resources'
        response = requests.delete(href, params={'path': file_path}, headers=self.headers)
        self.check_response(response)


    def create_dir(self, dir_path):
        href = f'{YDiskClient.API_URL}/resources'
        response = requests.put(href, params={'path': dir_path}, headers=self.headers)
        self.check_response(response)


    def upload_from_url(self, url, path):
        href = f'{self.API_URL}/resources/upload'
        response = requests.post(href, params={'url': url, 'path': path}, headers=self.headers, timeout=5)
        info = self.check_response(response)
        op = YDiskOperationHandler(self, 'upload', info)
        while op.status != 'success':
            op.check_status()
            time.sleep(1)


    def upload(self, ydisk_path, data):
        href = f'{self.API_URL}/resources/upload'
        response = requests.get(href, params={'path': ydisk_path, 'overwrite': True}, headers=self.headers)
        info = self.check_response(response)

        response = requests.put(info['href'], data=data)
        info = self.check_response(response)


if __name__ == '__main__':
    with open("access_token.txt") as tokenfile:
        ydisk_token = tokenfile.read().strip()

    ydisk = YDiskClient(ydisk_token)
    path = '/Обучение/Netology/Python/YDisk client/TestDir/'
    try:
        if ydisk.path_exists(path):
            print(f'Путь существует')
        else:
            ydisk.create_dir(path)
            print(f'Путь создан')
    except requests.exceptions.ConnectionError as connect_err:
        print(connect_err)
    except YDiskUnauthorizedError as unauth_err:
        print(unauth_err)
    except YDiskError as ydisk_err:
        print(ydisk_err)
