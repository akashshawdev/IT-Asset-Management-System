# IT Asset Management System

A lightweight internal IT operations platform for device tracking, support ticket management and employee onboarding workflows - built for small-to-medium office environments.

Built as a personal project alongside my MSc in Software Engineering, inspired by real pain points in IT operations: unstructured onboarding, manual ticket handling and no central view of office hardware.

---

## Features

- **Dashboard** - Live overview of ticket stats, resolution rate and pending onboarding tasks
- **Ticket Management** - Submit, filter and resolve IT support tickets by category, priority and assignee
- **User Onboarding** - Register new employees, assign system permissions and link workstations in one step
- **Workstation Tracking** - Monitor all office devices and run automated configuration scripts per machine

---

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python + Flask | Lightweight, easy to prototype and extend |
| Database | SQLite | Zero-config, suitable for single-office scale |
| Frontend | Jinja2 + HTML/CSS/JS | No build step, runs anywhere |

---

## Setup

```bash
git clone https://github.com/akashshawdev/IT-Asset-Management-System
cd IT-Asset-Management-System
pip install flask
python app.py
```

Open `http://localhost:5000` in your browser. The database is created and seeded with sample data automatically on first run.

---

## Project Structure

```
IT-Asset-Management-System/
├── app.py                  # Flask routes and database logic
├── templates/
│   ├── base.html           # Shared layout and sidebar
│   ├── index.html          # Dashboard
│   ├── tickets.html        # Ticket management
│   ├── users.html          # User onboarding
│   └── workstations.html   # Device tracking
└── static/
    ├── css/style.css
    └── js/main.js
```

> Note: `itops.db` is auto-generated on first run and intentionally excluded from version control. `__pycache__` is also excluded.

---

## Roadmap

- **Azure Active Directory integration** - sync users and permissions via Microsoft Graph API
- **Email notifications** - alert assignees on ticket creation or status change
- **Role-based access control** - separate views for IT admins vs. regular staff
- **Reporting** - weekly ticket volume charts and average resolution time tracking
- **REST API** - expose endpoints so other internal tools can create or update tickets programmatically

---

*Built by Akash Kumar Shaw - MSc Software Engineering, University of Europe for Applied Sciences*
