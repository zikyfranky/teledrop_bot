from init import initialize
from flask import Flask, request
from flask_restful import Resource, Api
from helper import get_user, update_user

app = Flask(__name__)
api = Api(app)

# Initialize firebase
initialize()

class TeleDropBot(Resource):
    def get(self, user_id):
        user = get_user(user_id)
        return {'status_code' : 404, 'message':'User doesn\'t exists'} if user is None else {'status_code' : 200, 'data' : user}

    def put(self, user_id):
        data = request.form
        success = update_user(user_id, data)
        return {'status_code': 400, 'message': 'An error occured'} if success is False else {'status_code' : 200, 'message':'Update successful'}

api.add_resource(TeleDropBot, '/<string:user_id>')

if __name__ == '__main__':
    app.run(debug=False)
