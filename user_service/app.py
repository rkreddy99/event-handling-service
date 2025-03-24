import tornado.ioloop
import tornado.web
import socket
import sys
from db import Database
from handlers import MainHandler, SubscribeHandler, UnsubscribeHandler, HealthHandler, ListSubscriptionsHandler


class Application(tornado.web.Application):
    def __init__(self, db, event_type_cmd_map):
        handlers = [
            (r"/", MainHandler),
            (r"/subscribe", SubscribeHandler),
            (r"/unsubscribe", UnsubscribeHandler),
            (r"/health", HealthHandler),
            (r"/list-subscriptions", ListSubscriptionsHandler)
        ]
        settings = dict(debug=True)
        super().__init__(handlers, **settings)
        self.db = db
        self.event_type_cmd_map = event_type_cmd_map


def main(port):
    # Initialize MySQL connection
    db = Database()
    db.connect()
    db.init_db()
    print("✅ Database connected and initialized")

    # Load event_type -> command map
    event_type_cmd_map = db.load_event_type_cmd_map()
    print(f"✅ Loaded command map: {event_type_cmd_map}")

    # Start the Tornado app
    app = Application(db, event_type_cmd_map)
    app.listen(port)

    # Print the server info
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"🚀 Server started at http://{local_ip}:{port}")

    # Start the Tornado IOLoop
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    port = 8021
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    main(port)
