import discord
import asyncio
from inventories import inventories

async def message(self, item:list[dict]|None, channel:discord.TextChannel):
    self.last_sent_message = await channel.send(item.get("message","No message provided"), embed=item.get("embed", None))
    print(f"Said {item.get('message','No message provided')}{' (with embed)' if item.get("embed", None) is not None else ""} in {channel.name} in {channel.guild.name}")

async def reply(self, item:list[dict]|None, channel:discord.TextChannel):
    await channel.send(item.get("message","No message provided"), reference=item.get("reply", self.last_sent_message), embed=item.get("embed", None))
    print(f"Said {item.get('message','No message provided')}{' (with embed)' if item.get("embed", None) is not None else ""} in {channel.name} in {channel.guild.name}")

async def react(self, item:list[dict]|None, channel:discord.TextChannel):
    message:discord.Message = item.get("message", self.last_sent_message)
    if type(item.get("react")) == discord.PartialEmoji:
        await message.add_reaction(item.get("react"))
    else:
        for char in item.get("react"):
            await message.add_reaction(char)
    print(f"Reacted to {message.content} (by {message.author}) in {message.channel} in {message.channel.guild} with {item.get('react')}")

async def role(self, item:list[dict]|None, channel:discord.TextChannel):
    try:
        role = channel.guild.get_role(int(item.get("role").strip("@&<>")))
        user = await channel.guild.fetch_member(int(item.get("user").strip("@<>")))
        if user is None:
            await channel.send("No user found!")
        await user.add_roles(role)
        await channel.send(f"Added role with ID {role.id} to user <@{user.id}>")
    except discord.errors.PrivilegedIntentsRequired:
        await channel.send("You do not have permission to add roles to users")
    except ValueError:
        await channel.send("That is not a valid ID!")

async def delete(self, item:list[dict]|None, channel:discord.TextChannel):
    try:
        temp_channel = await self.fetch_channel(item.get("channel"))
        message = await channel.fetch_message(item.get("message"))
        await message.delete()
    except discord.errors.PrivilegedIntentsRequired:
        await channel.send("You do not have permission to delete messages")

async def wait(self, item, channel):
    print(f"Sleeping for {item.get('time', 0)} seconds...")
    await asyncio.sleep(item.get("time"))

async def write(self, item, channel):
    path = item.get("path")
    store = item.get("extra")
    store["id"] = self.last_sent_message.id
    inventories.add_meta(item.get("id"), item.get("name"), store)

async def error(self, item, channel):
    error = item.get("error")
    print(f"Raising error {error}")
    raise error

async def call(self, item, channel) -> int:
    wait_type = item.get("wait_type", None)
    if wait_type is not None:
        msg = await self.wait_for(wait_type, check=item.get("check", lambda x: True))
    else:
        msg = item.get("message")

    func = item.get("call", lambda x:None)
    return await func(self, msg.author.id, msg)
    