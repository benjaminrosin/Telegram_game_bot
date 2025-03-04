from random import randrange


def rps_game(player_choice, oponnent_choice=None):
    if oponnent_choice is None:
        oponnent_choice = computer_choice()
    if oponnent_choice == player_choice:
        result = f"{oponnent_choice} \ntie"
    elif (
        (oponnent_choice == "✂️" and player_choice == "📄")
        or (oponnent_choice == "🧱" and player_choice == "✂️")
        or (oponnent_choice == "📄" and player_choice == "🧱")
    ):
        result = f"{oponnent_choice} \nYou Lose, Bot Wins"
    else:
        result = f"{oponnent_choice} \nYou win, Bot loses"
    return result


def computer_choice():
    suggestions = ["✂️", "📄", "🧱"]
    return suggestions[randrange(0, 3)]
