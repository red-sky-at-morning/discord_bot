from queue import Full
import random
import re
import discord

# >roll [n]d[n] [filters]
def parse(command:list[str]) -> list[dict]:
    iters, size = command[0].split("d")
    filter_str = command[1] if len(command) > 2 else ""
    
    try:
        iters = int(iters)
        if len(size.split("+")) > 1:
            bonus = int(size.split("+")[1])
        else:
            bonus = 0
        size = int(size.split("+")[0])
    except ValueError:
        return [{"type":"message","message":"I don't know how to read that roll! Try >roll 3d20"}]
    
    return get_roll_message(size, iters, bonus, filter_str)

def get_roll_message(size:int, iters:int, bonus, filters:str) -> list[dict]:
    filter = Filters.get_filter_from_string(filters.strip("1234567890"))
    rolls, filtered_rolls = roll(size, iters, filter, get_trailing_number(filters))

    tot = sum(filtered_rolls) + bonus

    out_str = ""
    for idx, item in enumerate(rolls):
        r_string = item
        if item not in filtered_rolls:
            r_string = f"~~{r_string}~~"
        else:
            filtered_rolls.remove(item)
        if item == 1:
            r_string = f"*{r_string}*"
        if item == size:
            r_string = f"**{r_string}**"
        out_str = out_str + (f"{r_string}, ") + ("\n" if (idx+1)%15 == 0 else "")
    out_str = out_str.strip(", \n")

    embed = discord.Embed(color = discord.Color.random(), description=f"Rolled {iters}d{size}{f'+{bonus}' if bonus else ''} and got **{tot}**")
    embed.add_field(name="Rolls",value=out_str)

    return [{"type":"message","message":"","embed":embed}]

def roll(size:int, iter:int, filter, val:int) -> tuple[list[int]]:
    print(f"rolling {iter}d{size}:")
    out = []
    
    for _ in range(iter):
        num = random.randint(1,size)
        out.append(num)

    out = sorted(out)
    filtered = filter(out, val)
    print(out)
    print(f"filtered with filter {filter.__name__}: {filtered}")

    return (out, filtered)

def get_trailing_number(s):
    m = re.search(r'\d+$', s)
    return int(m.group()) if m else None

class Filters:
    def shallowcopy(func):
        def wrapper(input:list[int], dummy:int):
            input = input.copy()
            return func(input, dummy)
        return wrapper

    @shallowcopy
    def keep_highest(input:list[int], keeps:int):
        return input[-keeps:]

    @shallowcopy
    def keep_lowest(input:list[int], keeps:int):
        return input[:keeps]
    
    @shallowcopy
    def drop_lowest(input:list[int], drops:int):
        return input[drops:]
    
    @shallowcopy
    def drop_highest(input:list[int], drops:int):
        return input[:-drops]
    
    @shallowcopy
    def keep_above(input:list[int], threshold:int):
        return list([i for i in input if i > threshold])
    
    @shallowcopy
    def keep_below(input:list[int], threshold:int):
        return list([i for i in input if i < threshold])

    @shallowcopy
    def chance(input:list[int], chance:int):
        chance = chance/100.0
        for item in input:
            rand = random.random()
            if rand > chance:
                input.remove(item)
        return input
    
    @shallowcopy
    def always(input:list[int], dummy):
        return input
    
    global keys
    keys = {"_": always, "kh": keep_highest, "kl":keep_lowest, "dl":drop_lowest, "dh":drop_highest, "ka":keep_above, "kb":keep_below, "ch":chance}
    def get_filter_from_string(filter:str):
        return keys.get(filter, keys.get("_"))
        # return keys.get("_")