from dateutil import parser
from dateutil.tz import tzutc
import datetime as dt
import discord

def get_time(e_message):
    # Get the time
    if "now" in (e_message):
        # Format: now + 5 mins
        if "+" in e_message:
            # String manipulation
            e_message = e_message.split("+")
            e_message[1] = e_message[1].strip()[:5]
            print(e_message)
            try:
                time = int(e_message[1][:-4])
            except Exception as e:
                # Add error handling
                print(e)
        else:
            time = 0
        # Set time to utcnow + provided time
        return_time = discord.utils.utcnow() + dt.timedelta(time)
    else:
        # If the time isn't relative, use the parser to parse it
        return_time = parser.parse(e_message)
    return return_time

def get_event_data(e_message):
    # String manipulation
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
    
    # Add error handling
    if (end_time.tzinfo == tzutc()):
        end_time.tzinfo == dt.timezone.utc
    if (start_time.tzinfo == tzutc()):
        start_time.tzinfo == dt.timezone.utc
    
    # Return
    return ({"name":name,"location":location,"start":start_time,"end":end_time})