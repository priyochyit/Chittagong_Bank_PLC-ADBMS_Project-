# Chittagong Bank PLC

A full-stack digital banking web application built with **Flask**. It simulates a real-world banking platform with role-based dashboards (Customer, Staff, and Admin), secure fund transfers, a SHA-256 hash-chained transaction ledger inspired by blockchain principles, and a heuristic AI/RL-style fraud-risk detector.

> **Academic / Portfolio Project Disclaimer**
> This project was built for learning and demonstration purposes (full-stack development, authentication, database design, and security concepts). The "Blockchain" and "AI" components are simplified educational implementations and should not be used for real financial transactions.

---

## Features

### Customer Dashboard
- KYC-based registration with NID front & back image upload, phone, date of birth, income source, and account purpose
- Secure login with bcrypt-hashed passwords and role verification
- Automatic session timeout after 2 minutes of inactivity
- Send money via Bank Transfer (Account No.), PayPal (email), or MFS (bKash/Nagad number)
- Real-time balance updates, transaction history, and digital receipts
- Self-service transaction reversal
- Editable profile with profile picture upload

### Employee (Staff) Dashboard
- View the complete transaction ledger across all users
- Reverse any transaction on behalf of customers

### Admin Dashboard
- Manage all users — edit details, change roles, adjust balances, delete accounts
- Disburse staff salaries (automatically logged as a transaction)
- One-click verification of the entire blockchain ledger for tampering
- Full transaction oversight and deletion

### Security & Intelligence
- Bcrypt password hashing
- SHA-256 hash-chained transaction ledger (`prev_hash` → `current_hash`) for tamper detection
- Heuristic AI/reinforcement-learning-style anomaly detector flags unusually large transactions
- Strict file-type and size validation for all uploads (NID images, profile pictures)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database / ORM | SQLAlchemy (SQLite by default) |
| Authentication | Flask-Login, Flask-Bcrypt |
| Frontend | HTML, Tailwind CSS, Vanilla JavaScript, Font Awesome |
| Configuration | python-dotenv |
| Deployment | Gunicorn (WSGI server) |

---

## Project Structure

```
chittagong-bank/
├── app.py                  # Main Flask app — models, routes, business logic
├── requirements.txt        # Python dependencies
├── Procfile                 # Start command for deployment (gunicorn)
├── .env.example             # Sample environment variables
├── .gitignore
├── static/
│   ├── Logo.svg             # Site logo / favicon
│   └── uploads/
│       └── default_avatar.png   # Default profile picture for new users
└── templates/
    ├── home.html
    ├── login.html
    ├── register.html
    ├── user.html
    ├── employee.html
    ├── admin.html
    └── script.js
```

---

## Getting Started (Local Setup)

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy the example file and update the values:
```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `SECRET_KEY` | Secret key Flask uses to sign session cookies |
| `DATABASE_URI` | SQLAlchemy database connection string |

### 5. Run the application
```bash
python app.py
```
Database tables are created automatically on first run. Open **http://127.0.0.1:5000** in your browser.

---

## Roles & Dashboards

During registration, choose a role to determine which dashboard you land on after login:

| Role | Dashboard Route |
|---|---|
| `user` | `/dashboard/user` |
| `staff` | `/dashboard/employee` |
| `admin` | `/dashboard/admin` |

---

## Deployment

This project is ready to deploy on platforms like [Render](https://render.com) using the included `requirements.txt` and `Procfile` (`gunicorn app:app`).

### Notes on Persistence
The default database is **SQLite**, a single file on disk. On hosting platforms with an ephemeral filesystem (e.g., Render's free tier), this file — along with any uploaded NID/profile images — will reset whenever the service restarts or redeploys. This is fine for demos, but for persistent production data, switch `DATABASE_URI` to a managed database (e.g., PostgreSQL).

---

## License

This project is licensed under the MIT License — feel free to use it for learning and reference.

---

## Author

Built as an academic/portfolio project to demonstrate full-stack web development with Flask, including authentication, relational database design, and applied security concepts.
