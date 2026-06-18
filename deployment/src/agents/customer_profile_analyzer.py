import json
import logging
import random
from typing import Dict, Any
from datetime import datetime, timedelta

from src.utils.bedrock_client import call_claude_with_json_response
from src.utils.dynamodb_logger import log_to_dynamodb

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Customer Profile Analyzer System Prompt
CUSTOMER_PROFILE_SYSTEM_PROMPT = """
You are a Customer Profile Analyzer for AML compliance.

Your job is to analyze a customer's profile and assess their risk level.

RISK FACTORS TO CONSIDER:

1. ACCOUNT AGE
   - New account (< 6 months) = Higher risk
   - Established account (> 2 years) = Lower risk

2. TRANSACTION HISTORY
   - Sudden change in behavior = Higher risk
   - Consistent normal pattern = Lower risk

3. PREVIOUS FLAGS
   - Previously flagged = Higher risk
   - Clean history = Lower risk

4. OCCUPATION & INCOME
   - Income matches transactions = Lower risk
   - Transactions exceed income = Higher risk

5. ACCOUNT TYPE
   - Business account = Different patterns expected
   - Personal account = Stricter thresholds

RESPOND ONLY WITH JSON:
{
    "customer_risk_level": "LOW" | "MEDIUM" | "HIGH",
    "risk_factors": ["factor1", "factor2"],
    "account_age_months": 0,
    "previous_flags": 0,
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation"
}
"""


def get_customer_profile(customer_id: str) -> Dict[str, Any]:
    """
    Get customer profile from database.
    
    WHY: In real world this would query your core banking system.
    For Phase 2 we generate realistic synthetic profiles.
    
    In Phase 3 we'll connect to real customer data.
    """
    # Seed random with customer_id for consistent results
    random.seed(hash(customer_id) % 1000)

    # Generate realistic customer profile
    account_age_months = random.randint(1, 120)
    previous_flags = random.randint(0, 3)
    monthly_income = random.choice([2000, 3500, 5000, 8000, 15000, 25000])
    account_type = random.choice(["PERSONAL", "BUSINESS", "SAVINGS"])
    occupation = random.choice([
        "Software Engineer",
        "Teacher",
        "Business Owner",
        "Retail Worker",
        "Doctor",
        "Unknown"
    ])

    return {
        "customer_id": customer_id,
        "account_age_months": account_age_months,
        "account_type": account_type,
        "occupation": occupation,
        "monthly_income": monthly_income,
        "previous_flags": previous_flags,
        "last_flag_date": (
            (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d')
            if previous_flags > 0 else None
        ),
        "country_of_origin": random.choice([
            "US", "US", "US", "UK", "Canada", "Mexico", "Unknown"
        ]),
        "is_pep": random.choice([False, False, False, True]),  # Politically Exposed Person
        "account_status": "ACTIVE"
    }


def format_profile_for_claude(profile: Dict[str, Any]) -> str:
    """Format customer profile for Claude to analyze"""
    formatted = "CUSTOMER PROFILE:\n"
    formatted += "=" * 60 + "\n"
    formatted += f"  Customer ID:        {profile.get('customer_id')}\n"
    formatted += f"  Account Age:        {profile.get('account_age_months')} months\n"
    formatted += f"  Account Type:       {profile.get('account_type')}\n"
    formatted += f"  Occupation:         {profile.get('occupation')}\n"
    formatted += f"  Monthly Income:     ${profile.get('monthly_income'):,}\n"
    formatted += f"  Previous Flags:     {profile.get('previous_flags')}\n"
    formatted += f"  Last Flag Date:     {profile.get('last_flag_date', 'Never')}\n"
    formatted += f"  Country of Origin:  {profile.get('country_of_origin')}\n"
    formatted += f"  Is PEP:             {profile.get('is_pep')}\n"
    formatted += f"  Account Status:     {profile.get('account_status')}\n"
    formatted += "=" * 60 + "\n"
    return formatted


def customer_profile_analyzer(customer_id: str,
                               investigation_id: str) -> Dict[str, Any]:
    """
    Analyze customer profile for risk factors.

    WHY this agent exists:
    Transaction patterns alone aren't enough.
    A $9,500 deposit means different things for:
    - New account with unknown occupation = HIGH risk
    - 5 year old account, business owner   = LOW risk

    Args:
        customer_id: Customer being investigated
        investigation_id: Links to transaction analysis

    Returns:
        Dictionary with customer_risk_level, risk_factors, reasoning
    """

    logger.info(f"👤 Analyzing customer profile: {customer_id}")

    try:
        # Step 1: Get customer profile
        profile = get_customer_profile(customer_id)
        logger.info(f"   Account age: {profile['account_age_months']} months")
        logger.info(f"   Previous flags: {profile['previous_flags']}")
        logger.info(f"   Is PEP: {profile['is_pep']}")

        # Step 2: Format for Claude
        formatted_profile = format_profile_for_claude(profile)

        # Step 3: Build prompt
        user_prompt = f"""
Please analyze this customer profile and assess their AML risk level.

{formatted_profile}

Consider all risk factors and return your assessment as JSON.
Pay special attention to:
- New accounts (< 6 months) are higher risk
- Previous flags significantly increase risk
- PEP (Politically Exposed Person) status increases risk
- Unknown occupation increases risk
"""

        # Step 4: Call Claude
        logger.info("🤖 Calling Claude for customer risk assessment...")
        analysis = call_claude_with_json_response(
            prompt=user_prompt,
            system_prompt=CUSTOMER_PROFILE_SYSTEM_PROMPT,
            max_tokens=1024
        )

        # Add raw profile to analysis for reference
        analysis['raw_profile'] = profile

        logger.info(f"✅ Customer analysis complete!")
        logger.info(f"   Customer Risk: {analysis.get('customer_risk_level')}")
        logger.info(f"   Risk Factors: {analysis.get('risk_factors')}")

        # Step 5: Log to DynamoDB
        log_to_dynamodb(
            investigation_id=investigation_id,
            agent_name="customer_profile_analyzer",
            agent_action="analyzed_customer_profile",
            input_data={
                'customer_id': customer_id,
                'account_age_months': profile['account_age_months'],
                'previous_flags': profile['previous_flags']
            },
            output_data=analysis,
            status="SUCCESS"
        )

        return analysis

    except Exception as e:
        logger.error(f"❌ Error in customer_profile_analyzer: {str(e)}")

        log_to_dynamodb(
            investigation_id=investigation_id,
            agent_name="customer_profile_analyzer",
            agent_action="analyzed_customer_profile",
            input_data={'customer_id': customer_id},
            output_data={},
            status="FAILURE",
            error_message=str(e)
        )

        return {
            "customer_risk_level": "MEDIUM",
            "risk_factors": ["analysis_failed"],
            "confidence": 0.0,
            "reasoning": f"Analysis failed: {str(e)}"
        }


# TEST
if __name__ == "__main__":
    print("🧪 Testing Customer Profile Analyzer...")
    print("")

    # Test with different customer IDs
    test_customers = [
        "CUST_NEW_001",    # Will generate new account
        "CUST_OLD_999",    # Will generate established account
        "CUST_FLAG_123",   # Will generate flagged account
    ]

    for customer_id in test_customers:
        print(f"Testing: {customer_id}")
        print("-" * 50)

        result = customer_profile_analyzer(
            customer_id=customer_id,
            investigation_id=f"TEST_PROFILE_{customer_id}"
        )

        print(f"   Customer Risk:  {result.get('customer_risk_level')}")
        print(f"   Risk Factors:   {result.get('risk_factors')}")
        print(f"   Confidence:     {result.get('confidence')}")
        print(f"   Reasoning:      {result.get('reasoning')[:80]}...")
        print("")

    print("✅ Customer Profile Analyzer test complete!")