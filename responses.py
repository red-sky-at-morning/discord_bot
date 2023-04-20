import fish
import song
import random
import json
import event as ev

testing_mode = False
banned_users = (694231818957750280, 0)


def handle_response(message, user_id: int, server, event_type, **kwargs):
    args = kwargs.get("args")
    if (event_type == "message"):
        message_raw = message
        p_message = message.lower()
        server = str(server)

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

            # Help last editted as of 11/19/22 3pm -- Version 1.0.3T -- Updated >roll command
            case '>help':
                return ([{"type": "message", "message": "Commands:"},
                            {"type":"message","message":">fish: Try and catch a fish. check your inventory with >fish inv [page]"},
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

        # If-else statement for commands with arguements and other messages

        if p_message[:5] == ">fish":
            if "inv" in p_message:
                i_message = p_message[p_message.index("inv")+3:]
                i_message.strip()
                # Add error handling
                try:
                    page = int(i_message)
                except ValueError:
                    return ([{"type": "message", "message": f"\"{i_message}\" is not a valid page number! Try >fish inv 1"}])
                return ([{"type": "message", "message": f"{fish.get_inv(user_id, page)}"}])
            elif "sell" in p_message:
                s_message = p_message[p_message.index("sell")+4:]
                s_message.strip()
                try:
                    index = int(s_message)
                except ValueError:
                    return ([{"type": "message", "message": f"\"{s_message}\" is not a valid inventory index! Try >fish sell 1"}])
                return(fish.sell(user_id, index))
            elif "shop" in p_message:
                return
            elif "stats" in p_message:
                with open (f"inventories/inv_{user_id}", "r") as inv, open("user_buffs.json", "r") as buffs:
                    data = json.load(buffs)
                    for user in data:
                        if user.get("id") == user_id:
                            username = args.get("username")
                            rod = user.get("rod")
                            fish_count = len(inv.readlines())
                            money = user.get("money")
                            return ([{"type":"message","message":f"Name: **{username}**\n\nFish in storage: {fish_count}\nRod Level: {rod}\nMoney: {money}"}])
            else:
                return ([{"type": "message", "message": "The waters are stirring..."}, {"type": "wait", "time": 2}, {"type": "message", "message": f"{fish.start_fish(user_id)}"}])
            
            
        elif ">roll" in p_message:
            r_message = p_message[5:]
            r_message.strip()
            d_message = r_message.split("d")
            khn = ""
            # Add error handling
            try:
                die_num = int(d_message[0])
            except ValueError:
                return ([{"type": "message", "message": f"\"{d_message[0]}\" is not a number! Try >roll 3d20"}])
            try:
                die_size = int(d_message[1])
            except ValueError:
                if ("k" in d_message[1]):
                    idx = d_message[1].find("k")
                    khn = d_message[1][idx:]
                    die_size = int(d_message[1][:idx])
                elif ("d" in d_message[1]):
                    idx = d_message[1].find("d")
                    khn = d_message[1][idx:]
                    die_size = int(d_message[1][:idx])
                else:
                    return ([{"type": "message", "message": f"\"{d_message[1]}\" is not a number! Try >roll 3d20"}])
            roll_list = []
            total = 0
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
                if ((roll_list[i] == die_size) or (roll_list[i] == 1)):
                    roll_list[i] = f"**{roll_list[i]}**"
                else:
                    roll_list[i] = str(roll_list[i])
            roll_list = f"{roll_list}".replace("'", "").replace("[","(").replace("]",")")
            return ([{"type": "message", "message": f"Rolled {die_num}d{die_size}, {khn}and got {total} {roll_list}"}])

        elif ">song" in p_message:
            s_message = message_raw[6:]
            s_message = s_message.split(" ")
            print(s_message)
            playlist = s_message[1]
            match s_message[0]:
                case "random":
                    song_f = (song.playlist_tracks(playlist, "RANDOM"))
                    return ([{"type": "message", "message": f"{song_f}"}])
                case "list":
                    song_f = (song.playlist_tracks(playlist, "LIST"))
                    return ([{"type": "message", "message": f"{song_f}"}])
                case _:
                    return ([{"type": "message", "message": "Not a valid command for >song! Try >song random or >song list instead!"}])

        elif ">role" in p_message:
            if ((server == "The Order") | (server == "swashbucklers and stuff") | (user_id == 630837649963483179)):
                r_message = message_raw[6:]
                r_message = r_message.split("\"")
                print(r_message)
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
            
            event = ev.get_event_data(e_message)
            name = event["name"]
            location = event["location"]
            start = event["start"]
            end = event["end"]
            
            return ([{"type": "event", "name": event["name"], "location": event["location"], "start": event["start"], "end": event["end"]},
                    {"type": "message", "message": f"Created an event called {name}, set in {location}, \
that starts at {start} and ends at {end}"}])

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
    
    elif (event_type == "react"):
        with open("shop_ids.json", "r") as shop:
            data = json.load(shop)
        for item in data:
            if kwargs.get("messageable").id == item.get("id"):
                if user_id != item.get("user_id"):
                    return
                match message:
                    case "✅":
                        # Get the file id
                        file_name = "inv_" + str(item.get("user_id"))
                        inv_list = []
                        with open(f"inventories/{file_name}", 'r') as inv, open ("user_buffs.json", "r") as buffs:
                            for line in inv.readlines():
                                inv_list.append(line)
                            user_data = json.load(buffs)
                        with open("user_buffs.json", "w") as buffs, open(f"inventories/{file_name}", 'w') as inv,\
                            open("shop_ids.json", "w") as shop:
                            for user in user_data:
                                if user["id"] == item.get("user_id"):
                                    user["money"] += item["price"]
                                    data.remove(item)
                                    del inv_list[item.get("index")-1]
                                    for line in inv_list:
                                        inv.write(line)
                                    json.dump(data, shop)
                                    json.dump(user_data, buffs)
                                    return ([{"type":"message","message":"Thanks for your buisness!"}])
                    case "❎":
                        print("Deal Closed")
                        data.remove(item)
                        with open("shop_ids.json", "w") as shop:
                            json.dump(data, shop)
                            return ([{"type":"message","message":"Looks like we're done here."}])
        
        if getattr(args.get("message_author"),"name") == "EclipseBot":
            if (message == "👎"):
                return([{"type":"message","message":"Don't be mean!"}])
            elif (message == "🖕"):
                return([{"type":"message","message":"Fuck off"}])
        
        elif (message == "👎") & (args.get("count") == 2):
            responses = ("bad post. bad", "you should feel bad about this", "lmao idiot", "no. just no.", "delete this")
            response = responses[random.randint(0,len(responses)-1)]
            return ([{"type":"reply","message":response,"id":kwargs.get("messageable")}])