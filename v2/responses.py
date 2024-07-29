import random
import discord

from fishing import fish

def handle_message(message: discord.Message, content:str, channel_id, user_id:int, server:int, **kwargs) -> list[dict]:
    m_list:list = content.split()
    m_list[0] = m_list[0].lower()
    m_list.append(content)
    response:list = []
    response += single_args_m(m_list[0], message, channel_id, user_id, server)
    response += multi_args_m(m_list, message, channel_id, user_id, server)
    response += message_responses(m_list, message, channel_id, user_id, server)
    return response

def single_args_m(command:str, message:discord.Message, channel_id:int, user_id:int, server:int) -> list[dict]:
    response:list = []
    match command:
        case '>test':
            response.append({"type": "message", "message": "Hello World!"})
        case '>test1':
            response.append({"type": "message", "message": "Hello World!"})

        case '>test2':
            response.append({"type": "message", "message": "Starting..."})
            response.append({"type": "wait", "time": 5})
            response.append({"type": "message", "message": "Finished!"})

        case '>test3':
            response.append({"type": "message", "message": "Okay!"})
            response.append({"type": "react", "react": "👍", "message":message})
        
        case '>test4':
            response.append({"type":"reply", "message":"Hello World!", "reply":message})
        case '>test5':
            embedVar = discord.Embed(title="Title", description="Desc", color=0x00ff00)
            embedVar.add_field(name="Field1", value="hi", inline=False)
            embedVar.add_field(name="Field2", value="hi2", inline=False)
            return([{"type":"message", "message":"", "embed":embedVar}])
        case ">test6":
            response.append({"type":"message","message":"Throwing exception and entering standby mode..."})
            response.append({"type":"error","error":Exception("Error for testing")})
    return response

def multi_args_m(command:list[str], message:discord.Message, channel_id:int, user_id:int, server:int) -> list[dict]:
    response:list = []
    match command:
        case command if command[0] == ">fish":
            response += fish.go_fish(user_id, str(message.author))
    return response

def message_responses(command:list[str], message:discord.Message, channel_id:int, user_id:int, server:int) -> list[dict]:
    response:list = []
    return response