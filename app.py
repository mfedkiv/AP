from flask import Flask
from API.event_API import eventQuery
from API.user_API import userQuery
from API.calendar_API import calendarQuery
from API.user_login_API import user_loginQuery
from API.user_registration_API import user_registerQuery
from config.config import Config
from flask_jwt_extended import JWTManager

from models.table_models import TokenBlockList, session

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(eventQuery)
app.register_blueprint(userQuery)
app.register_blueprint(calendarQuery)
app.register_blueprint(user_loginQuery)
app.register_blueprint(user_registerQuery)

jwt = JWTManager(app)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = session.query(TokenBlockList.id).filter_by(jti=jti).first()
    return token is not None


if __name__ == "__main__":
    app.run(debug=True)

