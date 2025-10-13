import requests, json, time, math
from termcolor import colored
import pandas as pd
from player import Player
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

# Get hitboxes
with open("hitboxes.json", "r") as file:
    hitboxes = json.loads(file.read())
hitbox_list = []
for hitbox in hitboxes:
    x1 = hitbox["hitbox"]["coordinate1"]["x"]
    x2 = hitbox["hitbox"]["coordinate2"]["x"]
    x3 = hitbox["hitbox"]["coordinate3"]["x"]
    x4 = hitbox["hitbox"]["coordinate4"]["x"]
    y1 = hitbox["hitbox"]["coordinate1"]["y"]
    y2 = hitbox["hitbox"]["coordinate2"]["y"]
    y3 = hitbox["hitbox"]["coordinate3"]["y"]
    y4 = hitbox["hitbox"]["coordinate4"]["y"]
    bounding_box = Polygon([(x1,y1), (x2,y2), (x3,y3),(x4, y4)])
    hitbox.update({"hitbox": {"bounding_box": bounding_box, "top_z": hitbox["hitbox"]["top_z"], "bottom_z": hitbox["hitbox"]["bottom_z"]}})
    hitbox_list.append(hitbox)

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

def apply_values(player, hitbox_data, event):
    hitbox_name = hitbox_data["name"]
    new_row = lambda player,stat,increment:pd.DataFrame({"name": [player.name], stat: increment})
    # Fell out of tower
    if (hitbox_name == "entire_tower_fail") and (event == "leave"):
        return(new_row(player, "entire_tower_fail", 1))
    if (hitbox_name == "level_01_spin") and (event == "enter"):
        return(new_row(player, "level_01_spin", 1))

def apply_hitbox_tags(player_list, data):
    for player in player_list:
        for hitbox in hitboxes:
            player_point = Point(player.coordinates["x"], player.coordinates["y"])
            intersecting_z = False
            intersecting_xy = hitbox["hitbox"]["bounding_box"].contains(player_point)
            if (player.coordinates["z"] > hitbox["hitbox"]["bottom_z"]) and (player.coordinates["z"] <= hitbox["hitbox"]["top_z"]):
                intersecting_z = True
            print(colored(f"{hitbox["name"]}, {intersecting_xy}, {intersecting_z}", "light_yellow"))
            if intersecting_xy and intersecting_z: # Add/keep tag
                if hitbox in player.tags:
                    new_row = apply_values(player=player, hitbox_data=hitbox, event="inside")
                    data = pd.concat([data, new_row], ignore_index=True)
                else:
                    player.tags.append(hitbox)
                    new_row = apply_values(player=player, hitbox_data=hitbox, event="enter")
                    data = pd.concat([data, new_row], ignore_index=True)
            else: # Remove/ignore tag
                if hitbox in player.tags:
                    player.tags.remove(hitbox)
                    new_row = apply_values(player=player, hitbox_data=hitbox, event="leave")
                    data = pd.concat([data, new_row], ignore_index=True)
                else:
                    new_row = apply_values(player=player, hitbox_data=hitbox, event="outside")
                    data = pd.concat([data, new_row], ignore_index=True)
    return(data)

def clear_disconnected(player_list, data):
    returning_player_list = []
    for player in player_list:
        if (time.time() - player.last_seen_timestamp) >= 3: # Player has disconnected!
            new_row = pd.DataFrame({"name": [player.name], "entire_tower_fail": [player.fail_counter]})
            data = pd.concat([data, new_row], ignore_index=True)   
            print(colored(f"Player with name {player.name} has disconnected", "light_blue"))
        else:
            returning_player_list.append(player)
    return(returning_player_list, data)

def cycle(seconds, interval, player_object_list, data):
    for _ in range(seconds):
        print(colored("Begin Cycle", "light_green"))
        player_object_list, data = clear_disconnected(player_object_list, data)
        player_object_list = update_player_info(player_object_list)
        data = apply_hitbox_tags(player_object_list, data)
        print(player_object_list[0].coordinates)
        print(player_object_list[0].tags)
        print(colored("End Cycle", "dark_grey"))
        time.sleep(interval)
    return(player_object_list, data)

player_object_list = []
data = pd.read_csv("data.csv")
while True:
    # Run for 20 seconds with 1 second intervals
    player_object_list, data = cycle(5, 1, player_object_list, data)
    ''' for player in player_object_list: # This doesn't duplicate disconnected players because they are removed
        if hasattr(player, "last_logged_fail_counter"): # This is so we don't add the previous fails
            delta = player.fail_counter - player.last_logged_fail_counter
        else:
            delta = player.fail_counter
        player.last_logged_fail_counter = player.fail_counter
        new_row = pd.DataFrame({"name": [player.name], "tower_fails": [delta]})
        data = pd.concat([data, new_row])'''
    # Clear up database
    column_to_group = ["entire_tower_fail", "level_01_spin"]
    grouped = data.groupby("name", as_index=False)[column_to_group].sum()
    grouped.to_csv("data.csv", index=False)