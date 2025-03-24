import pymysql
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Database:
    """
    A class to manage MySQL database operations for subscriptions using pymysql.
    """

    def __init__(self):
        # Read MySQL credentials from environment variables
        self.host = os.getenv("MYSQL_HOST")
        self.database = os.getenv("MYSQL_DATABASE")
        self.user = os.getenv("MYSQL_USER")
        self.password = os.getenv("MYSQL_PASSWORD")
        self.port = int(os.getenv("MYSQL_PORT", 3306))
        self.connection = None

    def connect(self):
        """Establishes a connection to the MySQL database."""
        print("🔌 Connecting to the MySQL database...")
        self.connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        print("✅ Connected to MySQL successfully.")

    def init_db(self):
        """Initializes the `subscriptions` table if it does not exist."""
        print("🛠️  Initializing the database and creating subscriptions table if not exists...")
        with self.connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    username VARCHAR(255) NOT NULL,
                    event_type VARCHAR(255) NOT NULL,
                    command TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (username, event_type)
                )
            ''')
        print("✅ Table 'subscriptions' is ready.")

    def upsert_subscription(self, username, event_type, command):
        """
        Inserts or updates a subscription for a (username, event_type) pair.
        """
        print(f"📥 Upserting subscription: username={username}, event_type={event_type}, command={command}")
        with self.connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO subscriptions (username, event_type, command)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                command = VALUES(command), updated_at = CURRENT_TIMESTAMP
            ''', (username, event_type, command))
        print("✅ Subscription added/updated successfully.")

    def delete_subscription(self, username, event_type):
        """
        Deletes a subscription for a given username and event_type.
        """
        print(f"❌ Deleting subscription for username={username}, event_type={event_type}")
        with self.connection.cursor() as cursor:
            cursor.execute('''
                DELETE FROM subscriptions
                WHERE username = %s AND event_type = %s
            ''', (username, event_type))
        print("✅ Subscription deleted successfully.")

    def load_event_type_cmd_map(self):
        """
        Loads all subscriptions into an in-memory dictionary.

        Returns:
            dict: Mapping of (username, event_type) to command.
        """
        print("🔄 Loading event_type-command map from database...")
        event_type_cmd_map = {}
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT username, event_type, command FROM subscriptions")
            records = cursor.fetchall()
            for record in records:
                event_type_cmd_map[(record['username'], record['event_type'])] = record['command']
        print(f"✅ Loaded {len(event_type_cmd_map)} subscriptions into in-memory map.")
        return event_type_cmd_map

    def list_subscriptions(self, username, event_type=None):
        """
        Lists all subscriptions for a username, optionally filtered by event_type.

        Args:
            username (str): The username whose subscriptions are listed.
            event_type (str, optional): Filters by event_type if provided.

        Returns:
            list: List of dictionaries containing subscription details.
        """
        print(f"📋 Listing subscriptions for username={username}" + (f", event_type={event_type}" if event_type else ""))
        
        query = '''
            SELECT username, event_type, command, created_at, updated_at
            FROM subscriptions
            WHERE username = %s
        '''
        params = [username]

        if event_type:
            query += " AND event_type = %s"
            params.append(event_type)

        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            records = cursor.fetchall()

        subscriptions = [
            {
                "username": record["username"],
                "event_type": record["event_type"],
                "command": record["command"],
                "created_at": str(record["created_at"]),
                "updated_at": str(record["updated_at"]),
            }
            for record in records
        ]

        print(f"✅ Found {len(subscriptions)} subscription(s) for username='{username}'" +
              (f", event_type='{event_type}'" if event_type else ""))
        return subscriptions

    def close(self):
        """Closes the MySQL connection."""
        if self.connection:
            self.connection.close()
            print("🔌 MySQL connection closed.")



