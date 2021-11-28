from flask_restful import Resource
from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.table_models import *

calendarQuery = Blueprint("calendarQuery", __name__)


class CalendarAPI(Resource):
    @jwt_required()
    def get(self, calendar_id):
        logged_in_user_id = get_jwt_identity()
        calendar = session.query(Calendar).filter(Calendar.id == calendar_id).first()
        if not calendar:
            return {'message': 'No calendars with this id.'}, 400
        if calendar.user_id != logged_in_user_id:
            return {'message': 'Access denied'}, 403
        return jsonify(str(calendar)), 200

    @jwt_required()
    def put(self, calendar_id):
        logged_in_user_id = get_jwt_identity()
        calendar = session.query(Calendar).filter(Calendar.id == calendar_id).first()
        if not calendar:
            return {'message': 'No calendars with this id.'}, 400
        if calendar.user_id != logged_in_user_id:
            return {'message': 'Access denied'}, 403
        params = request.json
        for key, value in params.items():
            setattr(calendar, key, value)
        session.commit()
        serialized = {
            "id": calendar.id,
            "title": calendar.title,
            "userId": calendar.user_id
        }
        return jsonify(serialized)


calendarQuery.add_url_rule('/calendars/<int:calendar_id>', view_func=CalendarAPI.as_view("calendarApi"))
