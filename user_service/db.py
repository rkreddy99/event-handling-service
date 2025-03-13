import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for database credentials)
load_dotenv()


class Database:
    """
    A class to manage asynchronous PostgreSQL database operations for subscriptions.
    """

    def __init__(self):
        # Connection pool placeholder
        self.pool = None

    async def connect(self):
        """
        Establishes a connection pool to the PostgreSQL database using asyncpg.
        """
        print("🔌 Connecting to the database...")
        self.pool = await asyncpg.create_pool(
            host=os.getenv("PGHOST"),
            database=os.getenv("PGDATABASE"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            min_size=1,  # Minimum number of connections
            max_size=5  # Maximum number of connections
        )
        print("✅ Connected to the database successfully.")

    async def init_db(self):
        """
        Initializes the 'subscriptions' table if it does not exist.
        The table holds subscriptions mapped by (username, event_type) as primary key.
        """
        print("🛠️  Initializing the database and creating subscriptions table if not exists...")
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    username TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    command TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (username, event_type)
                )
            ''')
        print("✅ Table 'subscriptions' is ready.")

    async def upsert_subscription(self, username, event_type, command):
        """
        Inserts a new subscription or updates the command if the (username, event_type) pair already exists.

        Args:
            username (str): The username associated with the subscription.
            event_type (str): The type of event for which the subscription is made.
            command (str): The command to execute when the event is triggered.
        """
        print(f"📥 Upserting subscription: username={username}, event_type={event_type}, command={command}")
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO subscriptions (username, event_type, command)
                VALUES ($1, $2, $3)
                ON CONFLICT (username, event_type)
                DO UPDATE SET command = $3, updated_at = CURRENT_TIMESTAMP
            ''', username, event_type, command)
        print("✅ Subscription added/updated successfully.")

    async def delete_subscription(self, username, event_type):
        """
        Deletes a subscription for a given username and event_type.

        Args:
            username (str): The username associated with the subscription.
            event_type (str): The type of event whose subscription needs to be removed.
        """
        print(f"❌ Deleting subscription for username={username}, event_type={event_type}")
        async with self.pool.acquire() as conn:
            await conn.execute('''
                DELETE FROM subscriptions WHERE username = $1 AND event_type = $2
            ''', username, event_type)
        print("✅ Subscription deleted successfully.")

    async def load_event_type_cmd_map(self):
        """
        Loads all subscriptions from the database into an in-memory dictionary.

        Returns:
            dict: A dictionary mapping (username, event_type) to command.
        """
        print("🔄 Loading event_type-command map from database...")
        event_type_cmd_map = {}
        async with self.pool.acquire() as conn:
            records = await conn.fetch("SELECT username, event_type, command FROM subscriptions")
            for record in records:
                # Map tuple (username, event_type) to command
                event_type_cmd_map[(record['username'], record['event_type'])] = record['command']
        print(f"✅ Loaded {len(event_type_cmd_map)} subscriptions into in-memory map.")
        return event_type_cmd_map

    async def list_subscriptions(self, username, event_type=None):
        """
        Lists all subscriptions for a given username. Optionally filters by event_type.

        Args:
            username (str): The username whose subscriptions are to be listed.
            event_type (str, optional): If provided, filters subscriptions for this specific event type.

        Returns:
            list: A list of dictionaries containing subscription details.
        """
        print(f"📋 Listing subscriptions for username={username}" + (f", event_type={event_type}" if event_type else ""))
        async with self.pool.acquire() as conn:
            if event_type:
                # Fetch specific subscription if event_type is provided
                query = '''
                    SELECT username, event_type, command, created_at, updated_at
                    FROM subscriptions
                    WHERE username = $1 AND event_type = $2
                '''
                records = await conn.fetch(query, username, event_type)
            else:
                # Fetch all subscriptions for the user
                query = '''
                    SELECT username, event_type, command, created_at, updated_at
                    FROM subscriptions
                    WHERE username = $1
                '''
                records = await conn.fetch(query, username)

        # Convert records to list of dictionaries
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
        print(f"✅ Found {len(subscriptions)} subscription(s) for username='{username}'" + (f", event_type='{event_type}'" if event_type else ""))
        return subscriptions

