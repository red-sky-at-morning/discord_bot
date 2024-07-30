import json
import os.path as path
import os
import discord

def get_path(user_id:int) -> str:
    path_str:str = f"fishing/inventories/inv_{user_id}"
    if path.isfile(f"{path_str}.json"):
        return f"{path_str}.json"
    else:
        inv_list:list = []
        if path.isfile(f"{path_str}.txt"):
            with open(f"{path_str}.txt", "r") as inv:
                inv_list = [line.strip("\n") for line in inv.readlines()]
            os.remove(f"{path_str}.txt")
        inv_dict = {"meta":{"id":user_id},"inventory":inv_list}
        with open(f"{path_str}.json", "w") as inv:
            json.dump(inv_dict, inv)
        return f"{path_str}.json"

def add_to_inventory(user_id:int, item) -> bool:
    try:
        user_path = get_path(user_id)
        with open(user_path, "r") as inv:
            data = json.load(inv)
        with open(user_path, 'w') as inv:
            data["inventory"].append(item)
            json.dump(data,inv)
        return True
    except Exception as e:
        print(e)
        return False

def remove_from_inventory(user_id:int, item) -> bool:
    return False #TODO implement

def read_from_inventory(user_id:int, username:str, start_index:int, step:int) -> list[dict]:
    with open(get_path(user_id), "r") as inv:
        data = json.load(inv)
    inventory = [f"{data['inventory'].index(line)+1}. {line}" for line in data["inventory"][start_index:start_index+step]]
    response = str(inventory).replace('"', "'").replace("', '", "\n").strip("[']")
    embed = discord.Embed(title=f"{username}'s Inventory", description=f"Page {int(start_index/20)+1} ({start_index+1} - {start_index + step+1})", color=0x6699ff)
    embed.add_field(name="Contents", value=response)
    return [{"type":"message","message":"","embed":embed}]
