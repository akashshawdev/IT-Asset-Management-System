from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import datetime
import os

app = Flask(__name__)
DB = "itops.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        priority TEXT NOT NULL,
        status TEXT DEFAULT 'Open',
        assignee TEXT DEFAULT 'Unassigned',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        department TEXT NOT NULL,
        role TEXT NOT NULL,
        permissions TEXT NOT NULL,
        workstation TEXT,
        status TEXT DEFAULT 'Pending',
        created_at TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS workstations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT NOT NULL,
        assigned_to TEXT,
        os TEXT NOT NULL,
        last_configured TEXT,
        status TEXT DEFAULT 'Available'
    )''')

    # Seed tickets if empty
    c.execute("SELECT COUNT(*) FROM tickets")
    if c.fetchone()[0] == 0:
        tickets = [
            ("VPN not connecting", "Network", "High", "Resolved", "Akash Shaw", "2026-05-20 09:10", "2026-05-20 11:30"),
            ("Outlook login loop", "Email", "Medium", "Resolved", "Akash Shaw", "2026-05-21 10:00", "2026-05-21 12:15"),
            ("New laptop setup - Marketing", "Hardware", "High", "Resolved", "Akash Shaw", "2026-05-22 08:30", "2026-05-22 14:00"),
            ("Printer offline - 2nd floor", "Hardware", "Low", "In Progress", "Akash Shaw", "2026-05-27 09:00", "2026-05-27 09:45"),
            ("Azure AD sync error", "Cloud", "High", "In Progress", "Akash Shaw", "2026-05-28 11:00", "2026-05-28 11:00"),
            ("Software license request - Adobe", "Software", "Medium", "Open", "Unassigned", "2026-05-29 14:30", "2026-05-29 14:30"),
            ("Wi-Fi drops in meeting room B", "Network", "Medium", "Open", "Unassigned", "2026-05-30 08:00", "2026-05-30 08:00"),
        ]
        c.executemany("INSERT INTO tickets (title,category,priority,status,assignee,created_at,updated_at) VALUES (?,?,?,?,?,?,?)", tickets)

    # Seed users if empty
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        users = [
            ("Lena Hoffmann", "l.hoffmann@homeandco.de", "Marketing", "Marketing Manager", "Drive, Slack, CRM", "WS-BERLIN-014", "Active", "2026-05-10 09:00"),
            ("Markus Braun", "m.braun@homeandco.de", "Finance", "Finance Analyst", "Drive, Slack, SAP", "WS-BERLIN-009", "Active", "2026-05-15 10:00"),
            ("Sophie Weber", "s.weber@homeandco.de", "Operations", "Operations Lead", "Drive, Slack, Jira, Admin Panel", "WS-BERLIN-021", "Active", "2026-05-18 09:30"),
            ("Jonas Klein", "j.klein@homeandco.de", "Sales", "Sales Representative", "Drive, Slack, CRM, HubSpot", None, "Pending", "2026-05-30 08:00"),
        ]
        c.executemany("INSERT INTO users (name,email,department,role,permissions,workstation,status,created_at) VALUES (?,?,?,?,?,?,?,?)", users)

    # Seed workstations if empty
    c.execute("SELECT COUNT(*) FROM workstations")
    if c.fetchone()[0] == 0:
        workstations = [
            ("WS-BERLIN-001", "Tobias Schepers", "Windows 11 Pro", "2026-05-01", "In Use"),
            ("WS-BERLIN-009", "Markus Braun", "Windows 11 Pro", "2026-05-15", "In Use"),
            ("WS-BERLIN-014", "Lena Hoffmann", "macOS Sonoma", "2026-05-10", "In Use"),
            ("WS-BERLIN-021", "Sophie Weber", "Windows 11 Pro", "2026-05-18", "In Use"),
            ("WS-BERLIN-022", None, "Windows 11 Pro", None, "Available"),
            ("WS-BERLIN-023", None, "macOS Sonoma", None, "Available"),
        ]
        c.executemany("INSERT INTO workstations (hostname,assigned_to,os,last_configured,status) VALUES (?,?,?,?,?)", workstations)

    conn.commit()
    conn.close()

# ── Routes ──────────────────────────────────────────────

@app.route("/")
def index():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    open_t = conn.execute("SELECT COUNT(*) FROM tickets WHERE status='Open'").fetchone()[0]
    inprog = conn.execute("SELECT COUNT(*) FROM tickets WHERE status='In Progress'").fetchone()[0]
    resolved = conn.execute("SELECT COUNT(*) FROM tickets WHERE status='Resolved'").fetchone()[0]
    users_pending = conn.execute("SELECT COUNT(*) FROM users WHERE status='Pending'").fetchone()[0]
    recent_tickets = conn.execute("SELECT * FROM tickets ORDER BY created_at DESC LIMIT 5").fetchall()
    conn.close()
    return render_template("index.html",
        total=total, open_t=open_t, inprog=inprog,
        resolved=resolved, users_pending=users_pending,
        recent_tickets=recent_tickets)

@app.route("/tickets")
def tickets():
    status_filter = request.args.get("status", "All")
    priority_filter = request.args.get("priority", "All")
    conn = get_db()
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []
    if status_filter != "All":
        query += " AND status=?"
        params.append(status_filter)
    if priority_filter != "All":
        query += " AND priority=?"
        params.append(priority_filter)
    query += " ORDER BY created_at DESC"
    tickets = conn.execute(query, params).fetchall()
    conn.close()
    return render_template("tickets.html", tickets=tickets,
        status_filter=status_filter, priority_filter=priority_filter)

@app.route("/tickets/new", methods=["POST"])
def new_ticket():
    title = request.form["title"]
    category = request.form["category"]
    priority = request.form["priority"]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_db()
    conn.execute("INSERT INTO tickets (title,category,priority,status,assignee,created_at,updated_at) VALUES (?,?,?,'Open','Unassigned',?,?)",
        (title, category, priority, now, now))
    conn.commit()
    conn.close()
    return redirect(url_for("tickets"))

@app.route("/tickets/update/<int:tid>", methods=["POST"])
def update_ticket(tid):
    status = request.form["status"]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_db()
    conn.execute("UPDATE tickets SET status=?, updated_at=? WHERE id=?", (status, now, tid))
    conn.commit()
    conn.close()
    return redirect(url_for("tickets"))

@app.route("/users")
def users():
    conn = get_db()
    users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    workstations = conn.execute("SELECT * FROM workstations WHERE status='Available'").fetchall()
    conn.close()
    return render_template("users.html", users=users, workstations=workstations)

@app.route("/users/new", methods=["POST"])
def new_user():
    name = request.form["name"]
    email = request.form["email"]
    department = request.form["department"]
    role = request.form["role"]
    permissions = request.form.getlist("permissions")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_db()
    conn.execute("INSERT INTO users (name,email,department,role,permissions,status,created_at) VALUES (?,?,?,?,?,'Pending',?)",
        (name, email, department, role, ", ".join(permissions), now))
    conn.commit()
    conn.close()
    return redirect(url_for("users"))

@app.route("/users/activate/<int:uid>", methods=["POST"])
def activate_user(uid):
    workstation = request.form.get("workstation", "")
    conn = get_db()
    conn.execute("UPDATE users SET status='Active', workstation=? WHERE id=?", (workstation, uid))
    if workstation:
        conn.execute("UPDATE workstations SET status='In Use', assigned_to=(SELECT name FROM users WHERE id=?) WHERE hostname=?", (uid, workstation))
    conn.commit()
    conn.close()
    return redirect(url_for("users"))

@app.route("/workstations")
def workstations():
    conn = get_db()
    ws = conn.execute("SELECT * FROM workstations ORDER BY status, hostname").fetchall()
    conn.close()
    return render_template("workstations.html", workstations=ws)

@app.route("/workstations/configure/<int:wid>", methods=["POST"])
def configure_workstation(wid):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_db()
    conn.execute("UPDATE workstations SET last_configured=? WHERE id=?", (now, wid))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "timestamp": now})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
