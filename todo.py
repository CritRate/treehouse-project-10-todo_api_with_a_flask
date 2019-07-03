from flask_restful import fields, marshal, marshal_with, Api, Resource, abort, reqparse, inputs
from flask.blueprints import Blueprint

import models

todo_fields = {
    'id': fields.String,
    'name': fields.String,
    'completed': fields.Boolean,
}


class TodoList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='not provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'completed',
            required=True,
            help='not provided',
            location=['form', 'json'],
            type=inputs.boolean
        )
        super().__init__()

    @marshal_with(todo_fields)
    def post(self):
        """Insert one todo to the database"""
        return models.Todo.create(**self.reqparse.parse_args()), 201

    def get(self):
        """Get all the todos from database"""
        return [marshal(todo, todo_fields)
                for todo in models.Todo.select()]


class Todo(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='not provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'completed',
            required=True,
            help='not provided',
            location=['form', 'json'],
            type=inputs.boolean
        )
        super().__init__()

    def delete(self, id):
        """Delete todo with specified id"""
        query = models.Todo.delete().where(models.Todo.id == id)
        query.execute()
        return '', 204

    @marshal_with(todo_fields)
    def put(self, id):
        """Update todo with specified id"""
        args = self.reqparse.parse_args()
        query = models.Todo.update(**args).where(models.Todo.id == id)
        query.execute()
        try:
            todo = models.Todo.get_by_id(id)
        except models.Todo.DoesNotExist:
            abort(404, message=f'Todo with id:{id} does not exist')
        return todo, 200


todo_api = Blueprint('todo', __name__)
api = Api(todo_api)
api.add_resource(
    TodoList,
    'todos'
)
api.add_resource(
    Todo,
    'todos/<int:id>'
)
