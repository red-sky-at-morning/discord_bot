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
        current_price*= 2
    return [{"type":"message","message":f"I'll buy your {fish} for {current_price}, <@{user_id}>!"}, {"type":"react", "react":"✅❎"}, {"type":"store", "name":"open_sale", "id":user_id, "extra": {"price":current_price, "index":idx}}]

def is_sale(user_id, message_id) -> bool:
    meta = inventories.get_meta(user_id)
    if message_id == meta.get("open_sales").get("id"):
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
    idx = meta.get("open_sale").get("index")
    price = meta.get("open_sale").get("price")
    money = meta.get("money") + price
    inventories.add_meta(user_id, "open_sale", {})
    inventories.add_meta(user_id, "money", money)
    inventories.remove_from_inventory(user_id, idx)
    return [{"type":"message","message":f"Pleasure doing business with you, <@{user_id}>"}]

def calc_price(user_id:int, price:dict) -> int:
    match price.get("type"):
        case "static":
            return price.get("price")
        case "dynamic":
            return -1 # TODO implement

def read_shop(user_id:int, shop:str) -> discord.Embed | None:
    shop_data:dict = data.get(shop, None)
    if not shop:
        return None
    restricted_users = shop_data.get("restrict_users", [])
    if (user_id in restricted_users) != shop_data.get("whitelist",False):
        return None
    color = shop_data.get("color")
    if color != "random":
        color = discord.Color.from_str(f"#{color}") 
    else:
        color = discord.Color.random()
    embed = discord.Embed(color=color, title=shop_data.get("title"))
    embed.description = shop_data.get("desc")
    embed.set_thumbnail(url=shop_data.get("url", None))
    for item in shop_data.get("items"):
        embed.add_field(name=item.get("name"),value=f"{item.get('desc')}\nPrice: ${calc_price(user_id, item.get('price'))}")
    return embed

def get_shop_message(user_id:int, shop:str) -> list[dict]:
    return None