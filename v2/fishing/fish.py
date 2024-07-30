import random
from fishing import inventories

with open("fishing/rewards/fish.txt", "r") as fish_f:
    fish:list = [line.strip("\n") for line in fish_f.readlines()]

with open("fishing/rewards/treasure.txt", "r") as treasure_f:
    treasure:list = [line.strip("\n") for line in treasure_f.readlines()]

wait_message:list[dict] = ({"type":"message", "message":"The waters are stirring..."}, {"type":"wait", "time":2})

def handle(command:list[str], user_id:int, username):
    print(command)
    if len(command) <= 2:
        return go_fish(user_id, username)
    match command[1]:
        case "inv":
            try:
                return inventories.read_from_inventory(user_id, username, (int(command[2])-1)*20, 20)
            except ValueError:
                return([{"type":"message","message":"Sorry, I can't tell what page you're looking for. Try >fish inv 1"}])
        case _:
            return([{"type":"message","message":"Sorry, I don't recognize that subcommand."}])

def go_fish(user_id:int, username) -> list[dict]:
    response:list[dict] = []
    response += wait_message
    roll:float = random.random()
    item:str

    print(roll)
    match roll:
        case roll if roll > .9:
            idx = random.randrange(0, len(treasure)-1)
            item = treasure[idx]
            if item == "{{USERNAME}}":
                item = username
        case roll if roll < .1:
            item = None
        case _:
            idx = random.randrange(0, len(fish)-1)
            item = fish[idx]
    if item is None:
        response.append({"type":"message","message":"Not even a nibble..."})
        return response
    inventories.add_to_inventory(user_id, item)
    response.append({"type":"message","message":f"<@{user_id}> got a {item}!"})
    return response

