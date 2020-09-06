from django.test import TestCase, Client
from .models import *
from hashlib import sha256
import json
import time


class JsonClient(Client):
    def post_json(self, url, data={}, **kwargs):
        return self.post(url, json.dumps(data), content_type='application/json', **kwargs)

    def put_json(self, url, data={}, **kwargs):
        return self.put(url, json.dumps(data), content_type='application/json', **kwargs)


class SimpleTest(TestCase):
    def setUp(self):
        self.client = JsonClient()
        self.admin = User(email='admin@lucky.com', pass_sha256=sha256(b'admin').hexdigest(), role=0)
        self.admin.save()
        r = self.client.post_json('/api/login', {'email': 'admin@lucky.com', 'password': 'admin'})
        self.admin_tok = r.json()['token']
        param = [
            {"email": "qqq@qq.com", "password": "6666666", "role": 0},
            {"email": "qqq1@qq.com", "password": "666667", "role": 1},
            {"email": "qqq2@qq.com", "password": "6666668", "role": 2},
            {"email": "qqq3@qq.com", "password": "6666669", "role": 2},
            {"email": "qqqnew@qq.com", "name": "Sam", "role": 3},
        ]
        responseadd = self.client.post_json('/api/user', param, HTTP_X_TOKEN=self.admin_tok)
        self.assertEqual(responseadd.status_code, 200)

    def test_login_failed(self):
        param = {
            "email": "qqq3@qq.com",
            "password": "666666"
        }
        responselogin = self.client.post_json('/api/login', param)
        self.assertEqual(responselogin.status_code, 401)

    def test_login_success(self):
        param = {
            "email": "qqq3@qq.com",
            "password": "6666669"
        }
        responselogin = self.client.post_json('/api/login', param)
        self.assertEqual(responselogin.status_code, 200)
        response = responselogin.json()
        this_id = response['id']
        # this_token = response['token']

        params = {
            "old_password": "6666669",
            "new_password": "6767000"
        }
        responsepasswd = self.client.put_json(f'/api/user/{this_id}/password', params)
        self.assertEqual(responsepasswd.status_code, 200)

        responselogout = self.client.post_json('/api/logout')
        self.assertEqual(responselogout.status_code, 200)
        
    def test_assign(self):
        param_HR = {"email": "qqq1@qq.com", "password": "666667", "role": 1}
        param_interviewer = {"email": "qqq2@qq.com", "password": "6666668", "role": 2}
        responseHR = self.client.post_json('/api/login', param_HR)
        responseHR = responseHR.json()
        responseinterviewer = self.client.post_json('/api/login', param_interviewer)
        responseinterviewer = responseinterviewer.json()
        id_interviewer = responseinterviewer['id']
        token_interviewer = responseinterviewer['token']
        id_HR = responseHR['id']
        token_HR = responseHR['token']
        param1 = {
            "hr": id_HR,
            "interviewer": id_interviewer
        }
        responseass1 = self.client.post_json('/api/user/assign/interviewer', param1, HTTP_X_TOKEN=self.admin_tok)## assign interviewer
        self.assertEqual(responseass1.status_code, 200)
        param2 = {
            "hr":id_HR,
            "interviewee": "qqqnew@qq.com"
        }
        responseass2 = self.client.post_json('/api/user/assign/interviewee', param2, HTTP_X_TOKEN=self.admin_tok)## assign interviewee
        self.assertEqual(responseass2.status_code, 200)
