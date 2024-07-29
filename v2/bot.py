import discord
import asyncio
import responses
import console

class Bot(discord.Client):
    def __init__(self, intents:discord.Intents):
        super().__init__(intents=intents)
        self.starting_mode = "TESTING"
        self.modes:tuple = ("ACTIVE", "CONSOLE", "STANDBY", "TESTING", "HYBRID")
        self.console_modes:tuple = ("CONSOLE", "HYBRID")
        self.mode:str = self.starting_mode
        self.ignore_errors:bool = False
        self.author:discord.User

    async def on_ready(self):
        self.author = await self.fetch_user(630837649963483179)
        await self.change_presence(activity=discord.Game("with code"))
        print(f"{self.user} is now running!")

    async def send_dm(self, user:discord.User, content:str) -> None:
        channel = await user.create_dm()
        await channel.send(content)
    
    async def on_error(self, event:str, *args, **kwargs):
        import sys
        extype, ex, trace = sys.exc_info()
        print(f"{extype.__name__} exception in {event}: {ex}")
        await self.send_dm(self.author, f"{extype.__name__} exception in {event}: {ex}")
        if not self.ignore_errors:
            print("Entering Standby mode...")
            await self.send_dm(self.author, "Entering Standby mode...")
            self.mode = self.modes[2]
    
    def switch_mode(self, mode) -> None:
        if mode not in self.modes:
            raise TypeError(f"Mode not found in mode list: {mode}")
        print(f"Switching to mode {mode}")
        self.mode = mode
    
    def verify_mode(self, server:int, channel:int, user:int) -> bool:
        restricted:bool = channel == 1041508830279905280 or server == 677632068041310208 or user == 630837649963483179
        match self.mode:
            case "ACTIVE":
                return True
            case "CONSOLE":
                return restricted
            case "HYBRID":
                return True
            case "STANDBY":
                return restricted
            case "TESTING":
                return restricted
    
    async def handle_response(self, response:list[dict]|None, channel:discord.TextChannel) -> None:
        if response is None:
            return
        for item in response:
            if not item:
                continue
            match item.get("type", None):
                case "message":
                    await channel.send(item.get("message","No message provided"), embed=item.get("embed", None))
                    print(f"Said {item.get('message','No message provided')} in {channel.name} in {channel.guild.name}")
                case "reply":
                    await channel.send(item.get("message","No message provided"), reference=item.get("reply"), embed=item.get("embed", None))
                    print(f"Replied to {item.get('reply').content} with {item.get('message','No message provided')} in {channel.name} in {channel.guild.name}")
                case "react":
                    message:discord.Message = item.get("message")
                    await message.add_reaction(item.get("react"))
                    print(f"Reacted to {message.content} (by {message.author}) in {message.channel} in {message.channel.guild} with {item.get('react')}")
                case "wait":
                    print(f"Sleeping for {item.get('time', 0)} seconds...")
                    await asyncio.sleep(item.get("time"))
                case "error":
                    error = item.get("error")
                    print(f"Raising error {error}")
                    raise error
                case "mode":
                    self.switch_mode(item.get("mode"))
                case None:
                    raise TypeError("No type provided for response")
                case _:
                    raise TypeError("Unexpected type for response")

    async def on_message(self, message:discord.Message):
        # Don't respond to our own messages
        if message.author == self.user:
            return

        # Get data from the message
        username = str(message.author)
        content = str(message.content)
        channel = message.channel
        channel_id = channel.id
        server = message.guild
        if server is not None:
            server_id = int(message.guild.id)
        else:
            server_id = -1
        user_id = int(message.author.id)

        # Print to console
        print(f"{username} ({user_id}) said {content} in #{channel} in {server}")

        if not self.verify_mode(server_id, channel_id, user_id):
            return

        response = responses.handle_message(message, content, channel_id, user_id, server_id)
        await self.handle_response(response, channel)

    def startup(self) -> None:
        with open("meta/TOKEN.txt", "r") as token:
            TOKEN = token.readline().strip()
        async def run():
            discord.utils.setup_logging(root=False)
            await asyncio.gather(
                self.start(TOKEN),
                console.run(self)
            )
        try:
            asyncio.run(run())
        except KeyboardInterrupt:
            print("\nGoodbye!")
        
if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    eclipse = Bot(intents=intents)
    eclipse.startup()