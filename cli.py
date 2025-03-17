import requests
import boto3
import json
import os

# HPC Service Configuration
HPC_SERVICE_URL = "https://<root_ip>:<port>"
HPC_AUTH_TOKEN = "MY_SECRET_TOKEN"

# AWS SQS Configuration
AWS_REGION = "us-east-1"  # Change to your AWS region


def register_user(user):
    """register a new user service via HPC"""

    url = f"{HPC_SERVICE_URL}/register"
    headers = {
        "Authorization": f"Bearer {HPC_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"user": user}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()  # Returns {'ip': 'x.x.x.x', 'port': 'xxxx', 'token': 'abc123'}
    else:
        raise Exception(f"Failed to register user: {response.text}")


def create_sqs_queue(user):
    """create an SQS queue for the user"""

    sqs = boto3.client("sqs", region_name=AWS_REGION)

    queue_name = f"{user}-event-queue"
    response = sqs.create_queue(QueueName=queue_name)

    queue_url = response["QueueUrl"]
    return queue_url


def subscribe_event(user, event_type, cmd):
    """subscribe or edit an event for a user"""

    # Register user and get their service details
    user_service = register_user(user)
    user_ip, user_port, user_token = user_service["ip"], user_service["port"], user_service["token"]

    # Create SQS queue and save queue_url
    queue_url = create_sqs_queue(user)

    # Subscribe (or edit) event
    url = f"https://{user_ip}:{user_port}/subscribe"
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }
    data = {"event_type": event_type, "cmd": cmd}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"Successfully subscribed/updated {user} to {event_type}.")
        return {"queue_url": queue_url, "user_service": user_service}
    else:
        raise Exception(f"Failed to subscribe/update user: {response.text}")


def unsubscribe_event(user, event_type):
    """unsubscribe from an event"""

    user_service = register_user(user)
    user_ip, user_port, user_token = user_service["ip"], user_service["port"], user_service["token"]

    url = f"https://{user_ip}:{user_port}/unsubscribe"
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }
    data = {"event_type": event_type}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"Successfully unsubscribed {user} from {event_type}.")
    else:
        raise Exception(f"Failed to unsubscribe user: {response.text}")


def list_subscriptions(user):
    """get list of subscriptions for a user"""

    user_service = register_user(user)
    user_ip, user_port, user_token = user_service["ip"], user_service["port"], user_service["token"]

    url = f"https://{user_ip}:{user_port}/list-subscriptions"
    headers = {
        "Authorization": f"Bearer {user_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        subscriptions = response.json()
        print(f"Subscriptions for {user}: {json.dumps(subscriptions, indent=4)}")
    else:
        raise Exception(f"Failed to fetch subscriptions: {response.text}")


if __name__ == "__main__":
    """CLI Execution"""

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

    if args.action in ["subscribe", "edit"]:
        if not args.event_type:
            print("Error: Event type is required for subscribing or editing.")
            exit(1)
        if not args.cmd:
            print("Error: --cmd is required for subscribing or editing.")
            exit(1)
        result = subscribe_event(args.user, args.event_type, args.cmd)
        print(f"Subscribed/Updated Successfully! Queue URL: {result['queue_url']}")

    elif args.action == "unsubscribe":
        if not args.event_type:
            print("Error: Event type is required for unsubscribing.")
            exit(1)
        unsubscribe_event(args.user, args.event_type)

    elif args.action == "info":
        list_subscriptions(args.user)

