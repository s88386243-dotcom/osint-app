from flask import Flask, render_template, request, jsonify
import os, json, requests

app = Flask(__name__)

# Load logs
LOG_FILE = "logs.json"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("[]")

def save_log(number, result):
    with open(LOG_FILE, "r+") as f:
        logs = json.load(f)
        logs.append({"number": number, "result": result})
        f.seek(0)
        json.dump(logs, f, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lookup", methods=["POST"])
def lookup():
    number = request.form.get("number")
    api_key = os.getenv("LOOKUP_API_KEY", "")
    # Example API call (replace with your actual API)
    response = requests.get(f"https://your-api.com/lookup?number={number}&key={api_key}")
    data = response.json()
    save_log(number, data)
    return render_template("result.html", number=number, data=data, history=[number])

@app.route("/premium")
def premium():
    return render_template("premium.html")

@app.route("/admin")
def admin():
    with open(LOG_FILE) as f:
        logs = json.load(f)
    total = len(logs)
    premium = sum(1 for log in logs if "premium" in log.get("result", {}))
    return render_template("admin.html", logs=logs, total=total, premium=premium)

if __name__ == "__main__":
    # ✅ Important Fix: Bind to 0.0.0.0 and PORT env
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
