import json
from main import run_main

def lambda_handler(event, context):
    """
    example event:
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
    print(event)
    run_main(event)
    
    return {
        'statusCode': 200,
        'body': 'Messages processed successfully.'
    }

