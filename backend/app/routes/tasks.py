from flask import Blueprint, jsonify, request
from ..db import DatabaseConnection

bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")