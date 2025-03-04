import telebot
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import bot_secrets
import html
import json
import utils

bot = telebot.TeleBot(bot_secrets.TOKEN)

# Store active trivia sessions: { user_id: { "question": "...", "correct": "..." } }
trivia_sessions = {}
trivia_cache = []  # Store pre-fetched questions


def get_trivia_question() -> dict | None:
    """Get a trivia question from the local cache, or fetch new ones if empty."""
    global trivia_cache
    if not trivia_cache:  # If empty, fetch more
        with open("questions.json", encoding="utf-8") as db:
            raw_data = json.load(db)
            trivia_cache = [
                {
                    key: html.unescape(value) if isinstance(value, str) else value
                    for key, value in entry.items()
                }
                for entry in raw_data
            ]

    if trivia_cache:
        return random.choice(trivia_cache)
    return None  # Return None if unable to fetch questions


def create_keyboard(options: list) -> InlineKeyboardMarkup:
    """Create inline buttons for the answer choices."""
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [InlineKeyboardButton(opt, callback_data=opt) for opt in options]
    keyboard.add(*buttons)
    return keyboard


def start(message: telebot.types.Message):
    """Start a trivia game by sending a question."""
    user_id = message.chat.id
    trivia_data = get_trivia_question()

    if trivia_data is None:
        bot.send_message(user_id, "⚠️ Sorry, I couldn't fetch a trivia question. Try again later!")
        return

    question, correct, incorrect, category, difficulty = (
        trivia_data["question"], trivia_data["correct_answer"], trivia_data["incorrect_answers"], trivia_data["category"],
        trivia_data["difficulty"]
    )

    options = incorrect + [correct]
    random.shuffle(options)

    trivia_sessions[user_id] = {
        "question": question,
        "correct": correct,
        "category": category,
        "difficulty": difficulty
    }

    text = f"🎯 *Category:* {category}\n💪 *Difficulty:* {difficulty}\n\n❓ *{question}*"
    bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=create_keyboard(options))


def callback_query(call: telebot.types.CallbackQuery):
    """Check the player's answer."""
    user_id = call.message.chat.id
    if user_id not in trivia_sessions:
        bot.answer_callback_query(call.id, "Start a new game with /trivia")
        return

    correct_answer = trivia_sessions[user_id]["correct"]
    if call.data == correct_answer:
        bot.edit_message_text(f"✅ Correct! The answer is: {correct_answer}", user_id, call.message.message_id)
    else:
        bot.edit_message_text(f"❌ Wrong! The correct answer was: {correct_answer}", user_id, call.message.message_id)

    del trivia_sessions[user_id]  # Remove session after answering

    start(call.message)


def reset_state():
    #del games[chat_id]
    # delete from cache
    print("skipping trivia reset")


def about():
    return ('🧠 * Trivia Challenge * 🧠\n'
            'Answer questions, and compete for the top spot! 🏆\n'
            "Ready to prove you're the ultimate trivia master? 🎯🎉")

