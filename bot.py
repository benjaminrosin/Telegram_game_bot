import logging
import bot_secrets
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import TicTacToe
import FourInRow
import Trivia
import utils
import emoji
import db_connect as db
import rock_paper_scissors.rps_bot as Rps

logging.basicConfig(
    format="[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

bot = telebot.TeleBot(bot_secrets.TOKEN)

games = {
    "Tic-Tac-Toe": TicTacToe,
    "4-In-A-Row": FourInRow,
    "Trivia": Trivia,
    "rock-paper-scissors": Rps,
}

#single_player_games = ["rock-paper-scissors"]


@bot.message_handler(commands=["start", "exit"])
def send_welcome(message: telebot.types.Message):

    text = message.text
    if text == "/start":
        logger.info(f"+ Start chat #{message.chat.id} from {message.chat.username}")
        bot.reply_to(message, "🤖 Welcome! 🤖")
    else:  # text == "exit"
        bot.reply_to(message, "🤖 Hi again 🤖")

    utils.send_main_menu(message, bot)


@bot.callback_query_handler(func=lambda call: call.data == "Play")
def play_callback_query(call):
    utils.edit_selected_msg(call, bot)

    keyboard = InlineKeyboardMarkup(row_width=1)
    game_options = []

    for g in games.keys():
        game_options.append(InlineKeyboardButton(g, callback_data=g))
    keyboard.add(*game_options)

    bot.send_message(call.message.chat.id, "Choose a game:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "Help")
def help_callback_query(call):
    utils.edit_selected_msg(call, bot)

    help(call.message)


@bot.callback_query_handler(func=lambda call: call.data == "LeaderBoards")
def scoreboard_callback_query(call):
    utils.edit_selected_msg(call, bot)

    scoreboard = "🏆 *Scoreboard* 🏆\n\n"
    for g in games:
        top = ['a', 'b', 'c']  # use mongo to get them
        scoreboard += '*{}*:\n🥇 *{}*\n🥈 *{}*\n🥉 *{}*\n\n'.format(g, *top)

    bot.send_message(call.message.chat.id, scoreboard, parse_mode="Markdown")
    utils.send_main_menu(call.message, bot)


@bot.callback_query_handler(func=lambda call: call.data == "Features")
def fetchers_callback_query(call):
    utils.edit_selected_msg(call, bot)

    msg = ""
    for g in games.values():
        msg += g.about()
        msg += "\n\n"

    bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
    utils.send_main_menu(call.message, bot)


# TO CHANGE
# reset_state
# init_state
# start
# callback_query

@bot.callback_query_handler(func=lambda call: call.data in games.keys())
def callback_query_for_choosing_game(call):
    game_type = call.data
    user_id = call.message.from_user.id
    chat_id = call.message.chat.id
    # check if a queue exists
    queue = db.get_queue_info("game_type", game_type)
    if queue is not None:
        # Retrive other player's data - no queues for single
        other_user_id = queue["user_id"]
        # Queue exists, delete it and create a new game
        db.delete_queue(other_user_id)
        state = games[game_type].init_state()
        db.create_state(user_id, other_user_id, game_type, state)
        games[game_type].start()
    else:
        # Queue does not exists, create one
        db.create_queue(user_id, chat_id, game_type)
        q_msg = "You have joined a queue, please wait for other players to play"
        bot.send_message(chat_id, q_msg, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: True)
def callback_query_for_move(call):
    user_id = call.message.from_user.id
    state = db.get_state_info("user_id", user_id)
    if state is not None:
        #is_single =  db.is_single(user_id) - Single-Player = True, Multi-Player = False
        game_type = state["game_type"]
        curr_game = games[game_type] # current game module
        curr_game.callback_query(call, state)

    # ask what to send
    # utils.edit_selected_msg(call, bot)


# TO CHANGE - DONE
@bot.message_handler(commands=["rename"])
def raname(message: telebot.types.Message):
    logger.info(
        f"[#{message.chat.id}.{message.message_id} {message.chat.username!r}] {message.text!r}"
    )
    arr = message.text.split()
    if len(arr) != 2:
        bot.reply_to(message, "correct use:\n/rename <new_name>\nthe name cannot contain spaces")
    else:  # correct behavior
        bot.reply_to(message, f"you choose {arr[1]}")
        logger.info(f"[#{message.chat.id}.{message.message_id} {message.chat.username!r}] {message.text!r}")
        #print('update DB')
        db.get_user_info(message.from_user.id, { "user_name": arr[1] })


def is_emoji(s: str) -> bool:
    return s in emoji.EMOJI_DATA


# TO CHANGE - DONE
@bot.message_handler(commands=["reemoji"])
def reemoji(message: telebot.types.Message):
    logger.info(f"[#{message.chat.id}.{message.message_id} {message.chat.username!r}] {message.text!r}")
    arr = message.text.split()
    if len(arr) != 2 or not is_emoji(arr[1]):
        bot.reply_to(message, "correct use:\n/reemoji <new_emoji>")
    else: # correct behavior
        bot.reply_to(message, f"you choose {arr[1]}")
        logger.info(f"[#{message.chat.id}.{message.message_id} {message.chat.username!r}] {message.text!r}")
        #print('update DB')
        db.get_user_info(message.from_user.id, { "emoji": arr[1] })


@bot.message_handler(commands=["help", "h"])
def help(message: telebot.types.Message):
    help_str = """
🤖 *Bot Commands Help*:

🎮 *Game Commands*:
- `/start` - Start the bot
- `/exit` - Returns to main menu
- `/help` - Get help

🛠 *Settings*:
- `/rename <new_name>` - Change your username in the game
- `/reemoji <emoji>` - Change your game emoji

    """
    bot.send_message(message.chat.id, help_str, parse_mode="Markdown")
    utils.send_main_menu(message, bot)


@bot.message_handler(func=lambda m: True)
def echo_all(message: telebot.types.Message):
    logger.info(
        f"[#{message.chat.id}.{message.message_id} {message.chat.username!r}] {message.text!r}"
    )
    bot.reply_to(message, f"You said: {message.text}")


logger.info("> Starting bot")
bot.infinity_polling()
logger.info("< Goodbye!")
