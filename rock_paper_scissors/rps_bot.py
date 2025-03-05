import telebot
import bot_secrets
import logging
from rock_paper_scissors.rps_game import rps_game

logging.basicConfig(
    format="[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

bot = telebot.TeleBot(bot_secrets.TOKEN)


def start(message: telebot.types.Message):
    send_rps_buttons(message.chat.id)


def send_rps_buttons(chat_id):
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        telebot.types.InlineKeyboardButton("🧱", callback_data="🧱"),
        telebot.types.InlineKeyboardButton("📄", callback_data="📄"),
        telebot.types.InlineKeyboardButton("✂️", callback_data="✂️"),
    )
    bot.send_message(chat_id=chat_id, text="Choose your move:", reply_markup=markup)


def callback_query(call: telebot.types.CallbackQuery):
    user_choice = call.data
    bot_choice = rps_game(user_choice)
    response = f"You chose: {user_choice}\nBot chose: {bot_choice}"

    # Edit the previous message instead of sending a new one
    bot.edit_message_text(
        chat_id=call.message.chat.id, message_id=call.message.message_id, text=response
    )

    # Send new buttons for replaying
    send_rps_buttons(call.message.chat.id)


def reset_state():
    pass


def about():
    return ('🪨✂️📜 * Rock Paper Scissors * 📜✂️🪨\n'
            ' - duel game\n'
            'the ultimate battle of chance! Choose rock (🪨) to crush scissors, '
            'scissors (✂️) to cut paper, or paper (📜) to cover rock. '
            'Think fast, play smart, and outwit your opponent in this timeless showdown! 🎮🔥')
