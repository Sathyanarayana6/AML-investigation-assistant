import json
import logging
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os

# Load credentials from .env
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get values from .env
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "aml-investigation-logs")

# Create DynamoDB connection
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def log_to_dynamodb(investigation_id, agent_name, agent_action, 
                    input_data, output_data, status="SUCCESS", error_message=None):
    """
    Log every agent action to DynamoDB.
    
    WHY: Financial compliance requires full audit trail.
    Every time Claude analyzes transactions, we log:
    - What was analyzed (input)
    - What Claude found (output)
    - When it happened (timestamp)
    - Whether it succeeded or failed (status)
    """
    try:
        # Build the log entry
        log_entry = {
            # Primary key - unique ID for this investigation
            'investigation_id': investigation_id,
            
            # When this happened
            'timestamp': datetime.now().isoformat(),
            
            # Which agent ran (transaction_analyzer, risk_calculator, etc.)
            'agent_name': agent_name,
            
            # What the agent did
            'agent_action': agent_action,
            
            # Did it succeed or fail?
            'status': status,
            
            # What went in (transaction data)
            'input_data': json.dumps(input_data) if not isinstance(input_data, str) else input_data,
            
            # What came out (Claude's analysis)
            'output_data': json.dumps(output_data) if not isinstance(output_data, str) else output_data,
        }

        # Add error message if something went wrong
        if error_message:
            log_entry['error_message'] = error_message

        # Save to DynamoDB
        table.put_item(Item=log_entry)
        logger.info(f"✅ Logged: {agent_name}/{agent_action} for {investigation_id}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to log to DynamoDB: {str(e)}")
        return False


def get_investigation_log(investigation_id):
    """
    Retrieve all logs for a specific investigation.
    
    WHY: Analysts can review exactly what the AI did
    and why it flagged a transaction as suspicious.
    """
    try:
        response = table.query(
            KeyConditionExpression='investigation_id = :inv_id',
            ExpressionAttributeValues={':inv_id': investigation_id},
            ScanIndexForward=True  # Oldest first
        )
        return response.get('Items', [])

    except Exception as e:
        logger.error(f"❌ Failed to retrieve logs: {str(e)}")
        return []


# TEST: Run this file directly to verify DynamoDB is working
if __name__ == "__main__":
    print("🧪 Testing DynamoDB Connection...")
    print(f"   Region: {AWS_REGION}")
    print(f"   Table: {DYNAMODB_TABLE_NAME}")
    print("")

    # Test writing a log entry
    test_id = f"TEST_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    success = log_to_dynamodb(
        investigation_id=test_id,
        agent_name="test_agent",
        agent_action="connection_test",
        input_data={"test": "input data"},
        output_data={"test": "output data"},
        status="SUCCESS"
    )

    if success:
        print("✅ DynamoDB write working!")

        # Test reading it back
        logs = get_investigation_log(test_id)
        if logs:
            print("✅ DynamoDB read working!")
            print(f"   Found {len(logs)} log entry")
            print(f"   Investigation ID: {logs[0]['investigation_id']}")
            print(f"   Timestamp: {logs[0]['timestamp']}")
            print(f"   Status: {logs[0]['status']}")
        else:
            print("⚠️  Could not read back the log")
    else:
        print("❌ DynamoDB write failed!")
        print("")
        print("Troubleshooting:")
        print("  1. Check DynamoDB table exists in AWS Console")
        print("  2. Verify table name in .env matches exactly")
        print("  3. Check IAM role has DynamoDB permissions")