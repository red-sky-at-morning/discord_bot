# Eclipsebot 
## Current version: V2.1.1
The code for midnight__sun's Eclipsebot on discord, written in discord.py.

Files in /v1/* are deprecated.

#### Cloning
This repo is missing a couple key components of Eclipsebot, namely its bot token. If you want to clone this repo and run your own bot, here is what you will need to do:
- visit the [discord dev portal](https://discord.com/developers/applications)
- create a new bot and note the token
- create a file called `TOKEN.txt` at `/meta/`
- paste your new bot token into that file
- import the requirements by running `pip3 import -r requirements.txt`
- run bot.py

If you do choose to clone this repo and have any trouble, please contact me on discord (@midnight__sun).

#### Module summaries:
- `bot.py` and `reponses.py`: Main codebase. `bot.py` contains the discord event handlers, such as `on_message`, and `reponses.py` contains responses to messages and commands.
- `console` module: allows anyone with console access to where Eclipsebot is running to see what messages Eclipsebot can see and type as Eclipsebot. Effectively allows Eclipsebot to act as a discord proxy (albeit a bad one, because you still need access to the discord servers)
- `inventories` module: logic for individual users' inventories. includes things like fishing, shopping, farming (soon), and others yet to come
- `shop` module: logic for creating data-driven shops, presenting them to users, and acting on any actions the users take. surprisingly important, it allows to upgrade almost every single one of the players' stats
- `roll` module: logic for dice rolling. uses function variables and is thus cursed.
- `fishing` module: logic for fishing. the first module implemented, it has fairly simple logic (for now).
- `farming` module: logic for farming. WIP