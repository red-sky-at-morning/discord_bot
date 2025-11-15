import builtins
import json
import os.path as path
import os
import discord

with open("fishing/meta/fish.txt", "r") as fish:
    fish_list = [line.strip("\n") for line in fish.readlines()]
with open("farming/meta/plants.json", "r") as plants:
    plants_dict = json.load(plants)
    
def update() -> None:
    with(open("inventories/meta/TEMPLATE.json")) as file:
            template:dict = json.load(file)
    for path in os.listdir("inventories/meta"):
        if not path.endswith(".json"):
            continue
        if "TEMPLATE" in path:
            continue
        with open(f"inventories/meta/{path}") as file:
            data = json.load(file)
        for key in template.keys():
            if key in data.keys():
                continue
            data[key] = template[key]
        for key in template.get("meta").keys():
            if key in data.get("meta").keys():
                continue
            data["meta"][key] = template["meta"][key]
        with open(f"inventories/meta/{path}", "w") as file:
            json.dump(data, file)
update()
    
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

def read_one_meta(user_id:int, attr:str) -> any:
    data = get_data(user_id)
    return data.get("meta").get(attr, None)

# Fish -----------------------------------------------

def get_total_fish_buffs(user_id:int) -> int:
    meta = get_meta(user_id)
    return (meta.get("rod_level") + meta.get("bait_level"))

def get_fish_time_reduction(user_id:int) -> int:
    meta = get_meta(user_id)
    return max(0,(meta.get("rod_time") + meta.get("bait_level")))

def get_fish_embed(user_id:int, username:str, user:discord.User) -> list[dict]:
    data = get_data(user_id)
    meta = get_meta(user_id)
    embed = discord.Embed(title=f"{username}'s Pier", color=0x6699ff)
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="Fish in tank:", value=len(data.get("fish")), inline=False)
    embed.add_field(name="Money:", value=meta.get("money"), inline=False)
    embed.add_field(name="Rod Level:", value=meta.get("rod_level"), inline=False)
    embed.add_field(name="Rod Speed:", value=meta.get("rod_time"), inline=False)
    return [{"type":"message","message":"","embed":embed}]


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

def remove_fish_from_inventory(user_id:int, idx:int) -> bool:
    try:
        user_path = get_path(user_id)
        data = get_data(user_id)
        with open(user_path, "w") as inv:
            data["fish"].pop(idx)
            json.dump(data, inv)
        return True
    except Exception as e:
        return False

def read_range_fish_from_inventory(user_id:int, username:str, user:discord.User, start_index:int, step:int) -> list[dict]:
    data = get_data(user_id)
    inventory = []
    for line in data["fish"][start_index:start_index+step]:
        idx = data["fish"].index(line)+1
        is_treasure = line not in fish_list
        fish = f"*{line}*" if is_treasure else line
        inventory.append(f"{idx}. {fish}")
    response = str(inventory).replace('"', "'").replace("', '", "\n").strip("[']")
    embed = discord.Embed(title=f"{username}'s Tank", description=f"Section {int(start_index/20)+1} ({start_index+1} - {start_index + step})", color=0x6699ff)
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="Contents", value=response)
    return [{"type":"message","message":"","embed":embed}]

def read_one_fish_from_inventory(user_id:int, idx:int) -> str:
    data = get_data(user_id)
    return data["fish"][idx]

# Farming -----------------------------------------------

def read_farm(user_id, idx) -> dict:
    data = get_data(user_id)
    return data.get("farm", None)[idx]

def get_seeds(user_id) -> dict | None:
    data = get_meta(user_id)
    return data.get("seeds", None)

def get_seeds_formatted(user_id) -> str:
    seeds = get_seeds(user_id)
    if seeds is None:
        return "No seeds yet. Buy some from the shop!"
    out = list(f"{plants_dict.get(key, {'name':"Unknown"}).get('name', 'Unnamed')} ({key}): {seeds[key]}" for key in seeds.keys())
    out = out.__str__().replace(r"', '", "\n").replace("-1", "∞").strip(r"[']")
    return out

def get_farm_embed(user_id:int, username:str, user:discord.User) -> list[dict]:
    meta = get_meta(user_id)
    embed = discord.Embed(title=f"{username}'s Shed", color=0x66ff66)
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="Farms owned:", value=meta.get("farm_plots", None), inline=False)
    embed.add_field(name="Money:", value=meta.get("money", 0), inline=False)
    embed.add_field(name="Seeds owned:", value=get_seeds_formatted(user_id), inline=False)
    return [{"type":"message","message":"","embed":embed}]

def put_farm(user_id:int, idx:int, farm:dict) -> bool:
    try:
        data = get_data(user_id)
        with open(get_path(user_id), "w") as file:
            data["farm"][idx] = farm
            json.dump(data,file)
        return True
    except Exception as e:
        return False