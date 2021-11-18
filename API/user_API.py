from flask_restful import Resource
from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.table_models import *

userQuery = Blueprint("userQuery", __name__)


class UserAPI(Resource):
    @jwt_required()
    def get(self, user_id):
        logged_in_user_id = get_jwt_identity()
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return {'message': 'Invalid id provided'}, 404
        if user.id != logged_in_user_id:
            return {'message': 'Access denied'}, 403
        serialized = {
            "id": user.id,
            "name": user.name,
            "surname": user.surname,
            "username": user.username
        }
        return jsonify(serialized), 200

    @jwt_required()
    def put(self, user_id):
        logged_in_user_id = get_jwt_identity()
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return {'message': 'No users with this id.'}, 404
        if user.id != logged_in_user_id:
            return {'message': 'Access denied'}, 403
        params = request.json
        if session.query(User).filter_by(username=params['username']).first() and user.username != params['username']:
            return {"message": "User with provided username already exists"}, 400
        for key, value in params.items():
            setattr(user, key, value)
        session.commit()
        serialized = {
            "id": user.id,
            "name": user.name,
            "surname": user.surname,
            "username": user.username
        }
        return serialized


userQuery.add_url_rule('/user/<int:user_id>', view_func=UserAPI.as_view("userApi"))


class UserEventsAPI(Resource):
    @jwt_required()
    def get(self, username):
        logged_in_user_id = get_jwt_identity()
        res = []
        user = session.query(User).filter(User.username == username).first()
        if not user:
            return {'message': 'No users with this username.'}, 400
        if user.id != logged_in_user_id:
            return {'message': 'Access denied'}, 403
        events_id = session.query(EventUsers).filter(user.id == EventUsers.user_id).all()
        for event in events_id:
            event = event.__dict__
            event_info = session.query(Event).get(event["event_id"]).__dict__
            del event_info['_sa_instance_state']
            res.append(event_info)
        return jsonify(res), 200


userQuery.add_url_rule('/user/events/<string:username>', view_func=UserEventsAPI.as_view("userEventsApi"))


class UserAddAPI(Resource):
    @jwt_required()
    def post(self, user_id, event_id):
        logged_in_user_id = get_jwt_identity()
        user = session.query(User).filter(User.id == user_id).first()
        event = session.query(Event).filter(Event.id == event_id).first()
        if not user:
            return {'message': 'No user with this id.'}, 404
        if not event:
            return {'message': 'No event with this id.'}, 404
        if event.owner != logged_in_user_id:
            return {'message': 'Access denied'}, 403

        new_member_calendar = session.query(Calendar).filter(Calendar.user_id == user_id).first()
        new_calendar_event = CalendarEvents(calendar_id=new_member_calendar.id, event_id=event_id)
        new_member = EventUsers(event_id=event_id, user_id=user_id)
        session.add(new_member)
        session.commit()

        session.add(new_calendar_event)
        session.commit()

        return "Successful operation.", 200


userQuery.add_url_rule('/user/add_user_to_event/<int:user_id>/<int:event_id>', view_func=UserAddAPI.as_view("userAddApi"))
