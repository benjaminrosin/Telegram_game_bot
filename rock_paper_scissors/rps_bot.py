import telebot
import bot_secrets
import logging
from rps_game import rps_game

logging.basicConfig(
    format="[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

bot = telebot.TeleBot(bot_secrets.TOKEN)


@bot.message_handler(commands=["start"])
def send_welcome(message: telebot.types.Message):
    logger.info(f"- starting from {message.chat.username}: {message.json}")
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("▶️ Play", callback_data="play"),
        telebot.types.InlineKeyboardButton("❌ Exit", callback_data="exit"),
    )
    bot.reply_to(
        message,
        "Welcome to Rock, Paper, Scissors!\nSelect an option:",
        reply_markup=markup,
    )


@bot.callback_query_handler(func=lambda call: call.data == "play")
def show_game_menu(call):
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        telebot.types.InlineKeyboardButton("🧱", callback_data="🧱"),
        telebot.types.InlineKeyboardButton("📄", callback_data="📄"),
        telebot.types.InlineKeyboardButton("✂️", callback_data="✂️"),
        telebot.types.InlineKeyboardButton("❌ Exit", callback_data="exit"),
    )
    bot.send_message(
        chat_id=call.message.chat.id,
        text="Choose your move:",
        reply_markup=markup,
    )


@bot.callback_query_handler(func=lambda call: call.data == "exit")
def exit_game(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Thanks for playing! 👋",
    )


@bot.callback_query_handler(func=lambda call: call.data in ["🧱", "📄", "✂️"])
def play_rps(call: telebot.types.CallbackQuery):
    user_choice = call.data
    bot_choice = rps_game(user_choice)
    response = f"You chose: {user_choice}\nBot chose: {bot_choice}"
    bot.send_message(chat_id=call.message.chat.id, text=response)
    show_game_menu(call)


logger.info("* starting bot")
bot.infinity_polling()
logger.info("* goodbye!")
