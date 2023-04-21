import fish
import song
import random
import json
import discord
import event as ev

testing_mode = True
banned_users = (694231818957750280, 0)

def handle_response(message, user_id: int, server, event_type, **kwargs):
    
    # Get the previous kwargs out of kwargs
    args = kwargs.get("args")
    
    # Check the event type
    if (event_type == "message"):
        
        #Format the message
        message_raw = message
        p_message = message.lower()
        server = str(server)

        # Guard Statements
        # Change the server name from "The Order" to change what server your testing mode works in
        if testing_mode & (server != "The Order"):
            return

        if user_id in banned_users:
            return

        # Match statement to check for no-argument commands
        match p_message:
            case '>test':
                return ([{"type": "message", "message": "Hello World!"}])

            case '>test2':
                return ([{"type": "message", "message": "Starting..."}, {"type": "wait", "time": 5}, {"type": "message", "message": "Finished!"}])

            case '>test3':
                return ([{"type": "message", "message": "Okay!"}, {"type": "react", "react": "👍"}])

            case '>test4':
                return ([{"type": "message", "message": "Timeout for 5 secs"}, {"type": "timeout", "time": 5}])
            
            case '>test5':
                return ([{"type":"reply", "message":"Hello World!", "id":kwargs.get("messageable")}])
            case '>test6':
                embedVar = discord.Embed(title="Title", description="Desc", color=0x00ff00)
                embedVar.add_field(name="Field1", value="hi", inline=False)
                embedVar.add_field(name="Field2", value="hi2", inline=False)
                return([{"type":"message", "message":"", "embed":embedVar}])
            
            case '>delshops':
                # This is my user ID. You might want to change this.
                if user_id != 630837649963483179:
                    return
                with open("meta/shop_ids.json", "r") as shop:
                    data = json.load(shop)
                for item in data:
                    if item.get("type") == "shop":
                        del data[data.index(item)]
                with open("meta/shop_ids.json", "w") as shop:
                    json.dump(data, shop)
                return([{"type":"message","message":"Shops Removed"}])

            # Help command last updated 4.20.2023 M/DD/YY - Added the new fish subcommands
            case '>help':
                return ([{"type": "message", "message": "Commands:"},
                            {"type":"message","message":">fish: Try and catch a fish."},
                            {"type":"message","message":">fish inv [page]: Check what fish you have in storage."},
                            {"type":"message","message":">fish sell [index]: Sell a fish from your inventory."},
                            {"type":"message","message":">fish shop: Buy upgrades and buffs."},
                            {"type":"message","message":">fish stats: Check your stats and upgrades."},
                            {"type":"message","message":">flip: Flip a coin"},
                            {"type":"message","message":">roll [number]d[size]: Roll some dice!\
 Use kh[#] for keep highest, dl[#] for drop lowest, kl[#] for keep lowest, and dh[#] for keep lowest."},
                            {"type":"message","message":">role \"[name]\" [hex code]:\
 Create a role with the provided name and color. Disabled by default."},
                            {"type":"message","message":">event \"[name]\" \"[location]\" <start time> <end time>:\
 Creates an event with the provided name, location, start time, and end time."}])

            case '>flip':
                roll = random.random()
                if roll <= .5:
                    return ([{"type": "message", "message": "Heads"}])
                else:
                    return ([{"type": "message", "message": "Tails"}])
            
            case "hi eclipsebot you look so cute today":
                return([{"type":"react","react":"💖"}, {"type":"message","message":"thanks, but i'm aroace"}])

        # If-else list for commands with arguements and other messages
        if p_message[:5] == ">fish":
            # Check what fish command the user is using
            if "inv" in p_message:
                # String manipulation, then pass to fish.py
                i_message = p_message[p_message.index("inv")+3:]
                i_message.strip()
                try:
                    page = int(i_message)
                except ValueError:
                    return ([{"type": "message", "message": f"\"{i_message}\" is not a valid page number! Try >fish inv 1"}])
                return ([{"type": "message", "message": f"{fish.get_inv(user_id, page)}"}])
            elif "sell" in p_message:
                # String manipulation, then pass to fish.py
                s_message = p_message[p_message.index("sell")+4:]
                s_message.strip()
                try:
                    index = int(s_message)
                except ValueError:
                    return ([{"type": "message", "message": f"\"{s_message}\" is not a valid inventory index! Try >fish sell 1"}])
                return(fish.sell(user_id, index))
            elif "shop" in p_message:
                # Pass to fish.py
                shop = fish.shop(user_id)
                return ([{"type":"message", "message":"", "embed":shop, "store_message":True, "metadata":{"user_id":user_id, "type":"shop"}}, {"type":"react", "react":"1️⃣", "self":"true"}, \
                    {"type":"react","react":"2️⃣", "self":"true"}, {"type":"react", "react":"3️⃣", "self":"true"}, \
                        {"type":"react", "react":"4️⃣", "self":"true"}, {"type":"react", "react":"5️⃣", "self":"true"}])
            elif "stats" in p_message:
                # Get the user's inventory, create an embed, then send it
                with open (f"inventories/inv_{user_id}", "r") as inv, open("meta/user_buffs.json", "r") as buffs:
                    data = json.load(buffs)
                    for user in data:
                        if user.get("id") == user_id:
                            break
                    username = args.get("username")
                    avatar = args.get("user").avatar.url
                    rod = user.get("rod")
                    fish_count = len(inv.readlines())
                    money = user.get("money")
                
                embedVar = discord.Embed(title=f"**{username}**", color=0x58abdf)
                embedVar.set_thumbnail(url=avatar)
                embedVar.add_field(name="Fish in storage:", value=fish_count, inline=False)
                embedVar.add_field(name="Rod Level:", value=rod, inline=False)
                embedVar.add_field(name="Money:", value=money, inline=False)
                
                if user.get("bait_duration") > 0:
                    bait_duration = user.get("bait_duration")
                    bait_power = user.get("bait_power")
                    embedVar.add_field(name="Bait:", value=f"Casts Left: {bait_duration}\nBonus: {bait_power}")
                
                return ([{"type":"message","message":"","embed":embedVar}])
            else:
                # Default command, pass to fish.py
                return ([{"type": "message", "message": "The waters are stirring..."}, {"type": "wait", "time": 2}, {"type": "message", "message": f"{fish.start_fish(user_id)}"}])
            
            
        elif ">roll" in p_message:
            # String manipulation
            r_message = p_message[5:]
            r_message.strip()
            d_message = r_message.split("d")
            khn = ""
            # Get the number of dice to roll
            try:
                die_num = int(d_message[0])
            except ValueError:
                return ([{"type": "message", "message": f"\"{d_message[0]}\" is not a number! Try >roll 3d20"}])
            try:
                die_size = int(d_message[1])
            except ValueError:
                # Check if it failed because the user passed more arguments
                # There's probably a better way to do this
                if ("k" in d_message[1]):
                    idx = d_message[1].find("k")
                    khn = d_message[1][idx:]
                    die_size = int(d_message[1][:idx])
                elif ("d" in d_message[1]):
                    idx = d_message[1].find("d")
                    khn = d_message[1][idx:]
                    die_size = int(d_message[1][:idx])
                else:
                    # Return an error
                    return ([{"type": "message", "message": f"\"{d_message[1]}\" is not a number! Try >roll 3d20"}])
            roll_list = []
            total = 0
            # Roll the dice and add them to a total and a list
            for i in range(die_num):
                r = random.randint(1, die_size)
                roll_list.append(r)
            if khn != "":
                roll_list.sort()
                try:
                    num = int(khn[2:])
                except ValueError:
                    return ([{"type": "message", "message": f"\"{khn}\" is not a number! Try >roll 3d20kh1"}])
                if "kh" in khn:
                    roll_list = roll_list[-num:]
                    khn = f"keeping highest {num}, "
                if "dl" in khn:
                    roll_list = roll_list[num:]
                    khn = f"dropping lowest {num}, "
                if "dh" in khn:
                    roll_list = roll_list[:-num]
                    khn = f"dropping highest {num}, "
                if "kl" in khn:
                    roll_list = roll_list[:num]
                    khn = f"keeping lowest {num}, "
            print (roll_list)
            for i in range(len(roll_list)):
                total += roll_list[i]
                # Highlight high and low rolls
                if ((roll_list[i] == die_size) or (roll_list[i] == 1)):
                    roll_list[i] = f"**{roll_list[i]}**"
                else:
                    roll_list[i] = str(roll_list[i])
            roll_list = f"{roll_list}".replace("'", "").replace("[","(").replace("]",")")
            return ([{"type": "message", "message": f"Rolled {die_num}d{die_size}, {khn}and got {total} {roll_list}"}])

        elif ">song" in p_message:
            # String manipulation
            s_message = message_raw[6:]
            s_message = s_message.split(" ")
            print(s_message)
            playlist = s_message[1]
            match s_message[0]:
                # Pass to song.py
                case "random":
                    song_f = (song.playlist_tracks(playlist, "RANDOM"))
                    return ([{"type": "message", "message": f"{song_f}"}])
                case "list":
                    song_f = (song.playlist_tracks(playlist, "LIST"))
                    return ([{"type": "message", "message": f"{song_f}"}])
                case _:
                    # Add error handling
                    return ([{"type": "message", "message": "Not a valid command for >song! Try >song random or >song list instead!"}])

        elif ">role" in p_message:
            # Get allowed servers (You probably want to change these)
            if ((server == "The Order") | (server == "swashbucklers and stuff") | (user_id == 630837649963483179)):
                
                # String manipulation
                r_message = message_raw[6:]
                r_message = r_message.split("\"")
                print(r_message)
                
                # Add default values
                name = "New Role"
                if r_message[1]:
                    name = r_message[1]
                color = "FFFFFF"
                if r_message[2]:
                    r_message[2] = r_message[2].strip("#")
                    color = f"#{r_message[2]}"
                
                return ([{"type": "role", "name": name, "color": color}, {"type": "message", "message": f"Gave you a role called \"{name}\""}])
            else:
                return ([{"type": "wait", "time": 3}, {"type": "react", "react": "✈️"}, {"type": "react", "react": "🏢"}])

        elif ">event" in p_message:
            e_message = message[7:]
            
            # Pass to event.py for string manipulation and other data, returns a dictionary
            event = ev.get_event_data(e_message)
            
            # Get variables from dictionary
            name = event["name"]
            location = event["location"]
            start = event["start"]
            end = event["end"]
            
            return ([{"type": "event", "name": event["name"], "location": event["location"], "start": event["start"], "end": event["end"]},
                    {"type": "message", "message": f"Created an event called {name}, set in {location}, \
that starts at {start} and ends at {end}"}])

        # Random other commands, you can delete these
        elif ">bite" in p_message:
            b_message = p_message[6:]
            if (user_id == "630837649963483179" or user_id == "390282832766959617") or b_message == "<@607316432807788549>":
                return ([{"type": "message", "message": f"<@{user_id}> bit {b_message}!"}, {"type": "wait", "time": 3}, {"type": "react", "react": "✈️"}, {"type": "react", "react": "🏢"}])
            else:
                return ([{"type": "message", "message": "Biting is mean!"}, {"type": "wait", "time": 3}, {"type": "react", "react": "✈️"}, {"type": "react", "react": "🏢"}])

        elif "ur mom" in p_message:
            return ([{"type": "message", "message": "ur dad"}])

        elif "ur dad" in p_message:
            return ([{"type": "message", "message": "ur mom"}])

        elif "balls" in p_message:
            return ([{"type": "message", "message": "no."}])

        elif ("riot" in p_message) or ("r1ot" in p_message) or ("ri0t" in p_message) or ("r10t" in p_message):
            return ([{"type": "message", "message": "no rioting"}, {"type": "wait", "time": 3}, {"type": "react", "react": "✈️"}, {"type": "react", "react": "🏢"}])

        elif ("etsy.com/listing" in p_message) and (("spell" in p_message) or ("pact" in p_message) or ("magic" in p_message)):
            return ([{"type": "react", "react": "⬇️"}])

        elif (">die" in p_message):
            return ([{"type": "message", "message": "you first"}])
        
        elif (args.get("mentioned")):
            responses = ("You called?", "haiiiiii", "OwO", "UwU", "Fuck off", "Bitch", "I'M HERE", ":3")
            response = responses[random.randint(0,len(responses)-1)]
            return ([{"type":"message","message":response}])

        else:
            num = random.random()
            if num < 0.001:
                return ([{"type": "wait", "time": 20}])
    
    # Add support for on react events
    elif (event_type == "react"):
        # Code for fishing shop reactions
        with open("meta/shop_ids.json", "r") as shop:
            data = json.load(shop)
        for item in data:
            # Check if the message being reacted to is a shop
            if kwargs.get("messageable").id == item.get("id"):
                # Check if the user is selling a fish
                if item.get("type") == "sale":
                    if user_id != item.get("user_id"):
                        return
                    match message:
                        case "✅":
                            # Get the file id
                            file_name = "inv_" + str(item.get("user_id"))
                            inv_list = []
                            # Get the user's inventory and user data
                            with open(f"inventories/{file_name}", 'r') as inv, open ("meta/user_buffs.json", "r") as buffs:
                                for line in inv.readlines():
                                    inv_list.append(line)
                                user_data = json.load(buffs)
                            with open("meta/user_buffs.json", "w") as buffs, open(f"inventories/{file_name}", 'w') as inv,\
                                open("meta/shop_ids.json", "w") as shop:
                                # Overwrite the user's buffs, inventory, and the shop ids
                                for user in user_data:
                                    # Add to the user's money and remove the fish
                                    if user["id"] == item.get("user_id"):
                                        user["money"] += item["price"]
                                        data.remove(item)
                                        del inv_list[item.get("index")-1]
                                        # Write the updated inventory, shop file, and user data 
                                        for line in inv_list:
                                            inv.write(line)
                                        json.dump(data, shop)
                                        json.dump(user_data, buffs)
                                        return ([{"type":"message","message":f"Thanks for your buisness, <@{user_id}>!"}])
                        case "❎":
                            # Remove the message from the shop file
                            print("Deal Closed")
                            data.remove(item)
                            with open("meta/shop_ids.json", "w") as shop:
                                json.dump(data, shop)
                                return ([{"type":"message","message":f"Looks like we're done here, , <@{user_id}>."}])
                elif item.get("type") == "shop":
                    # Open the shop data and the user's buffs
                    with open("meta/shop_data.json", "r") as shops, open("meta/user_buffs.json", "r") as buffs:
                        shop_data = json.load(shops)
                        # Check if the user has an entry in the user_buffs file
                        buff = json.load(buffs)
                        for user in buff:
                            if user.get("id") == user_id:
                                break
                        else:
                            return([{"type":"message","message":f"Hey! You don't have any money, <@{user_id}>!"}, {"type":"react", "react":message, "add":False}])
                    match message:
                        # Pass relevant information to fish.py
                        case "1️⃣":
                            # Make sure you can't buy a rod upgrade for a lower display price
                            if user_id != item.get("user_id"):
                                return([{"type":"message","message":"Sorry, I can't let you buy that."}])
                            reply = fish.buy(0, user, user_id, shop_data, buff, "rod", 1)
                            return([{"type":"message","message":reply}, {"type":"react", "react":message, "add":False}])
                        case "2️⃣":
                            reply = fish.buy(1, user, user_id, shop_data, buff, "bait", 1, duration=5)
                            return([{"type":"message","message":reply}, {"type":"react", "react":message, "add":False}])
                        case "3️⃣":
                            reply = fish.buy(2, user, user_id, shop_data, buff, "bait", 2, duration=5)
                            return([{"type":"message","message":reply}, {"type":"react", "react":message, "add":False}])
                        case "4️⃣":
                            reply = fish.buy(3, user, user_id, shop_data, buff, "bait", 5, duration=10)
                            return([{"type":"message","message":reply}, {"type":"react", "react":message, "add":False}])
                        case "5️⃣":
                            reply = fish.buy(4, user, user_id, shop_data, buff, "cheese", 0)
                            return([{"type":"message","message":reply}, {"type":"react", "react":message, "add":False}])

        # Misc reactions
        if getattr(args.get("message_author"),"name") == "EclipseBot":
            if (message == "👎"):
                return([{"type":"message","message":"Don't be mean!"}])
            elif (message == "🖕"):
                return([{"type":"message","message":"Fuck off"}])
        
        # Starboard-like system
        elif (message == "👎") & (args.get("count") == 2):
            responses = ("bad post. bad", "you should feel bad about this", "lmao idiot", "no. just no.", "delete this")
            response = responses[random.randint(0,len(responses)-1)]
            return ([{"type":"reply","message":response,"id":kwargs.get("messageable")}])