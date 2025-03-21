import pymysql

timeout = 10

connection = pymysql.connect(
    charset="utf8mb4",
    connect_timeout=timeout,
    cursorclass=pymysql.cursors.DictCursor,
    db="defaultdb",
    host="event-handling-service-event-handling-service.l.aivencloud.com",
    password="AVNS_gZLS0lFs9Rf0rIkJt9A",
    read_timeout=timeout,
    port=15095,
    user="avnadmin",
    write_timeout=timeout,
)

try:
    cursor = connection.cursor()
    cursor.execute("USE testdb")
    

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(255) PRIMARY KEY,
            role ENUM('admin', 'user') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_port TEXT NOT NULL,
            queue_url TEXT NOT NULL,
            token TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            event_type VARCHAR(255) NOT NULL,
            command TEXT NOT NULL,
            username VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (event_type, username),
            FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS acl_function (
            function_name VARCHAR(255) PRIMARY KEY,
            function_path TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_acl_mapping (
            event_type VARCHAR(255) NOT NULL,
            function_name VARCHAR(255) NOT NULL,
            PRIMARY KEY (event_type, function_name),
            FOREIGN KEY (function_name) REFERENCES acl_function(function_name) ON DELETE CASCADE
        )
    """)

    cursor.execute("SHOW TABLES")
    print(cursor.fetchall(), "\n")

    # inserting data in users
    cursor.execute("INSERT INTO users (username, role, ip_port, queue_url, token) VALUES ('saatvik.rao', 'admin', 'http://10.253.2.59:8020', 'https://sqs.us-east-1.amazonaws.com/1234567890/queue_name', 'abc123')")
    cursor.execute("INSERT INTO users (username, role, ip_port, queue_url, token) VALUES ('test.user', 'user', 'http://', 'https://', 'def456')")
    cursor.execute("SELECT * FROM users")
    print(f"users table: {cursor.fetchall()}\n")

    # inserting data in subscriptions
    cursor.execute("INSERT INTO subscriptions (event_type, command, username) VALUES ('test2', 'python /home/tachyon/event_handling/test_script.py <strategy> <date>', 'saatvik.rao')")
    cursor.execute("INSERT INTO subscriptions (event_type, command, username) VALUES ('test2', 'python bash updated_test.sh <strategy> <date>', 'test.user')")
    cursor.execute("SELECT * FROM subscriptions")
    print(f"subscriptions table: {cursor.fetchall()}\n")

    # inserting data in acl_function
    cursor.execute("INSERT INTO acl_function (function_name, function_path) VALUES ('admin_tag_check', 'acl_checks.admin_tag_check')")
    cursor.execute("SELECT * FROM acl_function")
    print(f"acl_function table: {cursor.fetchall()}\n")

    # inserting data in event_acl_mapping
    cursor.execute("INSERT INTO event_acl_mapping (event_type, function_name) VALUES ('test2', 'admin_tag_check')")
    cursor.execute("SELECT * FROM event_acl_mapping")
    print(f"event_acl_mapping table: {cursor.fetchall()}\n")

    # commit the changes to db
    connection.commit()

finally:
    connection.close()
