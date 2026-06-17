from cachetools import TTLCache
from typing import Dict, Any, List
import time

class SessionManager:
    def __init__(self, ttl_seconds: int = 5 * 3600):
        # 5 hours TTL
        self.cache = TTLCache(maxsize=1000, ttl=ttl_seconds)

    def create_session(self, chat_id: int, message_id: int, bill_data: Dict[str, Any], payer_id: int, payer_username: str):
        session_id = f"{chat_id}_{message_id}"
        self.cache[session_id] = {
            "bill_data": bill_data,
            "payer_id": payer_id,
            "payer_username": payer_username,
            "participants": {f"@{payer_username}" if payer_username else f"user_{payer_id}": []},
            "joined_users": set(),
            "created_at": time.time()
        }
        return session_id

    def get_session(self, session_id: str):
        return self.cache.get(session_id)

    def add_participant(self, session_id: str, user_id: int, username: str):
        session = self.cache.get(session_id)
        if session:
            user_key = f"@{username}" if username else f"user_{user_id}"
            session["joined_users"].add(user_key)
            return True
        return False

    def finalize_split(self, session_id: str) -> Dict[str, Any]:
        session = self.cache.get(session_id)
        if not session:
            return None
        
        bill_data = session["bill_data"]
        joined_users = list(session["joined_users"])
        payer_key = f"@{session['payer_username']}" if session['payer_username'] else f"user_{session['payer_id']}"
        
        # If no one joined and no one was mentioned, everyone who joined gets unassigned items
        # Logic for proportional split
        items = bill_data.get("items", [])
        unassigned = bill_data.get("unassigned_items", [])
        
        results = {}
        
        # Process assigned items
        for item in items:
            assignees = item.get("assigned_to", [])
            if not assignees:
                # If unassigned, split among all joined users + payer
                assignees = joined_users + [payer_key] if payer_key not in joined_users else joined_users
            
            # Replace 'sender' with actual payer
            assignees = [payer_key if a == "sender" else a for a in assignees]
            
            price_per_person = item["price"] / len(assignees)
            for user in assignees:
                results[user] = results.get(user, 0) + price_per_person

        # Process specifically unassigned items
        all_participants = list(set(joined_users + [payer_key]))
        for item in unassigned:
            price_per_person = item["price"] / len(all_participants)
            for user in all_participants:
                results[user] = results.get(user, 0) + price_per_person

        # Calculate proportional tax and service charge
        subtotal = bill_data.get("subtotal", sum(i["price"] for i in items) + sum(i["price"] for i in unassigned))
        if subtotal == 0: subtotal = 1 # Avoid division by zero
        
        total_extras = bill_data.get("tax", 0) + bill_data.get("service_charge", 0)
        
        final_summary = []
        for user, amount in results.items():
            proportion = amount / subtotal
            user_total = amount + (proportion * total_extras)
            final_summary.append({
                "user": user,
                "base": amount,
                "total": user_total
            })
            
        return {
            "summary": final_summary,
            "total": bill_data.get("total", subtotal + total_extras),
            "payer": payer_key
        }
