import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "BYR@qjn517120",
    "database": "youtime",
}


def get_db_connection():
    """
    获取一个新的数据库连接
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"数据库连接失败: {e}")
    return None


def get_db_cursor(connection):
    """
    从现有连接获取数据库游标
    """
    if connection and connection.is_connected():
        try:
            cursor = connection.cursor(dictionary=True)  # 使用字典游标
            return cursor
        except Error as e:
            print(f"获取游标失败: {e}")
            return None
    return None


def get_db_connection_and_cursor():
    """
    获取数据库连接和游标
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)  # 使用字典游标
            return connection, cursor
    except Error as e:
        print(f"数据库连接失败: {e}")
    return None, None


def close_db_resources(connection, cursor=None):
    """
    关闭数据库连接和游标
    """
    if cursor:
        cursor.close()
    if connection and connection.is_connected():
        connection.close()


class DatabaseConnection:
    """
    数据库上下文管理器
    用于自动管理数据库连接和游标的获取与释放
    """

    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = get_db_connection()
        if not self.connection:
            return None, None
        self.cursor = get_db_cursor(self.connection)
        if not self.cursor:
            close_db_resources(self.connection)
            return None, None
        return self.connection, self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        close_db_resources(self.connection, self.cursor)
