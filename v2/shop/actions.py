from inventories import inventories

def perform(user_id: int, actions: list[dict]) -> list[dict]:
    response:list[dict] = []
    if not actions:
        return response
    for action in actions:
        match action.get("type"):
            case "change_resource":
                change_resource(user_id, action.get("resource"), action.get("amount"))
            case "set_resource":
                set_resource(user_id, action.get("resource"), action.get("amount"))
            case "message":
                response.append({"type":"message","message":action.get("message")})
            case _:
                raise TypeError(f"Unexpected action in shop: {action.get("type")}")
    return response

def change_resource(user_id:int, resource:str, amount:int):
    meta = inventories.get_meta(user_id)
    user_resource = meta.get(resource)
    user_resource += amount
    inventories.add_meta(user_id, resource, user_resource)

def set_resource(user_id:int, resource:str, value:any):
    inventories.add_meta(user_id, resource, value)

# perform_action(1, [{"type": "change_resource", "resource": "rod_level", "amount": 1}])
