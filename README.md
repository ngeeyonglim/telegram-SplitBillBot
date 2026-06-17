# SplitBillBot 🧾🤖

A Telegram Bot that splits bills using Google Gemini 1.5 Pro. Upload a receipt, describe who had what, and let the bot do the math!

## Features
- **Multimodal AI**: Uses Gemini 1.5 Pro to read receipts and understand natural language instructions.
- **Natural Language Mapping**: "Alice had the pizza, I had the wings" - the bot understands exactly who owes what.
- **Interactive Participation**: Group members can click "🙋 Join Split" to be included in shared items.
- **Proportional Splitting**: Automatically distributes tax, service charges, and tips proportionally across participants.
- **Secure Finalization**: Only the person who uploaded the receipt (the Payer) can finalize the split.
- **In-Memory Sessions**: Sessions automatically expire after 5 hours to keep things clean.

## Setup

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd telegram-SplitBillBot
   ```

2. **Create a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   GEMINI_API_KEY=your_gemini_api_key
   ```

4. **Run the Bot**:
   ```bash
   python main.py
   ```

## Usage
1. Add the bot to your Telegram group.
2. (Optional) Disable **Privacy Mode** via [@BotFather](https://t.me/BotFather) so the bot can see photos without being tagged.
3. Upload a receipt photo with a caption like:
   > @Alice had the salad, @Bob and I shared the pizza.
4. Participants who shared the "unassigned" items (items not mentioned) can click **Join Split**.
5. The Payer clicks **Finalize** to get the summary.

## Domain Language
- **Payer**: The user who uploads the receipt.
- **Participant**: Anyone who is mentioned or joins the split.
- **Unassigned Item**: Items Gemini couldn't map to a specific person.
- **Final Split**: The final calculation of who owes the Payer.

## Project Structure
- `src/bot/`: Telegram bot handlers (`aiogram`).
- `src/logic/`: Gemini integration and session math.
- `docs/`: ADRs, PRD, and Implementation Issues.
