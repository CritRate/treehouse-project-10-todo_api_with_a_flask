from app import app

import unittest
import json
from models import Todo
from peewee import *

test_db = SqliteDatabase(':memory:')

URL = 'http://0.0.0.0:8000/api/v1/todos'


class TestFlaskApi(unittest.TestCase):
    def setUp(self):
        test_db.bind([Todo], bind_refs=False, bind_backrefs=False)

        test_db.connect()
        test_db.create_tables([Todo])

        self.app = app.test_client()
        self.app.testing = True

        # test data
        self.todo_one = {
            'name': 'Flask API',
            'completed': False
        }

        self.todo_two = {
            'name': 'Flask API v2',
            'completed': True
        }
        self.todo_three = {
            'name': 'Flask API v3',
            'completed': False
        }

    def tearDown(self):
        test_db.drop_tables([Todo])
        test_db.close()

    def test_blank_db(self):
        resp = self.app.get(URL)
        data = json.loads(resp.get_data())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data, [])

    def test_post_todo_success(self):
        resp = self.app.post(URL, data=json.dumps(
            self.todo_one), content_type='application/json')
        self.todo_one['id'] = '1'
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(json.loads(resp.get_data()), self.todo_one)

    def test_post_todo_fail(self):
        no_name_todo = {
            'completed': False
        }
        resp = self.app.post(URL, data=json.dumps(
            no_name_todo), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('not provided',
                      json.loads(resp.get_data())['message']['name'])

    def test_get_todos(self):
        self.app.post(URL, data=json.dumps(
            self.todo_one), content_type='application/json')
        self.app.post(URL, data=json.dumps(
            self.todo_two), content_type='application/json')
        self.app.post(URL, data=json.dumps(
            self.todo_three), content_type='application/json')
        resp = self.app.get(URL, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(json.loads(resp.get_data())), 3)

    def test_update_todo_success(self):
        self.app.post(URL, data=json.dumps(
            self.todo_one), content_type='application/json')
        resp = self.app.put(URL + '/1', data=json.dumps(self.todo_two),
                            content_type='application/json')
        self.todo_two['id'] = '1'
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.get_data()), self.todo_two)

    def test_update_todo_fail(self):
        self.app.post(URL, data=json.dumps(
            self.todo_one), content_type='application/json')
        resp = self.app.put(URL + '/10', data=json.dumps(self.todo_two),
                            content_type='application/json')
        self.todo_two['id'] = '1'
        self.assertEqual(resp.status_code, 404)
        self.assertIn('Todo with id:10 does not exist',
                      json.loads(resp.get_data())['message'])

    def test_delete_todo(self):
        self.app.post(URL, data=json.dumps(
            self.todo_one), content_type='application/json')
        resp = self.app.delete(URL + '/1')
        self.assertEqual(resp.status_code, 204)


if __name__ == '__main__':
    unittest.main()
