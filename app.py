from flask import Flask, render_template
import time

app = Flask(__name__)

menu_script = '''<script>
        function openMenu() {
            var x = document.getElementById("menu-mobile");
            if (x.style.display === "flex") {
                x.style.display = "none";
            } else {
                x.style.display = "flex";
            }
        } 
    </script>'''

menu_html = '''<section id="navbar-section">
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
    <section id="information-section">
        <div>
            <p>
                Hello Pioneers, John Coffee Cup from Coffee Cup Studios here. I've just learned that Coffee Stain
                Studios will be releasing their game on console this November. This will give them a huge leg up in the
                market, so we will have to respond. I believe the best way to ensure a victory over the “Stainers” is to
                build a giant obstacle-course tower and race factory carts to the top.</br></br>
                -John Coffee Cup (Founder & CEO)</p>
            <a href="/eventinfo">Event Information</a>
        </div>
    </section>'''

@app.route("/")
def root():
    return render_template("index.html", menu_script=menu_script, menu_html=menu_html)

@app.route("/data")
def data():
    number = time.ctime()
    return render_template("data.html", time=number)

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
    return render_template("eventinfo.html", discord_link="https://discord.gg/Ywa4jfn8hG", menu_script=menu_script, menu_html=menu_html)

@app.route("/submitlevel")
def submit_level():
    # Delete this before November!
    if (time.gmtime())[2] <= 15:
        open = True
    else:
        open = False
    return render_template("submitlevel.html", form_link="https://docs.google.com/forms/d/e/1FAIpQLSdY048SsmOonBgR_u5R6QDFcViwNoxHHw9A2rOjmMCeTds4Rw/viewform", open=open, menu_script=menu_script, menu_html=menu_html)

@app.route("/serverhelp")
def server_help():
    return render_template("serverhelp.html", discord_link="https://discord.gg/Ywa4jfn8hG", menu_script=menu_script, menu_html=menu_html)

if __name__ == "__main__":
    app.run(debug=True)