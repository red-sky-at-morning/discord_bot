import bot
import asyncio
from aioconsole import ainput

q = bot.getQueue()

def run_async_console(client):
    global q
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    servers = list(client.guilds)
    server = servers[0]
    
    channels = list(server.text_channels)
    channel = channels[0]
    
    async def handle_console(uinput):
        nonlocal servers, server, channels, channel
        
        if len(uinput) == 0:
            return
        
        if uinput[0] != ".":
            if ".clear" in uinput:
                return
            q.put({"message":uinput, "channel":channel, "server":server})
            return
        
        if uinput[:7] == ".server":
            uinput = uinput[7:].strip()
            try:
                uinput = int(uinput)
            except ValueError:
                if uinput == "list":
                    for guild in servers:
                        print(guild.name.lower())
                    return
                for guild in servers:
                    if guild.name.lower() != uinput:
                        continue
                    server = guild
                    channels = server.text_channels
                    channel = channels[0]
                    print(f"Moved to #{channel} in {server}")
                    return
                else:
                    print("Server not found")
                    return
            else:
                for guild in servers:
                    if guild.id != uinput:
                        continue
                    server = guild
                    channels = server.text_channels
                    channel = channels[0]
                    print(f"Moved to #{channel} in {server}")
                else:
                    print("Server not found")
                    return
        # ---
        elif uinput [:8] == ".channel":
            uinput = uinput[8:].strip()
            try:
                uinput = int(uinput)
            except ValueError:
                if uinput == "list":
                    for tchannel in channels:
                        print(tchannel)
                    return
                for tchannel in channels:
                    if tchannel.name.lower() != uinput:
                        continue
                    channel = tchannel
                    print(f"Moved to #{channel} in {server}")
                    return
                else:
                    print(f"Channel not found in {server}")
                    return
            else:
                for tchannel in channels:
                    if tchannel.id != uinput:
                        continue
                    channel = tchannel
                    print(f"Moved to #{channel} in {server}")
                else:
                    print(f"Channel not found in {server}")
                    return
        else:
            print("Command not found")
            return
    
    async def run_console():
        print(f"Opening console in #{str(channel)} in {str(server)}")
        
        while True:
            uinput = await ainput("")
            uinput = uinput.lower()
            await handle_console(uinput)
    
    loop.run_until_complete(run_console())