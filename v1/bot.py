import discord
import responses
import chat_window
import asyncio
import datetime as dt
import queue
import json
import argparse

intents = discord.Intents.default()
intents.message_content = True

q = queue.Queue()
terminal_args = argparse.Namespace()

open_chat = False

async def handle_event(message, user_message, channel, server, server_id, user_id, event_type, **kwargs):
    response = (responses.handle_response(user_message, user_id, server, event_type, args=kwargs, messageable=message, server_id=server_id))
    # Iterate over the response and execute the commands
    print(response)
    for item in response:
        print(item)
        match (item.get("type")):
            case "message":
                try:
                    # Send the message and store it in case another command references it
                    stored_message = await channel.send(item["message"], embed=item.get("embed", None))
                except discord.errors.HTTPException:
                    await channel.send("Message was too long to send, or might have been empty!")
                if not item.get("store_message", False):
                    continue
                # If we want to store the message data, we send data to the meta/shop_ids file with any extra data
                with open("meta/shop_ids.json","r") as shop:
                    data = json.load(shop)
                metadata = item.get("metadata", {})
                metadata["id"] = stored_message.id
                data.append(metadata)
                with open("meta/shop_ids.json","w") as shop:
                        json.dump(data, shop)
            case "reply":
                # This could probably be a type of message command but im to lazy to rewrite it now
                try:
                    stored_message = await channel.send(item["message"], reference=item["id"])
                except discord.errors.HTTPException:
                    await channel.send("Message was too long to send, or might have been empty!")
            case "react":
                # Check if we want to add the reaction (Defaults to yes)
                if not item.get("add", True):
                    # If we want to remove reactions, do that
                    await message.remove_reaction(item["react"], kwargs.get("user"))
                    continue
                    # If we want to add it to a message we just sent, change the message
                if item.get("self", False):
                    await stored_message.add_reaction(item["react"])
                    continue
                    # Add reactions
                await message.add_reaction(item["react"])
                    
            case "role":
                # Get the color
                if item.get("color", None):
                    color = discord.Colour.from_str(item["color"])
                # Get the highest we can move the role to
                for role in server.roles:
                    if getattr(role, "name") == "EclipseBot":
                        pos = max(server.roles.index(role)-1, 1)
                try:
                    # Create the role and move it to the position we grabbed earlier
                    created_role = await server.create_role(name=item["name"], color=color)
                    await created_role.edit(position=1)
                    await message.author.add_roles(created_role)
                # Add error handling
                except discord.errors.Forbidden:
                    await channel.send("No permissions to create roles!")
                except discord.errors.HTTPException:
                    await channel.send("Failed to create the role!")
            case "timeout":
                # Get the time
                time = item.get("time", 0)
                try:
                    # Timeout the user
                    secs = int(time)
                    await message.author.timeout(dt.timedelta(seconds=secs))
                # Add error handling
                except discord.errors.Forbidden:
                    await channel.send("No permissions to time out users!")
            case "event":
                try:
                    # Create the event and send the link to it
                    event = await server.create_scheduled_event(name=item["name"], location=item["location"],
                                                        start_time=item["start"], end_time=item["end"])
                    await channel.send(event.url)
                # Add error handling
                except ValueError:
                    await channel.send("You have to provide a valid timezone! Try \"UTC\" or \"UTC-0500\"")
                except discord.errors.Forbidden:
                    await channel.send("No permissions to create events!")
                except discord.errors.HTTPException:
                    await channel.send("Failed to create the event! The start or end time might not have been within 5 years.")
            case "wait":
                # Sleep for that many seconds with the typing indicator
                async with channel.typing():
                    await asyncio.sleep(item["time"])
            case _:
                continue

def run_disc_bot():
    # Read in the token from the meta/TOKEN.txt file.
    with open("meta/TOKEN.txt", "r") as important:
        TOKEN = important.readline().strip()
    client = discord.Client(intents=intents)

    # On ready, change the activity and print to the console
    @client.event
    async def on_ready():
        await client.change_presence(activity=discord.Game(name="Gone fishin' 🎣"))
        print(f'{client.user} is now running!')
    
    # Watch for reactions
    @client.event
    async def on_raw_reaction_add(payload):
        
        # Get data from the payload
        server = await client.fetch_guild(payload.guild_id)
        channel = await client.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        message_author = message.author
        user = await client.fetch_user(int(payload.user_id))
        emoji = payload.emoji
        count = discord.utils.get(message.reactions, emoji=emoji.name).count
        username = user.name
        
        # Don't respond to our own reactions
        if user == client.user:
            return
        
        # Print to console
        print(f"{username} ({payload.user_id}) reacted to \"{message.content}\" (by {message_author}) \
with {emoji} in #{channel} in {server}")
        
        # Handle the reaction
        await handle_event(message, emoji, channel, server, payload.guild_id, payload.user_id, \
            "react", message_author=message_author, react_author=username, count=count, user=user)

    # Watch for messages
    @client.event
    async def on_message(message):
        # Don't respond to our own messages
        if message.author == client.user:
            return

        # Get data from the message
        username = str(message.author)
        user_message = str(message.content)
        channel = message.channel
        server = message.guild
        server_id = int(message.guild.id)
        user_id = int(message.author.id)

        # Print to console
        print(f"{username} ({user_id}) said {user_message} in #{channel} in {server}")

        # Get extra data, then handle the message
        if client.user.mentioned_in(message):
            await handle_event(message, user_message, channel, server, server_id, user_id, "message", mentioned=True)
        else:
            await handle_event(message, user_message, channel, server, server_id, user_id, "message", username = username, user=message.author)
    
    async def run_bot():
        run_console = input("Run console? y/n: ") == "y"
        discord.utils.setup_logging(root=False)
        await asyncio.gather(
            client.start(TOKEN),
            chat_window.run_console(client, run_console)
        )
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    
if __name__ == "__main__":
    run_disc_bot()