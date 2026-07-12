from flask import Flask, render_template, request, redirect
import sqlite3
import csv
from flask import Response

app = Flask(__name__)

# ---------------- HOME PAGE ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- ABOUT PAGE ----------------

@app.route("/about")
def about():
    return render_template("about.html")


# ---------------- REQUEST PAGE ----------------

@app.route("/request")
def request_page():
    return render_template("request.html")


# ---------------- SUBMIT FORM ----------------

@app.route("/submit", methods=["POST"])
def submit():

    ambulance = request.form["ambulance"]
    driver = request.form["driver"]
    mobile = request.form["mobile"]
    patient_name = request.form["patient_name"]
    patient_age = request.form["patient_age"]
    emergency = request.form["emergency"]
    location = request.form["location"]
    hospital = request.form["hospital"]
    distance = request.form["distance"]
    notes = request.form["notes"]

    conn = sqlite3.connect("emergency.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO emergency_requests
    (
        ambulance_number,
        driver_name,
        mobile_number,
        patient_name,
        patient_age,
        emergency_type,
        current_location,
        destination_hospital,
        distance,
        notes,
        status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        ambulance,
        driver,
        mobile,
        patient_name,
        patient_age,
        emergency,
        location,
        hospital,
        distance,
        notes,
        "Pending"
    ))

       

    conn.commit()
    conn.close()

    return redirect("/login")



# ---------------- ADMIN PAGE ----------------

# ---------------- ADMIN PAGE ----------------

@app.route("/admin")
def admin():

    search = request.args.get("search", "")

    conn = sqlite3.connect("emergency.db")
    cursor = conn.cursor()

    if search:

        cursor.execute("""
        SELECT * FROM emergency_requests
        WHERE ambulance_number LIKE ?
        OR patient_name LIKE ?
        """,
        (f"%{search}%", f"%{search}%"))

    else:

        cursor.execute("SELECT * FROM emergency_requests")

    data = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM emergency_requests")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM emergency_requests WHERE status='Approved'")
    approved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM emergency_requests WHERE status='Rejected'")
    rejected = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM emergency_requests WHERE status='Pending'")
    pending = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        data=data,
        total=total,
        approved=approved,
        rejected=rejected,
        pending=pending,
        search=search
    )


# ---------------- LOGIN PAGE ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            return redirect("/admin")

        return "<h2>❌ Invalid Username or Password</h2>"

    return render_template("login.html")


# ---------------- APPROVE REQUEST ----------------

@app.route("/approve/<int:id>")
def approve(id):

    conn = sqlite3.connect("emergency.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE emergency_requests SET status='Approved' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- REJECT REQUEST ----------------

@app.route("/reject/<int:id>")
def reject(id):

    conn = sqlite3.connect("emergency.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE emergency_requests SET status='Rejected' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- POLICE DASHBOARD ----------------

@app.route("/police")
def police():

    conn = sqlite3.connect("emergency.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM emergency_requests
        WHERE status='Approved'
    """)

    data = cursor.fetchall()

    conn.close()

    return render_template("police.html", data=data)


# ---------------- HOSPITAL DASHBOARD ----------------

@app.route("/hospital")
def hospital_dashboard():

    conn = sqlite3.connect("emergency.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM emergency_requests
        WHERE status='Approved'
    """)

    data = cursor.fetchall()

    conn.close()

    return render_template("hospital.html", data=data)
# ---------------- MAP PAGE ----------------

@app.route("/map")
def map():
    return render_template("map.html")

# ---------------- TRAFFIC DASHBOARD ----------------

@app.route("/traffic")
def traffic():

    conn = sqlite3.connect("emergency.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM emergency_requests
        WHERE status='Approved'
    """)

    data = cursor.fetchall()

    conn.close()

    return render_template("traffic.html", data=data)
# ---------------- EXPORT CSV ----------------

@app.route("/export")
def export():

    conn = sqlite3.connect("emergency.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM emergency_requests")
    rows = cursor.fetchall()

    conn.close()

    def generate():

        data = csv.writer(Echo())

        yield data.writerow([
            "ID",
            "Ambulance",
            "Driver",
            "Mobile",
            "Patient",
            "Age",
            "Emergency",
            "Location",
            "Hospital",
            "Distance",
            "Notes",
            "Status"
        ])

        for row in rows:
            yield data.writerow(row)

    class Echo:
        def write(self, value):
            return value

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=EmergencyRequests.csv"
        }
    )
# ---------------- DELETE REQUEST ----------------

@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("emergency.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM emergency_requests WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")
    # ---------------- NOTIFICATIONS ----------------

@app.route("/notifications")
def notifications():

    conn = sqlite3.connect("emergency.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM emergency_requests
        WHERE status='Approved'
    """)

    data = cursor.fetchall()

    conn.close()

    return render_template("notifications.html", data=data)


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)