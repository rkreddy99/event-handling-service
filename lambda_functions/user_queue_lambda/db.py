import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    """MySQL DB Handler."""

    def __init__(self):
        self.connection = None

    def init(self):
        """Initialize MySQL connection."""
        try:
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
                write_timeout=10
            )
        except pymysql.MySQLError as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def fetch_user_by_queue_url(self, queue_url):
        """
        Fetch user details using queue_url.
        
        Args:
            queue_url (str): The queue_url to filter user records.

        Returns:
            dict: User details or None if not found.
        """
        try:
            with self.connection.cursor() as cursor:
                query = """
                SELECT username, ip_port, token 
                FROM users 
                WHERE queue_url = %s
                """
                cursor.execute(query, (queue_url,))
                result = cursor.fetchone()
                return result
        except pymysql.MySQLError as e:
            print(f"Error querying database: {e}")
            return None
    
    def close(self):
        """Close MySQL connection."""
        if self.connection:
            self.connection.close()
