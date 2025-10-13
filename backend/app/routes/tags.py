from flask import Blueprint, jsonify, request, session
from ..db import DatabaseConnection

tag_bp = Blueprint("tags", __name__, url_prefix="/api/tags")

@tag_bp.route("/", methods=["GET"])
def get_tags():
    """
    获取所有标签
    仅返回未删除的标签
    需要用户登录,依赖session中的user_id
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401

    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute(
            "SELECT id, name, color, created_at, updated_at "
            "FROM tags WHERE user_id = %s AND is_deleted = 0",
            (user_id,),
        )
        tags = cursor.fetchall()
    return jsonify(tags), 200

@tag_bp.route("/", methods=["POST"])
def create_tag():
    """
    创建新标签
    期望的JSON负载格式:
    {
        "name": "标签名称",
    }
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401

    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "缺少必要字段"}), 400

    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute(
            "INSERT INTO tags (user_id, name) VALUES (%s, %s)",
            (user_id, name),
        )
        conn.commit()
    return jsonify({"message": "标签创建成功"}), 201

@tag_bp.route("/<int:tag_id>", methods=["PUT"])
def update_tag(tag_id):
    """
    更新标签
    期望的JSON负载格式:
    {
        "name": "新标签名称"
    }
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401

    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "缺少必要字段"}), 400

    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute(
            "UPDATE tags SET name = %s, updated_at = NOW() "
            "WHERE id = %s AND user_id = %s AND is_deleted = 0",
            (name, tag_id, user_id),
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "标签未找到或无权限"}), 404
        conn.commit()
    return jsonify({"message": "标签更新成功"}), 200

@tag_bp.route("/<int:tag_id>", methods=["DELETE"])
def delete_tag(tag_id):
    """
    删除标签（软删除）
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401

    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute(
            "UPDATE tags SET is_deleted = 1, updated_at = NOW() "
            "WHERE id = %s AND user_id = %s AND is_deleted = 0",
            (tag_id, user_id),
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "标签未找到或无权限"}), 404
        conn.commit()
    return jsonify({"message": "标签删除成功"}), 200

@tag_bp.route("/<int:tag_id>/purge", methods=["DELETE"])
def purge_tag(tag_id):
    """
    永久删除标签
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401

    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute(
            "DELETE FROM tags WHERE id = %s AND user_id = %s",
            (tag_id, user_id),
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "标签未找到或无权限"}), 404
        conn.commit()
    return jsonify({"message": "标签永久删除成功"}), 200

@tag_bp.route("/<int:tag_id>/tasks", methods=["GET"])
def get_tasks_by_tag(tag_id):
    """
    获取指定标签下的所有任务
    需要用户登录,依赖session中的user_id
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401

    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute(
            "SELECT 1 FROM tags WHERE id = %s AND user_id = %s AND is_deleted = 0",
            (tag_id, user_id),
        )
        if not cursor.fetchone():
            return jsonify({"error": "标签未找到或无权限"}), 404
        cursor.execute(
            "SELECT t.id, t.title, t.description, t.status, t.priority, t.due_date, t.created_at, t.updated_at "
            "FROM tasks t "
            "JOIN task_tags tt ON t.id = tt.task_id "
            "WHERE tt.tag_id = %s AND t.user_id = %s AND t.is_deleted = 0",
            (tag_id, user_id),
        )
        tasks = cursor.fetchall()
    return jsonify(tasks), 200


@tag_bp.route("/assign", methods=["POST"])
def assign_tags_to_task():
    """
    将标签批量关联到任务
    期望JSON:
    {
        "task_id": 1,
        "tag_ids": [2, 3]
    }
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401

    data = request.get_json()
    task_id = data.get("task_id")
    tag_ids = data.get("tag_ids")

    if not task_id or not tag_ids or not isinstance(tag_ids, list):
        return jsonify({"error": "缺少参数"}), 400

    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500

        cursor.execute(
            "SELECT 1 FROM tasks WHERE id = %s AND user_id = %s AND is_deleted = 0",
            (task_id, user_id),
        )
        if not cursor.fetchone():
            return jsonify({"error": "任务未找到或无权限"}), 404

        placeholders = ",".join(["%s"] * len(tag_ids))
        cursor.execute(
            f"SELECT id FROM tags WHERE user_id = %s AND is_deleted = 0 AND id IN ({placeholders})",
            tuple([user_id] + tag_ids),
        )
        valid_tag_ids = {row["id"] for row in cursor.fetchall()}
        if len(valid_tag_ids) != len(tag_ids):
            return jsonify({"error": "存在无效或无权限的标签"}), 400

        values = [(task_id, tag_id) for tag_id in valid_tag_ids]
        cursor.executemany(
            "INSERT IGNORE INTO task_tags (task_id, tag_id) VALUES (%s, %s)",
            values,
        )
        conn.commit()

    return jsonify({"message": "标签关联成功"}), 200


@tag_bp.route("/remove", methods=["POST"])
def remove_tag_from_task():
    """
    解除任务与标签的关联
    期望JSON:
    {
        "task_id": 1,
        "tag_id": 2
    }
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401

    data = request.get_json()
    task_id = data.get("task_id")
    tag_id = data.get("tag_id")

    if not task_id or not tag_id:
        return jsonify({"error": "缺少参数"}), 400

    with DatabaseConnection() as (conn, cursor):
        if not conn or not cursor:
            return jsonify({"error": "数据库连接失败"}), 500
        cursor.execute(
            "DELETE tt FROM task_tags tt "
            "JOIN tasks t ON tt.task_id = t.id "
            "WHERE tt.task_id = %s AND tt.tag_id = %s AND t.user_id = %s",
            (task_id, tag_id, user_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "关联未找到或无权限"}), 404

    return jsonify({"message": "标签移除成功"}), 200
