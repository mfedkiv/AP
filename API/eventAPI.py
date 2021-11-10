import re
from cmath import e

import bcrypt
from flask_restful import Resource
from flask import jsonify, request, Blueprint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from models.table_models import *

eventQuery = Blueprint("eventQuery", __name__)

engine = create_engine(connection_string)
Session = sessionmaker()
session = Session(bind=engine)


class EventAPI(Resource):
    def get(self, calendarId):
        result = []
        eventsId = session.query(CalendarEvents).filter(CalendarEvents.calendar_id == calendarId).all()
        if not eventsId:
            return {'message': 'No events for calendar with this id.'}, 400
        for event in eventsId:
            event = event.__dict__
            eventInfo = session.query(Event).get(event["event_id"]).__dict__
            del eventInfo['_sa_instance_state']
            result.append(eventInfo)
        return jsonify(result), 200

    def post(self, calendarId):
        new_event = Event(**request.json)
        session.add(new_event)
        session.commit()

        new_calendarEvent = CalendarEvents(calendar_id=calendarId, event_id=new_event.id)
        session.add(new_calendarEvent)
        session.commit()

        new_eventUsers = EventUsers(event_id=new_event.id, user_id=new_event.owner)
        session.add(new_eventUsers)
        session.commit()

        serialized = {
            "id": new_event.id,
            "title": new_event.title,
            "date": new_event.date,
            "owner": new_event.owner
        }
        return jsonify(serialized)


eventQuery.add_url_rule('/events/<int:calendarId>', view_func=EventAPI.as_view("eventApi"))


class EventCalendarAPI(Resource):
    def get(self, eventId):
        try:
            event = session.query(Event).get(eventId)
            if not event:
                return {'message': 'No events with this id.'}, 400
            event = event.__dict__
            del event['_sa_instance_state']
            return jsonify(event), 200
        except Exception:
            return "Unsuccessful operation"

    def put(self, eventId):
        try:
            event = session.query(Event).filter(Event.id == eventId).first()
            params = request.json
            if not event:
                return {'message': 'No events with this id.'}, 400
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
        except Exception:
            return "Unsuccessful operation"

    def delete(self, eventId):
        event = session.query(Event).filter(Event.id == eventId).first()
        eventCalendar = session.query(CalendarEvents).filter(CalendarEvents.event_id == eventId).all()
        eventUsers = session.query(EventUsers).filter(EventUsers.event_id == eventId).all()
        if not event:
            return {'message': 'No events with this id.'}, 400
        for item in eventCalendar:
            session.delete(item)
        for i in eventUsers:
            session.delete(i)
        session.delete(event)
        session.commit()
        session.close()
        return '', 204


eventQuery.add_url_rule('/event/<int:eventId>', view_func=EventCalendarAPI.as_view("eventCalendarApi"))


class UserRegistrationAPI(Resource):
    def post(self):
        try:
            new_user = User(**request.json)
            session.add(new_user)
            session.commit()

            serialized_user = {
                "id": new_user.id,
                "name": new_user.name,
                "surname": new_user.surname,
                "username": new_user.username
            }

            hashed = bcrypt.hashpw(new_user.password.encode('utf-8'), bcrypt.gensalt())
            new_user.password = hashed

            new_calendar = Calendar(title=request.json["name"] + "'s calendar", user_id=new_user.id)
            session.add(new_calendar)
            session.commit()

            return jsonify(serialized_user)

        except IntegrityError as err:
            if err.orig.args:
                return {"message": "User with such username already exists."}, 400


eventQuery.add_url_rule('/user', view_func=UserRegistrationAPI.as_view("userRegistrationApi"))


class UserAPI(Resource):
    def get(self, userId):
        user = session.query(User).get(userId)
        if not user:
            return {'message': 'No users with this id.'}, 400
        user = user.__dict__
        del user['_sa_instance_state']
        return jsonify(user), 200

    def put(self, userId):
        user = session.query(User).filter(User.id == userId).first()
        params = request.json
        if not user:
            return {'message': 'No users with this id.'}, 400
        for key, value in params.items():
            setattr(user, key, value)
        session.commit()
        serialized = {
            "id": user.id,
            "name": user.name,
            "surname": user.surname,
            "username": user.username,
            "password": user.password
        }

        return serialized


eventQuery.add_url_rule('/user/<int:userId>', view_func=UserAPI.as_view("userApi"))


class UserEventsAPI(Resource):
    def get(self, username):
        res = []
        user = session.query(User).filter(User.username == username).first()
        if not user:
            return {'message': 'No events with this username.'}, 400
        eventsId = session.query(EventUsers).filter(user.id == EventUsers.user_id).all()
        for event in eventsId:
            event = event.__dict__
            eventInfo = session.query(Event).get(event["event_id"]).__dict__
            del eventInfo['_sa_instance_state']
            res.append(eventInfo)
        return jsonify(res), 200


eventQuery.add_url_rule('/user/events/<string:username>', view_func=UserEventsAPI.as_view("userEventsApi"))


class UserAddAPI(Resource):
    def post(self, userId, eventId):
        new_member = EventUsers(event_id=eventId, user_id=userId)
        session.add(new_member)
        session.commit()

        new_member_calendar = session.query(Calendar).filter(Calendar.user_id == userId).first()
        new_calendar_event = CalendarEvents(calendar_id=new_member_calendar.user_id, event_id=eventId)
        session.add(new_calendar_event)
        session.commit()

        if not new_member and new_member_calendar:
            return {'message': 'No events or users with this id.'}, 400

        return "Successful operation.", 200


eventQuery.add_url_rule('/user/add_user_to_event/<int:userId>/<int:eventId>',
                        view_func=UserAddAPI.as_view("userAddApi"))


class CalendarAPI(Resource):
    def get(self, calendarId):
        calendar = session.query(Calendar).get(calendarId)
        if not calendar:
            return {'message': 'No calendars with this id.'}, 400
        calendar = calendar.__dict__
        del calendar['_sa_instance_state']
        return jsonify(calendar), 200

    def put(self, calendarId):
        calendar = session.query(Calendar).filter(Calendar.id == calendarId).first()
        params = request.json
        if not calendar:
            return {'message': 'No calendars with this id.'}, 400
        for key, value in params.items():
            setattr(calendar, key, value)
        session.commit()
        serialized = {
            "id": calendar.id,
            "title": calendar.title,
            "userId": calendar.user_id
        }

        return jsonify(serialized)


eventQuery.add_url_rule('/calendars/<int:calendarId>', view_func=CalendarAPI.as_view("calendarApi"))
