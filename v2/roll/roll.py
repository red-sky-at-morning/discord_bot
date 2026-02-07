from queue import Full
import random
import re
import discord
import math

# >roll [n]d[n] [filters]
def parse(command:list[str]) -> list[dict]:
    if command[0].startswith("["):
        m = re.search(r"\[(.*)\]", command[-1])
        if m:
            items = m.group(1).split(", ")
        else:
            return[{"type":"message","message":"I don't know how to randomize those items! Try >roll [one, two, three]"}]
        picks = 1

        if len(command) > len(items)+1:
            try:
                picks = int(command[-2])
            except ValueError:
                return[{"type":"message","message":f"I don't know how to randomize those items! Try >roll [one, two, three]"}]
        
        return get_randomized_array_message(items, picks)

    else:
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
    funny_numbers = (69, 420)
    if tot in funny_numbers:
        tot = f"{tot}. nice"

    out_str = ""
    for idx, item in enumerate(rolls):
        r_string = item
        if item not in filtered_rolls:
            r_string = f"~~{r_string}~~"
        else:
            filtered_rolls.remove(item)
        if item == 1:
            r_string = f"*{r_string}*"
        elif item == size:
            r_string = f"**{r_string}**"
        out_str = out_str + (f"{r_string}, ") + ("\n" if (idx+1)%15 == 0 else "")
    out_str = out_str.strip(", \n")

    embed = discord.Embed(description=f"Rolled {iters}d{size}{f'+{bonus}' if bonus else ''} and got **{tot}**")
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

def get_randomized_array_message(items:list[str], picks:int) -> list[dict]:
    randomized, filtered_randomized = randomize(items, picks)

    desc_str = ", ".join(filtered_randomized)

    out_str = ""
    for idx, item in enumerate(randomized):
        r_string = item
        if item in filtered_randomized:
            r_string = f"**{r_string}**"
            filtered_randomized.remove(item)
        out_str = out_str + (f"{r_string}, ") + ("\n" if (idx+1)%15 == 0 else "")
    out_str = out_str.strip(", \n")

    embed = discord.Embed(description=f"Randomized the list [{', '.join(items)}] and got **{desc_str}**")
    embed.add_field(name="Items",value=out_str)

    print(f"results:{randomized}, {filtered_randomized}")
    return [{"type":"message","message":"","embed":embed}]

def randomize(items:list[str], picks:int) -> tuple[list[str]]:
    print(f"picking {picks} items from array {items}")
    out = items.copy()
    
    for idx in range(len(items)-1, 0, -1):
        new_idx = random.randint(0, idx)
        out[idx], out[new_idx] = out[new_idx], out[idx]
    
    return (out, out[:picks])

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