from flask_restful import Resource
from flask import request, Blueprint
from models.table_models import *

user_registerQuery = Blueprint("user_registerQuery", __name__)


class UserRegistrationAPI(Resource):
    @staticmethod
    def post():
        new_user = User(**request.json)
        params = request.json
        if session.query(User).filter_by(username=params['username']).first():
            return {"message": "User with provided username already exists"}, 406
        session.add(new_user)
        session.commit()
        token = new_user.get_token()
        new_calendar = Calendar(title=request.json["username"] + "'s calendar", user_id=new_user.id)
        session.add(new_calendar)
        session.commit()

        return {'access_token': token}


user_registerQuery.add_url_rule('/register', view_func=UserRegistrationAPI.as_view("userRegistrationApi"))
