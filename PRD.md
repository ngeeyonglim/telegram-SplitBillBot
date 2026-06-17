# PRD: SplitBillBot

## Problem Statement
Splitting bills in group settings (restaurants, bars, etc.) is often a tedious manual process. Users have to manually transcribe items from a receipt, calculate individual shares, and then apply taxes and service charges proportionally. Current solutions often require all participants to download a specific app or manually enter data into a shared spreadsheet.

## Solution
A Telegram Bot that integrates directly into existing group chats. Users can simply upload a photo of a receipt and provide a natural language description of who had what. The bot uses Gemini 1.5 Pro to process the image and text, automatically mapping items to users and providing an interactive "Join" mechanism for shared or unassigned items, finally outputting a clear summary of who owes the payer.

## User Stories
1. As a group member, I want to upload a receipt photo to the group chat, so that I can start a split bill session without leaving Telegram.
2. As a payer, I want to mention users in the caption (e.g., "@Alice had the pizza"), so that the bot automatically assigns those items to them.
3. As a participant, I want to see which items are still "unassigned" after the initial scan, so that I know what else needs to be split.
4. As a participant, I want to click a "Join Split" button, so that I am included in the proportional distribution of shared items.
5. As a group member, I want the bot to automatically calculate my share including a fair portion of tax and service charges, so that the split is accurate.
6. As a group member, I want the bot to expire active sessions after 5 hours, so that the group chat doesn't get cluttered with stale requests.
7. As a payer, I want to click a "Finalize" button, so that I can get a final list of amounts owed to me by each person.
8. As a user, I want the bot to handle mentions like "me" or "I" and map them to the person who sent the photo.
9. As a user, I want the bot to recognize shared items (e.g., "shared the wings") and split them among all mentioned participants.
10. As a group admin, I want to be able to use the bot without it tracking every single conversation (Privacy Mode), only responding when a photo or command is sent.

## Implementation Decisions
- **Core Engine:** Python with `aiogram` for Telegram API and `google-generativeai` for Gemini 1.5 Pro.
- **Multimodal OCR/NLP:** A single prompt sent to Gemini 1.5 Pro containing both the image and the user's description to handle extraction and assignment in one pass.
- **Session Management:** In-memory storage using `cachetools.TTLCache` with a 5-hour Time-To-Live (TTL).
- **Proportional Logic:** All "bottom-line" charges (tax, tip, service charge) are distributed proportionally based on each person's base consumption.
- **Identity Mapping:** Uses Telegram handles (`@username`) or internal IDs as unique keys for participants.
- **Unassigned Items:** Items detected on the receipt but not mentioned in the text are pooled for people who click the "Join" button.

## Testing Decisions
- **Logic Validation:** Unit tests for the `SessionManager` to ensure proportional math and TTL expiration work as expected.
- **Integration Tests:** Mocking the Gemini API response to test how the bot handles various edge cases (no mentions, all mentions, partial matches).
- **Behavioral Focus:** Tests should verify that the final summary matches the sum of the receipt total, ensuring no money is "lost" or "created" in the calculation.

## Out of Scope
- **Payment Integration:** Direct payment processing (Venmo/Revolut links) is deferred to a future version.
- **Persistent History:** Long-term database storage for historical bills (bills are reset/lost on bot restart).
- **Multi-Receipt Splits:** Handling multiple receipts in a single session.
- **Web UI:** A dedicated web interface for manual item correction (handled entirely via Telegram buttons/text).

## Further Notes
- The bot assumes that the user who uploads the photo is the "Payer" unless specified otherwise.
- Gemini's "sender" mapping is critical for correctly identifying the uploader in the split list.
