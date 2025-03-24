import importlib
import traceback
from db import Database
from typing import Dict, Any, List
from sqs_service import SQSService

async def process_event(event_json: Dict[str, Any], db: Database):
    """
    Main processor to filter authorized users based on event and strategy JSON.
    {
      "Records": [
        {
          "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
          "receiptHandle": "MessageReceiptHandle",
          "body": {
            "event_type": "test2"
            "strategy": "test_strat_ut"
           },
          "attributes": {
            "ApproximateReceiveCount": "1",
            "SentTimestamp": "1523232000000",
            "SenderId": "123456789012",
            "ApproximateFirstReceiveTimestamp": "1523232000001"
          },
          "messageAttributes": {},
          "md5OfBody": "{{{md5_of_body}}}",
          "eventSource": "aws:sqs",
          "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:MyQueue",
          "awsRegion": "us-east-1"
        }
      ]
    }

    """
    event_data = event_json["body"]
    event_type = event_data.get("event_type")
    if not event_type:
        raise ValueError("event_type missing in event data")

    # Fetch users who have subscribed to the event
    subscribers = db.get_subscribers(event_type)
    print(f"subscribers: {subscribers}")
    # Fetch required access checks
    acl_check_funcs = db.get_event_acl_functions(event_type)
    print(f"[INFO] Acl check functions for event '{event_type}': {acl_check_funcs}")
    
    authorized_users = []

    for user in subscribers:
        if await check_user_event_access(user, event_data, acl_check_funcs):
            authorized_users.append(user)

    print(f"[RESULT] Authorized users: {authorized_users}")

    # add event to user queues
    # TODO: call this function in parallel instead of using for loop
    for user in authorized_users:
        await send_event_to_user_queue(user, event_json, db)

    return authorized_users

async def check_user_event_access(user, event_data, acl_functions):
    """Dynamically fetch and execute all ACL functions for an event."""
    for acl_func in acl_functions:
        func_path = acl_func["function_path"]
        module_name, func_name = func_path.rsplit('.', 1)

        module = importlib.import_module(module_name)  # Import module dynamically
        acl_function = getattr(module, func_name)  # Get function from module

        if not acl_function(user, event_data):
            return False

    return True  # All checks passed

async def send_event_to_user_queue(username, event_json, db):
    """ send events to user queues """
    try:
        queue_url = db.get_user_queue_url(username)
        print(f"for {username} queue_url: {queue_url}")
        region_name = "us-east-1"
        sqs_service = SQSService(queue_url=queue_url, region_name=region_name)
        
        # For FIFO queues, messages with the same MessageGroupId are processed in order
        message_id = sqs_service.send_message(
                        message_body=event_json['body'],
                        # TODO: check this
                        message_group_id=f"{username}_test_group",  # Required for FIFO queues
                    )
        if message_id:
            print(f"Test message sent successfully with ID: {message_id}")
    except Exception as e:
        print(f"Some issue in sending event to user queue: {e}")
        print(f"Traceback: {traceback.format_exc()}")
