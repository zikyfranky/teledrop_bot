import json
from init import initialize
from flask import Flask, request
from flask_restful import Resource, Api
from helper import get_user, get_user_refs, update_user_refs, get_user_ref_count, get_user_bep20, update_user_bep20, get_user_twitter, update_user_twitter, get_user_step, update_user_step, get_user_tg_group, update_user_tg_group, get_user_tg_channel, update_user_tg_channel

app = Flask(__name__)
api = Api(app)

# Initialize firebase
initialize()

class User(Resource):
    def get(self, user_id):
        user = get_user(user_id)
        return user

class UserRef(Resource):
    def get(self, user_id):
        refs = get_user_refs(user_id)
        ref_count = get_user_ref_count(user_id)
        return json.dumps({"refs":refs, "ref_count":ref_count})

    def put(self, user_id):
        ref = request.form['ref']
        return update_user_refs(user_id, ref)

class UserBEP20(Resource):
    def get(self, user_id):
        bep20 = get_user_bep20(user_id)
        return bep20

    def put(self, user_id):
        bep20 = request.form['bep20']
        return update_user_bep20(user_id, bep20)

class UserTwitter(Resource):
    def get(self, user_id):
        twitter = get_user_twitter(user_id)
        return twitter

    def put(self, user_id):
        twitter = request.form['twitter']
        return update_user_twitter(user_id, twitter)

class UserStep(Resource):
    def get(self, user_id):
        step = get_user_step(user_id)
        return step

    def put(self, user_id):
        step = request.form['step']
        return update_user_step(user_id, step)
class UserTGChannel(Resource):
    def get(self, user_id):
        tg_channel = get_user_tg_channel(user_id)
        return tg_channel

    def put(self, user_id):
        tg_channel = request.form['tg_channel']
        return update_user_tg_channel(user_id, tg_channel)

class UserTGGroup(Resource):
    def get(self, user_id):
        tg_group = get_user_tg_group(user_id)
        return tg_group

    def put(self, user_id):
        tg_group = request.form['tg_group']
        return update_user_tg_group(user_id, tg_group)

api.add_resource(User, '/<string:user_id>')
api.add_resource(UserRef, '/<string:user_id>/refs')
api.add_resource(UserBEP20, '/<string:user_id>/bep20')
api.add_resource(UserTwitter, '/<string:user_id>/twitter')
api.add_resource(UserStep, '/<string:user_id>/step')
api.add_resource(UserTGChannel, '/<string:user_id>/tg_channel')
api.add_resource(UserTGGroup, '/<string:user_id>/tg_group')

if __name__ == '__main__':
    app.run(debug=False)
