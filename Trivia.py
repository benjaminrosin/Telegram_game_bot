import telebot
import requests
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import bot_secrets
import html


bot = telebot.TeleBot(bot_secrets.TOKEN)

# Store active trivia sessions: { user_id: { "question": "...", "correct": "..." } }
trivia_sessions = {}
trivia_cache = []  # Store pre-fetched questions


def fetch_trivia_questions():
    """Fetch 50 trivia questions from API and store them in trivia_cache."""
    global trivia_cache
    url = "https://opentdb.com/api.php?amount=50&type=multiple"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if "results" in data and data["results"]:
            trivia_cache = [
                {
                    "question": html.unescape(q["question"]),
                    "correct": html.unescape(q["correct_answer"]),
                    "options": [html.unescape(opt) for opt in q["incorrect_answers"]] + [
                            html.unescape(q["correct_answer"])],
                    "category": html.unescape(q["category"]),
                    "difficulty": q["difficulty"].capitalize()
                }
                for q in data["results"]
            ]
            random.shuffle(trivia_cache)  # Shuffle to mix up questions
            return

        else:
            print(f"API Error {response.status_code}: {response.text}")


def get_trivia_question():
    """Get a trivia question from the local cache, or fetch new ones if empty."""
    if not trivia_cache:  # If empty, fetch more
        fetch_trivia_questions()

    if trivia_cache:
        return trivia_cache.pop()  # Pop one question from the cache
    return None  # Return None if unable to fetch questions


def create_keyboard(options):
    """Create inline buttons for the answer choices."""
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [InlineKeyboardButton(opt, callback_data=opt) for opt in options]
    keyboard.add(*buttons)
    return keyboard


#@bot.message_handler(commands=["trivia"])
def start(message):
    """Start a trivia game by sending a question."""
    user_id = message.chat.id
    trivia_data = get_trivia_question()

    if trivia_data is None:
        bot.send_message(user_id, "⚠️ Sorry, I couldn't fetch a trivia question. Try again later!")
        return

    question, correct, options, category, difficulty = (
        trivia_data["question"], trivia_data["correct"], trivia_data["options"], trivia_data["category"],
        trivia_data["difficulty"]
    )

    trivia_sessions[user_id] = {
        "question": question,
        "correct": correct,
        "category": category,
        "difficulty": difficulty
    }

    text = f"🎯 *Category:* {category}\n💪 *Difficulty:* {difficulty}\n\n❓ *{question}*"
    bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=create_keyboard(options))


#@bot.callback_query_handler(func=lambda call: call.data)
def callback_query(call):
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

def reset_state():
    #del games[chat_id]
    # delete from cache
    print("skipping trivia reset")


#(bot.polling())
