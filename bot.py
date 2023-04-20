import discord
import responses
import asyncio
import datetime as dt
import json

intents = discord.Intents.default()
intents.message_content = True

async def handle_event(message, user_message, channel, server, server_id, user_id, event_type, **kwargs):
    response = (responses.handle_response(user_message, user_id, server, event_type, args=kwargs, messageable=message, server_id=server_id))
    if response:
        for item in response:   
            print(item)
            match (item.get("type")):
                case "message":
                    try:
                        message_1 = await channel.send(item["message"])
                    except discord.errors.HTTPException:
                        await channel.send("Message was too long to send!")
                    if item.get("store_message", False):
                        with open("meta/shop_ids.json","r") as shop:
                            data = json.load(shop)
                        metadata = item.get("metadata", {})
                        metadata["id"] = message_1.id
                        data.append(metadata)
                        with open("meta/shop_ids.json","w") as shop:
                                json.dump(data, shop)
                case "reply":
                    try:
                        await channel.send(item["message"], reference=item["id"])
                    except discord.errors.HTTPException:
                        await channel.send("Message was too long to send!")
                case "react":
                    if item.get("self", False):
                        message = message_1
                    await message.add_reaction(item["react"])
                case "role":
                    if item["color"]:
                        color = discord.Colour.from_str(item["color"])
                    for role in server.roles:
                        if getattr(role, "name") == "EclipseBot":
                            pos = server.roles.index(role)-1
                    try:
                        created_role = await server.create_role(name=item["name"], color=color)
                        await created_role.edit(position=pos)
                        await message.author.add_roles(created_role)
                    except discord.errors.Forbidden:
                        await channel.send("No permissions to create roles!")
                    except discord.errors.HTTPException:
                        await channel.send("Failed to create the role!")
                case "timeout":
                    time = item["time"]
                    try:
                        secs = int(time)
                        await message.author.timeout(dt.timedelta(seconds=secs))
                    except ValueError:
                        print(f"ValueError with item[\"time\"] ({time})")
                    except discord.errors.Forbidden:
                        await channel.send("No permissions to time out users!")
                case "event":
                    try:
                        event = await server.create_scheduled_event(name=item["name"], location=item["location"],
                                                            start_time=item["start"], end_time=item["end"])
                        await channel.send(event.url)
                    except ValueError:
                        await channel.send("You have to provide a valid timezone! Try \"UTC\" or \"UTC-0500\"")
                    except discord.errors.Forbidden:
                        await channel.send("No permissions to create events!")
                    except discord.errors.HTTPException:
                        await channel.send("Failed to create the event! The start or end time might not have been within 5 years.")
                case "wait":
                    async with channel.typing():
                        await asyncio.sleep(item["time"])
                case _:
                    pass

def run_disc_bot():
    with open("meta/TOKEN.txt", "r") as important:
        token = important.readline().strip()
    TOKEN = token
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        await client.change_presence(activity=discord.Game(name="Gone fishin' 🎣"))
        print(f'{client.user} is now running!')
    
    @client.event
    async def on_raw_reaction_add(payload):
        
        server = await client.fetch_guild(payload.guild_id)
        channel = await client.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        message_author = message.author
        user = await client.fetch_user(int(payload.user_id))
        emoji = str(payload.emoji)
        count = discord.utils.get(message.reactions, emoji=payload.emoji.name).count
        username = user.name
        
        if user == client.user:
            return
        
        print(f"{username} ({payload.user_id}) reacted to \"{message.content}\" (by {message_author}) \
with {emoji} in #{channel} in {server}")
        
        await handle_event(message, emoji, channel, server, payload.guild_id, payload.user_id, \
            "react", message_author=message_author, react_author=username, count=count)

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = message.channel
        server = message.guild
        server_id = int(message.guild.id)
        user_id = int(message.author.id)

        print(f"{username} ({user_id}) said {user_message} in #{channel} in {server}")

        if client.user.mentioned_in(message):
            await handle_event(message, user_message, channel, server, server_id, user_id, "message", mentioned=True)
        else:
            await handle_event(message, user_message, channel, server, server_id, user_id, "message", username = username)
        
        
    
    client.run(TOKEN)

if __name__ == "__main__":
    run_disc_bot()