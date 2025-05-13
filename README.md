# 🎮 GameMaster Bot

A Telegram bot offering multiple games in one place! Challenge friends or test your knowledge.

This bot was developed during a hackathon as part of the DEVBOOST program.

## Developed by:
- **Benjamin Rosin**
- **Itamar Saban**
- **Yousef Matar**

## The Games
- 🎯 **Tic-Tac-Toe**: The classic game where you need to align three symbols. Challenge a friend!
- 🔢 **Four in a Row**: Connect four of your pieces vertically, horizontally, or diagonally to win.
- ✂️ **Rock Paper Scissors**: The timeless hand game with a digital twist!
- 🧠 **Trivia**: Test your knowledge with questions across various categories.

## Features
- 📊 **Leaderboards**: Track your scores across all games
- 🔄 **Customization**: Change your username and emoji
- 👥 **Multiplayer**: Challenge other users in real-time
- 📱 **Accessibility**: Easy to use interface with inline buttons

## Instructions for Developers 
### Prerequisites
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- MongoDB (running locally)

### Setup
1. Clone this repository 
2. CD into the project directory
3. Get an API Token for a bot via the [BotFather](https://telegram.me/BotFather)
4. Create a `bot_secrets.py` file with your bot token:
   ```python
   TOKEN = 'your_bot_token_here'
   ```
5. Make sure MongoDB is running locally on the default port

### Running the bot
Run the bot (This will also install Python 3.13 and all dependencies):
```
uv run bot.py
```

## Tech Stack
- Python 3.13
- PyTelegramBotAPI
- MongoDB
- emoji package

## Extending the Bot
The bot's architecture makes it easy to add new games. To create a new game:

1. Create a new Python file for your game
2. Implement the following required functions:
   - `init_state()`: Initialize the game state
   - `start(state)`: Start the game and send initial message
   - `callback_query(call, state)`: Handle user interactions
   - `about()`: Return game description for the Features section

Then register your game in the `games` dictionary in `bot.py`.

<!--
# 🚧 YOUR BOT NAME HERE

## The Team
- 🚧 Participant 1 Name
- 🚧 Participant 2 Name
- 🚧 Participant 3 Name

## About this bot

🚧 ENTER DESCRIPTION HERE

🚧 YOU CAN ADD A t.me LINK TO THE BOT HERE

🚧 ADD SCREENSHOTS/GIFS/SCREENCAST HERE (REFER TO MARKDOWN'S SYNTAX FOR HELP ON DISPLAYING IMAGES)

🚧 ADD ANY OTHER NOTES REGARDING THE BOT
 
## Instructions for Developers 
### Prerequisites
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- (uv van install python for you)
- 🚧 ADD ANY OTHER PREREQUISITE HERE (MONGODB?)

### Setup
- git clone this repository 
- cd into the project directory
- Get an API Token for a bot via the [BotFather](https://telegram.me/BotFather)
- Create a `bot_secretes.py` file with your bot token:

      BOT_TOKEN = 'xxxxxxx'
  
### Running the bot        
- Run the bot (This will also install Python 3.13 and all dependencies):

      uv run bot.py
