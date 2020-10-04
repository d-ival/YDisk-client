import os
import requests
import json

class YDiskUploader:
    def __init__(self, file_path: str, token: str, destination_folder: str = "/"):
        self.file_path = file_path
        self.oauth_token = token
        self.url = "https://cloud-api.yandex.net:443/v1/disk/resources/upload"
        self.headers = {
            "Authorization": "OAuth " + self.oauth_token
        }
        self.destination_folder = "/"
        if len(destination_folder) != 0:
            destination_folder = destination_folder.replace("\\", "/")
            if not destination_folder.startswith("/"):
                destination_folder = "/" + destination_folder
            if not destination_folder.endswith("/"):
                destination_folder += "/"
            self.destination_folder = destination_folder

    def upload(self):
        """Метод загруджает файлы по списку file_list на яндекс диск"""
        result = {
            "error": False,
            "msg": ""
        }
        if not os.path.isfile(self.file_path):
            result["error"] = True
            result["msg"] = f'Некорректный путь к файлу: {self.file_path}'
            return result

        with open(self.file_path, mode="rb") as f:
            filedata = f.read()

        ydisk_path = self.destination_folder + os.path.basename(self.file_path)
        params = {
            "path": ydisk_path,
            "overwrite": True
        }

        response = requests.get(self.url, params=params, headers=self.headers)
        resp_info = json.loads(response.text)
        ok_codes = (200, 201)
        if not response.status_code in ok_codes:
            resp_info = json.loads(response.text)
            result["error"] = True
            result["msg"] = f"Ошибка при получении ссылки для загрузки файла: {resp_info['message']}"
            return result

        response = requests.put(resp_info['href'], data = filedata)
        if not response.status_code in ok_codes:
            error_info = json.loads(response.text)
            result["error"] = True
            result["msg"] = f"Ошибка при попытке загрузки файла на Яндекс.Диск: {error_info['message']}"
            return result

        result["msg"] = "Загрузка файла успешно завершена"
        return result


if __name__ == '__main__':
    with open("access-token.txt") as tokenfile:
        token = tokenfile.read().strip()
    uploader = YDiskUploader('c:\\tmp\\testydisk.txt', token=token, destination_folder='Обучение\\Netology\\Python\\YDisk client')
    result = uploader.upload()
    print(result["msg"])