import json
import logging
import boto3
from datetime import datetime

# Import our orchestrator
try:
    from src.agents.orchestrator import run_investigation
except ImportError:
    import sys
    sys.path.insert(0, '/var/task')
    from src.agents.orchestrator import run_investigation

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def validate_event(event: dict) -> tuple:
    """
    Validate incoming Lambda event.

    WHY: Lambda can receive malformed requests.
    We validate before processing to avoid errors.

    Returns:
        (is_valid, error_message)
    """
    # Check required fields
    if not event.get('customer_id'):
        return False, "Missing required field: customer_id"

    if not event.get('transactions'):
        return False, "Missing required field: transactions"

    if not isinstance(event.get('transactions'), list):
        return False, "transactions must be a list"

    if len(event.get('transactions')) == 0:
        return False, "transactions list cannot be empty"

    return True, None


def build_response(status_code: int, body: dict) -> dict:
    """
    Build standard Lambda response.

    WHY: Lambda needs a specific response format
    for API Gateway to work correctly.
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body, default=str)
    }


def lambda_handler(event, context):
    """
    Main Lambda entry point.

    WHY this is important:
    This is what AWS calls when an alert comes in.
    It's the BRIDGE between the outside world
    and our multi-agent pipeline.

    Flow:
    1. Receive alert from bank system
    2. Validate the data
    3. Run full investigation pipeline
    4. Return results

    Args:
        event: Alert data from bank system
        context: AWS Lambda context (runtime info)

    Returns:
        HTTP response with investigation results
    """
    # Log the incoming request
    logger.info("=" * 60)
    logger.info("🚨 AML Alert Received!")
    logger.info(f"   Request ID: {context.aws_request_id if context else 'LOCAL_TEST'}")
    logger.info(f"   Time: {datetime.now().isoformat()}")

    try:
        # Step 1: Parse event body
        # API Gateway sends body as string, direct Lambda sends as dict
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event

        logger.info(f"   Customer ID: {body.get('customer_id')}")
        logger.info(f"   Transactions: {len(body.get('transactions', []))}")

        # Step 2: Validate incoming data
        is_valid, error_message = validate_event(body)
        if not is_valid:
            logger.error(f"❌ Validation failed: {error_message}")
            return build_response(400, {
                'success': False,
                'error': error_message,
                'timestamp': datetime.now().isoformat()
            })

        # Step 3: Extract data from event
        customer_id = body.get('customer_id')
        customer_name = body.get('customer_name', 'Unknown')
        transactions = body.get('transactions', [])
        investigation_id = body.get('investigation_id')

        # Step 4: Run full investigation pipeline
        logger.info("🚀 Starting investigation pipeline...")
        report = run_investigation(
            customer_id=customer_id,
            customer_name=customer_name,
            transactions=transactions,
            investigation_id=investigation_id
        )

        # Step 5: Check if investigation succeeded
        if report.get('status') == 'FAILED':
            logger.error(f"❌ Investigation failed: {report.get('error')}")
            return build_response(500, {
                'success': False,
                'error': report.get('error'),
                'investigation_id': report.get('investigation_id'),
                'timestamp': datetime.now().isoformat()
            })

        # Step 6: Build success response
        final_decision = report.get('final_decision', {})

        response_body = {
            'success': True,
            'investigation_id': report.get('investigation_id'),
            'customer_id': customer_id,
            'customer_name': customer_name,
            'timestamp': datetime.now().isoformat(),
            'results': {
                'final_risk_level': final_decision.get('final_risk_level'),
                'final_risk_score': final_decision.get('final_risk_score'),
                'recommended_action': final_decision.get('recommended_action'),
                'summary': final_decision.get('summary'),
                'transaction_patterns': report.get('transaction_analysis', {}).get('patterns_found', []),
                'customer_risk': report.get('customer_analysis', {}).get('customer_risk_level'),
                'confidence': final_decision.get('confidence'),
                'reasoning': final_decision.get('reasoning')
            }
        }

        logger.info("✅ Investigation complete!")
        logger.info(f"   Risk Level: {final_decision.get('final_risk_level')}")
        logger.info(f"   Action: {final_decision.get('recommended_action')}")

        return build_response(200, response_body)

    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON: {str(e)}")
        return build_response(400, {
            'success': False,
            'error': f'Invalid JSON: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
        return build_response(500, {
            'success': False,
            'error': f'Internal server error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })


# =============================================
# LOCAL TEST
# =============================================

class MockContext:
    """
    Mock AWS Lambda context for local testing.
    
    WHY: When testing locally we don't have
    real AWS Lambda context object.
    This simulates it.
    """
    aws_request_id = "LOCAL_TEST_001"
    function_name = "aml-investigation-assistant"
    memory_limit_in_mb = 512


if __name__ == "__main__":
    print("🧪 Testing Lambda Handler Locally...")
    print("=" * 60)
    print("")

    # Test Case 1: Valid suspicious transactions
    print("Test 1: Valid Suspicious Request")
    print("-" * 40)

    test_event = {
        "customer_id": "CUST_LAMBDA_001",
        "customer_name": "John Doe",
        "investigation_id": "INV_LAMBDA_TEST_001",
        "transactions": [
            {"date": "2026-01-01", "type": "DEPOSIT",
             "amount": 9500, "description": "Cash deposit",
             "destination": "Main account"},
            {"date": "2026-01-02", "type": "DEPOSIT",
             "amount": 9200, "description": "Cash deposit",
             "destination": "Main account"},
            {"date": "2026-01-03", "type": "DEPOSIT",
             "amount": 9800, "description": "Cash deposit",
             "destination": "Main account"},
            {"date": "2026-01-04", "type": "DEPOSIT",
             "amount": 9100, "description": "Cash deposit",
             "destination": "Main account"},
            {"date": "2026-01-05", "type": "DEPOSIT",
             "amount": 9600, "description": "Cash deposit",
             "destination": "Main account"},
        ]
    }

    response = lambda_handler(test_event, MockContext())
    body = json.loads(response['body'])

    print(f"   Status Code:      {response['statusCode']}")
    print(f"   Success:          {body['success']}")
    print(f"   Investigation ID: {body['investigation_id']}")
    print(f"   Risk Level:       {body['results']['final_risk_level']}")
    print(f"   Risk Score:       {body['results']['final_risk_score']}")
    print(f"   Action:           {body['results']['recommended_action']}")
    print(f"   Patterns:         {body['results']['transaction_patterns']}")
    print(f"   Summary:          {body['results']['summary']}")
    print("")

    # Test Case 2: Missing customer_id (validation test)
    print("Test 2: Missing customer_id (should fail validation)")
    print("-" * 40)

    bad_event = {
        "transactions": [
            {"date": "2026-01-01", "type": "DEPOSIT",
             "amount": 9500, "description": "Cash deposit",
             "destination": "Main account"}
        ]
    }

    response2 = lambda_handler(bad_event, MockContext())
    body2 = json.loads(response2['body'])

    print(f"   Status Code: {response2['statusCode']}")
    print(f"   Success:     {body2['success']}")
    print(f"   Error:       {body2['error']}")
    print("")

    # Test Case 3: Empty transactions (validation test)
    print("Test 3: Empty transactions (should fail validation)")
    print("-" * 40)

    empty_event = {
        "customer_id": "CUST_TEST_003",
        "transactions": []
    }

    response3 = lambda_handler(empty_event, MockContext())
    body3 = json.loads(response3['body'])

    print(f"   Status Code: {response3['statusCode']}")
    print(f"   Success:     {body3['success']}")
    print(f"   Error:       {body3['error']}")
    print("")

    print("✅ Lambda Handler test complete!")