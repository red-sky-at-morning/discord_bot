import json
import discord

from inventories import inventories

with open("shop/meta/shop.json", "r") as shop:
    data:dict = json.load(shop)
with open("fishing/meta/treasure.txt", "r") as treasure:
    treasure_list = treasure.readlines()

def sell_fish(user_id:int, idx:int) -> list[dict]:
    fish = inventories.read_one_from_inventory(user_id, idx)
    meta = data.get("meta", None)
    if meta is None:
        raise FileNotFoundError("Could not read shop metadata")
    current_price = meta.get("fish_price", 0)
    if fish in treasure:
        current_price*= meta.get("treasure_modifier",-1)
    return None

def read_shop(user_id:int, shop:str) -> dict | None:
    shop = data.get(shop, None)
    if not shop:
        return None
    return shop

def get_shop_message(user_id:int, shop:str) -> list[dict]:
    return None