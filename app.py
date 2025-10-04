from flask import Flask, render_template
import time

app = Flask(__name__)

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/data")
def data():
    number = time.ctime()
    return render_template("data.html", time=number)

@app.route("/serverlist")
def server_list():
    servers = [{"name": "Server 1", "online": "12", "ip": "127.0.0.1", "port": "1324", "password": "anotheruser"}, {"name": "Server 2", "online": "15", "ip": "127.0.0.1", "port": "1324", "password": "milk"}]
    rendered_servers = ""
    for server in servers:
        rendered_servers = rendered_servers + f"{(render_template("serverlist.html", name=server["name"], online=server["online"], ip=server["ip"], port=server["port"], password=server["password"]))}"
    return rendered_servers

@app.route("/eventinfo")
def event_info():
    return render_template("eventinfo.html", discord_link="https://discord.gg/Ywa4jfn8hG")

@app.route("/submitlevel")
def submit_level():
    # Delete this before November!
    if (time.gmtime())[2] <= 15:
        open = True
    else:
        open = False
    return render_template("submitlevel.html", form_link="https://docs.google.com/forms/d/e/1FAIpQLSdY048SsmOonBgR_u5R6QDFcViwNoxHHw9A2rOjmMCeTds4Rw/viewform", open=open)

if __name__ == "__main__":
    app.run(debug=True)