from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import json
from database import init_db, save_appointment, get_all_appointments, create_user, get_user_by_email, get_appointments_by_user, update_appointment_status

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret-key"

init_db()

API_KEY = ""
API_URL = "https://api.groq.com/openai/v1/chat/completions"
BUSINESS_DATA_FILE = "dentist-info.json"

with open(BUSINESS_DATA_FILE, "r") as file:
    business_data = file.read()

SYSTEM_PROMPT = f"""
You are an AI appointment booking assistant for a dental clinic.

Business Information (in JSON format):
{business_data}

Your job:
- Politely collect these details from the patient, one at a time, through natural conversation:
  1. Name
  2. Phone number
  3. Service needed
  4. Preferred date
  5. Preferred time

- Ask only one missing detail at a time. Do not ask for everything at once.
- You can answer questions about clinic hours, location, or services using the information above.
- Be warm, professional, and reassuring.

IMPORTANT - Once you have collected ALL 5 details, do these two things in your reply:
1. Confirm the appointment to the patient in a friendly sentence.
2. On a NEW line, output exactly this format (this line will not be shown to the patient):
APPOINTMENT_DATA: {{"name": "...", "phone": "...", "service": "...", "date": "...", "time": "..."}}

Only output the APPOINTMENT_DATA line once, after all 5 details are known. Never output it early or with missing details.
"""

def send_message(user_msg):
    chat_history = session.get("chat_history", [])
    chat_history.append({"role": "user", "content": user_msg})

    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + chat_history

    response = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"model": "openai/gpt-oss-120b", "messages": full_messages}
    )

    bot_message = response.json()["choices"][0]["message"]["content"]

    chat_history.append({"role": "assistant", "content": bot_message})
    session["chat_history"] = chat_history

    return bot_message

def check_and_extract_booking(bot_message):
    if "APPOINTMENT_DATA:" not in bot_message:
        return bot_message

    clean_reply, data_part = bot_message.split("APPOINTMENT_DATA:", 1)
    appointment_data = json.loads(data_part.strip())
    save_appointment(appointment_data, session["user_id"])

    return clean_reply.strip()

# registration page - user picks a role (patient or owner)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        role = request.form.get("role")

        create_user(name, email, phone, password, role)
        return redirect(url_for("login"))

    return render_template("register.html")

# login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = get_user_by_email(email)

        # user is a tuple: (id, name, email, phone, password, role)
        if user and user[4] == password:
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            session["role"] = user[5]
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# chatbot page - only for logged in patients (owners can view it too, no harm)
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    if "user_id" not in session:
        return jsonify({"reply": "Please login first."}), 401

    user_msg = request.json.get("message")
    bot_reply = send_message(user_msg)
    clean_reply = check_and_extract_booking(bot_reply)
    return jsonify({"reply": clean_reply})

# patient's own appointments page
@app.route("/my-appointments")
def my_appointments():
    if "user_id" not in session:
        return redirect(url_for("login"))

    appointments = get_appointments_by_user(session["user_id"])
    return render_template("my_appointments.html", appointments=appointments)

# owner dashboard - only for users with role "owner"
@app.route("/owner")
def owner():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "owner":
        return "Access denied. Owners only.", 403

    appointments = get_all_appointments()
    return render_template("owner.html", appointments=appointments)

# owner accepts an appointment
@app.route("/owner/accept/<int:appointment_id>")
def accept_appointment(appointment_id):
    if "user_id" not in session or session.get("role") != "owner":
        return redirect(url_for("login"))

    update_appointment_status(appointment_id, "accepted")
    return redirect(url_for("owner"))

# owner denies an appointment
@app.route("/owner/deny/<int:appointment_id>")
def deny_appointment(appointment_id):
    if "user_id" not in session or session.get("role") != "owner":
        return redirect(url_for("login"))

    update_appointment_status(appointment_id, "denied")
    return redirect(url_for("owner"))

if __name__ == "__main__":
    app.run(debug=True)