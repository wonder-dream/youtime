from flask import Blueprint, jsonify, request
from ..db import DatabaseConnection

task_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")

@task_bp.route("/", methods=["GET"])
def get_tasks():
    """
    获取所有任务
    """
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "缺少用户ID"}), 400
    
    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute(
            "SELECT id, title, description, status, priority, due_date, created_at, updated_at "
            "FROM tasks WHERE user_id = %s AND is_deleted = 0",
            (user_id,)
        )
        tasks = cursor.fetchall()
    return jsonify(tasks), 200

@task_bp.route("/", methods=["POST"])
def create_task():
    """
    创建新任务
    """
    data = request.get_json()
    user_id = data.get("user_id")
    title = data.get("title")
    description = data.get("description", "")
    status = data.get("status", "pending")
    priority = data.get("priority", "medium")
    due_date = data.get("due_date")

    if not user_id or not title:
        return jsonify({"error": "缺少必要字段"}), 400

    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute(
            "INSERT INTO tasks (user_id, title, description, status, priority, due_date) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, title, description, status, priority, due_date)
        )
        conn.commit()
        task_id = cursor.lastrowid
    return jsonify({"message": "任务创建成功", "task_id": task_id}), 201

@task_bp.route("/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """
    更新任务
    """
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

    values.append(task_id)

    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        sql = f"UPDATE tasks SET {', '.join(fields)}, updated_at = NOW() WHERE id = %s AND is_deleted = 0"
        cursor.execute(sql, tuple(values))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "任务未找到或未更新"}), 404
    return jsonify({"message": "任务更新成功"}), 200

@task_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """
    删除任务（软删除）
    """
    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute(
            "UPDATE tasks SET is_deleted = 1, updated_at = NOW() WHERE id = %s AND is_deleted = 0",
            (task_id,)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "任务未找到或已删除"}), 404
    return jsonify({"message": "任务删除成功"}), 200