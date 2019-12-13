# encoding = utf-8
# =====================================================
#   Copyright (C) 2019 All rights reserved.
#
#   filename : smutil.py
#   version  : 0.1
#   author   : Jack Wang / 544907049@qq.com
#   date     : 2019-12-13 上午 11:01
#   desc     : 
# =====================================================
import json
import requests


class Smms:

    @classmethod
    def get_token(cls, username, password):
        """
        提供用户名和密码返回用户的 API Token，若用户没有生成 Token 则会自动为其生成一个。
        :param username: 用户名/邮件地址
        :param password: 密码
        :return: API Token
        """
        url = 'https://sm.ms//api/v2/token'
        data = {'username': username, 'password': password}
        re = requests.post(url, data=data)
        if json.loads(re.content)['success']:
            token = json.loads(re.content)['data']['token']
            return token
        else:
            raise KeyError

    @classmethod
    def upload(cls, image, token=None):
        """
        图片上传接口。
        :param image: 图片的地址
        :param token: API Token
        :return: 返回图片上传后的URL
        """
        url = 'https://sm.ms/api/upload'
        params = {'format': 'json', 'ssl': True}
        files = {'smfile': open(image, 'rb')}
        headers = {'Authorization': token}
        if token:
            re = requests.post(url, headers=headers, files=files, params=params)
        else:
            re = requests.post(url, files=files, params=params)
        re_json = json.loads(re.text)
        try:
            if re_json['success']:
                return re_json['data']['url']
            else:
                return re_json['images']
        except KeyError:
            if re_json['code'] == 'unauthorized':
                raise ConnectionRefusedError

    @classmethod
    def get_history(cls, token):
        """
        提供 API Token，获得对应用户的所有上传图片信息。
        :param token: API Token
        :return: {dict}
        """
        url = 'https://sm.ms/api/v2/upload_history'
        params = {'format': 'json', 'ssl': True}
        headers = {'Authorization': token}
        re = requests.get(url, headers=headers, params=params)
        re_json = json.loads(re.text)
        try:
            if re_json['success']:
                return re_json['data']
            else:
                raise KeyError
        except KeyError:
            if re_json['code'] == 'unauthorized':
                raise ConnectionRefusedError

    @classmethod
    def get_history_ip(cls):
        """
        获得上传历史. 返回同一 IP 一个小时内上传的图片数据。
        :return: {dict}
        """
        url = 'https://sm.ms/api/v2/history'
        params = {'format': 'json', 'ssl': True}
        re = requests.get(url, params=params)
        re_json = json.loads(re.text)
        if re_json['success']:
            return re_json['data']
        else:
            raise KeyError
