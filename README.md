# 🎓 Smart Campus Resource & Room Booking System

A Python-based campus resource booking application built with **Streamlit** and **SQLite**. It helps students request campus resources and enables administrators to manage resources, review booking requests, and maintain booking history.

## ✨ Features

### 👨‍🎓 Student Dashboard
- Browse available campus resources.
- View resource details, categories, departments, and capacity.
- Submit booking requests by selecting a date and time slot.
- Track booking status.
- View personal booking records and history.
- Cancel bookings where permitted.

### 🛡️ Admin Dashboard
- View booking statistics by status.
- Add, edit, view, and manage campus resources.
- Review pending student booking requests.
- Approve or reject requests with an admin note.
- View and filter all booking records.
- Access booking history and audit logs.
- Download booking history as a CSV file.

### 🗄️ Database Management
- Uses SQLite for local data storage.
- Stores resource, booking, and history records.
- Checks for conflicting reservations.
- Records booking status changes for audit purposes.

## 🧰 Tech Stack

- **Python** — Application logic
- **Streamlit** — Web interface
- **SQLite** — Database
- **Pandas** — Tabular data display and CSV export in the admin dashboard

## 📁 Project Structure

```text
Smart Campus/
│
├── app.py
├── admin.py
├── student.py
├── database.py
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/virendrasinghrathore07/Smart-Campus-Booking-System
```

### 2. Open the project folder

```bash
cd smart-campus-resource-booking-system
```

### 3. Create a virtual environment (recommended)

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Run the application

```bash
python -m streamlit run app.py
```

Streamlit will display a local URL in the terminal. Open that URL in your browser to use the application.

## 🗃️ Database

The application uses SQLite and stores its data in `campus.db`. The database and initial resource records are initialized by the database setup code.

The database file is generated locally and should not normally be committed to a public repository.

## 🔐 Security Note

- Use demo credentials only for demonstration.
- Do not publish real passwords, API keys, private student information, or production database files.
- Authentication and access controls should be reviewed before deploying the application for real-world use.

## 🚀 Future Improvements

- Email or in-app notifications for booking decisions.
- Calendar-based resource availability.
- Improved authentication and role-based access control.
- Deployment to a cloud hosting platform.
- Reports and analytics for resource utilization.

## 🎯 Project Objective

The objective is to simplify campus resource reservations, reduce scheduling conflicts, and provide a centralized workflow for students and administrators.

## 👨‍💻 Author

**Virendra Singh Rathore**

B.Tech — Computer Science / Artificial Intelligence & Data Science

---

*Developed as a campus resource management project.*
