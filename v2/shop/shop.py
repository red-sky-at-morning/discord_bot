import json
import discord
from shop import actions

from inventories import inventories

with open("shop/meta/shop.json", "r") as shop:
    data:dict = json.load(shop)

with open("fishing/meta/fish.txt", "r") as fish:
    fish_list = [line.strip("\n") for line in fish.readlines()]

number_reacts:tuple = ("1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","0️⃣","⬅️","➡️")
error_message:list[dict] = [{"type":"message","message":"Hey! What are you trying to pull?"}]

def sell_fish(user_id:int, idx:int) -> list[dict]:
    fish = inventories.read_one_from_inventory(user_id, idx)
    meta = data.get("meta", None)
    if meta is None:
        raise FileNotFoundError("Could not read shop metadata")
    current_price = meta.get("fish_price", 0)
    if fish.strip("\n") not in fish_list:
        current_price*= meta.get("treasure_modifier")
    return [{"type":"message","message":f"I'll buy your {fish} for {current_price}, <@{user_id}>!"}, {"type":"react", "react":"✅❎"}, {"type":"store", "name":"open_sales", "id":user_id, "extra": {"price":current_price, "index":idx}}]

def is_sale(user_id, message_id) -> bool:
    meta = inventories.get_meta(user_id)
    if message_id == meta.get("open_sales").get("id"):
        return True
    return False

def is_shop(user_id, message_id) -> bool:
    meta = inventories.get_meta(user_id)
    if message_id == meta.get("open_shops").get("id"):
        return True
    return False

def complete_sale(user_id, message_id, succeed:bool) -> list[dict]:
    meta = inventories.get_meta(user_id)
    inventories.add_meta(user_id, "open_sales", {})
    if not succeed:
        return [{"type":"message","message":f"Don't waste my time, <@{user_id}>"}]
    idx = meta.get("open_sales").get("index")
    price = meta.get("open_sales").get("price")
    money = meta.get("money") + price
    inventories.add_meta(user_id, "money", money)
    inventories.remove_from_inventory(user_id, idx)
    return [{"type":"message","message":f"Pleasure doing business with you, <@{user_id}>"}]

def calc_price(user_id:int, price:dict) -> int:
    match price.get("type"):
        case "static":
            return price.get("price")
        case "dynamic":
            stat = price.get("attribute")
            user_val = inventories.read_one_meta(user_id, stat)
            try:
                user_val *= 1
            except ValueError:
                raise ValueError("Found unexpected non-integer value in attribute")
            return price.get("mult") * user_val
        
def read_shop(shop:str) -> dict | None:
    shop_data:dict = data.get(shop, None)
    if not shop_data:
        return None
    return shop_data

def validate(emoji:str) -> bool:
    return emoji in number_reacts

def get_shop_embed(user_id:int, shop:str) -> discord.Embed | None:
    shop_data:dict = read_shop(shop)
    if not shop_data:
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
    embed.set_footer(text="Shops are unique to each user.\nIf you want to buy something, use >shop.")
    for item in shop_data.get("items"):
        embed.add_field(name=item.get("name"),value=f"{item.get('desc')}\nPrice: ${calc_price(user_id, item.get('price'))}",inline=False)
    return embed

def get_shop_message(user_id:int, shop:str) -> list[dict]:
    shop_data:dict = read_shop(shop)
    if not shop_data:
        return error_message
    embed = get_shop_embed(user_id, shop)
    nums = number_reacts[0:len(shop_data.get("items"))]
    return [{"type":"message","message":"","embed":embed},{"type":"react","react":nums},{"type":"store", "name":"open_shops", "id":user_id, "extra": {"type":shop}}]

def sell_item(user_id:int, message_id:int, react:str) -> list[dict]:
    if not is_shop(user_id, message_id):
        return error_message
    meta = inventories.get_meta(user_id)
    user_shop:dict = meta.get("open_shops")
    user_money = meta.get("money")

    item_idx = number_reacts.index(react)
    shop_type = read_shop(user_shop.get("type"))

    shop_item = shop_type.get("items")[item_idx]

    # Subtract the user's money
    item_price = calc_price(user_id, shop_item.get("price"))
    if(user_money < item_price):
        return error_message
    user_money -= item_price
    inventories.add_meta(user_id, "money", user_money)
    
    # Perform the action
    response = [{"type":"message","message":f"Thanks for buying {shop_item.get("name")} for ${item_price}, <@{user_id}>!"}]
    response += (actions.perform(user_id, shop_item.get("action")))

    return response


def read_item(shop:str, index:int) -> dict:
    pass