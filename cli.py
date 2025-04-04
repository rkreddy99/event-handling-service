import requests
import json
import asyncpg
import os
import pymysql


# HPC Service Configuration
HPC_SERVICE_URL = "https://<root_ip>:<port>"
HPC_AUTH_TOKEN = "MY_SECRET_TOKEN"

# DB Configuration
connection = pymysql.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE"),
    port=int(os.getenv("MYSQL_PORT", 3306)),
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)


def register_user(user):
    """
    Registers a new user service via HPC
    """

    url = f"{HPC_SERVICE_URL}/register"
    headers = {
        "Authorization": f"Bearer {HPC_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"user": user}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()  # returns ip, port, token, queue_url
    else:
        raise Exception(f"Failed to register user: {response.text}")


async def add_user_to_db(username, ip_port, token, queue_url):
    """
    Adds user to the db
    """

    print(f"Adding user to db, username: {username}, ip_port: {ip_port}, token: {token}, queue_url: {queue_url}")
    query_user = "INSERT INTO users (username, ip_port, token, queue_url) VALUES ($1, $2, $3, $4)"
    with connection.cursor() as cursor:
        cursor.execute(query_user, username, ip_port, token, queue_url)


async def get_user_event_details(user, event_type):
    """
    Fetches user event from the db
    """

    print(f"Fetching user event details for: {user} of event: {event_type}")
    query_subscriptions = "SELECT * FROM subscriptions WHERE username = $1 AND event_type = $2"
    with connection.cursor() as cursor:
        result = cursor.execute(query_subscriptions, user, event_type)

    return result[0] if result else None


async def get_user_service_details(user):
    """
    Fetches user's service details from the db
    """

    print(f"Fetching user service details for: {user}")
    query_user = "SELECT * FROM users WHERE username = $1"
    with connection.cursor() as cursor:
        result = cursor.execute(query_user, user)

    return result[0] if result else None


def subscribe_event(username, event_type, cmd):
    """
    Subscribes an event for a user
    """

    user_event_details = get_user_event_details(username, event_type)
    user_service_details = get_user_service_details(username)

    # If user event pair already exists
    if user_event_details is not None:
        raise Exception(f"Subscription already exists for user: {username} of event: {event_type} \nPlease use 'edit' to update the event subscription.")

    # If user does not exist, register them
    if user_service_details is None:
        user_service = register_user(username)
        user_ip, user_port, user_token, queue_url = user_service["ip"], user_service["port"], user_service["token"], user_service["queue_url"]

        ip_port = f"{user_ip}:{user_port}"

        # Add this user to db - users table
        add_user_to_db(username, ip_port, user_token, queue_url)
    else:
        ip_port, user_token = user_service_details["ip_port"], user_service_details["token"]

    url = f"https://{ip_port}/subscribe"
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }
    data = {"event_type": event_type, "cmd": cmd}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"Successfully subscribed {username} to {event_type}.")
        print(f"Registed user-event details: {get_user_event_details(username, event_type)}")
    else:
        raise Exception(f"Failed to subscribe user: {response.text}")


def edit_event(username, event_type, cmd):
    """
    Edits an event for a user
    """

    user_event_details = get_user_event_details(username, event_type)

    if user_event_details is None:
        raise Exception(f"Subscription not found for user: {username} of event_type: {event_type} \nPlease use 'subscribe' to create a new subscription.")

    user_service_details = get_user_service_details(username)
    ip_port, token = user_service_details["ip_port"], user_service_details["token"]

    url = f"https://{ip_port}/subscribe"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {"event_type": event_type, "cmd": cmd}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"Successfully updated {username} subscription to {event_type}.")
        print(f"Updated user-event details: {get_user_event_details(username, event_type)}")
    else:
        raise Exception(f"Failed to update user: {response.text}")


def unsubscribe_event(username, event_type):
    """
    Unsubscribes user from an event
    """

    user_event_details = get_user_event_details(username, event_type)
    if user_event_details is None:
        raise Exception(f"Subscription not found for user: {username} of event_type: {event_type} \nPlease use 'subscribe' to create a new subscription.")

    user_service_details = get_user_service_details(username)
    ip_port, token = user_service_details["ip_port"], user_service_details["token"]

    url = f"https://{ip_port}/unsubscribe"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {"event_type": event_type}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"Successfully unsubscribed {username} from {event_type}.")
    else:
        raise Exception(f"Failed to unsubscribe user: {response.text}")


def list_subscriptions(user):
    """
    Gets a list of subscriptions for a user
    """

    user_service_details = get_user_service_details(user)
    if user_service_details is None:
        raise Exception(f"User not found: {user}")

    ip_port, token = user_service_details["ip_port"], user_service_details["token"]

    url = f"https://{ip_port}/list-subscriptions"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        subscriptions = response.json()
        print(f"Subscriptions for {user}: \n{json.dumps(subscriptions, indent=4)}\n")
    else:
        raise Exception(f"Failed to fetch subscriptions: {response.text}")


if __name__ == "__main__":
    """
    CLI Execution
    """

    import argparse

    parser = argparse.ArgumentParser(description="Subscribe, Unsubscribe, Edit, or Get Info on event subscriptions.")
    parser.add_argument("action", choices=["subscribe", "unsubscribe", "edit", "info"], help="Action to perform")
    parser.add_argument("user", help="Username")
    parser.add_argument("--event_type", help="Event type (Required for subscribe, unsubscribe, edit)", required=False)
    parser.add_argument("--cmd", help="Command to execute for the event (Required for subscribe/edit)", required=False)

    args = parser.parse_args()

    if not args.user:
        print("Error: User is required.")
        exit(1)

    if not args.event_type and args.action in ["subscribe", "unsubscribe", "edit"]:
        print(f"Error: Event type is required for action: {args.action}")
        exit(1)

    if not args.cmd and args.action in ["subscribe", "edit"]:
        print(f"Error: --cmd is required for action: {args.action}")
        exit(1)

    try:
        if args.action in ["subscribe"]:
            subscribe_event(args.user, args.event_type, args.cmd)
            print(f"\nSubscribed Successfully!")

        elif args.action == "edit":
            edit_event(args.user, args.event_type, args.cmd)
            print(f"\nEdited Successfully!")

        elif args.action == "unsubscribe":
            unsubscribe_event(args.user, args.event_type)
            print(f"\nUnsubscribed Successfully!")

        elif args.action == "info":
            list_subscriptions(args.user)

    except Exception as e:
        print(f"Error trying to perform action: {args.action} error: {e}")

