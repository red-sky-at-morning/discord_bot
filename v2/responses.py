import random
import discord

from fishing import fish
from shop import shop

cmd_prefix:str = '?'

def handle_message(message: discord.Message, content:str, channel_id, user_id:int, server:int, **kwargs) -> list[dict]:
    if not content:
        return None
    m_list:list = content.split()
    m_list[0] = m_list[0].lower()
    m_list.append(content)
    response:list = []
    response += multi_args_m(m_list, message, channel_id, user_id, server)
    response += single_args_m(m_list[0], message, channel_id, user_id, server)
    response += message_responses(m_list, message, channel_id, user_id, server, kwargs.get("mentioned"))
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
        case "toggle_error_standby":
            response.append({"type":"message","message":"Toggling switching to Standby mode on error..."})
            response.append({"type":"special","action":"toggle_error_standby"})
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
                shop_data = shop.read_shop(user_id, "test")
            else:
                shop_data = shop.read_shop(user_id, command[1])
            if shop_data == None:
                response += [{"type":"message","message":"Hey! What are you trying to pull?"}]
            else:
                response += [{"type":"message","message":"", "embed":shop_data}]
        case "mode":
            if user_id != 630837649963483179:
                return
            response += [{"type":"mode","mode":command[1].upper()},{"type":"message","message":f"Switching to {command[1].upper()} mode..."}]
        case "role":
            if command[1] == "add":
                response += [{"type":"role","role":command[2],"user":command[3]}]
        case "echo":
            if cmd_prefix != "?":
                response += [{"type":"message","message":command[-1].removeprefix(f"{cmd_prefix}echo ")},{"type":"delete","message":message.id,"channel":message.channel.id}]
    return response

def message_responses(command:list[str], message:discord.Message, channel_id:int, user_id:int, server:int, mentioned:bool) -> list[dict]:
    response:list = []
    if mentioned:
        responses = ("You called?", "haiiiiii", "OwO", "UwU", "Fuck off", "Bitch", "I'M HERE", ":3", "At least take me to dinner first", "You what", "Find my pages")
        response += [{"type":"message","message":responses[random.randint(0,len(responses)-1)]}]
    return response

def handle_react(message:discord.Message, emoji:discord.PartialEmoji, count, channel_id:int, user_id:int, server:int) -> list[dict]:
    if not emoji:
        return None
    
    response = []
    response += make_sale(message, emoji, channel_id, user_id, server)

    return response


def make_sale(message:discord.Message, emoji:discord.PartialEmoji, channel_id, user_id, server) -> list[dict]:
    if not shop.is_sale(user_id, message.id):
        return []
    
    if emoji.name == "❎":
        return shop.complete_sale(user_id, message.id, False)
    elif emoji.name == "✅":
        return shop.complete_sale(user_id, message.id, True)
    else:
        return []