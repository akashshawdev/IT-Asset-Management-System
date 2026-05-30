# ITOps ServiceDesk Automation Platform

A lightweight internal IT support and workstation management system built to streamline operational workflows at small-to-medium offices.

Built as a personal project alongside my MSc in Software Engineering, inspired by repetitive pain points in IT operations: slow onboarding, manual ticket tracking and unstructured workstation setup.

---

## Features

- **Ticket Management** - Submit, filter and resolve IT support tickets. Track by category, priority and assignee.
- **User Onboarding** - Register new employees, assign system permissions and link workstations in one step.
- **Workstation Configuration** - Track all office devices and run simulated automated setup scripts per device.
- **Dashboard** - Overview of open/resolved tickets, pending onboardings and resolution rate.

---

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python + Flask | Lightweight, quick to prototype, easy to extend |
| Database | SQLite | Zero-config, perfect for single-office scale |
| Frontend | Jinja2 + plain HTML/CSS/JS | No build step, runs anywhere |

---

## Setup

```bash
git clone https://github.com/akashshawdev/itops-servicedesk
cd itops-servicedesk
pip install flask
python app.py
```

Then open `http://localhost:5000` in your browser. The database is created and seeded automatically on first run.

---

## Project Structure

```
itops-servicedesk/
├── app.py                  # Flask routes and database logic
├── itops.db                # SQLite database (auto-created)
├── templates/
│   ├── base.html           # Shared layout and sidebar
│   ├── index.html          # Dashboard
│   ├── tickets.html        # Ticket management
│   ├── users.html          # User onboarding
│   └── workstations.html   # Device management
└── static/
    ├── css/style.css
    └── js/main.js
```

---

## What I'd add next

- **Azure Active Directory integration** - sync users and permissions directly via Microsoft Graph API
- **Email notifications** - alert assignees when a ticket is created or updated
- **Role-based access control** - separate views for IT admins vs. regular staff
- **Reporting** - weekly ticket volume charts, average resolution time tracking
- **REST API** - expose endpoints so other internal tools can create tickets programmatically

---

## Screenshots

> Dashboard, Tickets, User Onboarding and Workstation pages - all functional with real SQLite persistence.

---

*Built by Akash Kumar Shaw - MSc Software Engineering, University of Europe for Applied Sciences*
