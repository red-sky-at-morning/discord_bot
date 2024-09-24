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
    if fish in treasure_list:
        current_price*= meta.get("treasure_modifier",1.5)
    return [{"type":"message","message":f"I'll buy your {fish} for {current_price}, <@{user_id}>!"}, {"type":"react", "react":"✅❎"}, {"type":"store", "name":"open_sale", "id":user_id, "extra": {"price":current_price}}]

def is_sale(user_id, message_id) -> bool:
    meta = inventories.get_meta(user_id)
    if message_id == meta.get("open_sale").get("id"):
        return True
    return False

def is_shop(user_id, message_id) -> bool:
    meta = inventories.get_meta(user_id)
    if message_id == meta.get("open_shop").get("id"):
        return True
    return False

def complete_sale(user_id, message_id, succeed:bool) -> list[dict]:
    meta = inventories.get_meta(user_id)
    if not succeed:
        inventories.add_meta(user_id, "open_sale", {})
        return [{"type":"message","message":f"Don't waste my time, <@{user_id}>"}]
    
    return None

def read_shop(user_id:int, shop:str) -> dict | None:
    shop = data.get(shop, None)
    if not shop:
        return None
    return shop

def get_shop_message(user_id:int, shop:str) -> list[dict]:
    return None