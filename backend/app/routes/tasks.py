from flask import Blueprint, jsonify, request, session
from ..db import DatabaseConnection

task_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


@task_bp.route("/", methods=["GET"])
def get_tasks():
    """
    获取所有任务
    仅返回未删除的任务
    需要用户登录,依赖session中的user_id
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401

    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute(
            "SELECT id, title, description, status, priority, due_date, created_at, updated_at "
            "FROM tasks WHERE user_id = %s AND is_deleted = 0",
            (user_id,),
        )
        tasks = cursor.fetchall()
    return jsonify(tasks), 200


@task_bp.route("/", methods=["POST"])
def create_task():
    """
    创建新任务
    期望的JSON负载格式:
    {
        "title": "任务标题",
        "description": "任务描述",
        "status": "0",  # 0: 未开始, 1: 进行中, 2: 已完成
        "priority": "1",  # 0: 低, 1: 中, 2: 高, 3: 紧急
        "due_date": "2024-12-31"
    }
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401

    data = request.get_json()
    title = data.get("title")
    description = data.get("description", "")
    status = data.get("status", "0")
    priority = data.get("priority", "1")
    due_date = data.get("due_date")

    if not title:
        return jsonify({"error": "缺少必要字段"}), 400

    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute(
            "INSERT INTO tasks (user_id, title, description, status, priority, due_date) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, title, description, status, priority, due_date),
        )
        conn.commit()
        task_id = cursor.lastrowid
    return jsonify({"message": "任务创建成功", "task_id": task_id}), 201


@task_bp.route("/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """
    更新任务
    只更新提供的字段
    期望的JSON负载格式:
    {
        "title": "new title",          # 可选
        "description": "new description",  # 可选
        "status": "1",                 # 可选
        "priority": "2",               # 可选
        "due_date": "2024-12-31"      # 可选
    }
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401

    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    status = data.get("status")
    priority = data.get("priority")
    due_date = data.get("due_date")

    if not any([title, description, status, priority, due_date]):
        return jsonify({"error": "没有提供更新字段"}), 400

    fields = []
    values = []

    if title:
        fields.append("title = %s")
        values.append(title)
    if description:
        fields.append("description = %s")
        values.append(description)
    if status:
        fields.append("status = %s")
        values.append(status)
    if priority:
        fields.append("priority = %s")
        values.append(priority)
    if due_date:
        fields.append("due_date = %s")
        values.append(due_date)

    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute(
            f"UPDATE tasks SET {', '.join(fields)}, updated_at = NOW() "
            "WHERE id = %s AND user_id = %s AND is_deleted = 0",
            tuple(values + [task_id, user_id]),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "任务未找到或未更新"}), 404
    return jsonify({"message": "任务更新成功"}), 200


@task_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """
    删除任务（软删除）
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401

    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute(
            "UPDATE tasks SET is_deleted = 1, updated_at = NOW() "
            "WHERE id = %s AND user_id = %s AND is_deleted = 0",
            (task_id, user_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "任务未找到或已删除"}), 404
    return jsonify({"message": "任务删除成功"}), 200


@task_bp.route("/<int:task_id>/purge", methods=["DELETE"])
def purge_task(task_id):
    """
    彻底删除任务
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401
    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute(
            "DELETE FROM tasks WHERE id = %s AND user_id = %s AND is_deleted = 1",
            (task_id, user_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "任务未找到或未软删除"}), 404
    return jsonify({"message": "任务已彻底删除"}), 200
