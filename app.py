from wtforms import StringField, SubmitField
from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm, CSRFProtect
from wtforms.validators import DataRequired
import time, threading, json
import pandas as pd

app = Flask(__name__)
app.secret_key = "secretkey"
csrf = CSRFProtect(app)

class SearchForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), ])
    submit = SubmitField("Search")

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
        <div id="subdiv">
            <span onclick="openMenu()" class="material-symbols-outlined">
                menu
            </span>
            <a href="/" id="header">Coffee Cup Studios</a>
            <div id="menu-mobile">
                <p class="menu-component" id="header">Coffee Cup Studios</p>
                <a class="menu-component" href="#">Mod Installer</a>
                <a class="menu-component" href="/submitlevel">Submit Level</a>
                <a class="menu-component" href="/eventinfo">Event Information</a>
            </div>
        </div>
    </section>
    '''

# Global variables
global entire_tower_fail
global servers

def get_globals():
    while True:
        # Get global stats
        global_data = pd.read_csv("global_data.csv")
        global entire_tower_fail
        entire_tower_fail = int(global_data["entire_tower_fail"][0])

        # Get server list
        global servers
        with open("server_data.json") as file:
            servers = json.loads(file.read())
        
        time.sleep(10)

x = threading.Thread(target=get_globals)
x.start()

@app.route("/", methods=["GET", "POST"])
def root():
    '''form = SearchForm()
    if form.validate_on_submit:
        username = form.username.data
        return redirect(f"/playerdata/{username}")'''
    #return render_template("index.html", menu_head=menu_head, menu_body=menu_body, form=form, global_stats=True, username=None)
    form = SearchForm()
    if form.validate_on_submit:
        username = form.username.data
        return render_template("index.html", menu_head=menu_head, menu_body=menu_body, form=form, global_stats=False, username=username)
    return render_template("index.html", menu_head=menu_head, menu_body=menu_body, form=form, global_stats=True, username=None)

@app.route("/data")
def data():
    return render_template("data.html", entire_tower_fail=entire_tower_fail)

@app.route("/serverlist")
def server_list():
    #servers = [{"name": "Server 1", "online": "12", "capacity": "24", "ip": "127.0.0.1", "port": "1324", "password": "anotheruser"}, {"name": "Server 2", "online": "15", "capacity": "24", "ip": "127.0.0.1", "port": "1324", "password": "milk"}]
    rendered_servers = ""
    for server in servers:
        percentage = (int(server["online"]) / int(server["capacity"])) * 100
        if percentage <= 50:
            colour = "green"
        elif percentage <= 75:
            colour = "amber"
        else:
            colour = "red"
        rendered_servers = rendered_servers + f"{(render_template("serverlist.html", name=server["name"], online=server["online"], capacity=server["capacity"], ip=server["ip"], port=server["port"], password=server["password"], percentage=percentage, colour=colour))}"
    return rendered_servers

@app.route("/eventinfo")
def event_info():
    return render_template("eventinfo.html", discord_link="https://discord.gg/Ywa4jfn8hG", menu_head=menu_head, menu_body=menu_body)

@app.route("/submitlevel")
def submit_level():
    # Delete this before December!
    if (time.gmtime())[2] <= 30:
        open = True
    else:
        open = False
    return render_template("submitlevel.html", form_link="https://docs.google.com/forms/d/e/1FAIpQLSdY048SsmOonBgR_u5R6QDFcViwNoxHHw9A2rOjmMCeTds4Rw/viewform", open=open, menu_head=menu_head, menu_body=menu_body)

@app.route("/playerdata/<username>", methods=["GET", "POST"])
def playerdata(username):
    player_data = pd.read_csv("player_data.csv")
    not_present = not player_data["name"].str.lower().eq(username.lower()).any()
    if not_present:
        return render_template("data.html", entire_tower_fail=entire_tower_fail)
    row = player_data[player_data["name"].str.lower() == username.lower()].squeeze()
    player_entire_tower_fail = str(row["entire_tower_fail"])
    return render_template("data.html", entire_tower_fail=player_entire_tower_fail)
    
@app.route("/serverhelp")
def server_help():
    return render_template("serverhelp.html", discord_link="https://discord.gg/Ywa4jfn8hG", menu_head=menu_head, menu_body=menu_body)

if __name__ == "__main__":
    app.run(debug=True)