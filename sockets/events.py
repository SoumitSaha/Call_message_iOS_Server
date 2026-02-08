import time
import eventlet
from flask import request
from flask_socketio import emit, disconnect
from ..authentication import verify_firebase_token
from ..db import get_db

def register_socket_handlers(socketio, logger):

    @socketio.on("connect")
    def on_connect(auth):
        token = auth.get("token") if isinstance(auth, dict) else None
        if not token:
            token = request.args.get("token")
        if not token:
            logger.warning("Socket connect missing token")
            disconnect()
            return

        try:
            decoded = verify_firebase_token(token)
        except Exception as e:
            logger.warning(f"Socket connect invalid token: {e}")
            disconnect()
            return

        if not decoded.get("email_verified", False):
            emit("auth_error", {"error": "Email not verified"})
            disconnect()
            return

        uid = decoded.get("uid")
        email = decoded.get("email")
        now = int(time.time())

        conn = get_db()
        c = conn.cursor()
        c.execute("""
          INSERT INTO users (uid, email, name, verified, last_online, sid)
          VALUES (?, ?, ?, ?, ?, ?)
          ON CONFLICT(uid) DO UPDATE SET
            email=excluded.email,
            verified=excluded.verified,
            last_online=excluded.last_online,
            sid=excluded.sid
        """, (uid, email, None, 1, now, request.sid))
        conn.commit()
        conn.close()

        sid = request.sid

        def ack_later():
            eventlet.sleep(0.2)
            socketio.emit("server_message", {"message": "Connected", "uid": uid}, to=sid)

        socketio.start_background_task(ack_later)

    @socketio.on("heartbeat")
    def on_heartbeat():
        sid = request.sid
        now = int(time.time())

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT uid FROM users WHERE sid=?", (sid,))
        row = c.fetchone()
        if not row:
            conn.close()
            disconnect()
            return

        c.execute("UPDATE users SET last_online=? WHERE uid=?", (now, row["uid"]))
        conn.commit()
        conn.close()

        emit("server_message", {"message": "Heartbeat ACK"})

    @socketio.on("disconnect")
    def on_disconnect():
        sid = request.sid
        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE users SET sid=NULL WHERE sid=?", (sid,))
        conn.commit()
        conn.close()
        logger.info(f"Socket disconnected sid={sid}")