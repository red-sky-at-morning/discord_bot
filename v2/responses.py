import random

# do things better this time
def handle_message(message:str, user_id:int, server:int, **kwargs) -> list[dict]:
    m_list:list = message.lower().split().append(message)
    response:list = []

    match m_list[0]:
        case _:
            num = random.random()
            if num < 0.05:
                response.append({"type":"wait","time":20})
    return response