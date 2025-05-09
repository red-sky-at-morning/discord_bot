import random
import discord

from inventories import inventories
from fishing import fish
from shop import shop

cmd_prefix:str = '?'
dev_id = 630837649963483179

def handle_message(message: discord.Message, content:str, channel_id, user_id:int, server:int, **kwargs) -> list[dict]:
    if not content:
        return None
    m_list:list = content.split()
    m_list[0] = m_list[0].lower()
    m_list.append(content)
    response:list = []
    response += dev_commands(m_list, message, channel_id, user_id, server)
    response += multi_args_m(m_list, message, channel_id, user_id, server)
    response += single_args_m(m_list[0], message, channel_id, user_id, server)
    response += message_responses(m_list, message, channel_id, user_id, server, kwargs.get("mentioned"))
    return response

def dev_commands(command:list[str], message:discord.Message, channel_id:int, user_id:int, server:int) -> list[dict]:
    response:list = []
    if command[0][0] != cmd_prefix:
        return response
    if user_id != dev_id:
        return response
    match command[0][1:]:
        case "toggle-error-standby":
            response.append({"type":"message","message":"Toggling switching to Standby mode on error..."})
            response.append({"type":"special","action":"toggle_error_standby"})
        case "mode":
            response += [{"type":"mode","mode":command[1].upper()},{"type":"message","message":f"Switching to {command[1].upper()} mode..."}]
        case "echo":
            response += [{"type":"message","message":command[-1].removeprefix(f"{cmd_prefix}echo ")},{"type":"delete","message":message.id,"channel":message.channel.id}]
    return response

def single_args_m(command:str, message:discord.Message, channel_id:int, user_id:int, server:int) -> list[dict]:
    response:list = []
    if command[0] != cmd_prefix:
        return response
    match command[1:]:
        case 'test':
            response.append({"type": "message", "message": "Hello World!"})
        case 'test1':
            response.append({"type": "message", "message": "Hello World!"})

        case 'test2':
            response.append({"type": "message", "message": "Starting..."})
            response.append({"type": "wait", "time": 5})
            response.append({"type": "message", "message": "Finished!"})

        case 'test3':
            response.append({"type": "message", "message": "Okay!"})
            response.append({"type": "react", "react": "👍", "message":message})
        
        case 'test4':
            response.append({"type":"reply", "message":"Hello World!", "reply":message})
        case 'test5':
            embedVar = discord.Embed(title="Title", description="Desc", color=0x00ff00)
            embedVar.add_field(name="Field1", value="hi", inline=False)
            embedVar.add_field(name="Field2", value="hi2", inline=False)
            return([{"type":"message", "message":"", "embed":embedVar}])
        case "test6":
            response.append({"type":"message","message":"Throwing exception and entering standby mode..."})
            response.append({"type":"error","error":Exception("Error for testing")})
        case "test7":
            response.append({"type":"message","message":"Goodbye world!"})
            response.append({"type":"delete","message":message.id, "channel":message.channel.id})
    return response

def multi_args_m(command:list[str], message:discord.Message, channel_id:int, user_id:int, server:int) -> list[dict]:
    response:list = []
    if command[0][0] != cmd_prefix:
        return response
    match command[0][1:]:
        case "fish":
            response += fish.handle(command, user_id, str(message.author), message)
        case "shop":
            if len(command) == 2:
                response += shop.get_shop_message(user_id, "test")
            else:
                response += shop.get_shop_message(user_id, command[1])
        case "inv":
            if len(command) < 3:
                response += ([{"type":"message","message":"Sorry, I can't tell what command you're trying to use. Try >inv fish"}])
            elif (len(command) == 3):
                if command[1] == "fish":
                    response += inventories.get_fish_embed(user_id, message.author.name, message.author)
            elif (len(command) > 3):
                try:
                    response += inventories.read_range_fish_from_inventory(user_id, message.author.name, message.author, (int(command[2])-1)*20, 20)
                except ValueError:
                    response += ([{"type":"message","message":"Sorry, I can't tell what page you're looking for. Try >inv fish 1"}])
        case "role":
            if command[1] == "add":
                response += [{"type":"role","role":command[2],"user":command[3]}]
    return response

responses = ("You called?", "haiiiiii", "OwO", "UwU", "Fuck off", "Bitch", "I'M HERE", ":3", "At least take me to dinner first", "You what", "Find my pages")
def message_responses(command:list[str], message:discord.Message, channel_id:int, user_id:int, server:int, mentioned:bool) -> list[dict]:
    response:list = []
    if mentioned:
        response += [{"type":"message","message":responses[random.randint(0,len(responses)-1)]}]
    return response

def handle_react(message:discord.Message, emoji:discord.PartialEmoji, count, channel_id:int, user_id:int, server:int) -> list[dict]:
    if not emoji:
        return None
    
    response = []
    response += make_sale(message, emoji, channel_id, user_id, server)

    return response


def make_sale(message:discord.Message, emoji:discord.PartialEmoji, channel_id, user_id, server) -> list[dict]:
    if shop.is_sale(user_id, message.id):    
        if emoji.name == "❎":
            return shop.complete_sale(user_id, message.id, False)
        elif emoji.name == "✅":
            return shop.complete_sale(user_id, message.id, True)
    elif shop.is_shop(user_id, message.id):
        if not shop.validate(emoji.name):
            return []
        else:
            return shop.sell_item(user_id, message.id, emoji.name)
    else:
        return []