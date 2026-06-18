import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from src.logic.gemini_handler import GeminiHandler
from src.logic.session_manager import SessionManager

@pytest.mark.asyncio
async def test_singlish_and_local_assignment():
    """
    Test if the logic handles complex assignments including Singlish and local names.
    Note: This tests the logic flow. In a real scenario, Gemini handles the parsing.
    Here we simulate Gemini's JSON output for a Singaporean context.
    """
    sm = SessionManager()
    
    # Scenario: "Me and @AhHock shared the Hor Fun. @Meiling dabao-ed the Laksa. 
    # I also had the Teh C. The rest shared the Satay."
    bill_data = {
        "items": [
            {"name": "Hor Fun", "price": 12.00, "assigned_to": ["sender", "@AhHock"]},
            {"name": "Laksa", "price": 7.50, "assigned_to": ["@Meiling"]},
            {"name": "Teh C", "price": 2.20, "assigned_to": ["sender"]}
        ],
        "unassigned_items": [
            {"name": "Satay", "price": 15.00}
        ],
        "subtotal": 36.70,
        "tax": 3.30, # GST/Service Charge
        "service_charge": 0.00,
        "total": 40.00
    }
    
    # Setup session
    session_id = sm.create_session(
        chat_id=123, 
        message_id=456, 
        bill_data=bill_data, 
        payer_id=1, 
        payer_username="Yong",
        mentions=["@AhHock", "@Meiling", "@BotName"]
    )
    
    # Simulate @AhHock and @Meiling joining (though mentions already added them)
    sm.add_participant(session_id, 2, "AhHock")
    sm.add_participant(session_id, 3, "Meiling")
    
    result = sm.finalize_split(session_id)
    
    # Checks
    summary = {u['user']: u['total'] for u in result['summary']}
    
    # Payer (Yong) should have Hor Fun/2 + Teh C + Satay/3 + proportional tax
    # @AhHock should have Hor Fun/2 + Satay/3 + proportional tax
    # @Meiling should have Laksa + Satay/3 + proportional tax
    
    assert "@Yong" in summary
    assert "@AhHock" in summary
    assert "@Meiling" in summary
    
    # Total check
    assert abs(sum(summary.values()) - 40.00) < 0.01
    
    # Proportion check: Meiling should pay more than Ah Hock because Laksa (7.5) > Teh C (2.2)
    assert summary["@Meiling"] > summary["@AhHock"]

@pytest.mark.asyncio
async def test_virtual_user_singapore_names():
    """Test virtual identities like 'Uncle' or 'Auntie'"""
    sm = SessionManager()
    
    bill_data = {
        "items": [
            {"name": "Kopi O", "price": 1.50, "assigned_to": ["Uncle"]},
            {"name": "Soft Boiled Eggs", "price": 2.00, "assigned_to": ["sender", "Uncle"]}
        ],
        "unassigned_items": [],
        "total": 3.50
    }
    
    session_id = sm.create_session(1, 1, bill_data, 1, "Nephew")
    result = sm.finalize_split(session_id)
    
    summary = {u['user']: u['total'] for u in result['summary']}
    assert "Uncle" in summary
    assert "@Nephew" in summary
    assert summary["Uncle"] == 2.50 # 1.50 + 1.00
    assert summary["@Nephew"] == 1.00

if __name__ == "__main__":
    # If run directly, simple print-based test
    import asyncio
    asyncio.run(test_singlish_and_local_assignment())
    asyncio.run(test_virtual_user_singapore_names())
    print("Local tests passed!")
