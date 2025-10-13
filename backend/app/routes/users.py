from flask import Blueprint, jsonify, request, session

from ..db import DatabaseConnection
from werkzeug.security import check_password_hash, generate_password_hash

user_bp = Blueprint("users", __name__, url_prefix="/api/users")


@user_bp.route("/", methods=["GET"])
def get_users():
    """
    获取所有用户（仅用于测试，实际应用中应移除或保护此接口）
    """
    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute("SELECT id, username, email FROM users")
        users = cursor.fetchall()
        return jsonify(users), 200


@user_bp.route("/", methods=["POST"])
def create_user():
    """
    创建新用户
    期望的JSON负载格式:
    {
        "username": "exampleuser",
        "email": "example@example.com",
        "password": "examplepass"
    }
    """
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")  # 明文密码

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
    """
    用户登录
    """
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
    session["user_id"] = row["id"]
    return (
        jsonify(
            {
                "message": "登录成功",
                "user": {"id": row["id"], "username": row["username"]},
            }
        ),
        200,
    )

@user_bp.route("/logout", methods=["POST"])
def logout():
    """
    用户登出
    """
    session.pop("user_id", None)
    return jsonify({"message": "退出登录成功"}), 200
    
@user_bp.route("/ping", methods=["GET"])
def ping():
    """
    ping测试接口
    """
    return jsonify({"message": "pong!"})



