import requests
import datetime
from tqdm import tqdm
import time
import json


def get_token():
    """Получение токена из файла"""
    with open('token.txt', 'r') as text:
        token_vk = text.readline().strip()
        token_ya = text.readline().strip()
    return token_vk, token_ya


def _transform_time(file):
    """Перевод даты в привычный формат"""
    date = datetime.datetime.fromtimestamp(file).strftime('%Y-%m-%d %H-%M-%S')
    return date


class VK:
    def __init__(self, token_vk, version, id_user):
        self.params = {
            'access_token': token_vk,
            'v': version,
            'owner_id': id_user
        }

    def info_photos(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'album_id': 'profile',
            'extended': '1',
            'photo_sizes': '1'
        }
        res = requests.get(url, params={**self.params, **params})
        profile_list = res.json()
        return profile_list

    def _logs(self):
        profile_list = self.info_photos()
        list_info = {}
        for file in profile_list['response']['items']:
            size = file['sizes'][-1]['type']
            photo_url = file['sizes'][-1]['url']
            file_name = file['likes']['count']
            date = _transform_time(file['date'])
            new_file = list_info.get(file_name, [])
            new_file.append({'file_name': file_name,
                             'size': size,
                             'url': photo_url,
                             'date': date})
            list_info[file_name] = new_file
        return list_info

    def get_url_json(self):
        json_list = []
        info_upload = {}
        img_dict = self._logs()
        counter = 0
        for i in tqdm(img_dict.keys()):
            time.sleep(1)
            for value in img_dict[i]:
                if len(img_dict[i]) == 1:
                    name = f'{value["file_name"]}.jpg'
                else:
                    name = f'{value["file_name"]} {value["date"]}.jpg'
                json_list.append({'file_name': name,
                                  'size': value['size']})
                if value["file_name"] == 0:
                    info_upload[name] = img_dict[i][counter]['url']
                    counter += 1
                else:
                    info_upload[name] = img_dict[i][0]['url']
        return json_list, info_upload


class Yadisk:
    def __init__(self, token_yandex):
        self.token = token_yandex

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def create_folder(self, name_folder):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/'
        headers = self.get_headers()
        params = {'path': f'/{name_folder}/'}
        response = requests.put(url, headers=headers, params=params)
        return name_folder

    def upload_backup(self, info_upload, folder_name):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        for key, value in tqdm(info_upload.items()):
            time.sleep(1)
            params_upload = {'path': f'/{folder_name}/{key}',
                             'url': f'{value}'}
            response = requests.post(url, headers=headers, params=params_upload)


if __name__ == '__main__':
    token_vk, token_ya = get_token()
    test = VK(token_vk, '5.131', input('id_user: '))
    json_list, info_upload = test.get_url_json()
    with open('logs.json', 'w') as w:
        json.dump(json_list, w)
    testUP = Yadisk(token_ya)
    name_folder = testUP.create_folder(input('Введитя имя папки: '))
    testUP.upload_backup(info_upload, name_folder)
