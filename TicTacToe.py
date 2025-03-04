import logging

import bot_secrets
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import utils

EMPTY = ' '
X = 'X'
O = 'O'
turn = False
state = [EMPTY] * 9

logging.basicConfig(
    format="[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

bot = telebot.TeleBot(bot_secrets.TOKEN)


def get_keyboard(game_state: list[str]) -> telebot.types.InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=3)

    buttons = []
    for i in range(9):
        buttons.append(InlineKeyboardButton(f"{game_state[i]}", callback_data=f"{i}"))
    keyboard.add(*buttons)

    return keyboard

def start(message):
    sent = bot.send_message(message.chat.id, "Choose an option:", reply_markup=get_keyboard(state))

def check_status():
    winner: str = ""
    for i in range(3):
        if state[3*i] == state[3*i + 1] == state[3*i + 2] != EMPTY:
            winner = state[3*i]
            break
        if state[i] == state[i + 3] == state[i + 6] != EMPTY:
            winner = state[i]
            break
    if winner == "":
        if state[0] == state[4] == state[8] != EMPTY:
            winner = state[0][0]
        if state[2] == state[4] == state[6] != EMPTY:
            winner = state[2]
    return winner
    
def reset_state():
    global turn, state
    turn = False
    state = [EMPTY] * 9

def callback_query(call):
    global turn
    pos = int(call.data)
    over = False
    if state[pos] != EMPTY:
        bot.answer_callback_query(call.id, "Not a legal move")
        return
    else:
        if not turn:
            state[pos] = X
        else:
            state[pos] = O
        turn = not turn
        if (w := check_status()) != "":
            bot.send_message(call.message.chat.id, f"{w} WON !!!")
            over = True
        elif state.count(EMPTY) == 0:
            bot.send_message(call.message.chat.id, "DRAW !!!")
            over = True
        
        if over:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            reset_state()
            utils.send_main_menu(call.message, bot)
            '''
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("Play a game", callback_data="Play"))
            keyboard.add(InlineKeyboardButton("Settings", callback_data="Settings"))
            keyboard.add(InlineKeyboardButton("LeaderBoards", callback_data="LeaderBoards"))
            bot.send_message(call.message.chat.id, "Choose an option:", reply_markup=keyboard)'''
            return

    #bot.delete_message(call.message.chat.id, call.message.message_id)
    #start(call.message)

    bot.edit_message_reply_markup(call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=get_keyboard(state))
    
    bot.answer_callback_query(call.id)


def about():
    return ('⭕❌ * Tic Tec Toe * ❌⭕\n'
            'Think fast, line up three, and claim victory! 🏆\n'
            'Are you ready to outsmart your opponent? 🎯🔥')
