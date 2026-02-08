from flask import Blueprint, request, jsonify

from ..authentication import require_auth
from ..db import get_db
bp_friends = Blueprint("friends", __name__)
