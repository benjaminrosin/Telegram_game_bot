import logging

import bot_secrets
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import TicTacToe

logging.basicConfig(
    format="[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

bot = telebot.TeleBot(bot_secrets.TOKEN)

games = [TicTacToe]
game = None

@bot.message_handler(commands=["start"])
def send_welcome(message: telebot.types.Message):
    logger.info(f"+ Start chat #{message.chat.id} from {message.chat.username}")
    bot.reply_to(message, "🤖 Welcome! 🤖")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Play a game", callback_data="Play"))
    keyboard.add(InlineKeyboardButton("Settings", callback_data="Settings"))
    keyboard.add(InlineKeyboardButton("LeaderBoards", callback_data="LeaderBoards"))
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=keyboard)
    

@bot.message_handler(commands=["exit"])
def exit_game(message: telebot.types.Message):
    global game
    game.reset_state()
    game = None
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Play a game", callback_data="Play"))
    keyboard.add(InlineKeyboardButton("Settings", callback_data="Settings"))
    keyboard.add(InlineKeyboardButton("LeaderBoards", callback_data="LeaderBoards"))
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=keyboard)

@bot.message_handler(commands=['play'])
def start(message: telebot.types.Message):
    game.start(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global game
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, 
                              message_id=call.message.message_id, 
                              reply_markup=InlineKeyboardMarkup())
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data == "Play":
        #keybord to choose a game
        game = TicTacToe
        bot.delete_message(chat_id, message_id)
        game.start(call.message)
    elif call.data == 'Settings':
        #choose other
        game = None
        pass
    elif call.data == 'LeaderBoards':
        game = None
        pass
    elif game is not None:
        game.callback_query(call)


@bot.message_handler(func=lambda m: True)
def echo_all(message: telebot.types.Message):
    logger.info(f"[#{message.chat.id}.{message.message_id} {message.chat.username!r}] {message.text!r}")
    bot.reply_to(message, f"You said: {message.text}")


logger.info("> Starting bot")
bot.infinity_polling()
logger.info("< Goodbye!")
