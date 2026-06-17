import logging
from typing import Dict, Any, TypedDict, List
from datetime import datetime

from langgraph.graph import StateGraph, END

from src.agents.transaction_analyzer import transaction_analyzer
from src.agents.customer_profile_analyzer import customer_profile_analyzer
from src.agents.risk_calculator import risk_calculator
from src.utils.dynamodb_logger import log_to_dynamodb

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================
# STATE - Shared data between all agents
# =============================================

class InvestigationState(TypedDict):
    """
    Shared state passed between all agents.
    
    WHY TypedDict?
    LangGraph needs to know what data flows
    between agents. TypedDict defines the
    structure clearly.
    
    Think of it like a folder that gets passed
    from one agent to the next, each adding
    their findings to it.
    """
    # Input data
    investigation_id: str
    customer_id: str
    customer_name: str
    transactions: List[Dict[str, Any]]

    # Agent 1 results
    transaction_analysis: Dict[str, Any]

    # Agent 2 results
    customer_analysis: Dict[str, Any]

    # Agent 3 results
    final_decision: Dict[str, Any]

    # Metadata
    started_at: str
    completed_at: str
    status: str


# =============================================
# AGENT NODES - Each agent is a node in graph
# =============================================

def run_transaction_analyzer(state: InvestigationState) -> InvestigationState:
    """
    Node 1: Run Transaction Analyzer Agent
    
    WHY first?
    Transaction patterns are the PRIMARY signal.
    We analyze these first before looking at
    customer profile.
    """
    logger.info(f"📊 Node 1: Running Transaction Analyzer...")

    result = transaction_analyzer(
        transactions=state["transactions"],
        investigation_id=state["investigation_id"],
        customer_id=state["customer_id"],
        customer_name=state["customer_name"]
    )

    # Add result to shared state
    state["transaction_analysis"] = result
    logger.info(f"✅ Node 1 complete: {result.get('risk_score')} risk")

    return state


def run_customer_profile_analyzer(state: InvestigationState) -> InvestigationState:
    """
    Node 2: Run Customer Profile Analyzer
    
    WHY second?
    We need transaction results first to provide
    context for customer analysis.
    Customer profile adds CONTEXT to transaction patterns.
    """
    logger.info(f"👤 Node 2: Running Customer Profile Analyzer...")

    result = customer_profile_analyzer(
        customer_id=state["customer_id"],
        investigation_id=state["investigation_id"]
    )

    # Add result to shared state
    state["customer_analysis"] = result
    logger.info(f"✅ Node 2 complete: {result.get('customer_risk_level')} risk")

    return state


def run_risk_calculator(state: InvestigationState) -> InvestigationState:
    """
    Node 3: Run Risk Calculator
    
    WHY last?
    Needs BOTH transaction AND customer results
    to make final decision.
    This is the final step before returning
    results to analyst.
    """
    logger.info(f"🧮 Node 3: Running Risk Calculator...")

    result = risk_calculator(
        transaction_analysis=state["transaction_analysis"],
        customer_analysis=state["customer_analysis"],
        investigation_id=state["investigation_id"],
        customer_id=state["customer_id"]
    )

    # Add result to shared state
    state["final_decision"] = result
    state["completed_at"] = datetime.now().isoformat()
    state["status"] = "COMPLETED"

    logger.info(f"✅ Node 3 complete: {result.get('recommended_action')}")

    return state


# =============================================
# BUILD THE GRAPH
# =============================================

def build_investigation_graph() -> StateGraph:
    """
    Build the LangGraph investigation pipeline.
    
    WHY StateGraph?
    StateGraph manages:
    - Order of agent execution
    - Data flow between agents
    - Error handling
    - State management
    
    Our graph is LINEAR (simple):
    Node1 → Node2 → Node3 → END
    
    In Phase 3 we'll add CONDITIONAL edges:
    Node1 → if HIGH risk → Node2 → Node3
    Node1 → if LOW risk → END (skip remaining)
    """
    # Create graph with our state
    graph = StateGraph(InvestigationState)

    # Add agent nodes
    graph.add_node("transaction_analyzer", run_transaction_analyzer)
    graph.add_node("customer_profile_analyzer", run_customer_profile_analyzer)
    graph.add_node("risk_calculator", run_risk_calculator)

    # Connect nodes in order
    graph.set_entry_point("transaction_analyzer")
    graph.add_edge("transaction_analyzer", "customer_profile_analyzer")
    graph.add_edge("customer_profile_analyzer", "risk_calculator")
    graph.add_edge("risk_calculator", END)

    # Compile the graph
    return graph.compile()


# =============================================
# MAIN INVESTIGATION FUNCTION
# =============================================

def run_investigation(customer_id: str,
                      customer_name: str,
                      transactions: List[Dict[str, Any]],
                      investigation_id: str = None) -> Dict[str, Any]:
    """
    Run complete AML investigation using all agents.
    
    This is the MAIN entry point for Phase 2.
    Called by Lambda handler when alert comes in.
    
    Args:
        customer_id: Customer being investigated
        customer_name: Customer name
        transactions: List of transactions to analyze
        investigation_id: Unique ID (auto-generated if not provided)
    
    Returns:
        Complete investigation report
    """

    # Generate investigation ID if not provided
    if not investigation_id:
        investigation_id = f"INV_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{customer_id}"

    logger.info(f"🚀 Starting AML Investigation")
    logger.info(f"   Investigation ID: {investigation_id}")
    logger.info(f"   Customer: {customer_id} ({customer_name})")
    logger.info(f"   Transactions: {len(transactions)}")
    logger.info("")

    # Log investigation start
    log_to_dynamodb(
        investigation_id=investigation_id,
        agent_name="orchestrator",
        agent_action="investigation_started",
        input_data={
            'customer_id': customer_id,
            'customer_name': customer_name,
            'transaction_count': len(transactions)
        },
        output_data={},
        status="STARTED"
    )

    try:
        # Build the graph
        graph = build_investigation_graph()

        # Set initial state
        initial_state: InvestigationState = {
            "investigation_id": investigation_id,
            "customer_id": customer_id,
            "customer_name": customer_name,
            "transactions": transactions,
            "transaction_analysis": {},
            "customer_analysis": {},
            "final_decision": {},
            "started_at": datetime.now().isoformat(),
            "completed_at": "",
            "status": "RUNNING"
        }

        # Run the graph!
        final_state = graph.invoke(initial_state)

        # Build complete report
        report = {
            "investigation_id": investigation_id,
            "customer_id": customer_id,
            "customer_name": customer_name,
            "transaction_count": len(transactions),
            "started_at": final_state["started_at"],
            "completed_at": final_state["completed_at"],
            "status": final_state["status"],
            "transaction_analysis": final_state["transaction_analysis"],
            "customer_analysis": final_state["customer_analysis"],
            "final_decision": final_state["final_decision"],
        }

        # Log completion
        log_to_dynamodb(
            investigation_id=investigation_id,
            agent_name="orchestrator",
            agent_action="investigation_completed",
            input_data={'customer_id': customer_id},
            output_data={
                'final_risk_level': final_state["final_decision"].get('final_risk_level'),
                'recommended_action': final_state["final_decision"].get('recommended_action')
            },
            status="COMPLETED"
        )

        logger.info("")
        logger.info("=" * 60)
        logger.info("🏁 INVESTIGATION COMPLETE!")
        logger.info(f"   Final Risk Level:   {final_state['final_decision'].get('final_risk_level')}")
        logger.info(f"   Recommended Action: {final_state['final_decision'].get('recommended_action')}")
        logger.info(f"   Summary: {final_state['final_decision'].get('summary')}")
        logger.info("=" * 60)

        return report

    except Exception as e:
        logger.error(f"❌ Investigation failed: {str(e)}")

        log_to_dynamodb(
            investigation_id=investigation_id,
            agent_name="orchestrator",
            agent_action="investigation_failed",
            input_data={'customer_id': customer_id},
            output_data={},
            status="FAILED",
            error_message=str(e)
        )

        return {
            "investigation_id": investigation_id,
            "status": "FAILED",
            "error": str(e)
        }


# TEST
if __name__ == "__main__":
    print("🧪 Testing Full Investigation Pipeline...")
    print("=" * 60)
    print("")

    # Test Case: Suspicious customer with structuring pattern
    test_transactions = [
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
    ]

    report = run_investigation(
        customer_id="CUST_SUSPECT_001",
        customer_name="John Doe",
        transactions=test_transactions,
        investigation_id="TEST_FULL_001"
    )

    print("")
    print("📋 INVESTIGATION REPORT:")
    print("-" * 60)
    print(f"Investigation ID:   {report.get('investigation_id')}")
    print(f"Customer:           {report.get('customer_name')}")
    print(f"Transactions:       {report.get('transaction_count')}")
    print(f"Status:             {report.get('status')}")
    print("")
    print("RESULTS:")
    print(f"  Transaction Risk: {report['transaction_analysis'].get('risk_score')}")
    print(f"  Patterns Found:   {report['transaction_analysis'].get('patterns_found')}")
    print(f"  Customer Risk:    {report['customer_analysis'].get('customer_risk_level')}")
    print(f"  Final Risk Level: {report['final_decision'].get('final_risk_level')}")
    print(f"  Action Required:  {report['final_decision'].get('recommended_action')}")
    print(f"  Summary:          {report['final_decision'].get('summary')}")
    print("")
    print("✅ Full pipeline test complete!")