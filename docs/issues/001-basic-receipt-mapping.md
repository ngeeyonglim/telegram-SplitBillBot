# Issue 1: Basic Receipt Mapping

## What to build
Implement the end-to-end flow for uploading a receipt photo with a natural language caption. The bot must use Gemini 1.5 Pro to:
1. Perform OCR and extract line items/prices.
2. Identify the Payer (sender) and any @mentioned Participants.
3. Map items to Participants based on instructions like "@Alice had the pizza" or "I had the wings".
4. Handle the "sender" mapping correctly in the data structure.

## Acceptance criteria
- [x] Bot responds to photo uploads in groups.
- [x] Gemini successfully extracts items and prices.
- [x] Participants mentioned in the caption are correctly assigned their items.
- [x] Payer is correctly identified and assigned their items (via "me", "I", etc.).

## Blocked by
None - can start immediately
