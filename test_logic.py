from src.logic.session_manager import SessionManager

def test_proportional_split():
    sm = SessionManager()
    bill_data = {
        "items": [
            {"name": "Pizza", "price": 20.0, "assigned_to": ["@Alice", "sender"]},
            {"name": "Cola", "price": 5.0, "assigned_to": ["@Alice"]}
        ],
        "unassigned_items": [
            {"name": "Wings", "price": 10.0}
        ],
        "subtotal": 35.0,
        "tax": 3.5,
        "service_charge": 5.0,
        "total": 43.5
    }
    
    session_id = sm.create_session(1, 1, bill_data, 123, "Bob")
    sm.add_participant(session_id, 456, "Alice")
    sm.add_participant(session_id, 789, "Charlie")
    
    result = sm.finalize_split(session_id)
    
    print(f"Payer: {result['payer']}")
    sum_totals = 0
    for user in result["summary"]:
        print(f"{user['user']}: Base {user['base']:.2f}, Total {user['total']:.2f}")
        sum_totals += user['total']
    
    print(f"Calculated Total: {sum_totals:.2f}")
    print(f"Receipt Total: {result['total']:.2f}")
    assert abs(sum_totals - result['total']) < 0.01

if __name__ == "__main__":
    test_proportional_split()
