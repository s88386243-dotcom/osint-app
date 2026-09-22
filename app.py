from flask import Flask, render_template, request, session
import requests, os, json

app = Flask(__name__)
app.secret_key = "supersecret"  # change this

API_KEY = os.getenv("LOOKUP_API_KEY")
LOG_FILE = "logs.json"

def save_log(entry):
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def check_limit():
    if "search_count" not in session:
        session["search_count"] = 0
    session["search_count"] += 1
    return session["search_count"]

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        count = check_limit()
        if count > 2 and "premium" not in session:
            return render_template("premium.html")

        number = request.form["number"]
        response = requests.get(
            f"https://your-api.com/lookup?number={number}",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        data = response.json()

        # Save log
        save_log({"number": number, "result": data})

        # Save user history (last 5 searches)
        if "history" not in session:
            session["history"] = []
        session["history"].append(number)
        session["history"] = session["history"][-5:]

        return render_template("result.html", data=data, number=number, history=session["history"])
    return render_template("index.html")

@app.route("/unlock")
def unlock():
    session["premium"] = True
    return "✅ Premium unlocked!"

@app.route("/admin")
def admin():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    else:
        logs = []
    total_searches = len(logs)
    premium_users = 1 if "premium" in session else 0
    return render_template("admin.html", logs=logs, total=total_searches, premium=premium_users)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
ECHO is on.
