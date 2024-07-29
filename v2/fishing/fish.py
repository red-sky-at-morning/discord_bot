import random

with open("fishing/rewards/fish.txt", "r") as fish_f:
    fish:list = [line.strip("\n") for line in fish_f.readlines()]

with open("fishing/rewards/treasure.txt", "r") as treasure_f:
    treasure:list = [line.strip("\n") for line in treasure_f.readlines()]

wait_message:list[dict] = ({"type":"message", "message":"The waters are stirring..."}, {"type":"wait", "time":2})

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
    add_to_inventory(user_id, item)
    response.append({"type":"message","message":f"<@{user_id}> got a {item}!"})
    return response

def add_to_inventory(user_id:int, item) -> bool:
    try:
        with open(f"fishing/inventories/inv_{user_id}.txt", "a") as inv:
            inv.write(f"\n{item}")
        return True
    except Exception as e:
        print(e)
        return False


def remove_from_inventory(user_id:int, item) -> bool:
    return False #TODO implement

def read_from_inventory(user_id:int, start_index:int, step:int) -> list[dict]:
    with open(f"fishing/inventories/inv_{user_id}.txt", "r") as inv:
        lines = inv.readlines()
    response = [line.strip('\n') for line in lines[start_index, start_index+step]]