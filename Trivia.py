import telebot
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import bot_secrets
import html
import json
import utils
import db_connect as db

bot = telebot.TeleBot(bot_secrets.TOKEN)

trivia_cache = []  # Store pre-fetched questions


def init_state():
    return {
            "question": '',
            "correct": '',
            "counter": 1,
            "wrong": 0,
        }


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


def start(state):
    """Start a trivia game by sending a question."""
    user_id = state["user_id_arr"][0]
    trivia_data = get_trivia_question()

    if trivia_data is None:
        bot.send_message(user_id, "⚠️ Sorry, I couldn't fetch a trivia question. Try again later!")
        utils.send_main_menu(user_id, bot)
        return

    state["question"] = trivia_data["question"]
    state["correct"] = trivia_data["correct_answer"]

    options = [state["correct"]] + trivia_data["incorrect_answers"]
    random.shuffle(options)

    text = (f"🎯 *Category:* {trivia_data["category"]}\n"
            f"💪 *Difficulty:* {trivia_data["difficulty"]}\n\n"
            f"❓ *{state["question"]}*")

    db.update_state_info(user_id, {"state": state})

    bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=create_keyboard(options))

#p---------------------------------------------------------------------------------------------------------------------------
# dont working
#---------------------------------------------------------------------------------------------------------------------------------------------------
def callback_query(call: telebot.types.CallbackQuery, state: dict):
    """Check the player's answer."""
    user_id = call.message.chat.id

    correct_answer = state["state"]["correct"]
    if call.data == correct_answer:
        bot.edit_message_text(f"✅ Correct! The answer is: {correct_answer}", user_id, call.message.message_id)
    else:
        bot.edit_message_text(f"❌ Wrong! The correct answer was: {correct_answer}", user_id, call.message.message_id)
        trivia_sessions[user_id]["wrong"] += 1

    if trivia_sessions[user_id]["counter"] == 5:
        bot.send_message(call.message.chat.id, f"out of {trivia_sessions[user_id]["counter"]} questions you "
                                               f"answered {trivia_sessions[user_id]["counter"] - trivia_sessions[user_id]["wrong"]} correctly.")
        del trivia_sessions[user_id]  # Remove session after answering
        utils.send_main_menu(call.message, bot)
        return

    start(call.message)


def reset_state():
    #del games[chat_id]
    # delete from cache
    print("skipping trivia reset")


def about():
    return ('🧠 * Trivia Challenge * 🧠\n'
            'Answer questions, and compete for the top spot! 🏆\n'
            "Ready to prove you're the ultimate trivia master? 🎯🎉")

