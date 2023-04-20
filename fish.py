import random
import json
import discord.embeds
# List of minecraft potion effects for random potions
effects = ('speed','slowness','haste','mining fatigue','strength','instant health','instant damage','jump boost','nausea','regeneration','resistance','fire resistance','water breathing','invisibility','blindness','night vision','hunger','weakness','poison',
           'wither','health boost','absorption','saturation','glowing','levitation','luck','bad luck','slow falling','conduit power','dolphin\'s grace','bad omen','hero of the village','darkness')
banned_users = (771802284929056769, 409071383004446720, 762031037852418058)

# Load list of fish for random fish
with open('meta/list_of_fish.txt','r') as fish:
    fish_list = []
    for line in fish.readlines():
        fish_list.append(line.strip("\n"))

def start_fish(user_id):
    # Check if the user is banned from fishing
    if user_id in banned_users:
        return (f"<@{user_id}> does not have a fishing liscense!")
    
    # Get the rod and buffs of the user
    with open("meta/user_buffs.json","r") as buffs:
        data = json.load(buffs)
        print(data)
    
    for user in data:
        print(user)
        # Get what item in data actually corresponds to the user
        if user_id == user.get("id", 0):
            print("passed")
            user_rod = user["rod"]/10
            bait_power = user["bait_power"]/10
            bait_duration = user["bait_duration"]
            break
    else:
        # If they don't have an entry, make one
        user_rod = 0
        bait_power = 0
        bait_duration = 0
        money = 0
        user = {"id":user_id,"rod":user_rod,"bait_duration":bait_duration,"bait_power":bait_power,"money":money}
        print("creating new user: ", user)
        data.append(user)
    
    # Roll the random number to determine what you get
    roll = random.random()
    print(roll)
    roll += user_rod + bait_power
    print(roll)
    
    # Update bait duration and power
    if bait_duration > 0:
        bait_duration -= 1
    if bait_duration <= 0:
        bait_power = 0
    
    # Make a filename using the userid
    file_name = "inv_" + str(user_id)
    
    to_return = ""
    # Get a potion
    if roll >= .95:
        roll2 = random.randint(0,32)
        effect = effects[roll2]
        # Add potion to the inventory file
        with open(f"inventories/{file_name}", 'a') as inv:
            inv.write(f"\nPotion of {effect}")
        # Return potion to print
        to_return = f"<@{user_id}> got a potion of {effect}"
    
    # Get a fish
    elif (roll > 0.2):
         # Roll which fish you get
        roll2 = random.randint(1,474)
        fish = fish_list[roll2]
        # Add fish to inventory
        with open(f"inventories/{file_name}", 'a') as inv:
            inv.write(f"\n{fish}")
        # Return fish to print
        to_return = f"<@{user_id}> caught a {fish}"
     
    # Get nothing
    else:
       to_return = "Not even a nibble..."
   
    print(data)
    for user in data:
        if user_id == user.get("id"):
            # Update the user's data
            print("passed")
            user["bait_power"] = bait_power*10
            user["bait_duration"] = bait_duration
            # Write updated data to the file
            with open("meta/user_buffs.json","w") as buffs:
                json.dump(data, buffs)
            break
    
    return to_return

def get_inv(user_id, page_raw):
    # Get the file id
    file_name = "inv_" + str(user_id)
    # Turn page_raw into page to list the next 20 items from that number
    page = (page_raw - 1) * 20
    # List lines in the file and add them to the list
    inv_list = []
    
    with open(f"inventories/{file_name}", 'r') as inv:
        for line in inv.readlines():
            inv_list.append(line.strip('\n'))
    # Return the 20 fish on that page with formatting
    for fish in inv_list:
        inv_list[inv_list.index(fish)] = f"{inv_list.index(fish)+1}. {fish}"
    f_inv = (f"{inv_list[page:page+20]}").strip("[']").replace('\'','').replace('"','').replace(", ", "\n")
    return (f_inv)

def sell(user_id, index):
    # Get the file id
    file_name = "inv_" + str(user_id)
    # Generate a random price between 5 and 25
    price = random.randint(0,20) + 5
    
    # Read their inventory, stop at the index provided
    with open(f"inventories/{file_name}", 'r') as inv:
        i=0
        fish=""
        for line in inv.readlines():
            i+=1
            if i == index:
                fish=line.strip('\n')
                break
        else:
            # If they provided an index that's not in their inventory, return an error
            return([{"type":"message","message":"Hey! What are you trying to pull?"}])
    return ([{"type":"message","message":f"I\'ll buy your {fish} for {price}. Deal?","store_message":True, "metadata":{"user_id":user_id,"type":"sale","index":index,"price":price}}, \
        {"type":"react", "react":"✅", "self":True}, {"type":"react", "react":"❎", "self":True}])

def shop(user_id):
    # Get shop data from meta/shop_data.json
    with open("meta/shop_data.json") as shop, open("meta/user_buffs.json") as buffs:
        data = json.load(shop)
        buffs = json.load(buffs)
        for users in buffs:
            if users.get("id", 0) == user_id:
                user = users
    
    # Create an embed with relevant information
    embed=discord.Embed(title="Shop", description="Everything's for sale.", color=0x58abdf)
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/966488795065229342/1098653939240538203/IMG_8414.png?width=612&height=701")
    for item in data:
        name = item.get("name", "temp")
        desc = item.get("desc", "temp")
        price = item.get("price", 0)
        id = item.get("id", -1)
        # Add a variable price for the fishing rod
        # Interject the price into anywhere it would show up because I couldn't think of a better way to do it
        if name == "Fishing Rod Upgrade":
            price = (user.get("rod")+1)*100
        embed.add_field(name=f"{id}. {name}", value=f"${price}\n{desc}", inline=False)
    return embed

def buy(index, user, shop_data, buff, to_increase, increase_by):
    # Get the price from the provided shop
    price = shop_data[index].get("price")
    if user.get("money") < price:
        # If the user can't pay, return
        return("Hey! You can't pay for that!")
    else:
        # Otherwise decrease their money and give them whatever they bought
        # Add a variable price for the fishing rod
        if index == 0:
            price = (user.get("rod")+1)*100
        user["money"] -= price
        if to_increase == "rod":
            user["rod"] += increase_by
        elif to_increase == "bait":
            user["bait_power"] += increase_by
            user["bait_duration"] += 5
        if to_increase is user["bait_power"]:
            user["bait_duration"] += 5
        with open("meta/user_buffs.json", "w") as buffs:
            json.dump(buff, buffs)
    return ("Thanks for your buisness.")