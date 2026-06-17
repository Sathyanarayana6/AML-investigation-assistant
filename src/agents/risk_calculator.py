import logging
from typing import Dict, Any, List

from src.utils.bedrock_client import call_claude_with_json_response
from src.utils.dynamodb_logger import log_to_dynamodb

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Risk Calculator System Prompt
RISK_CALCULATOR_SYSTEM_PROMPT = """
You are a Senior AML Risk Calculator for a financial compliance team.

Your job is to combine transaction analysis and customer profile analysis
to make a FINAL risk decision.

SCORING RULES:

TRANSACTION RISK WEIGHT: 60%
- HIGH transaction risk   = 60 points
- MEDIUM transaction risk = 30 points
- LOW transaction risk    = 0 points

CUSTOMER RISK WEIGHT: 40%
- HIGH customer risk      = 40 points
- MEDIUM customer risk    = 20 points
- LOW customer risk       = 0 points

FINAL SCORE → DECISION:
- 80-100 points = CRITICAL  → IMMEDIATE_REVIEW
- 60-79 points  = HIGH      → ESCALATE_TO_ANALYST
- 30-59 points  = MEDIUM    → MONITOR
- 0-29 points   = LOW       → NO_ACTION

AUTOMATIC ESCALATION RULES:
- PEP (Politically Exposed Person) detected → Always ESCALATE minimum
- 3+ AML patterns detected → Always IMMEDIATE_REVIEW
- Previous flags > 2 → Always ESCALATE minimum

RESPOND ONLY WITH JSON:
{
    "final_risk_score": 0-100,
    "final_risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
    "recommended_action": "NO_ACTION" | "MONITOR" | "ESCALATE_TO_ANALYST" | "IMMEDIATE_REVIEW",
    "transaction_risk_contribution": 0-60,
    "customer_risk_contribution": 0-40,
    "escalation_triggers": [],
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation of final decision",
    "summary": "One sentence summary for analyst"
}
"""


def format_combined_analysis(transaction_analysis: Dict[str, Any],
                              customer_analysis: Dict[str, Any]) -> str:
    """
    Format both analyses for Claude to combine.
    
    WHY: Claude needs both results in one clear format
    to make an accurate final decision.
    """
    formatted = "COMBINED ANALYSIS FOR FINAL RISK DECISION:\n"
    formatted += "=" * 60 + "\n\n"

    # Transaction Analysis Summary
    formatted += "TRANSACTION ANALYSIS RESULTS:\n"
    formatted += f"  Risk Score:      {transaction_analysis.get('risk_score', 'UNKNOWN')}\n"
    formatted += f"  Patterns Found:  {transaction_analysis.get('patterns_found', [])}\n"
    formatted += f"  Confidence:      {transaction_analysis.get('confidence', 0)}\n"
    formatted += f"  Reasoning:       {transaction_analysis.get('reasoning', 'N/A')[:150]}\n"
    formatted += "\n"

    # Customer Analysis Summary
    formatted += "CUSTOMER PROFILE RESULTS:\n"
    formatted += f"  Customer Risk:   {customer_analysis.get('customer_risk_level', 'UNKNOWN')}\n"
    formatted += f"  Risk Factors:    {customer_analysis.get('risk_factors', [])}\n"
    formatted += f"  Confidence:      {customer_analysis.get('confidence', 0)}\n"
    formatted += f"  Reasoning:       {customer_analysis.get('reasoning', 'N/A')[:150]}\n"

    # Add raw profile details if available
    raw_profile = customer_analysis.get('raw_profile', {})
    if raw_profile:
        formatted += "\n"
        formatted += "CUSTOMER DETAILS:\n"
        formatted += f"  Account Age:     {raw_profile.get('account_age_months')} months\n"
        formatted += f"  Previous Flags:  {raw_profile.get('previous_flags')}\n"
        formatted += f"  Is PEP:          {raw_profile.get('is_pep')}\n"
        formatted += f"  Occupation:      {raw_profile.get('occupation')}\n"
        formatted += f"  Monthly Income:  ${raw_profile.get('monthly_income', 0):,}\n"

    formatted += "\n" + "=" * 60 + "\n"
    return formatted


def risk_calculator(transaction_analysis: Dict[str, Any],
                    customer_analysis: Dict[str, Any],
                    investigation_id: str,
                    customer_id: str = None) -> Dict[str, Any]:
    """
    Calculate final risk score combining all agent results.

    WHY this is the most important agent:
    It makes the FINAL decision that analysts will act on.
    It must be:
    - Accurate (catch real money laundering)
    - Fair (not flag innocent customers)
    - Explainable (analyst must understand WHY)
    - Auditable (every decision logged to DynamoDB)

    Args:
        transaction_analysis: Results from Agent 1
        customer_analysis: Results from Agent 2
        investigation_id: Links all agents together
        customer_id: Customer being investigated

    Returns:
        Final risk decision with score, level, and recommended action
    """

    logger.info(f"🧮 Calculating final risk score...")
    logger.info(f"   Transaction Risk: {transaction_analysis.get('risk_score')}")
    logger.info(f"   Customer Risk: {customer_analysis.get('customer_risk_level')}")

    try:
        # Step 1: Format combined analysis
        combined = format_combined_analysis(
            transaction_analysis,
            customer_analysis
        )

        # Step 2: Build prompt
        user_prompt = f"""
Please calculate the final AML risk score and recommended action.

{combined}

Apply the scoring rules and escalation triggers.
Return your final decision as JSON.
"""

        # Step 3: Call Claude for final decision
        logger.info("🤖 Calling Claude for final risk calculation...")
        final_decision = call_claude_with_json_response(
            prompt=user_prompt,
            system_prompt=RISK_CALCULATOR_SYSTEM_PROMPT,
            max_tokens=1024
        )

        logger.info(f"✅ Final decision made!")
        logger.info(f"   Final Risk Score:  {final_decision.get('final_risk_score')}")
        logger.info(f"   Final Risk Level:  {final_decision.get('final_risk_level')}")
        logger.info(f"   Recommended Action: {final_decision.get('recommended_action')}")

        # Step 4: Log to DynamoDB
        log_to_dynamodb(
            investigation_id=investigation_id,
            agent_name="risk_calculator",
            agent_action="calculated_final_risk",
            input_data={
                'transaction_risk': transaction_analysis.get('risk_score'),
                'customer_risk': customer_analysis.get('customer_risk_level'),
                'patterns_found': transaction_analysis.get('patterns_found', [])
            },
            output_data=final_decision,
            status="SUCCESS"
        )

        return final_decision

    except Exception as e:
        logger.error(f"❌ Error in risk_calculator: {str(e)}")

        log_to_dynamodb(
            investigation_id=investigation_id,
            agent_name="risk_calculator",
            agent_action="calculated_final_risk",
            input_data={},
            output_data={},
            status="FAILURE",
            error_message=str(e)
        )

        return {
            "final_risk_score": 50,
            "final_risk_level": "MEDIUM",
            "recommended_action": "ESCALATE_TO_ANALYST",
            "confidence": 0.0,
            "reasoning": f"Calculation failed: {str(e)}",
            "summary": "Manual review required due to system error"
        }


# TEST
if __name__ == "__main__":
    print("🧪 Testing Risk Calculator...")
    print("")

    # Test Case 1: HIGH transaction + HIGH customer = CRITICAL
    print("Test 1: HIGH + HIGH = Should be CRITICAL")
    print("-" * 50)

    result1 = risk_calculator(
        transaction_analysis={
            "risk_score": "HIGH",
            "patterns_found": ["STRUCTURING", "RAPID_MOVEMENT"],
            "confidence": 0.95,
            "reasoning": "Multiple deposits under $10K with rapid withdrawal"
        },
        customer_analysis={
            "customer_risk_level": "HIGH",
            "risk_factors": ["new_account", "previous_flags", "unknown_occupation"],
            "confidence": 0.90,
            "reasoning": "New account with 2 previous flags",
            "raw_profile": {
                "account_age_months": 2,
                "previous_flags": 2,
                "is_pep": False,
                "occupation": "Unknown",
                "monthly_income": 2000
            }
        },
        investigation_id="TEST_RISK_001",
        customer_id="CUST_TEST_001"
    )

    print(f"   Final Risk Score:    {result1.get('final_risk_score')}")
    print(f"   Final Risk Level:    {result1.get('final_risk_level')}")
    print(f"   Recommended Action:  {result1.get('recommended_action')}")
    print(f"   Summary:             {result1.get('summary')}")
    print("")

    # Test Case 2: LOW transaction + LOW customer = NO ACTION
    print("Test 2: LOW + LOW = Should be NO ACTION")
    print("-" * 50)

    result2 = risk_calculator(
        transaction_analysis={
            "risk_score": "LOW",
            "patterns_found": [],
            "confidence": 0.97,
            "reasoning": "Normal salary and bill payments"
        },
        customer_analysis={
            "customer_risk_level": "LOW",
            "risk_factors": [],
            "confidence": 0.95,
            "reasoning": "Established account with clean history",
            "raw_profile": {
                "account_age_months": 60,
                "previous_flags": 0,
                "is_pep": False,
                "occupation": "Software Engineer",
                "monthly_income": 8000
            }
        },
        investigation_id="TEST_RISK_002",
        customer_id="CUST_TEST_002"
    )

    print(f"   Final Risk Score:    {result2.get('final_risk_score')}")
    print(f"   Final Risk Level:    {result2.get('final_risk_level')}")
    print(f"   Recommended Action:  {result2.get('recommended_action')}")
    print(f"   Summary:             {result2.get('summary')}")
    print("")

    # Test Case 3: HIGH transaction + LOW customer = ESCALATE
    print("Test 3: HIGH + LOW = Should be ESCALATE")
    print("-" * 50)

    result3 = risk_calculator(
        transaction_analysis={
            "risk_score": "HIGH",
            "patterns_found": ["STRUCTURING"],
            "confidence": 0.92,
            "reasoning": "Multiple deposits just under $10K"
        },
        customer_analysis={
            "customer_risk_level": "LOW",
            "risk_factors": [],
            "confidence": 0.95,
            "reasoning": "Long established account clean history",
            "raw_profile": {
                "account_age_months": 84,
                "previous_flags": 0,
                "is_pep": False,
                "occupation": "Business Owner",
                "monthly_income": 15000
            }
        },
        investigation_id="TEST_RISK_003",
        customer_id="CUST_TEST_003"
    )

    print(f"   Final Risk Score:    {result3.get('final_risk_score')}")
    print(f"   Final Risk Level:    {result3.get('final_risk_level')}")
    print(f"   Recommended Action:  {result3.get('recommended_action')}")
    print(f"   Summary:             {result3.get('summary')}")
    print("")

    print("✅ Risk Calculator test complete!")