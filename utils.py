import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import urllib.parse
import bot_secrets


def send_main_menu(message: telebot.types.Message, bot: telebot.TeleBot):
    share_message = f"Check out this awesome game bot!\nLet's play together: {bot_secrets.BOT_USERNAME}"
    encoded_share_message = urllib.parse.quote(share_message)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("Play a game", callback_data="Play"))
    keyboard.add(InlineKeyboardButton("Help", callback_data="Help"))
    keyboard.add(InlineKeyboardButton("LeaderBoards", callback_data="LeaderBoards"))
    keyboard.add(InlineKeyboardButton("Fetchers", callback_data="Fetchers"))
    keyboard.add(InlineKeyboardButton("Share with Friends", url=f"tg://msg?text={encoded_share_message}"))
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=keyboard)


def edit_selected_msg(call: telebot.types.CallbackQuery, bot: telebot.TeleBot):
    bot.edit_message_text(f"You selected: *{call.data}*",
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=InlineKeyboardMarkup(),
                          parse_mode='Markdown')
