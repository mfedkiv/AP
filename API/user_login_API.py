from datetime import datetime, timezone

from flask_jwt_extended import jwt_required, get_jwt
from flask_restful import Resource
from flask import request, Blueprint, jsonify

from models.table_models import User, session, TokenBlockList

user_loginQuery = Blueprint("user_loginQuery", __name__)


class UserLoginAPI(Resource):
    @staticmethod
    def post():
        params = request.json
        if not session.query(User).filter_by(username=params['username']).first():
            return {"message": "User with provided username not found"}, 404
        user = User.authenticate(**params)
        if not user:
            return {'message': 'Invalid password'}, 406
        token = user.get_token()
        return {'access_token': token}


class UserLogoutAPI(Resource):
    @jwt_required()
    def delete(self):
        jti = get_jwt()["jti"]
        now = datetime.now(timezone.utc)
        session.add(TokenBlockList(jti=jti, created_at=now))
        session.commit()
        return jsonify(msg="JWT revoked")


user_loginQuery.add_url_rule('/login', view_func=UserLoginAPI.as_view("userLoginApi"))
user_loginQuery.add_url_rule('/logout', view_func=UserLogoutAPI.as_view("userLogoutApi"))
