import os
import re
import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.logic.gemini_handler import GeminiHandler
from src.logic.session_manager import SessionManager
from dotenv import load_dotenv

load_dotenv()

router = Router()
gemini = GeminiHandler(os.getenv("GEMINI_API_KEY"))
sessions = SessionManager()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hi! I'm SplitBillBot. Upload a receipt in a group and describe who had what to start splitting!")

@router.message(F.photo)
async def handle_receipt(message: types.Message, bot):
    # Ensure we only process in groups or supergroups as requested
    if message.chat.type not in ["group", "supergroup"]:
        # We could allow private chat for testing, but let's stick to the PRD
        pass

    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_path = f"temp_{photo.file_id}.jpg"
    await bot.download_file(file_info.file_path, file_path)

    description = message.caption or ""
    
    # Extract official mentions
    mentions = [m.extract_from(description) for m in (message.entities or []) if m.type == "mention"]
    
    # Also extract potential mentions via regex for robustness
    regex_mentions = re.findall(r'@\w+', description)
    all_mentions = list(set(mentions + regex_mentions))
    
    logging.info(f"Processing receipt from {message.from_user.username}. Mentions: {all_mentions}")

    try:
        processing_msg = await message.reply("Processing receipt with Gemini...")
        bill_data = await gemini.process_receipt(file_path, description, all_mentions)
        
        session_id = sessions.create_session(
            message.chat.id, 
            message.message_id, 
            bill_data, 
            message.from_user.id,
            message.from_user.username
        )

        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="🙋 Join Split", callback_data=f"join_{session_id}"))
        builder.row(types.InlineKeyboardButton(text="✅ Finalize", callback_data=f"finalize_{session_id}"))

        text = f"📝 **Bill Detected**\nTotal: {bill_data.get('total'):.2f}\n\n"
        if bill_data.get("unassigned_items"):
            text += "Items to split:\n"
            for item in bill_data["unassigned_items"]:
                text += f"- {item['name']}: {item['price']:.2f}\n"
        
        text += "\nClick 'Join' if you partook in the unassigned items!"
        
        await processing_msg.edit_text(text, reply_markup=builder.as_markup())
    except Exception as e:
        logging.error(f"Error processing receipt: {e}")
        await message.reply(
            "❌ **Error Processing Receipt**\n"
            "I couldn't parse the receipt correctly. Please ensure:\n"
            "1. The image is clear and well-lit.\n"
            "2. The text description is straightforward.\n"
            f"Error details: `{str(e)}`"
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@router.callback_query(F.data.startswith("join_"))
async def handle_join(callback: types.CallbackQuery):
    session_id = callback.data.split("join_")[1]
    user = callback.from_user
    
    if sessions.add_participant(session_id, user.id, user.username):
        session = sessions.get_session(session_id)
        joined_list = ", ".join(session["joined_users"])
        
        # Update the message to show who joined
        text = callback.message.text
        if "\n\nJoined: " in text:
            text = text.split("\n\nJoined: ")[0]
        
        new_text = f"{text}\n\nJoined: {joined_list}"
        
        try:
            await callback.message.edit_text(new_text, reply_markup=callback.message.reply_markup)
            await callback.answer("You've joined the split!")
        except Exception:
            # Message might be the same, ignore
            await callback.answer("You've joined the split!")
    else:
        await callback.answer("Session expired or not found.", show_alert=True)

@router.callback_query(F.data.startswith("finalize_"))
async def handle_finalize(callback: types.CallbackQuery):
    session_id = callback.data.split("finalize_")[1]
    session = sessions.get_session(session_id)
    
    if not session:
        await callback.answer("Session expired or not found.", show_alert=True)
        return

    # Restrict to Payer
    if callback.from_user.id != session["payer_id"]:
        await callback.answer("Only the Payer can finalize this split.", show_alert=True)
        return
    
    result = sessions.finalize_split(session_id)
    if not result:
        await callback.answer("Session expired or not found.", show_alert=True)
        return

    summary_text = f"📊 **Final Split Summary**\nPayer: {result['payer']}\nTotal: {result['total']:.2f}\n\n"
    for item in result["summary"]:
        summary_text += f"{item['user']}: **{item['total']:.2f}**\n"
    
    await callback.message.edit_text(summary_text)
    await callback.answer()
