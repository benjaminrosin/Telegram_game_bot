import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import bot_secrets
import utils

bot = telebot.TeleBot(bot_secrets.TOKEN)

# Game storage: { chat_id: { "grid": [...], "turn": "🔴" } }
games = {}

ROWS, COLS = 6, 7
EMPTY, RED, YELLOW = "⚪", "🔴", "🟡"


def create_grid():
    """Initialize an empty grid."""
    return [[EMPTY] * COLS for _ in range(ROWS)]


def format_grid(grid: list[list[str]]) -> str:
    """Convert grid to a string for Telegram messages."""
    grid_str = "\n".join("".join(row) for row in grid)
    column_numbers = "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n"
    return f"{grid_str}\n{column_numbers}"


def drop_piece(grid: list[list[str]], column: int, piece: str) -> bool:
    """Drop a piece into the column if possible."""
    for row in reversed(grid):
        if row[column] == EMPTY:
            row[column] = piece
            return True
    return False  # Column is full


def check_winner(grid: list[list[str]], piece: str) -> bool:
    """Check for a win (horizontal, vertical, diagonal)."""
    # Horizontal & Vertical
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(grid[r][c + i] == piece for i in range(4)):
                return True
    for r in range(ROWS - 3):
        for c in range(COLS):
            if all(grid[r + i][c] == piece for i in range(4)):
                return True
    # Diagonal (↘)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(grid[r + i][c + i] == piece for i in range(4)):
                return True
    # Diagonal (↙)
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(grid[r - i][c + i] == piece for i in range(4)):
                return True
    return False


def is_draw(grid: list[list[str]]) -> bool:
    """Check if the grid is full (draw)."""
    return all(cell != EMPTY for row in grid for cell in row)


def create_keyboard() -> InlineKeyboardMarkup:
    """Generate inline keyboard for column selection."""
    keyboard = InlineKeyboardMarkup()
    buttons = [InlineKeyboardButton(str(i+1), callback_data=str(i)) for i in range(COLS)]
    keyboard.add(*buttons)
    return keyboard


def start(message: telebot.types.Message):
    """Start a new 4-in-a-Row game."""
    chat_id = message.chat.id
    games[chat_id] = {"grid": create_grid(), "turn": RED}
    bot.send_message(chat_id, format_grid(games[chat_id]["grid"]), reply_markup=create_keyboard())


def callback_query(call: telebot.types.CallbackQuery):
    """Handle player moves."""
    chat_id = call.message.chat.id
    if chat_id not in games:
        bot.answer_callback_query(call.id, "Game not found.")
        return

    game = games[chat_id]
    column = int(call.data)

    if not drop_piece(game["grid"], column, game["turn"]):
        bot.answer_callback_query(call.id, "Column is full! Choose another.")
        return

    if check_winner(game["grid"], game["turn"]):
        bot.edit_message_text(format_grid(game["grid"]) + f"\n\n🎉 {game['turn']} Wins!", chat_id, call.message.message_id)
        del games[chat_id]
        utils.send_main_menu(call.message, bot)
        return

    if is_draw(game["grid"]):
        bot.edit_message_text(format_grid(game["grid"]) + "\n\n😲 It's a Draw!", chat_id, call.message.message_id)
        del games[chat_id]
        utils.send_main_menu(call.message, bot)
        return

    # Switch turns
    game["turn"] = YELLOW if game["turn"] == RED else RED
    bot.edit_message_text(format_grid(game["grid"]), chat_id, call.message.message_id, reply_markup=create_keyboard())


def reset_state():
    #del games[chat_id]
    # delete from cache
    print("skipping 4 in row reset")


def about():
    return ('🔴🟡 * 4 in a Row * 🟡🔴\n'
            'Drop your pieces, connect four, and outplay your opponent! 🏆\n'
            'Think ahead, block their moves, and claim victory! 🎯🔥')
