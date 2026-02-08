import logging
from flask import Flask, jsonify
from flask_socketio import SocketIO
from .config import ALLOWED_ORIGINS
from .db import init_db
from .authentication import init_firebase
from .routes.users import bp_users
from .routes.friends import bp_friends
from .sockets.events import register_socket_handlers

def create_app():
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins=ALLOWED_ORIGINS)

    logging.basicConfig(level=logging.INFO)
    event_logger = logging.getLogger("voip-server:events:")

    init_firebase()
    init_db()

    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    app.register_blueprint(bp_users)
    app.register_blueprint(bp_friends)

    register_socket_handlers(socketio, event_logger)

    return app, socketio