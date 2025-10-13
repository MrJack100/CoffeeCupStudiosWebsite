import requests, json, time, math
from termcolor import colored
import pandas as pd
from player import Player

def get_player_data():
    d = requests.get("http://108.248.215.239:25560/getPlayer")
    d.encoding = d.apparent_encoding
    response = json.loads(d.text)
    full_data = []
    for player in response:
        if player["Speed"] == 0:
            moving = False
        else:
            moving = True
        extracted_data = {
            "coordinates": {
                "x": player["location"]["x"],
                "y": player["location"]["y"],
                "z": player["location"]["z"]
            },
            "moving": moving,
            "name": player["features"]["properties"]["name"]
        }
        full_data.append(extracted_data)
    return(full_data)

def record_trigger(target_name:str):
    full_data = get_player_data()
    target_found = False
    for data in full_data:
        if target_name in data["name"]:
            target_found = True
            target_data = data
            break
        else:
            pass
    if not target_found:
        print("Target not found, stopping")
        return(None)
    new_trigger = target_data["coordinates"]["y"]
    return(new_trigger)

def check_commands():
    r = requests.get("http://108.248.215.239:25560/getChatMessages")
    r.encoding = r.apparent_encoding
    data = json.loads(r.text)
    message = data[-1]
    if message["Sender"] == "Aquatic":
        if "adminAquaticRecordTrigger" in message["Message"]:
            name = message["Message"].replace("adminAquaticRecordTrigger ", "")
            new_trigger = record_trigger("Aquatic")
            with open("triggers.json", "r") as file:
                existing_triggers = json.loads(file.read())
            for trigger in existing_triggers:
                if name == trigger["name"]:
                    return(None)
            with open("triggers.json", "w") as file:
                existing_triggers.append({"name": name, "height": new_trigger})
                file.write(json.dumps(existing_triggers))
            print(f"New trigger created under name {name} at {new_trigger}")

def update_player_info(player_object_list):
    player_data_list = get_player_data()
    print(colored(len(player_data_list), "magenta"))
    returning_player_list = []
    for player_data in player_data_list:
        if player_data["name"] != "":
            print(player_data)
            print(player_object_list)
            match_made = False
            for player_object in player_object_list:
                if player_object.name == player_data["name"]: # match made
                    match_made = True
                    player_object.coordinates.update(player_data["coordinates"])
                    player_object.last_seen_timestamp = time.time()
                    returning_player_list.append(player_object)
                    print(colored(f"Match made between {player_object} and \"{player_data["name"]}\", coordinates updated", "light_blue"))
                    print(colored(f"Last_seen_timestamp is {player_object.last_seen_timestamp}", "light_blue"))
            if not match_made: # no match made now need to determine if new player has joined or old player has left
                print(colored(f"No match made with \"{player_data["name"]}\"", "light_yellow"))
                new_player = Player(player_data["name"])
                new_player.coordinates = player_data["coordinates"]
                new_player.last_seen_timestamp = time.time()
                returning_player_list.append(new_player)
            print("---")
    for player_object in player_object_list:
        if (player_object in returning_player_list):
            pass
        else:
            returning_player_list.append(player_object)
    return(returning_player_list)

def apply_hitbox_tags(player_list, hitboxes):
    for player in player_list:
        # Ensure player is inside the tower
        x_axis, y_axis = False, False
        if (player.coordinates["x"] > 14397.377902408776) and (player.coordinates["x"] < 31124.373651582413):
            x_axis = True
        else:
            x_axis = False
        if (player.coordinates["y"] > -28309.481527612134) and (player.coordinates["y"] < -23845.810039281783):
            y_axis = True
        else:
            y_axis = False
        if x_axis and y_axis:
            # Check hitboxes
            for hitbox in hitboxes:
                if player.coordinates["z"] >= hitbox["height"]:
                    if hitbox in player.tags:
                        pass
                    else:
                        player.tags.append(hitbox)
                elif player.coordinates["z"] < hitbox["height"]:
                    if hitbox in player.tags:
                        player.tags.remove(hitbox)
                        player.fail_counter += 1
                    else:
                        pass
                else:
                    pass
            # {'coordinates': {'x': 31124.373651582413, 'y': -28309.481527612134, 'z': 63265.1396852457}, 'moving': False, 'name': 'Aquatic'}
            # {'coordinates': {'x': 14397.377902408776, 'y': -23845.810039281783, 'z': 63265.13970277222}, 'moving': False, 'name': 'Aquatic'}
            dx = (22707.163884883645 - player.coordinates["x"])
            dy = (-26036.91355881732 - player.coordinates["y"])
            distance_from_centre_radius = math.sqrt((dx ** 2) + (dy ** 2))
            if distance_from_centre_radius >= 18000:
                player.tags.append({"name": "killzone", "height": None})
        else:
            pass

def clear_disconnected(player_list, data):
    returning_player_list = []
    for player in player_list:
        if (time.time() - player.last_seen_timestamp) >= 3: # Player has disconnected!
            new_row = pd.DataFrame({"name": [player.name], "fails": [player.fail_counter]})
            data = pd.concat([data, new_row])   
            print(colored(f"Player with name {player.name} has disconnected", "light_blue"))
        else:
            returning_player_list.append(player)
    return(returning_player_list, data)

def cycle(seconds, interval, player_object_list, data):
    for _ in range(seconds):
        print(colored("Begin Cycle", "light_green"))
        player_object_list, data = clear_disconnected(player_object_list, data)
        player_object_list = update_player_info(player_object_list)
        apply_hitbox_tags(player_object_list, hitboxes=[{"name": "level01", "height": 17116.406155571487}, {"name": "level00", "height": 13561.826156406483}])
        print(colored("End Cycle", "dark_grey"))
        print(player_object_list)
        time.sleep(interval)
    return(player_object_list, data)

player_object_list = []
data = pd.read_csv("data.csv")
while True:
    # Run for 20 seconds with 1 second intervals
    player_object_list, data = cycle(5, 1, player_object_list, data)
    for player in player_object_list: # This doesn't duplicate disconnected players because they are removed
        if hasattr(player, "last_logged_fail_counter"): # This is so we don't add the previous fails
            delta = player.fail_counter - player.last_logged_fail_counter
        else:
            delta = player.fail_counter
        player.last_logged_fail_counter = player.fail_counter
        new_row = pd.DataFrame({"name": [player.name], "fails": [delta]})
        data = pd.concat([data, new_row])
    # Clear up database
    grouped = data.groupby("name", as_index=False)["fails"].sum()
    grouped.to_csv("data.csv", index=False)