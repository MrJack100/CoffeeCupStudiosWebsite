from flask import Flask, render_template
import time, threading
import pandas as pd

app = Flask(__name__)

menu_head = '''
    <link rel="stylesheet" href="static/menu.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&icon_names=menu"/>
    <script>
        function openMenu() {
            var x = document.getElementById("menu-mobile");
            if (x.style.display === "flex") {
                x.style.display = "none";
            } else {
                x.style.display = "flex";
            }
        } 
    </script>'''

menu_body = '''<section id="navbar-section">
        <span onclick="openMenu()" class="material-symbols-outlined">
            menu
        </span>
        <p id="header">Coffee Cup Studios</p>
        <div id="menu-mobile">
            <p class="menu-component" id="header">Coffee Cup Studios</p>
            <a class="menu-component" href="#">Mod Installer</a>
            <a class="menu-component" href="/submitlevel">Submit Level</a>
        </div>
    </section>
    '''

# Global variables
global entire_tower_fail

def get_globals():
    while True:
        # Get global stats
        global_data = pd.read_csv("global_data.csv")
        global entire_tower_fail
        entire_tower_fail = int(global_data["entire_tower_fail"][0])

        # Get server list
        
        time.sleep(15)

x = threading.Thread(target=get_globals)
x.start()

@app.route("/")
def root():
    return render_template("index.html", menu_head=menu_head, menu_body=menu_body)

@app.route("/data")
def data():
    return render_template("data.html", entire_tower_fail=entire_tower_fail)

@app.route("/serverlist")
def server_list():
    servers = [{"name": "Server 1", "online": "12", "capacity": "24", "ip": "127.0.0.1", "port": "1324", "password": "anotheruser"}, {"name": "Server 2", "online": "15", "capacity": "24", "ip": "127.0.0.1", "port": "1324", "password": "milk"}]
    rendered_servers = ""
    for server in servers:
        percentage = (int(server["online"]) / int(server["capacity"])) * 100
        if percentage <= 50:
            colour = "green"
        elif percentage <= 75:
            colour = "amber"
        else:
            colour = "red"
        rendered_servers = rendered_servers + f"{(render_template("serverlist.html", name=server["name"], online=server["online"], ip=server["ip"], port=server["port"], password=server["password"], percentage=percentage, colour=colour))}"
    return rendered_servers

@app.route("/eventinfo")
def event_info():
    return render_template("eventinfo.html", discord_link="https://discord.gg/Ywa4jfn8hG", menu_head=menu_head, menu_body=menu_body)

@app.route("/submitlevel")
def submit_level():
    # Delete this before November!
    if (time.gmtime())[2] <= 15:
        open = True
    else:
        open = False
    return render_template("submitlevel.html", form_link="https://docs.google.com/forms/d/e/1FAIpQLSdY048SsmOonBgR_u5R6QDFcViwNoxHHw9A2rOjmMCeTds4Rw/viewform", open=open, menu_head=menu_head, menu_body=menu_body)

@app.route("/serverhelp")
def server_help():
    return render_template("serverhelp.html", discord_link="https://discord.gg/Ywa4jfn8hG", menu_head=menu_head, menu_body=menu_body)

if __name__ == "__main__":
    app.run(debug=True)