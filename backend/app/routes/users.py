from flask import Blueprint, jsonify, request
from ..db import DatabaseConnection
from werkzeug.security import check_password_hash, generate_password_hash

user_bp = Blueprint("users", __name__, url_prefix="/api/users")


# 获取所有用户
@user_bp.route("/", methods=["GET"])
def get_users():
    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute("SELECT id, username, email FROM users")
        users = cursor.fetchall()
        return jsonify(users), 200


# 创建用户
@user_bp.route("/", methods=["POST"])
def create_user():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")  # 之后记得加哈希，别明文存储

    if not username or not email or not password:
        return jsonify({"error": "缺少必要字段"}), 400

    password_hash = generate_password_hash(password)

    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password_hash),
        )
        conn.commit()
    return jsonify({"message": "用户创建成功"}), 201


@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "缺少用户名或密码"}), 400
    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute(
            "SELECT id, username, password_hash FROM users WHERE username = %s",
            (username,),
        )
        row = cursor.fetchone()
    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify({"error": "无效的用户名或密码"}), 401
    return (
        jsonify(
            {
                "message": "登录成功",
                "user": {"id": row["id"], "username": row["username"]},
            }
        ),
        200,
    )


# ping测试接口
@user_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "pong!"})
