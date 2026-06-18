import google.generativeai as genai
import json
import os
import asyncio
from PIL import Image
from typing import List, Dict, Any

class GeminiHandler:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Using a more robust configuration for JSON output
        self.model = genai.GenerativeModel(
            model_name='gemini-3.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )

    async def process_receipt(self, image_path: str, user_description: str, mentions: List[str]) -> Dict[str, Any]:
        image = Image.open(image_path)
        
        prompt = f"""
        Analyze the provided receipt image and the following user description: "{user_description}"
        
        Participants explicitly mentioned in the conversation: {", ".join(mentions) if mentions else "None"}
        
        Your goal is to extract the line items and prices from the receipt and map them to the participants based on the description.
        
        Instructions:
        1. Extract ALL line items and their corresponding prices.
        2. Identify the subtotal, tax, and any service charges/tips/gratuity listed.
        3. Mapping Rules:
           - "sender" refers to the person who sent the message (keywords: "me", "I", "my").
           - If an item is explicitly linked to a name or "me" (e.g., "Alice had the burger"), assign it to them.
           - If a name is mentioned without an "@" (e.g., "Bob had the pizza"), use that name exactly as a virtual identity.
           - Use the EXACT handles provided in the 'Participants mentioned' list (which start with @) where they match the description.
           - If an item is "shared" and specific names are mentioned, assign it to all of those names/handles.
           - If an item is "shared" without names, or not mentioned at all, mark it as "unassigned".
        
        Constraint: Return ONLY a JSON object. Do not include any markdown formatting or preamble.
        
        JSON Structure:
        {{
            "items": [
                {{"name": "Item Name", "price": 12.50, "assigned_to": ["@username", "sender"]}}
            ],
            "subtotal": 0.00,
            "tax": 0.00,
            "service_charge": 0.00,
            "total": 0.00,
            "unassigned_items": [
                {{"name": "Item Name", "price": 5.00}}
            ]
        }}
        """
        
        try:
            # Use generate_content_async and wrap in asyncio.wait_for for a 60s timeout
            response = await asyncio.wait_for(
                self.model.generate_content_async([prompt, image]),
                timeout=180.0
            )
            
            data = json.loads(response.text)
            # Basic validation
            if "total" not in data or "items" not in data:
                raise ValueError("Incomplete data received from Gemini.")
            return data
        except asyncio.TimeoutError:
            raise Exception("Gemini API timed out after 180 seconds. Please try again with a clearer image or shorter description.")
        except json.JSONDecodeError:
            # Fallback if Gemini includes markdown or other text despite instructions
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            return json.loads(text.strip())
