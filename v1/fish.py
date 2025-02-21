import random
import json
import discord.embeds
# List of minecraft potion effects for random potions
effects = ()
banned_users = (409071383004446720, 762031037852418058, 706256700813869096, 1131763352604000317, 629075346473353256, 714653407021105202)

# Load list of fish for random fish
with open('meta/list_of_fish.txt','r') as fish:
    fish_list = []
    for line in fish.readlines():
        fish_list.append(line.strip("\n"))

# Change the list of potions out for an actual loot table
with open('meta/fishing_treasure.txt', 'r') as treasure:
    treasure_list = []
    for line in treasure.readlines():
        treasure_list.append(line.strip("\n"))

def start_fish(user_id, username):
    # Check if the user is banned from fishing
    if user_id in banned_users:
        return ([{"type":"message","message":f"<@{user_id}> does not have a fishing liscense!"}])
    
    # Get the rod and buffs of the user
    with open("meta/user_buffs.json","r") as buffs:
        data = json.load(buffs)
    
    for user in data:
        # Get what item in data actually corresponds to the user
        # For each 3 rod levels above 5, the user gets one cast.
        if user_id != user.get("id", 0):
            continue
        print("passed")
        user_rod = user["rod"]
        bait_power = user["bait_power"]/10
        bait_duration = user["bait_duration"]
        break
    else:
        # If they don't have an entry, make one
        user_rod = 0
        bait_power = 0
        bait_duration = 0
        user = {"id":user_id,"rod":user_rod,"bait_duration":bait_duration,"bait_power":bait_power,"money":0, "bite":0}
        print("creating new user: ", user)
        data.append(user)
    if user_rod <= 5:
        user_casts = 1
        rod_power = user_rod / 20
    else:
        user_casts = int(user_rod-4)
        rod_power = user_rod / 20
    
    # Change the return system to allow notifications when bait runs out
    to_return = [{"type": "message", "message": "The waters are stirring..."}, {"type": "wait", "time": 2}]
    
    # Make a filename using the userid
    file_name = "inv_" + str(user_id)
    
    # Roll the random number to determine what you get
    for _ in range(user_casts):
        roll = random.random()
        print(roll)
        roll += bait_power + rod_power
        print(roll)

        if roll >= 2:
            to_return.append({"type":"message","message":f"Critical Cast!"})
            user["money"] += 25

        # Get treasure_list
        if roll >= 0.99:
            roll2 = random.randint(0,len(treasure_list) - 1)
            treasure = treasure_list[roll2]
            if treasure == "{{USERNAME}}":
                treasure = username
            # Add potion to the inventory file
            with open(f"inventories/{file_name}", 'a') as inv:
                inv.write(f"\n{treasure}")
            # Return potion to print
            to_return.append({"type":"message","message":f"<@{user_id}> got a {treasure}!"})

        # Get a fish
        elif (roll > 0.2):
            # Roll which fish you get
            roll2 = random.randint(0,len(fish_list) - 1)
            fish = fish_list[roll2]
            # Add fish to inventory
            with open(f"inventories/{file_name}", 'a') as inv:
                inv.write(f"\n{fish}")
            # Return fish to print
            to_return.append({"type":"message","message":f"<@{user_id}> got a {fish}!"})
            
        # Get nothing
        else:
            to_return.append({"type":"message","message":f"Not even a nibble..."})
    
    # Update bait duration and power
    if bait_duration > 0:
        bait_duration -= 1
        if bait_duration == 0:
            bait_power = 0
            to_return.append({"type":"message","message":f"Your bait ran out."})
    
    for user in data:
        if user_id != user.get("id"):
            continue
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
    page = (page_raw - 1) * 10
    # List lines in the file and add them to the list
    inv_list = []
    
    with open(f"inventories/{file_name}", 'r') as inv:
        for line in inv.readlines():
            if (line.strip('\n') != "") & (line.strip('\n') != " "):
                inv_list.append(line.strip('\n'))
    with open(f"inventories/{file_name}", 'w') as inv:
        for line in inv_list:
            inv.write(f"{line}\n")
    # Return the 20 fish on that page with formatting
    for fish in inv_list:
        inv_list[inv_list.index(fish)] = f"{inv_list.index(fish)+1}. {fish}"
    f_inv = (f"{inv_list[page:page+10]}").strip("[']").replace('\'','').replace('"','').replace(", ", "\n")
    return (f_inv)

def sell(user_id, index):
    # Get the file id
    file_name = "inv_" + str(user_id)
    # Generate a random price between 5 and 25
    price = random.randint(0,90) + 10
    
    # Read their inventory, stop at the index provided
    with open(f"inventories/{file_name}", 'r') as inv:
        # If they provided an index that's not in their inventory, return an error
        user_inv = inv.readlines()
        if (index > len(user_inv) or index < 1):
            return([{"type":"message","message":"Hey! What are you trying to pull?"}])
        fish=user_inv[index-1]
        if fish == "":
            return([{"type":"message","message":"Hey! What are you trying to pull?"}])
        if fish in treasure_list:
            if fish.lower()=="midnight__sun": price+=450 
            price += 50
    return ([{"type":"message","message":f"I\'ll buy your {fish} for {price}, <@{user_id}>. Deal?","store_message":True, "metadata":{"user_id":user_id,"type":"sale","index":index,"price":price}}, \
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

def buy(index, user, user_id, shop_data, buff, to_increase, increase_by, **kwargs):
    # Get the price from the provided shop
    price = shop_data[index].get("price")
    name = shop_data[index].get("name")
    FAIL = f"Sorry, I can't sell you that {name}, <@{user_id}>."
    if (user.get("money") < price) | (user.get("money") < 0):
        # If the user can't pay, return
        return(f"Hey! You can't pay for that {name}, <@{user_id}>!")
    else:
        # Otherwise decrease their money and give them whatever they bought
        # Add a variable price for the fishing rod
        if name == "Fishing Rod Upgrade":
            price = (user.get("rod")+1)*100
        user["money"] -= price
        match to_increase:
            case "rod":
                if user.get("rod") >= 10:
                    return(FAIL)
                user["rod"] += increase_by
            case "bait":
                if user.get("bait_duration") > 10:
                    return(FAIL)
                user["bait_power"] += increase_by
                user["bait_duration"] += kwargs.get("duration")
            case "bite":
                if user.get("bite") > 0:
                    return(FAIL)
                user["bite"] += 1
        with open("meta/user_buffs.json", "w") as buffs:
            json.dump(buff, buffs)
    return (f"Thanks for buying {name}, <@{user_id}>")