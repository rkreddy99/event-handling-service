import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    """Asynchronous MySQL DB Handler."""

    def __init__(self):
        self.connection = None

    def init(self):
        """Initialize MySQL connection."""
        self.connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10,
            read_timeout=10,
            write_timeout=10,
            autocommit=True
        )

    def get_event_acl_functions(self, event_type: str):
        """Fetch all access check functions for given event_type."""
        query = """
        SELECT f.function_name, f.function_path
        FROM acl_function f
        JOIN event_acl_mapping e ON f.function_name = e.function_name
        WHERE event_type = %s
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (event_type,))
            functions = cursor.fetchall()
            return functions

    def get_subscribers(self, event_type: str):
        """Fetch all users who have subscribed to event_type."""
        query = """
        SELECT username
        FROM subscriptions
        WHERE event_type = %s
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (event_type,))
            rows = cursor.fetchall()
            usernames = [row['username'] for row in rows]
            return usernames

    def get_user_queue_url(self, username: str):
        """Fetch queue URL for a given username."""
        query = """
        SELECT queue_url
        FROM users
        WHERE username = %s
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (username,))
            rows = cursor.fetchall()

            if len(rows) == 1:
                return rows[0]['queue_url']
            elif len(rows) > 1:
                raise Exception(f"Multiple entries found for {username}")
            else:
                return None

    def close(self):
        """Close MySQL connection."""
        if self.connection:
            self.connection.close()

