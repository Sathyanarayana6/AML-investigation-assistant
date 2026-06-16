import json
import logging
from typing import Dict, List, Any
from datetime import datetime

from src.utils.bedrock_client import call_claude_with_json_response
from src.utils.dynamodb_logger import log_to_dynamodb
from src.agents.transaction_analyzer_prompt import TRANSACTION_ANALYZER_SYSTEM_PROMPT

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def format_transactions_for_claude(transactions: List[Dict[str, Any]]) -> str:
    """
    Format raw transaction data into readable text for Claude.
    
    WHY: Claude understands natural language better than raw JSON.
    We convert transaction dictionaries into a clear, readable format.
    """
    formatted = "TRANSACTION HISTORY:\n"
    formatted += "=" * 60 + "\n"

    for i, tx in enumerate(transactions, 1):
        formatted += f"\nTransaction {i}:\n"
        formatted += f"  Date:        {tx.get('date', 'N/A')}\n"
        formatted += f"  Type:        {tx.get('type', 'N/A')}\n"
        formatted += f"  Amount:      ${tx.get('amount', 0):,.2f}\n"
        formatted += f"  Description: {tx.get('description', 'N/A')}\n"
        formatted += f"  Destination: {tx.get('destination', 'N/A')}\n"

    formatted += "\n" + "=" * 60 + "\n"
    formatted += f"Total Transactions: {len(transactions)}\n"

    return formatted


def transaction_analyzer(transactions: List[Dict[str, Any]], 
                         investigation_id: str,
                         customer_id: str = None, 
                         customer_name: str = None) -> Dict[str, Any]:
    """
    Main agent function - analyzes transactions for AML patterns.
    
    WHY this structure:
    1. Format data for Claude (readable format)
    2. Call Claude with system prompt (expert instructions)
    3. Get back structured JSON (risk score, patterns, reasoning)
    4. Log everything to DynamoDB (audit trail)
    5. Return analysis to caller (Lambda or test)
    
    Args:
        transactions: List of transaction dictionaries
        investigation_id: Unique ID for this investigation
        customer_id: Customer being investigated
        customer_name: Customer name for context
    
    Returns:
        Dictionary with patterns_found, risk_score, confidence, reasoning
    """

    logger.info(f"🔍 Starting analysis for investigation: {investigation_id}")
    logger.info(f"   Customer: {customer_id}")
    logger.info(f"   Transactions to analyze: {len(transactions)}")

    # Handle empty transactions
    if not transactions or len(transactions) == 0:
        logger.warning("⚠️  No transactions provided")
        return {
            "patterns_found": [],
            "risk_score": "LOW",
            "confidence": 0.95,
            "reasoning": "No transactions provided for analysis",
            "recommended_action": "NO_ACTION"
        }

    try:
        # Step 1: Format transactions for Claude
        formatted_transactions = format_transactions_for_claude(transactions)

        # Step 2: Build the prompt
        user_prompt = f"""
Please analyze the following transaction history for AML patterns.

CUSTOMER INFORMATION:
  Customer ID:   {customer_id if customer_id else 'Unknown'}
  Customer Name: {customer_name if customer_name else 'Unknown'}
  Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC

{formatted_transactions}

Identify any suspicious AML patterns and return your analysis as JSON.
Remember to check for: STRUCTURING, SMURFING, LAYERING, 
CIRCULAR_TRANSFERS, and RAPID_MOVEMENT patterns.
"""

        # Step 3: Call Claude for analysis
        logger.info("🤖 Calling Claude for analysis...")
        analysis = call_claude_with_json_response(
            prompt=user_prompt,
            system_prompt=TRANSACTION_ANALYZER_SYSTEM_PROMPT,
            max_tokens=1024
        )

        logger.info(f"✅ Analysis complete!")
        logger.info(f"   Risk Score: {analysis.get('risk_score')}")
        logger.info(f"   Patterns Found: {analysis.get('patterns_found')}")
        logger.info(f"   Confidence: {analysis.get('confidence')}")

        # Step 4: Log to DynamoDB (audit trail)
        log_to_dynamodb(
            investigation_id=investigation_id,
            agent_name="transaction_analyzer",
            agent_action="analyzed_patterns",
            input_data={
                'transaction_count': len(transactions),
                'customer_id': customer_id,
                'customer_name': customer_name
            },
            output_data=analysis,
            status="SUCCESS"
        )

        # Step 5: Return analysis
        return analysis

    except Exception as e:
        logger.error(f"❌ Error in transaction_analyzer: {str(e)}")

        # Log the failure too (important for debugging)
        log_to_dynamodb(
            investigation_id=investigation_id,
            agent_name="transaction_analyzer",
            agent_action="analyzed_patterns",
            input_data={'transaction_count': len(transactions)},
            output_data={},
            status="FAILURE",
            error_message=str(e)
        )

        # Return safe default on failure
        return {
            "patterns_found": [],
            "risk_score": "MEDIUM",
            "confidence": 0.0,
            "reasoning": f"Analysis failed: {str(e)}",
            "recommended_action": "ESCALATE_TO_ANALYST"
        }


# TEST: Run directly to verify agent works
if __name__ == "__main__":
    print("🧪 Testing Transaction Analyzer Agent...")
    print("")

    # Test Case 1: Structuring Pattern
    print("Test 1: Structuring Pattern (should be HIGH risk)")
    print("-" * 50)

    structuring_transactions = [
        {"date": "2026-01-01", "type": "DEPOSIT", "amount": 9500, 
         "description": "Cash deposit", "destination": "Main account"},
        {"date": "2026-01-02", "type": "DEPOSIT", "amount": 9200, 
         "description": "Cash deposit", "destination": "Main account"},
        {"date": "2026-01-03", "type": "DEPOSIT", "amount": 9800, 
         "description": "Cash deposit", "destination": "Main account"},
        {"date": "2026-01-04", "type": "DEPOSIT", "amount": 9100, 
         "description": "Cash deposit", "destination": "Main account"},
        {"date": "2026-01-05", "type": "DEPOSIT", "amount": 9600, 
         "description": "Cash deposit", "destination": "Main account"},
        {"date": "2026-01-06", "type": "DEPOSIT", "amount": 9300, 
         "description": "Cash deposit", "destination": "Main account"},
        {"date": "2026-01-07", "type": "DEPOSIT", "amount": 9700, 
         "description": "Cash deposit", "destination": "Main account"},
        {"date": "2026-01-08", "type": "DEPOSIT", "amount": 9400, 
         "description": "Cash deposit", "destination": "Main account"},
    ]

    result = transaction_analyzer(
        transactions=structuring_transactions,
        investigation_id="TEST_STRUCTURING_001",
        customer_id="CUST_12345",
        customer_name="John Doe"
    )

    print(f"   Patterns Found:      {result.get('patterns_found')}")
    print(f"   Risk Score:          {result.get('risk_score')}")
    print(f"   Confidence:          {result.get('confidence')}")
    print(f"   Recommended Action:  {result.get('recommended_action')}")
    print(f"   Reasoning:           {result.get('reasoning')[:100]}...")
    print("")

    # Test Case 2: Legitimate Transactions
    print("Test 2: Legitimate Transactions (should be LOW risk)")
    print("-" * 50)

    legitimate_transactions = [
        {"date": "2026-01-01", "type": "DEPOSIT", "amount": 3500, 
         "description": "Salary payment", "destination": "Main account"},
        {"date": "2026-01-05", "type": "PAYMENT", "amount": 150, 
         "description": "Electric bill", "destination": "Utility company"},
        {"date": "2026-01-10", "type": "TRANSFER", "amount": 1200, 
         "description": "Rent payment", "destination": "Landlord account"},
        {"date": "2026-01-15", "type": "WITHDRAWAL", "amount": 200, 
         "description": "ATM withdrawal", "destination": "ATM"},
        {"date": "2026-01-20", "type": "PAYMENT", "amount": 80, 
         "description": "Internet bill", "destination": "ISP company"},
    ]

    result2 = transaction_analyzer(
        transactions=legitimate_transactions,
        investigation_id="TEST_LEGITIMATE_001",
        customer_id="CUST_67890",
        customer_name="Jane Smith"
    )

    print(f"   Patterns Found:      {result2.get('patterns_found')}")
    print(f"   Risk Score:          {result2.get('risk_score')}")
    print(f"   Confidence:          {result2.get('confidence')}")
    print(f"   Recommended Action:  {result2.get('recommended_action')}")
    print(f"   Reasoning:           {result2.get('reasoning')[:100]}...")
    print("")
    print("✅ Agent test complete!")