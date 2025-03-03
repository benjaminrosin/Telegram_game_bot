import logging

import bot_secrets
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import TicTacToe
import FourInARow

logging.basicConfig(
    format="[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

bot = telebot.TeleBot(bot_secrets.TOKEN)

games = {"Tic-Tac-Toe": TicTacToe,
        "4-In-A-Row": FourInARow,}
game = None

@bot.message_handler(commands=["start", "exit"])
def send_welcome(message: telebot.types.Message):
    global game

    text = message.text
    if text == "start":
        logger.info(f"+ Start chat #{message.chat.id} from {message.chat.username}")
        bot.reply_to(message, "🤖 Welcome! 🤖")
    else: # text == "exit"
        if game is not None:
            game.reset_state()
            game = None

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Play a game", callback_data="Play"))
    keyboard.add(InlineKeyboardButton("Settings", callback_data="Settings"))
    keyboard.add(InlineKeyboardButton("LeaderBoards", callback_data="LeaderBoards"))
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ["Play", "Settings", "LeaderBoards"])
def callback_query(call):
    global game
    game = None

    bot.edit_message_reply_markup(chat_id=call.message.chat.id, 
                              message_id=call.message.message_id, 
                              reply_markup=InlineKeyboardMarkup())
    
    # chat_id = call.message.chat.id
    # message_id = call.message.message_id

    if call.data == "Play":
        keyboard = InlineKeyboardMarkup()
        game_options = []
        for g in games.keys():
            game_options.append(InlineKeyboardButton(g, callback_data=g))
        keyboard.add(*game_options)
        bot.send_message(call.message.chat.id, "Choose a game:", reply_markup=keyboard)
        #keybord to choose a game
        #bot.delete_message(chat_id, message_id)
    elif call.data == 'Settings':
        pass
    else: # call.data == 'LeaderBoards'
        pass

@bot.callback_query_handler(func=lambda call: call.data not in ["Play", "Settings", "LeaderBoards"])
def callback_query_for_choosing_game(call):
    global game
    if game is not None:
        game.callback_query(call)
        return
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, 
                              message_id=call.message.message_id, 
                              reply_markup=InlineKeyboardMarkup())

    game = games[call.data]
    game.start(call.message)


@bot.message_handler(func=lambda m: True)
def echo_all(message: telebot.types.Message):
    logger.info(f"[#{message.chat.id}.{message.message_id} {message.chat.username!r}] {message.text!r}")
    bot.reply_to(message, f"You said: {message.text}")


logger.info("> Starting bot")
bot.infinity_polling()
logger.info("< Goodbye!")
