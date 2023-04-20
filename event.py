from dateutil import parser
from dateutil.tz import tzutc
import datetime as dt
import discord

def get_time(e_message):
    if "now" in (e_message):
        # now + 5 mins
        if "+" in e_message:
            e_message = e_message.split("+")
            e_message[1] = e_message[1].strip()[:5]
            print(e_message)
            try:
                time = int(e_message[1][:-4])
            except Exception as e:
                print(e)
        else:
            time = 0
        return_time = discord.utils.utcnow() + dt.timedelta(time)
    else:
        return_time = parser.parse(e_message)
    return return_time

def get_event_data(e_message):
    e_message = e_message.split("<")
    e_message[0] = e_message[0].split("\"")
    for item in e_message[0]:
        if item == '' or item == ' ':
            e_message[0].remove(item)
    name = e_message[0][0]
    location = e_message[0][1]
    e_message[1], e_message[2] = e_message[1][0:-2], e_message[2][0:-1]
    
    start_time = get_time(e_message[1])
    end_time = get_time(e_message[2])
    
    if (end_time.tzinfo == tzutc()):
        end_time.tzinfo == dt.timezone.utc
    if (start_time.tzinfo == tzutc()):
        start_time.tzinfo == dt.timezone.utc
    
    return ({"name":name,"location":location,"start":start_time,"end":end_time})