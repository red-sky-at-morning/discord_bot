import asyncio
import discord
import aioconsole

async def handle_message(uinput, server, channel):
    if len(uinput) == 0:
        return
    await channel.send(uinput)
    print(f"Said {uinput} in #{channel} in {server}")
    return

async def handle_command(client, uinput, servers:list, server:discord.Guild, channels, channel):
    if uinput[:6] == ".leave":
        print(f"leaving {server.name}")
        await server.leave()
        servers.remove(server)
        server = servers[0]
    elif uinput[:7] == ".server":
        uinput = uinput[7:].strip()
        try:
            uinput = int(uinput)
        except ValueError:
            if uinput == "list":
                for guild in servers:
                    print(guild.name.lower())
                return ({"server":server,"channel":channel})
            for guild in servers:
                guild:discord.Guild
                if guild.name.lower() != uinput:
                    continue
                server = guild
                channels = list(server.text_channels)
                for channel in list(channels):
                    if client.user not in channel.members:
                        channels.pop(channels.index(channel))
                channel = channels[0]
                return ({"server":server,"channel":channel})
            else:
                print("Server not found")
                return ({"server":server,"channel":channel})
        else:
            for guild in servers:
                if guild.id != uinput:
                    continue
                server = guild
                channels = list(server.text_channels)
                for channel in list(channels):
                    if client.user not in channel.members:
                        channels.pop(channels.index(channel))
                channel = channels[0]
            else:
                print("Server not found")
                return ({"server":server,"channel":channel})
    # ---
    elif uinput [:8] == ".channel":
        uinput = uinput[8:].strip()
        try:
            uinput = int(uinput)
        except ValueError:
            if uinput == "list":
                for tchannel in list(channels):
                    print(tchannel)
                return ({"server":server,"channel":channel})
            for tchannel in channels:
                if tchannel.name.lower() != uinput:
                    continue
                channel = tchannel
                return ({"server":server,"channel":channel})
            else:
                print(f"Channel not found in {server}")
                return ({"server":server,"channel":channel})
        else:
            for tchannel in channels:
                if tchannel.id != uinput:
                    continue
                channel = tchannel
            else:
                print(f"Channel not found in {server}")
                return ({"server":server,"channel":channel})
    else:
        print("Command not found")
        return ({"server":server,"channel":channel})

async def run(client:discord.Client):
    await client.wait_until_ready()
    servers = list(client.guilds)
    server = servers[0]
    channels = list(server.text_channels)
    for channel in list(channels):
        if client.user not in channel.members:
            channels.pop(channels.index(channel))
    channel = channels[0]
    
    while True:
        try:
            uinput = await aioconsole.ainput("")
            if client.mode not in client.console_modes:
                continue
            rinput = uinput
            uinput = uinput.lower()
            if ".clear" in uinput:
                continue
            if uinput[0] != ".":
                await handle_message(rinput, server, channel)
            else:
                new = await handle_command(client, uinput,servers,server,channels,channel)
                server = new.get("server")
                channels = list(server.text_channels)
                channel = new.get("channel")
                print(f"Moved to #{channel} in {server}")
        except KeyboardInterrupt:
            break
    await client.close()
    return