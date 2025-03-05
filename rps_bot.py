import telebot
import bot_secrets
import logging
from rps_game import rps_game
import utils
import db_connect as db


logging.basicConfig(
    format="[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

bot = telebot.TeleBot(bot_secrets.TOKEN)


WAIT_MSG = "Wait for your opponent's move"
YOURES_MSG = "Your move!"


def init_state():
    return ["", ""]


def start(state):
    users_id = state["user_id_arr"]

    msg = []
    for i in [0, 1]:
        msg.append(
            (
                bot.send_message(
                    state["user_id_arr"][i],
                    f"Game Started, {WAIT_MSG}",
                    reply_markup=get_rps_buttons(),
                ).id
            )
        )

    db.update_state_info(users_id[0], {"msg_id_arr": msg})


def get_rps_buttons() -> telebot.types.InlineKeyboardMarkup:
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        telebot.types.InlineKeyboardButton("🧱", callback_data="🧱"),
        telebot.types.InlineKeyboardButton("📄", callback_data="📄"),
        telebot.types.InlineKeyboardButton("✂️", callback_data="✂️"),
    )
    # bot.send_message(chat_id=user_id, text="Choose your move:", reply_markup=markup)
    return markup


def check_winner(choices):
    result = rps_game(choices)
    print("###############", result)
    if result == 0:
        response = "It's a tie!"
    elif result == 1:
        response = "Player 1 lost Player 2 won"
    elif result == -1:
        response = "Player 1 won Player 2 lost"
    return response


def callback_query(call: telebot.types.CallbackQuery, state):
    user_id = call.message.chat.id
    index = state["user_id_arr"].index(user_id)

    if state["state"][index]:
        bot.answer_callback_query(call.id, "wait for your opponents move.")
        return

    state["state"][index] = call.data
    db.update_state_info(state["user_id_arr"][0], {"state": state["state"]})

    if all(state["state"]):
        result = check_winner(state["state"])

        winner = rps_game(state["state"])

        if winner == 2:
            for i in [0, 1]:
                bot.edit_message_text(
                    "It's a tie",
                    state["user_id_arr"][i],
                    state["msg_id_arr"][i],
                    reply_markup=telebot.types.InlineKeyboardMarkup(),
                )
                # db.inc_score(state["user_id_arr"][i], 3, state["game_type"])
                utils.send_main_menu(state["user_id_arr"][i], bot)

        else:
            bot.edit_message_text(
                "hgcfvhvhjvhkjvhjvjhvhjvje",
                state["user_id_arr"][index],
                state["msg_id_arr"][index],
                reply_markup=telebot.types.InlineKeyboardMarkup(),
            )
            # db.inc_score(state["user_id_arr"][index], 7, state["game_type"])
            utils.send_main_menu(state["user_id_arr"][index], bot)

            bot.edit_message_text(
                "hgcfvhvhjvhkjvhjvjhvhjvje",
                state["user_id_arr"][not index],
                state["msg_id_arr"][not index],
                reply_markup=telebot.types.InlineKeyboardMarkup(),
            )
            utils.send_main_menu(state["user_id_arr"][not index], bot)
