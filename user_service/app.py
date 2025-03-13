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


async def main(port):
    db = Database()
    await db.connect()
    await db.init_db()
    print("✅ Database connected and initialized")

    # Load event_type -> command map
    event_type_cmd_map = await db.load_event_type_cmd_map()
    print(f"✅ Loaded command map: {event_type_cmd_map}")

    app = Application(db, event_type_cmd_map)
    app.listen(port)

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"🚀 Server started at http://{local_ip}:{port}")


if __name__ == "__main__":
    port = 8021
    if len(sys.argv) > 1:
        port = sys.argv[1]
    import asyncio

    async def start_server():
        await main(port)  # Set everything up
        await asyncio.Event().wait()  # Keeps running forever

    asyncio.run(start_server())

