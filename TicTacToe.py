import logging

import bot_secrets
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import utils
import db_connect as db


logging.basicConfig(
    format="[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

EMPTY = ' '
X, O = 'X', 'O'  # noqa: E741
WAIT_MSG = "Wait for your opponent's move"
YOURS_MSG = "Your move!"

logging.basicConfig(
    format="[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)

bot = telebot.TeleBot(bot_secrets.TOKEN)


def get_keyboard(game_state: list[str]) -> telebot.types.InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=3)

    buttons = []
    for i in range(9):
        buttons.append(InlineKeyboardButton(f"{game_state[i]}", callback_data=f"{i}"))
    keyboard.add(*buttons)

    return keyboard


def init_state():
    return [EMPTY] * 9


def start(state):
    user1_id, user2_id = state["user_id_arr"]

    turn = state["turn"]
    msg = [None, None]
    m1 = bot.send_message(state["user_id_arr"][not turn], f"Game Started, {WAIT_MSG}", reply_markup=get_keyboard(state["state"]))
    m2 = bot.send_message(state["user_id_arr"][turn], f"Game Started, {YOURS_MSG}", reply_markup=get_keyboard(state["state"]))
    msg[not turn] = m1.id
    msg[turn] = m2.id
    logger.info(f"m1: {m1}, m2: {m2} - {msg=} {turn=}")
    db.update_state_info(user1_id, {"msg_id_arr": msg})


def check_status(grid):
    winner: str = ""
    for i in range(3):
        if grid[3*i] == grid[3*i + 1] == grid[3*i + 2] != EMPTY:
            winner = grid[3*i]
            break
        if grid[i] == grid[i + 3] == grid[i + 6] != EMPTY:
            winner = grid[i]
            break
    if winner == "":
        if grid[0] == grid[4] == grid[8] != EMPTY:
            winner = grid[0][0]
        if grid[2] == grid[4] == grid[6] != EMPTY:
            winner = grid[2]
    return winner


def callback_query(call, state):
    turn = state["turn"]
    if call.from_user.id != state["user_id_arr"][turn]:
        bot.answer_callback_query(call.id, "It's not your turn")
        return
    # right player
    pos = int(call.data)
    over = False
    tmp_state = state["state"]
    if tmp_state[pos] != EMPTY:
        bot.answer_callback_query(call.id, "Not a legal move")
        return
    else:
        if not turn:
            tmp_state[pos] = X
        else:
            tmp_state[pos] = O
        if (w := check_status(tmp_state)) != "":
            #blaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
            bot.send_message(call.message.chat.id, f"{w} WON !!!")
            over = True
        elif tmp_state.count(EMPTY) == 0:
            bot.send_message(call.message.chat.id, "DRAW !!!")
            over = True
        
        if over:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            # TO DO
            utils.send_main_menu(call.message, bot)
            return

    db.update_state_info(state["user_id_arr"][turn], {"state": tmp_state, "turn": int(1-turn)})
    logger.info(f"state after: {db.get_state_info_by_ID(state["user_id_arr"][turn])}")
    bot.edit_message_text(WAIT_MSG,
                    state["user_id_arr"][turn],
                            state["msg_id_arr"][turn],
                            reply_markup=get_keyboard(state["state"]))
    bot.edit_message_text(YOURS_MSG,
                    state["user_id_arr"][not turn],
                            state["msg_id_arr"][not turn],
                            reply_markup=get_keyboard(state["state"]))

    bot.answer_callback_query(call.id)


def about():
    return ('⭕❌ * Tic Tec Toe * ❌⭕\n'
            ' - duel game\n'
            'Think fast, line up three, and claim victory! 🏆\n'
            'Are you ready to outsmart your opponent? 🎯🔥')
