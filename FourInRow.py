import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import bot_secrets


bot = telebot.TeleBot(bot_secrets.TOKEN)

# Game storage: { chat_id: { "grid": [...], "turn": "🔴" } }
games = {}

ROWS, COLS = 6, 7
EMPTY, RED, YELLOW = "⚪", "🔴", "🟡"


def create_grid():
    """Initialize an empty grid."""
    return [[EMPTY] * COLS for _ in range(ROWS)]


def format_grid(grid):
    """Convert grid to a string for Telegram messages."""
    column_numbers = "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n"
    grid_str = "\n".join("".join(row) for row in grid)
    return f"{column_numbers}{grid_str}"


def drop_piece(grid, column, piece):
    """Drop a piece into the column if possible."""
    for row in reversed(grid):
        if row[column] == EMPTY:
            row[column] = piece
            return True
    return False  # Column is full


def check_winner(grid, piece):
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


def is_draw(grid):
    """Check if the grid is full (draw)."""
    return all(cell != EMPTY for row in grid for cell in row)


def create_keyboard():
    """Generate inline keyboard for column selection."""
    keyboard = InlineKeyboardMarkup()
    buttons = [InlineKeyboardButton(str(i+1), callback_data=str(i)) for i in range(COLS)]
    keyboard.add(*buttons)
    return keyboard


#@bot.message_handler(commands=["start4inarow"])
def start(message):
    """Start a new 4-in-a-Row game."""
    chat_id = message.chat.id
    games[chat_id] = {"grid": create_grid(), "turn": RED}
    bot.send_message(chat_id, format_grid(games[chat_id]["grid"]), reply_markup=create_keyboard())


#@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def callback_query(call):
    """Handle player moves."""
    chat_id = call.message.chat.id
    if chat_id not in games:
        bot.answer_callback_query(call.id, "Game not found. Start a new one with /start4inarow")
        return

    game = games[chat_id]
    column = int(call.data)

    if not drop_piece(game["grid"], column, game["turn"]):
        bot.answer_callback_query(call.id, "Column is full! Choose another.")
        return

    if check_winner(game["grid"], game["turn"]):
        bot.edit_message_text(format_grid(game["grid"]) + f"\n\n🎉 {game['turn']} Wins!", chat_id, call.message.message_id)
        del games[chat_id]
        return

    if is_draw(game["grid"]):
        bot.edit_message_text(format_grid(game["grid"]) + "\n\n😲 It's a Draw!", chat_id, call.message.message_id)
        del games[chat_id]
        return

    # Switch turns
    game["turn"] = YELLOW if game["turn"] == RED else RED
    bot.edit_message_text(format_grid(game["grid"]), chat_id, call.message.message_id, reply_markup=create_keyboard())


def reset_state():
    #del games[chat_id]
    # delete from cache
    print("skipping 4 in row reset")

#bot.polling()
