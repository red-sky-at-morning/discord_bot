import random
import discord
import json
import time

from shop import shop
from inventories import inventories

with open("farming/meta/plants.json", "r") as plants_f:
    plants:dict = json.load(plants_f)

def handle(command:list[str], user_id:int, username, message:discord.Message) -> list[dict]:
    print(command)
    return check_farm(user_id, username, 0)

levels = ("🟫","🌱","🌿","🌾","🌻","🌧️")
def square(size:int, progress:int) -> str:
    if (progress not in range(0,5)):
        raise IndexError(f"Could not find character to use for progress level {progress}")
    out:str = ""
    for i in range(size):
        for j in range(size):
            if (i==int(size/2) and i==j):
                out += levels[5]
            else:
                out += levels[progress]
        out += "\n"
    return out

# [0,4]
def calc_progress(plant:str, planted_tick:int, watered:bool) -> int:
    if plant is None: return 0
    time_elapsed = time.time() - planted_tick
    tick = plants.get(plant).get("tick")
    progress = int(time_elapsed/tick)
    progress = max(min(0, progress), 4)
    return progress

def check_farm(user_id:int, username:str, idx:int) -> list[dict]:
    if (inventories.read_one_meta(user_id, "farm_plots") == 0):
        return [{"type":"message", "message":"You don't own any farm plots yet. Buy one from the shop first."}]

    farm = inventories.read_farm(user_id, idx)
    size = farm.get("size")
    progress = calc_progress(farm.get("plant"), farm.get("planted_tick"), farm.get("watered"))

    plant = plants.get(farm.get("plant"))
    name:str = ""
    if plant is not None:
        name = plant.get("name")        

    embed = discord.Embed(title=f"{username}'s Farms", color=0x66ff99)
    plant_str = f"Growing {name}\nProgress: {progress+1}{" (Ready for harvest!)" if progress == 4 else ""}{"💧" if farm.get("watered") else ""}\n{square(size, progress)}"
    unplanted_str = "Not growing anything yet. Use >farm plant to plant something!"
    embed.add_field(name="Farm 1",value=plant_str if plant is not None else unplanted_str, inline=False)
    return [{"type":"message", "message":"", "embed":embed}]