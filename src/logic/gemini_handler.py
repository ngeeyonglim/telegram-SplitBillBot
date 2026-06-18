import google.generativeai as genai
import json
import os
import asyncio
import logging
import time
import io
from PIL import Image
from typing import List, Dict, Any

class GeminiHandler:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Using a more robust configuration for JSON output
        self.model = genai.GenerativeModel(
            model_name='gemini-3.5-flash',
            generation_config={
                "response_mime_type": "application/json"
            }
        )

    async def process_receipt(self, image_path: str, user_description: str, mentions: List[str]) -> Dict[str, Any]:
        start_time = time.time()
        logging.info(f"Starting receipt processing for {image_path}")
        
        # Prepare image: resize and convert to bytes for faster transmission
        image = Image.open(image_path)
        # Convert to RGB if necessary (to avoid issues with RGBA/indexed JPEGs)
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        max_dim = 1600
        if max(image.size) > max_dim:
            scale = max_dim / max(image.size)
            new_size = (int(image.size[0] * scale), int(image.size[1] * scale))
            image = image.resize(new_size, Image.LANCZOS)
            logging.info(f"Resized image to {new_size}")

        # Save to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=85)
        img_bytes = img_byte_arr.getvalue()
        
        logging.info(f"Image prepared. Size: {len(img_bytes) / 1024:.2f} KB")

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
            api_start = time.time()
            logging.info("Sending request to Gemini API (3.5-flash)...")
            
            # Use raw bytes and native request_options timeout for better reliability
            response = await self.model.generate_content_async(
                [
                    prompt,
                    {'mime_type': 'image/jpeg', 'data': img_bytes}
                ],
                request_options={'timeout': 300} # 5 minute API-side timeout
            )
            
            api_duration = time.time() - api_start
            logging.info(f"Gemini API responded in {api_duration:.2f}s")
            
            data = json.loads(response.text)
            # Basic validation
            if "total" not in data or "items" not in data:
                raise ValueError("Incomplete data received from Gemini.")
            
            total_duration = time.time() - start_time
            logging.info(f"Total processing time: {total_duration:.2f}s")
            return data
        except Exception as e:
            api_duration = time.time() - api_start
            logging.error(f"Gemini API error/timeout after {api_duration:.2f}s: {e}")
            if "deadline exceeded" in str(e).lower() or "timeout" in str(e).lower():
                raise Exception("The AI took too long to process the image. This usually happens with very complex receipts or high server load. Please try again or use a clearer photo.")
            raise
