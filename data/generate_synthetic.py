import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Set seed for reproducible results
random.seed(42)


def generate_structuring_case(num_transactions: int = 15) -> List[Dict[str, Any]]:
    """
    Generate STRUCTURING pattern.
    
    WHY suspicious: Deposits just under $10K avoid mandatory 
    bank reporting threshold (CTR - Currency Transaction Report)
    """
    transactions = []
    customer_id = f"CUST_{random.randint(10000, 99999)}"
    base_date = datetime.now() - timedelta(days=30)

    for i in range(num_transactions):
        # Always just under $10,000 - that's the red flag!
        amount = round(random.uniform(8500, 9900), 2)
        tx_date = base_date + timedelta(days=i * random.randint(1, 3))

        transactions.append({
            'transaction_id': f"TXN_{random.randint(100000, 999999)}",
            'customer_id': customer_id,
            'date': tx_date.strftime('%Y-%m-%d'),
            'type': 'DEPOSIT',
            'amount': amount,
            'currency': 'USD',
            'description': 'Cash deposit',
            'destination': 'Main checking account',
            'aml_pattern': 'STRUCTURING',
            'risk_level': 'HIGH'
        })

    return transactions


def generate_smurfing_case(num_people: int = 5) -> List[Dict[str, Any]]:
    """
    Generate SMURFING pattern.
    
    WHY suspicious: Multiple different people all sending 
    money to the same destination account = coordinated scheme
    """
    transactions = []
    # Same destination for all - that's the red flag!
    destination_account = f"ACCT_{random.randint(10000, 99999)}"
    base_date = datetime.now() - timedelta(days=2)

    for i in range(num_people):
        # Each person sends just under threshold
        amount = round(random.uniform(2500, 4500), 2)
        tx_time = base_date + timedelta(hours=random.randint(0, 48))

        transactions.append({
            'transaction_id': f"TXN_{random.randint(100000, 999999)}",
            'customer_id': f"CUST_{random.randint(10000, 99999)}",  # Different customer each time!
            'date': tx_time.strftime('%Y-%m-%d'),
            'type': 'TRANSFER',
            'amount': amount,
            'currency': 'USD',
            'description': 'Wire transfer',
            'destination': destination_account,  # Same destination!
            'aml_pattern': 'SMURFING',
            'risk_level': 'HIGH'
        })

    return transactions


def generate_layering_case() -> List[Dict[str, Any]]:
    """
    Generate LAYERING pattern.
    
    WHY suspicious: Money moves A→B→C→D→External 
    all within 24 hours with no business reason
    """
    transactions = []
    base_time = datetime.now() - timedelta(days=1)
    accounts = [
        f"ACCT_{random.randint(10000, 99999)}" for _ in range(5)
    ]

    amount = round(random.uniform(25000, 75000), 2)

    for i in range(len(accounts) - 1):
        # Small fee deducted each hop - money shrinks slightly
        amount = round(amount * 0.99, 2)
        tx_time = base_time + timedelta(hours=i * 3)

        transactions.append({
            'transaction_id': f"TXN_{random.randint(100000, 999999)}",
            'customer_id': accounts[i],
            'date': tx_time.strftime('%Y-%m-%d'),
            'type': 'TRANSFER',
            'amount': amount,
            'currency': 'USD',
            'description': f'Transfer to account',
            'destination': accounts[i + 1],  # Each goes to next account
            'aml_pattern': 'LAYERING',
            'risk_level': 'HIGH'
        })

    return transactions


def generate_rapid_movement_case() -> List[Dict[str, Any]]:
    """
    Generate RAPID_MOVEMENT pattern.
    
    WHY suspicious: Large deposit immediately withdrawn
    = classic money mule behavior
    """
    base_time = datetime.now() - timedelta(days=3)
    large_amount = round(random.uniform(50000, 150000), 2)
    customer_id = f"CUST_{random.randint(10000, 99999)}"

    return [
        {
            'transaction_id': f"TXN_{random.randint(100000, 999999)}",
            'customer_id': customer_id,
            'date': base_time.strftime('%Y-%m-%d'),
            'type': 'DEPOSIT',
            'amount': large_amount,
            'currency': 'USD',
            'description': 'Large cash deposit',
            'destination': 'Main account',
            'aml_pattern': 'RAPID_MOVEMENT',
            'risk_level': 'HIGH'
        },
        {
            'transaction_id': f"TXN_{random.randint(100000, 999999)}",
            'customer_id': customer_id,
            # Withdrawn just 47 minutes later!
            'date': (base_time + timedelta(minutes=47)).strftime('%Y-%m-%d'),
            'type': 'WITHDRAWAL',
            'amount': round(large_amount * 0.995, 2),  # Almost full amount
            'currency': 'USD',
            'description': 'Large cash withdrawal',
            'destination': 'External account',
            'aml_pattern': 'RAPID_MOVEMENT',
            'risk_level': 'HIGH'
        }
    ]


def generate_circular_transfer_case() -> List[Dict[str, Any]]:
    """
    Generate CIRCULAR_TRANSFERS pattern.
    
    WHY suspicious: Money goes A→B→C→A repeatedly
    with fees = no legitimate purpose, just moving money in circles
    """
    transactions = []
    base_time = datetime.now() - timedelta(days=5)
    accounts = [
        f"ACCT_{random.randint(10000, 99999)}" for _ in range(3)
    ]
    amount = 25000.00

    # Repeat the circle 4 times
    for cycle in range(4):
        for i in range(len(accounts)):
            amount = round(amount - 100, 2)  # $100 fee each hop
            next_account = accounts[(i + 1) % len(accounts)]
            tx_time = base_time + timedelta(days=cycle, hours=i * 2)

            transactions.append({
                'transaction_id': f"TXN_{random.randint(100000, 999999)}",
                'customer_id': accounts[i],
                'date': tx_time.strftime('%Y-%m-%d'),
                'type': 'TRANSFER',
                'amount': amount,
                'currency': 'USD',
                'description': 'Account transfer',
                'destination': next_account,
                'aml_pattern': 'CIRCULAR_TRANSFERS',
                'risk_level': 'HIGH'
            })

    return transactions


def generate_legitimate_transactions(num_transactions: int = 50) -> List[Dict[str, Any]]:
    """
    Generate LEGITIMATE normal transactions.
    
    WHY: We need negative examples too!
    The agent must correctly identify SAFE transactions
    and not flag everything as suspicious.
    """
    transactions = []
    customer_id = f"CUST_{random.randint(10000, 99999)}"
    base_date = datetime.now() - timedelta(days=60)

    # Real-world transaction types
    transaction_types = [
        {'type': 'DEPOSIT',    'amount': 3500,  'desc': 'Monthly salary',      'dest': 'Main account'},
        {'type': 'PAYMENT',    'amount': 1200,  'desc': 'Rent payment',         'dest': 'Landlord'},
        {'type': 'PAYMENT',    'amount': 150,   'desc': 'Electric bill',        'dest': 'Utility company'},
        {'type': 'PAYMENT',    'amount': 80,    'desc': 'Internet bill',        'dest': 'ISP'},
        {'type': 'WITHDRAWAL', 'amount': 200,   'desc': 'ATM withdrawal',       'dest': 'ATM'},
        {'type': 'PAYMENT',    'amount': 500,   'desc': 'Grocery shopping',     'dest': 'Supermarket'},
        {'type': 'TRANSFER',   'amount': 300,   'desc': 'Savings transfer',     'dest': 'Savings account'},
        {'type': 'PAYMENT',    'amount': 50,    'desc': 'Phone bill',           'dest': 'Telecom'},
        {'type': 'DEPOSIT',    'amount': 500,   'desc': 'Freelance payment',    'dest': 'Main account'},
        {'type': 'PAYMENT',    'amount': 100,   'desc': 'Restaurant dinner',    'dest': 'Restaurant'},
    ]

    for i in range(num_transactions):
        tx_type = random.choice(transaction_types)
        tx_date = base_date + timedelta(days=random.randint(0, 60))
        # Small random variation in amount (looks natural)
        amount = round(tx_type['amount'] + random.uniform(-50, 50), 2)

        transactions.append({
            'transaction_id': f"TXN_{random.randint(100000, 999999)}",
            'customer_id': customer_id,
            'date': tx_date.strftime('%Y-%m-%d'),
            'type': tx_type['type'],
            'amount': max(amount, 10),  # Minimum $10
            'currency': 'USD',
            'description': tx_type['desc'],
            'destination': tx_type['dest'],
            'aml_pattern': 'LEGITIMATE',
            'risk_level': 'LOW'
        })

    return transactions


def create_full_dataset() -> Dict[str, Any]:
    """
    Create the complete test dataset with all patterns.
    
    WHY: We need enough data to properly test our agent.
    Mix of suspicious and legitimate transactions.
    """
    print("📊 Generating synthetic AML dataset...")
    print("")

    # Generate all pattern types
    structuring = []
    for i in range(5):  # 5 structuring cases
        structuring.extend(generate_structuring_case())
    print(f"   ✅ Structuring cases:         {len(structuring)} transactions")

    smurfing = []
    for i in range(5):  # 5 smurfing cases
        smurfing.extend(generate_smurfing_case())
    print(f"   ✅ Smurfing cases:            {len(smurfing)} transactions")

    layering = []
    for i in range(5):  # 5 layering cases
        layering.extend(generate_layering_case())
    print(f"   ✅ Layering cases:            {len(layering)} transactions")

    rapid_movement = []
    for i in range(5):  # 5 rapid movement cases
        rapid_movement.extend(generate_rapid_movement_case())
    print(f"   ✅ Rapid movement cases:      {len(rapid_movement)} transactions")

    circular = []
    for i in range(5):  # 5 circular transfer cases
        circular.extend(generate_circular_transfer_case())
    print(f"   ✅ Circular transfer cases:   {len(circular)} transactions")

    legitimate = generate_legitimate_transactions(50)
    print(f"   ✅ Legitimate transactions:   {len(legitimate)} transactions")

    total = len(structuring) + len(smurfing) + len(layering) + len(rapid_movement) + len(circular) + len(legitimate)
    print("")
    print(f"   📊 Total transactions: {total}")

    dataset = {
        'generated_at': datetime.now().isoformat(),
        'total_transactions': total,
        'summary': {
            'structuring_count': len(structuring),
            'smurfing_count': len(smurfing),
            'layering_count': len(layering),
            'rapid_movement_count': len(rapid_movement),
            'circular_transfers_count': len(circular),
            'legitimate_count': len(legitimate)
        },
        'data': {
            'structuring': structuring,
            'smurfing': smurfing,
            'layering': layering,
            'rapid_movement': rapid_movement,
            'circular_transfers': circular,
            'legitimate': legitimate
        }
    }

    return dataset


def save_dataset(dataset: Dict[str, Any], filename: str = 'data/sample_transactions.json'):
    """Save dataset to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(dataset, f, indent=2)
        print(f"   💾 Dataset saved to: {filename}")
        return True
    except Exception as e:
        print(f"   ❌ Failed to save: {str(e)}")
        return False


# Run when executed directly
if __name__ == "__main__":
    print("🚀 AML Synthetic Data Generator")
    print("=" * 50)
    print("")

    dataset = create_full_dataset()
    print("")
    save_dataset(dataset)

    print("")
    print("=" * 50)
    print("✅ Dataset generation complete!")
    print("")
    print("Pattern breakdown:")
    for pattern, count in dataset['summary'].items():
        print(f"   {pattern}: {count}")