import asyncio
import json
from db import Database
from processor import process_event
from sqs_service import SQSService

async def main(event_json):
    """
    event_json example:
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
    # Setup DB connection
    db = Database()
    db.init()

    try:
        for record in event_json['Records']:
            await process_event(record, db)
            # delete record from queue
            delete_record_from_queue(record)
    finally:
        db.close()


def delete_record_from_queue(record):
    """ deletes event from queue """
    # delete record from queue
    receipt_handle = record['receiptHandle']
    region_name = "us-east-1"
    queue_url = get_queue_url(record['eventSourceARN'])
    
    sqs_service = SQSService(queue_url=queue_url, region_name=region_name)
    # Delete the message
    try:
        sqs_service.delete_message(receipt_handle)
    except Exception as e:
        print(f"Error deleting message: {str(e)}")


def get_queue_url(queue_arn):
    """ returns queue url """
    region = queue_arn.split(":")[3]
    account_id = queue_arn.split(":")[4]
    queue_name = queue_arn.split(":")[5]

    # Construct queue URL
    queue_url = f"https://sqs.{region}.amazonaws.com/{account_id}/{queue_name}"

    print(f"Queue URL: {queue_url}")
    return queue_url


# Synchronous wrapper
def run_main(event_json):
    asyncio.run(main(event_json))


