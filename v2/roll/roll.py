from queue import Full
import random

# >roll [n]d[n] [filters]
def parse(command:list[str]) -> list[dict]:
    iters, size = command[0].split("d")
    filter_str = command[1] if len(command) > 2 else ""
    
    try:
        size = int(size)
        iters = int(iters)
    except ValueError:
        return [{"type":"message","message":"I don't know how to read that roll! Try >roll 3d20"}]
    
    return get_roll_message(size, iters, filter_str)

def get_roll_message(size:int, iters:int, filters:str) -> list[dict]:
    print(f"rolling {iters}d{size}:")
    rolls = roll(size, iters, Filters.get_filter_from_string(filters))
    return [{"type":"message","message":rolls}]

def roll(size:int, iter:int, filter) -> list[int]:
    out = []
    
    for _ in range(iter):
        num = random.randint(1,size)
        out.append(num)
    
    out = sorted(out)
    out = filter(out)

    return out

class Filters:
    def keep_highest(input:list[int], keeps:int):
        return input[-keeps:]

    def keep_lowest(input:list[int], keeps:int):
        return input[:keeps]
    
    def drop_lowest(input:list[int], drops:int):
        return input[drops:]
    
    def drop_highest(input:list[int], drops:int):
        return input[:-drops]
    
    def keep_above(input:list[int], threshold:int):
        return list([i for i in input if i > threshold])
    
    def keep_below(input:list[int], threshold:int):
        return list([i for i in input if i < threshold])

    def chance(input:list[int], chance:float):
        for item in input:
            rand = random.random()
            if rand > chance:
                input.remove(item)
        return input
    
    def always(input:list[int]):
        return input
    
    global keys
    keys = {"_": always, "kh": keep_highest, "kl":keep_lowest, "dl":drop_lowest, "dh":drop_highest, "ka":keep_above, "kb":keep_below, "ch":chance}
    def get_filter_from_string(filter:str):
        # return keys.get(filter, keys.get("_"))
        return keys.get("_")