from flask import Blueprint, request, jsonify
from ..authentication import require_auth
from ..db import get_db

bp_users = Blueprint("users", __name__)

@bp_users.get("/users/search")
@require_auth(require_verified=True)
def search_user():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"error": "Missing q query param"}), 400

    my_uid = request.firebase.get("uid")

    q_esc = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    like = f"%{q_esc.lower()}%"

    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT uid, email, name, verified, last_online
        FROM users
        WHERE uid != ?
          AND (
            lower(email) LIKE ? ESCAPE '\\'
            OR lower(COALESCE(name, '')) LIKE ? ESCAPE '\\'
          )
        ORDER BY lower(COALESCE(name, '')) ASC, lower(email) ASC
        LIMIT 20
    """, (my_uid, like, like))

    rows = c.fetchall()
    conn.close()

    result = jsonify([
        {
            "uid": r["uid"],
            "email": r["email"],
            "name": r["name"],
            "verified": bool(r["verified"]),
            "last_online": r["last_online"]
        }
        for r in rows
    ])

    return result, 200