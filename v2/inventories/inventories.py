import builtins
import json
import os.path as path
import os
import discord

with open("fishing/meta/fish.txt", "r") as fish:
    fish_list = [line.strip("\n") for line in fish.readlines()]
    
def get_path(user_id:int) -> str:
    path_str:str = f"inventories/meta/inv_{user_id}"
    if path.isfile(f"{path_str}.json"):
        return f"{path_str}.json"
    else:
        inv_list:list = []
        if path.isfile(f"{path_str}.txt"):
            with open(f"{path_str}.txt", "r") as inv:
                inv_list = [line.strip("\n") for line in inv.readlines()]
            os.remove(f"{path_str}.txt")
        with(open("inventories/meta/TEMPLATE.json")) as template:
            inv_dict = json.load(template)
        inv_dict["meta"]["id"] = user_id
        inv_dict["fish"] = inv_list
        with open(f"{path_str}.json", "w") as inv:
            json.dump(inv_dict, inv)
        return f"{path_str}.json"

def get_data(user_id:int):
    with open(get_path(user_id), "r") as inv:
        data = json.load(inv)
    return data

def add_fish_to_inventory(user_id:int, item) -> bool:
    try:
        user_path = get_path(user_id)
        data = get_data(user_id)
        with open(user_path, 'w') as inv:
            data["fish"].append(item)
            json.dump(data,inv)
        return True
    except Exception as e:
        print(e)
        return False

def remove_from_inventory(user_id:int, idx:int) -> bool:
    try:
        user_path = get_path(user_id)
        data = get_data(user_id)
        with open(user_path, "w") as inv:
            data["fish"].pop(idx)
            json.dump(data, inv)
        return True
    except Exception as e:
        return False

def read_range_from_inventory(user_id:int, username:str, user:discord.User, start_index:int, step:int) -> list[dict]:
    data = get_data(user_id)
    inventory = [(f"{data['fish'].index(line)+1}. {f'*{line}*' if line not in fish_list else line}") for line in data["fish"][start_index:start_index+step]]
    response = str(inventory).replace('"', "'").replace("', '", "\n").strip("[']")
    embed = discord.Embed(title=f"{username}'s Tank", description=f"Page {int(start_index/20)+1} ({start_index+1} - {start_index + step+1})", color=0x6699ff)
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="Contents", value=response)
    return [{"type":"message","message":"","embed":embed}]

def read_one_from_inventory(user_id:int, idx:int) -> str:
    data = get_data(user_id)
    return data["fish"][idx]

def get_meta(user_id):
    return get_data(user_id).get("meta")

def add_meta(user_id, name, item):
    user_path = get_path(user_id)
    data = get_data(user_id)
    match type(data["meta"].get(name)):
        case builtins.list:
            data["meta"][name].append(item)
        case _:
            data["meta"][name] = item
    print(data["meta"])
    with open(user_path, 'w') as inv:
        json.dump(data,inv)

def get_total_buffs(user_id:int) -> int:
    meta = get_meta(user_id)
    return (meta.get("rod_level") + meta.get("bait_level"))

def read_meta(user_id:int, username:str, user:discord.User) -> list[dict]:
    data = get_data(user_id)
    embed = discord.Embed(title=f"{username}'s Inventory", color=0x6699ff)
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="Fish in storage:", value=len(data.get("fish")), inline=False)
    embed.add_field(name="Rod Level:", value=data.get("meta").get("rod_level"), inline=False)
    embed.add_field(name="Money:", value=data.get("meta").get("money"), inline=False)
    return [{"type":"message","message":"","embed":embed}]
