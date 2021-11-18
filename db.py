from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.table_models import *
from config.config import connection_string

from datetime import datetime

engine = create_engine(connection_string)
Base.metadata.bind = engine

Session = sessionmaker()
session = Session(bind=engine)
#
# user1 = User(id=1, name="name1", surname="surname1", username="username1", password="password1")
# user2 = User(id=2, name="name2", surname="surname2", username="username2", password="password2")
# user3 = User(id=3, name="name3", surname="surname3", username="username3", password="password3")
# user4 = User(id=4, name="name4", surname="surname4", username="username4", password="password4")
#
# event1 = Event(id=1, title="event1", date=datetime.now(), owner=1)
# event2 = Event(id=2, title="event2", date=datetime.now(), owner=1)
# event3 = Event(id=3, title="event3", date=datetime.now(), owner=1)
# event4 = Event(id=4, title="event4", date=datetime.now(), owner=2)
# event5 = Event(id=5, title="event5", date=datetime.now(), owner=3)
#
# calendar1 = Calendar(id=1, title="calendar1")
# calendar2 = Calendar(id=2, title="calendar2")
# calendar3 = Calendar(id=3, title="calendar3")
#
# event_users_1 = EventUsers(event_id=1, user_id=1)
# event_users_2 = EventUsers(event_id=1, user_id=2)
# event_users_3 = EventUsers(event_id=1, user_id=3)
# event_users_4 = EventUsers(event_id=2, user_id=4)
# event_users_5 = EventUsers(event_id=3, user_id=1)
# event_users_6 = EventUsers(event_id=5, user_id=1)
#
# calendar_events_1 = CalendarEvents(calendar_id=1, event_id=1)
# calendar_events_2 = CalendarEvents(calendar_id=1, event_id=2)
# calendar_events_3 = CalendarEvents(calendar_id=1, event_id=3)
# calendar_events_4 = CalendarEvents(calendar_id=2, event_id=4)
# calendar_events_5 = CalendarEvents(calendar_id=2, event_id=5)
# calendar_events_6 = CalendarEvents(calendar_id=3, event_id=1)
#
# users = [user1, user2, user3, user4]
# events = [event1, event2, event3, event4, event5]
# calendars = [calendar1, calendar2, calendar3]
#
# event_users = [event_users_1, event_users_2, event_users_3, event_users_4, event_users_5, event_users_6]
# calendar_events = [calendar_events_1, calendar_events_2, calendar_events_3, calendar_events_4, calendar_events_5, calendar_events_6]
#
# session.add_all(users)
# # session.commit()
#
# session.add_all(events)
# # session.commit()
#
# session.add_all(calendars)
# # session.commit()
#
# session.add_all(event_users)
# # session.commit()
#
# # session.commit()
#
# session.add_all(calendar_events)
# # session.commit()
#
# session.commit()

# Base.metadata.drop_all(engine)
# Base.metadata.create_all(engine)
