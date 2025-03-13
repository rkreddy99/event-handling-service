import tornado.web
import tornado.escape
from utils import execute_cmd
from auth import authenticate


class MainHandler(tornado.web.RequestHandler):
    """
    Handler to receive an event and trigger a command associated with the (username, event_type).
    """

    @authenticate
    async def post(self):
        """
        Trigger command for a given username and event_type by replacing placeholders with data from request.

        Request JSON:
            {
                "username": "user1",
                "event_type": "deploy",
                ... (any other placeholders to be replaced in command)
            }

        Response:
            200 OK: {"status": "Command executed"}
            400 Bad Request: {"error": "event_type and username are required"}
            404 Not Found: {"error": "No command found for this event_type and username"}
        """
        body = tornado.escape.json_decode(self.request.body)
        event_type = body.get("event_type")
        username = body.get("username")
        if not event_type or not username:
            self.set_status(400)
            self.write({"error": "event_type and username are required"})
            return

        key = (username, event_type)
        command_template = self.application.event_type_cmd_map.get(key)
        if not command_template:
            self.set_status(404)
            self.write({"error": "No command found for this event_type and username"})
            return

        # Replace placeholders in command
        command = command_template
        for k, v in body.items():
            command = command.replace(f"<{k}>", str(v))

        print(f"⚙️ Executing command: {command}")

        # Execute command
        await execute_cmd(command)
        self.write({"status": "Command executed"})


class SubscribeHandler(tornado.web.RequestHandler):
    """
    Handler to subscribe a user to an event with a command.
    """

    @authenticate
    async def post(self):
        """
        Add or update a subscription for a username and event_type.

        Request JSON:
            {
                "username": "user1",
                "event_type": "deploy",
                "command": "bash deploy.sh <branch>"
            }

        Response:
            200 OK: {"status": "Subscription added/updated"}
            400 Bad Request: {"error": "event_type, command, and username are required"}
        """
        body = tornado.escape.json_decode(self.request.body)
        event_type = body.get("event_type")
        command = body.get("command")
        username = body.get("username")
        if not event_type or not command or not username:
            self.set_status(400)
            self.write({"error": "event_type, command, and username are required"})
            return

        # Insert or update in DB
        await self.application.db.upsert_subscription(username, event_type, command)
        # Update in-memory map
        self.application.event_type_cmd_map[(username, event_type)] = command

        print(f"✅ Subscription added/updated for ({username}, {event_type}) -> {command}")

        self.write({"status": "Subscription added/updated"})


class UnsubscribeHandler(tornado.web.RequestHandler):
    """
    Handler to remove a user's subscription to an event.
    """

    @authenticate
    async def post(self):
        """
        Delete a subscription for a username and event_type.

        Request JSON:
            {
                "username": "user1",
                "event_type": "deploy"
            }

        Response:
            200 OK: {"status": "Subscription removed"}
            400 Bad Request: {"error": "event_type and username are required"}
        """
        body = tornado.escape.json_decode(self.request.body)
        event_type = body.get("event_type")
        username = body.get("username")
        if not event_type or not username:
            self.set_status(400)
            self.write({"error": "event_type and username are required"})
            return

        # Remove from DB
        await self.application.db.delete_subscription(username, event_type)
        # Remove from in-memory map
        self.application.event_type_cmd_map.pop((username, event_type), None)

        print(f"🗑️ Subscription removed for ({username}, {event_type})")

        self.write({"status": "Subscription removed"})


class ListSubscriptionsHandler(tornado.web.RequestHandler):
    """
    Handler to list all subscriptions for a username, optionally filtered by event_type.
    """

    @authenticate
    async def get(self):
        """
        List subscriptions for a username (optionally filtered by event_type).

        Query parameters:
            - username (required)
            - event_type (optional)

        Example:
            GET /list_subscriptions?username=user1
            GET /list_subscriptions?username=user1&event_type=deploy

        Response:
            200 OK: List of subscriptions
            400 Bad Request: {"error": "username is required"}
        """
        username = self.get_argument("username", None)
        event_type = self.get_argument("event_type", None)

        if not username:
            self.set_status(400)
            self.write({"error": "username is required"})
            return

        # Fetch subscriptions from DB
        subscriptions = await self.application.db.list_subscriptions(username, event_type)

        print(f"📋 Listed {len(subscriptions)} subscription(s) for username='{username}'" + (f", event_type='{event_type}'" if event_type else ""))

        self.write({"subscriptions": subscriptions})


class HealthHandler(tornado.web.RequestHandler):
    """
    Health check endpoint to ensure the server is running.
    """

    @authenticate
    def get(self):
        """
        Health check endpoint.

        Response:
            200 OK: {"status": "ok"}
        """
        self.write({"status": "ok"})

