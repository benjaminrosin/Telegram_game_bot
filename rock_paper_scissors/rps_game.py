from random import randrange


def rps_game(player_choice):
    suggestions = ["✂️", "📄", "🧱"]

    bot_choice = suggestions[randrange(0, 3)]

    if bot_choice == player_choice:
        result = f"{bot_choice} \ntie"
    elif (
        (bot_choice == "✂️" and player_choice == "📄")
        or (bot_choice == "🧱" and player_choice == "✂️")
        or (bot_choice == "📄" and player_choice == "🧱")
    ):
        result = f"{bot_choice} \nYou Lose, Bot Wins"
    else:
        result = f"{bot_choice} \nYou win, Bot loses"
    return result
