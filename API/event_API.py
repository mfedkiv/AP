from flask_restful import Resource
from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.table_models import *

eventQuery = Blueprint("eventQuery", __name__)


class EventAPI(Resource):
    @jwt_required()
    def get(self, calendar_id):
        logged_in_user_id = get_jwt_identity()
        calendar = session.query(Calendar).filter(Calendar.user_id == logged_in_user_id).first()
        if calendar.id != calendar_id:
            return {'message': 'Access denied'}, 403
        result = []
        events_id = session.query(CalendarEvents).filter(CalendarEvents.calendar_id == calendar_id).all()
        if not events_id:
            return {'message': 'No events for calendar with this id.'}, 400
        for event in events_id:
            event = event.__dict__
            event_info = session.query(Event).get(event["event_id"]).__dict__
            del event_info['_sa_instance_state']
            result.append(event_info)
        return jsonify(result), 200

    @jwt_required()
    def post(self, calendar_id):
        logged_in_user_id = get_jwt_identity()
        calendar = session.query(Calendar).filter(Calendar.user_id == logged_in_user_id).first()
        if calendar.id != calendar_id:
            return {'message': 'Access denied'}, 403

        new_event = Event(**request.json)
        all_users = session.query(User).filter(new_event.owner == User.id).first()
        if not all_users:
            return {'message': 'There are no users with this id.'}, 400

        all_calendars = session.query(Calendar).filter(Calendar.id == calendar_id).first()
        if not all_calendars:
            return {'message': 'There are no calendars with this id.'}, 400

        session.add(new_event)
        session.commit()

        new_calendar_event = CalendarEvents(calendar_id=calendar_id, event_id=new_event.id)
        session.add(new_calendar_event)
        session.commit()

        new_event_users = EventUsers(event_id=new_event.id, user_id=new_event.owner)
        session.add(new_event_users)
        session.commit()

        serialized = {
            "id": new_event.id,
            "title": new_event.title,
            "date": new_event.date,
            "owner": new_event.owner
        }
        return jsonify(serialized)


eventQuery.add_url_rule('/events/<int:calendar_id>', view_func=EventAPI.as_view("eventApi"))


class EventCalendarAPI(Resource):
    @jwt_required()
    def get(self, event_id):
        event = session.query(Event).get(event_id)
        if not event:
            return {'message': 'No events with this id.'}, 404
        event = event.__dict__
        del event['_sa_instance_state']
        return jsonify(event), 200

    @jwt_required()
    def put(self, event_id):
        logged_in_user_id = get_jwt_identity()
        event = session.query(Event).filter(Event.id == event_id).first()
        if not event:
            return {'message': 'No events with this id.'}, 400
        if event.owner != logged_in_user_id:
            return {'message': 'Access denied'}, 403
        params = request.json
        for key, value in params.items():
            setattr(event, key, value)
        session.commit()
        serialized = {
            "id": event.id,
            "title": event.title,
            "date": event.date,
            "owner": event.owner
        }
        return serialized

    @jwt_required()
    def delete(self, event_id):
        logged_in_user_id = get_jwt_identity()
        event = session.query(Event).filter(Event.id == event_id).first()
        event_calendar = session.query(CalendarEvents).filter(CalendarEvents.event_id == event_id).all()
        event_users = session.query(EventUsers).filter(EventUsers.event_id == event_id).all()
        if not event:
            return {'message': 'No events with this id.'}, 400
        if event.owner != logged_in_user_id:
            return {'message': 'Access denied'}, 403
        for item in event_calendar:
            session.delete(item)
        for i in event_users:
            session.delete(i)
        session.delete(event)
        session.commit()
        session.close()
        return '', 204


eventQuery.add_url_rule('/event/<int:event_id>', view_func=EventCalendarAPI.as_view("eventCalendarApi"))
