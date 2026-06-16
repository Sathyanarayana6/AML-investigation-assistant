import json
import sys
import os
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.transaction_analyzer import transaction_analyzer


# =============================================
# TEST DATA - One example of each pattern
# =============================================

STRUCTURING_TRANSACTIONS = [
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

SMURFING_TRANSACTIONS = [
    {"date": "2026-01-01", "type": "TRANSFER", "amount": 3500,
     "description": "Wire transfer from Customer A (CUST_11111)",
     "destination": "ACCT_99999"},
    {"date": "2026-01-01", "type": "TRANSFER", "amount": 3200,
     "description": "Wire transfer from Customer B (CUST_22222)",
     "destination": "ACCT_99999"},
    {"date": "2026-01-01", "type": "TRANSFER", "amount": 4100,
     "description": "Wire transfer from Customer C (CUST_33333)",
     "destination": "ACCT_99999"},
    {"date": "2026-01-01", "type": "TRANSFER", "amount": 2900,
     "description": "Wire transfer from Customer D (CUST_44444)",
     "destination": "ACCT_99999"},
    {"date": "2026-01-01", "type": "TRANSFER", "amount": 3800,
     "description": "Wire transfer from Customer E (CUST_55555)",
     "destination": "ACCT_99999"},
]

LAYERING_TRANSACTIONS = [
    {"date": "2026-01-01", "type": "TRANSFER", "amount": 50000,
     "description": "Transfer to account", "destination": "ACCT_11111"},
    {"date": "2026-01-01", "type": "TRANSFER", "amount": 49500,
     "description": "Transfer to account", "destination": "ACCT_22222"},
    {"date": "2026-01-01", "type": "TRANSFER", "amount": 49000,
     "description": "Transfer to account", "destination": "ACCT_33333"},
    {"date": "2026-01-01", "type": "TRANSFER", "amount": 48500,
     "description": "Transfer to account", "destination": "ACCT_44444"},
]

RAPID_MOVEMENT_TRANSACTIONS = [
    {"date": "2026-01-01", "type": "DEPOSIT", "amount": 100000,
     "description": "Large cash deposit", "destination": "Main account"},
    {"date": "2026-01-01", "type": "WITHDRAWAL", "amount": 99500,
     "description": "Large cash withdrawal", "destination": "External account"},
]

CIRCULAR_TRANSACTIONS = [
    {"date": "2026-01-01", "type": "TRANSFER", "amount": 25000,
     "description": "Account transfer", "destination": "ACCT_BBB"},
    {"date": "2026-01-01", "type": "TRANSFER", "amount": 24900,
     "description": "Account transfer", "destination": "ACCT_CCC"},
    {"date": "2026-01-01", "type": "TRANSFER", "amount": 24800,
     "description": "Account transfer", "destination": "ACCT_AAA"},
    {"date": "2026-01-02", "type": "TRANSFER", "amount": 24700,
     "description": "Account transfer", "destination": "ACCT_BBB"},
    {"date": "2026-01-02", "type": "TRANSFER", "amount": 24600,
     "description": "Account transfer", "destination": "ACCT_CCC"},
    {"date": "2026-01-02", "type": "TRANSFER", "amount": 24500,
     "description": "Account transfer", "destination": "ACCT_AAA"},
]

LEGITIMATE_TRANSACTIONS = [
    {"date": "2026-01-01", "type": "DEPOSIT",    "amount": 3500,
     "description": "Monthly salary",   "destination": "Main account"},
    {"date": "2026-01-05", "type": "PAYMENT",    "amount": 1200,
     "description": "Rent payment",     "destination": "Landlord"},
    {"date": "2026-01-10", "type": "PAYMENT",    "amount": 150,
     "description": "Electric bill",    "destination": "Utility company"},
    {"date": "2026-01-15", "type": "WITHDRAWAL", "amount": 200,
     "description": "ATM withdrawal",   "destination": "ATM"},
    {"date": "2026-01-20", "type": "PAYMENT",    "amount": 80,
     "description": "Internet bill",    "destination": "ISP"},
]


# =============================================
# TESTS
# =============================================

class TestTransactionAnalyzer:

    def test_structuring_detection(self):
        """
        Test 1: Agent should detect STRUCTURING pattern
        WHY: 8 deposits all just under $10K is classic structuring
        """
        print("\n🧪 Test 1: Structuring Detection")

        result = transaction_analyzer(
            transactions=STRUCTURING_TRANSACTIONS,
            investigation_id="TEST_STRUCT_001",
            customer_id="CUST_TEST_001"
        )

        # Verify structure of response
        assert "patterns_found" in result, "Missing patterns_found"
        assert "risk_score" in result, "Missing risk_score"
        assert "confidence" in result, "Missing confidence"
        assert "reasoning" in result, "Missing reasoning"

        # Verify correct detection
        assert result["risk_score"] == "HIGH", \
            f"Expected HIGH risk, got {result['risk_score']}"
        assert "STRUCTURING" in result["patterns_found"], \
            f"Expected STRUCTURING in patterns, got {result['patterns_found']}"

        print(f"   ✅ Risk Score: {result['risk_score']}")
        print(f"   ✅ Patterns: {result['patterns_found']}")


    def test_smurfing_detection(self):
        """
        Test 2: Agent should detect SMURFING pattern
        WHY: 5 different people all sending to same account
        """
        print("\n🧪 Test 2: Smurfing Detection")

        result = transaction_analyzer(
            transactions=SMURFING_TRANSACTIONS,
            investigation_id="TEST_SMURF_001",
            customer_id="CUST_TEST_002"
        )

        assert result["risk_score"] == "HIGH", \
            f"Expected HIGH risk, got {result['risk_score']}"

        # Claude may detect SMURFING or STRUCTURING or both
        # Either way it should be HIGH risk
        suspicious_patterns = ["SMURFING", "STRUCTURING"]
        assert any(p in result["patterns_found"] for p in suspicious_patterns), \
            f"Expected suspicious pattern, got {result['patterns_found']}"

        print(f"   ✅ Risk Score: {result['risk_score']}")
        print(f"   ✅ Patterns: {result['patterns_found']}")

    def test_layering_detection(self):
        """
        Test 3: Agent should detect LAYERING pattern
        WHY: Money moving through 4 accounts in same day
        """
        print("\n🧪 Test 3: Layering Detection")

        result = transaction_analyzer(
            transactions=LAYERING_TRANSACTIONS,
            investigation_id="TEST_LAYER_001",
            customer_id="CUST_TEST_003"
        )

        assert result["risk_score"] == "HIGH", \
            f"Expected HIGH risk, got {result['risk_score']}"
        assert "LAYERING" in result["patterns_found"], \
            f"Expected LAYERING in patterns, got {result['patterns_found']}"

        print(f"   ✅ Risk Score: {result['risk_score']}")
        print(f"   ✅ Patterns: {result['patterns_found']}")


    def test_rapid_movement_detection(self):
        """
        Test 4: Agent should detect RAPID_MOVEMENT pattern
        WHY: $100K in then $99.5K out same day
        """
        print("\n🧪 Test 4: Rapid Movement Detection")

        result = transaction_analyzer(
            transactions=RAPID_MOVEMENT_TRANSACTIONS,
            investigation_id="TEST_RAPID_001",
            customer_id="CUST_TEST_004"
        )

        assert result["risk_score"] in ["HIGH", "MEDIUM"], \
            f"Expected HIGH or MEDIUM risk, got {result['risk_score']}"
        assert "RAPID_MOVEMENT" in result["patterns_found"], \
            f"Expected RAPID_MOVEMENT in patterns, got {result['patterns_found']}"

        print(f"   ✅ Risk Score: {result['risk_score']}")
        print(f"   ✅ Patterns: {result['patterns_found']}")


    def test_circular_transfers_detection(self):
        """
        Test 5: Agent should detect CIRCULAR_TRANSFERS pattern
        WHY: Money going A→B→C→A repeatedly with fees
        """
        print("\n🧪 Test 5: Circular Transfers Detection")

        result = transaction_analyzer(
            transactions=CIRCULAR_TRANSACTIONS,
            investigation_id="TEST_CIRCULAR_001",
            customer_id="CUST_TEST_005"
        )

        assert result["risk_score"] == "HIGH", \
            f"Expected HIGH risk, got {result['risk_score']}"
        assert "CIRCULAR_TRANSFERS" in result["patterns_found"], \
            f"Expected CIRCULAR_TRANSFERS in patterns, got {result['patterns_found']}"

        print(f"   ✅ Risk Score: {result['risk_score']}")
        print(f"   ✅ Patterns: {result['patterns_found']}")


    def test_legitimate_transactions(self):
        """
        Test 6: Agent should NOT flag legitimate transactions
        WHY: Normal salary/bills should be LOW risk
        """
        print("\n🧪 Test 6: Legitimate Transactions")

        result = transaction_analyzer(
            transactions=LEGITIMATE_TRANSACTIONS,
            investigation_id="TEST_LEGIT_001",
            customer_id="CUST_TEST_006"
        )

        assert result["risk_score"] == "LOW", \
            f"Expected LOW risk, got {result['risk_score']}"
        assert result["patterns_found"] == [], \
            f"Expected no patterns, got {result['patterns_found']}"

        print(f"   ✅ Risk Score: {result['risk_score']}")
        print(f"   ✅ Patterns: {result['patterns_found']} (correctly empty)")


    def test_output_format(self):
        """
        Test 7: Verify JSON output format is always correct
        WHY: Lambda and dashboard depend on consistent format
        """
        print("\n🧪 Test 7: Output Format Validation")

        result = transaction_analyzer(
            transactions=LEGITIMATE_TRANSACTIONS,
            investigation_id="TEST_FORMAT_001",
            customer_id="CUST_TEST_007"
        )

        # Check all required fields exist
        assert "patterns_found" in result
        assert "risk_score" in result
        assert "confidence" in result
        assert "reasoning" in result
        assert "recommended_action" in result

        # Check field types
        assert isinstance(result["patterns_found"], list)
        assert isinstance(result["risk_score"], str)
        assert isinstance(result["confidence"], float)
        assert isinstance(result["reasoning"], str)

        # Check valid values
        assert result["risk_score"] in ["LOW", "MEDIUM", "HIGH"]
        assert 0.0 <= result["confidence"] <= 1.0

        print(f"   ✅ All fields present and correct types")
        print(f"   ✅ Risk score is valid value")
        print(f"   ✅ Confidence is between 0 and 1")


    def test_empty_transactions(self):
        """
        Test 8: Agent should handle empty transaction list gracefully
        WHY: Edge case - what if no transactions are passed?
        """
        print("\n🧪 Test 8: Empty Transactions Edge Case")

        result = transaction_analyzer(
            transactions=[],
            investigation_id="TEST_EMPTY_001",
            customer_id="CUST_TEST_008"
        )

        assert result["risk_score"] == "LOW"
        assert result["patterns_found"] == []

        print(f"   ✅ Handled empty transactions gracefully")
        print(f"   ✅ Returned LOW risk (correct default)")