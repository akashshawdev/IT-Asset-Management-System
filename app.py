from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import sqlite3
import datetime
import os

app = Flask(__name__)
CORS(app)

DB = "itops.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row):
    return dict(row) if row else None

def rows_to_list(rows):
    return [dict(r) for r in rows]

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        user_email TEXT DEFAULT '',
        category TEXT DEFAULT 'General',
        priority TEXT NOT NULL DEFAULT 'medium',
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
        permissions TEXT NOT NULL DEFAULT '',
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

    c.execute('''CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        assigned_to TEXT DEFAULT '',
        serial_number TEXT DEFAULT '',
        status TEXT DEFAULT 'active',
        created_at TEXT NOT NULL
    )''')


    # Migration: add columns if they dont exist
    try:
        c.execute("ALTER TABLE tickets ADD COLUMN user_email TEXT DEFAULT """)
        conn.commit()
    except:
        pass
    # Seed tickets
    c.execute("SELECT COUNT(*) FROM tickets")
    if c.fetchone()[0] == 0:
        tickets = [
            ("VPN not connecting", "User cannot connect to VPN", "m.braun@homeandco.de", "Network", "High", "Resolved", "Akash Shaw", "2026-05-20 09:10", "2026-05-20 11:30"),
            ("Outlook login loop", "Outlook keeps asking for password", "l.hoffmann@homeandco.de", "Email", "Medium", "Resolved", "Akash Shaw", "2026-05-21 10:00", "2026-05-21 12:15"),
            ("New laptop setup - Marketing", "New hire needs laptop configured", "s.weber@homeandco.de", "Hardware", "High", "Resolved", "Akash Shaw", "2026-05-22 08:30", "2026-05-22 14:00"),
            ("Printer offline - 2nd floor", "Office printer not responding", "j.klein@homeandco.de", "Hardware", "Low", "In Progress", "Akash Shaw", "2026-05-27 09:00", "2026-05-27 09:45"),
            ("Azure AD sync error", "AD sync failing with error code 503", "m.braun@homeandco.de", "Cloud", "High", "In Progress", "Akash Shaw", "2026-05-28 11:00", "2026-05-28 11:00"),
            ("Software license request - Adobe", "Need Adobe CC license", "l.hoffmann@homeandco.de", "Software", "Medium", "Open", "Unassigned", "2026-05-29 14:30", "2026-05-29 14:30"),
            ("Wi-Fi drops in meeting room B", "Intermittent Wi-Fi disconnections", "s.weber@homeandco.de", "Network", "Medium", "Open", "Unassigned", "2026-05-30 08:00", "2026-05-30 08:00"),
        ]
        c.executemany("INSERT INTO tickets (title,description,user_email,category,priority,status,assignee,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)", tickets)

    # Seed users
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        users = [
            ("Lena Hoffmann", "l.hoffmann@homeandco.de", "Marketing", "Marketing Manager", "Drive, Slack, CRM", "WS-BERLIN-014", "Active", "2026-05-10 09:00"),
            ("Markus Braun", "m.braun@homeandco.de", "Finance", "Finance Analyst", "Drive, Slack, SAP", "WS-BERLIN-009", "Active", "2026-05-15 10:00"),
            ("Sophie Weber", "s.weber@homeandco.de", "Operations", "Operations Lead", "Drive, Slack, Jira, Admin Panel", "WS-BERLIN-021", "Active", "2026-05-18 09:30"),
            ("Jonas Klein", "j.klein@homeandco.de", "Sales", "Sales Representative", "Drive, Slack, CRM, HubSpot", None, "Pending", "2026-05-30 08:00"),
        ]
        c.executemany("INSERT INTO users (name,email,department,role,permissions,workstation,status,created_at) VALUES (?,?,?,?,?,?,?,?)", users)

    # Seed workstations
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

    # Seed assets
    c.execute("SELECT COUNT(*) FROM assets")
    if c.fetchone()[0] == 0:
        assets = [
            ("MacBook Pro 14\"", "laptop", "Lena Hoffmann", "SN-MBP-001", "active", "2026-05-10 09:00"),
            ("Dell XPS 15", "laptop", "Markus Braun", "SN-XPS-002", "active", "2026-05-15 10:00"),
            ("Logitech MX Keys", "keyboard", "Sophie Weber", "SN-LGT-003", "active", "2026-05-18 09:30"),
            ("HP LaserJet Pro", "printer", "Office 2nd Floor", "SN-HPL-004", "maintenance", "2026-05-27 09:00"),
        ]
        c.executemany("INSERT INTO assets (name,type,assigned_to,serial_number,status,created_at) VALUES (?,?,?,?,?,?)", assets)

    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════
# UI ROUTES (existing — untouched)
# ═══════════════════════════════════════════════

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
def tickets_ui():
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
def new_ticket_ui():
    title = request.form["title"]
    category = request.form["category"]
    priority = request.form["priority"]
    n = now()
    conn = get_db()
    conn.execute("INSERT INTO tickets (title,category,priority,status,assignee,created_at,updated_at) VALUES (?,?,?,'Open','Unassigned',?,?)",
        (title, category, priority, n, n))
    conn.commit()
    conn.close()
    return redirect(url_for("tickets_ui"))

@app.route("/tickets/update/<int:tid>", methods=["POST"])
def update_ticket_ui(tid):
    status = request.form["status"]
    conn = get_db()
    conn.execute("UPDATE tickets SET status=?, updated_at=? WHERE id=?", (status, now(), tid))
    conn.commit()
    conn.close()
    return redirect(url_for("tickets_ui"))

@app.route("/users")
def users_ui():
    conn = get_db()
    users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    workstations = conn.execute("SELECT * FROM workstations WHERE status='Available'").fetchall()
    conn.close()
    return render_template("users.html", users=users, workstations=workstations)

@app.route("/users/new", methods=["POST"])
def new_user_ui():
    name = request.form["name"]
    email = request.form["email"]
    department = request.form["department"]
    role = request.form["role"]
    permissions = request.form.getlist("permissions")
    conn = get_db()
    conn.execute("INSERT INTO users (name,email,department,role,permissions,status,created_at) VALUES (?,?,?,?,?,'Pending',?)",
        (name, email, department, role, ", ".join(permissions), now()))
    conn.commit()
    conn.close()
    return redirect(url_for("users_ui"))

@app.route("/users/activate/<int:uid>", methods=["POST"])
def activate_user_ui(uid):
    workstation = request.form.get("workstation", "")
    conn = get_db()
    conn.execute("UPDATE users SET status='Active', workstation=? WHERE id=?", (workstation, uid))
    if workstation:
        conn.execute("UPDATE workstations SET status='In Use', assigned_to=(SELECT name FROM users WHERE id=?) WHERE hostname=?", (uid, workstation))
    conn.commit()
    conn.close()
    return redirect(url_for("users_ui"))

@app.route("/workstations")
def workstations_ui():
    conn = get_db()
    ws = conn.execute("SELECT * FROM workstations ORDER BY status, hostname").fetchall()
    conn.close()
    return render_template("workstations.html", workstations=ws)

@app.route("/workstations/configure/<int:wid>", methods=["POST"])
def configure_workstation_ui(wid):
    conn = get_db()
    conn.execute("UPDATE workstations SET last_configured=? WHERE id=?", (now(), wid))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "timestamp": now()})


# ═══════════════════════════════════════════════
# JSON API ROUTES
# ═══════════════════════════════════════════════

@app.route("/api/health")
def api_health():
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat()
    })

# ── Tickets API ──────────────────────────────────

@app.route("/api/tickets", methods=["GET"])
def api_get_tickets():
    conn = get_db()
    tickets = rows_to_list(conn.execute("SELECT * FROM tickets ORDER BY created_at DESC").fetchall())
    conn.close()
    return jsonify({"tickets": tickets})

@app.route("/api/tickets/<int:tid>", methods=["GET"])
def api_get_ticket(tid):
    conn = get_db()
    ticket = row_to_dict(conn.execute("SELECT * FROM tickets WHERE id=?", (tid,)).fetchone())
    conn.close()
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    return jsonify({"ticket": ticket})

@app.route("/api/tickets", methods=["POST"])
def api_create_ticket():
    data = request.get_json(force=True, silent=True) or {}
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400
    description = data.get("description", "")
    user_email = data.get("user_email", "")
    priority = data.get("priority", "medium").capitalize()
    category = data.get("category", "General")
    n = now()
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO tickets (title,description,user_email,category,priority,status,assignee,created_at,updated_at) VALUES (?,?,?,?,?,'Open','Unassigned',?,?)",
        (title, description, user_email, category, priority, n, n)
    )
    ticket_id = cur.lastrowid
    ticket = row_to_dict(conn.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone())
    conn.commit()
    conn.close()
    return jsonify({"id": ticket_id, "status": "created", "ticket": ticket}), 201

@app.route("/api/tickets/<int:tid>/status", methods=["PATCH"])
def api_update_ticket_status(tid):
    data = request.get_json(force=True, silent=True) or {}
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    status = data.get("status", "").strip()
    valid = ["open", "in_progress", "resolved", "closed"]
    if status.lower() not in valid:
        return jsonify({"error": f"status must be one of: {', '.join(valid)}"}), 400
    status_map = {"open": "Open", "in_progress": "In Progress", "resolved": "Resolved", "closed": "Closed"}
    mapped = status_map[status.lower()]
    conn = get_db()
    existing = conn.execute("SELECT id FROM tickets WHERE id=?", (tid,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "Ticket not found"}), 404
    conn.execute("UPDATE tickets SET status=?, updated_at=? WHERE id=?", (mapped, now(), tid))
    conn.commit()
    conn.close()
    return jsonify({"id": tid, "status": "updated", "new_status": mapped})

# ── Users API ──────────────────────────────────

@app.route("/api/users", methods=["GET"])
def api_get_users():
    conn = get_db()
    users = rows_to_list(conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall())
    conn.close()
    return jsonify({"users": users})

@app.route("/api/users/onboard", methods=["POST"])
def api_onboard_user():
    data = request.get_json(force=True, silent=True) or {}
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    department = data.get("department", "").strip()
    role = data.get("role", "").strip()
    if not all([name, email, department, role]):
        return jsonify({"error": "name, email, department and role are all required"}), 400
    permissions = data.get("permissions", "Drive, Slack, Email")
    if isinstance(permissions, list):
        permissions = ", ".join(permissions)
    n = now()
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO users (name,email,department,role,permissions,status,created_at) VALUES (?,?,?,?,?,'Pending',?)",
        (name, email, department, role, permissions, n)
    )
    user_id = cur.lastrowid
    user = row_to_dict(conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone())
    conn.commit()
    conn.close()
    return jsonify({"id": user_id, "status": "onboarded", "user": user}), 201

# ── Assets API ──────────────────────────────────

@app.route("/api/assets", methods=["GET"])
def api_get_assets():
    conn = get_db()
    assets = rows_to_list(conn.execute("SELECT * FROM assets ORDER BY created_at DESC").fetchall())
    conn.close()
    return jsonify({"assets": assets})

@app.route("/api/assets", methods=["POST"])
def api_create_asset():
    data = request.get_json(force=True, silent=True) or {}
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    name = data.get("name", "").strip()
    asset_type = data.get("type", "").strip()
    if not name or not asset_type:
        return jsonify({"error": "name and type are required"}), 400
    assigned_to = data.get("assigned_to", "")
    serial_number = data.get("serial_number", "")
    n = now()
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO assets (name,type,assigned_to,serial_number,status,created_at) VALUES (?,?,?,?,'active',?)",
        (name, asset_type, assigned_to, serial_number, n)
    )
    asset_id = cur.lastrowid
    asset = row_to_dict(conn.execute("SELECT * FROM assets WHERE id=?", (asset_id,)).fetchone())
    conn.commit()
    conn.close()
    return jsonify({"id": asset_id, "status": "created", "asset": asset}), 201


# ═══════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════

init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
