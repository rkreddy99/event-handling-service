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
        CREATE TABLE users (
            username VARCHAR(255) PRIMARY KEY,
            role ENUM('admin', 'user') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_port TEXT NOT NULL,
            queue_url TEXT NOT NULL,
            token TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE subscriptions (
            event_type VARCHAR(255) PRIMARY KEY,
            command TEXT NOT NULL,
            username VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE acl_function (
            acl_id INT AUTO_INCREMENT PRIMARY KEY,
            function_name TEXT NOT NULL,
            function_path TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE event_acl_mapping (
            event_type VARCHAR(255) NOT NULL,
            acl_id INT NOT NULL,
            PRIMARY KEY (event_type, acl_id),
            FOREIGN KEY (acl_id) REFERENCES acl_function(acl_id) ON DELETE CASCADE
        )
    """)

    cursor.execute("SHOW TABLES")
    print(cursor.fetchall(), "\n")

    cursor.execute("INSERT INTO users (username, role, ip_port, queue_url, token) VALUES ('saatvik.rao', 'admin', 'http://10.253.2.59:8020', 'https://sqs.us-east-1.amazonaws.com/1234567890/queue_name', 'abc123')")
    cursor.execute("INSERT INTO users (username, role, ip_port, queue_url, token) VALUES ('test.user', 'user', 'http://', 'https://', 'def456')")
    cursor.execute("SELECT * FROM users")

    # print the table in a good format
    for row in cursor.fetchall():
        print(row)

finally:
    connection.close()
