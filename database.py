
import sqlite3
from datetime import datetime

DB_NAME = "campus.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 10000")
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                department TEXT NOT NULL,
                capacity INTEGER DEFAULT 1,
                specifications TEXT,
                guidelines TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                roll_number TEXT NOT NULL,
                section TEXT NOT NULL,
                year TEXT NOT NULL,
                mobile TEXT NOT NULL,
                email TEXT NOT NULL,
                description TEXT NOT NULL,
                resource_id INTEGER NOT NULL,
                booking_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                admin_note TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(resource_id) REFERENCES resources(id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                note TEXT DEFAULT '',
                changed_at TEXT NOT NULL,
                FOREIGN KEY(booking_id) REFERENCES bookings(id)
            )
        """)

        count = conn.execute(
            "SELECT COUNT(*) FROM resources"
        ).fetchone()[0]

        if count == 0:
            resources = [
                ("Computer Lab 1", "Lab", "Computer Science", 60,
                 "Desktop computers, internet, projector",
                 "Maintain silence. No unauthorized software."),
                ("AI and Data Science Lab", "Lab", "AI & Data Science", 40,
                 "AI workstations, GPU systems, MATLAB",
                 "Use systems for approved academic work."),
                ("Cyber Security Lab", "Lab", "Computer Science", 30,
                 "Security workstations and networking equipment",
                 "Only authorized security testing is permitted."),
                ("Physics Lab", "Lab", "Physics", 35,
                 "Physics instruments and measurement apparatus",
                 "Handle instruments carefully."),
                ("Chemistry Lab", "Lab", "Chemistry", 35,
                 "Chemistry apparatus and laboratory equipment",
                 "Follow laboratory safety rules."),
                ("Electrical Engineering Lab", "Lab", "Electrical Engineering", 30,
                 "Electrical circuits and testing instruments",
                 "Switch off equipment after use."),
                ("Mechanical Engineering Lab", "Lab", "Mechanical Engineering", 30,
                 "Mechanical tools and workshop equipment",
                 "Wear required protective equipment."),
                ("Civil Engineering Lab", "Lab", "Civil Engineering", 30,
                 "Civil engineering testing apparatus",
                 "Follow staff instructions."),
                ("Seminar Hall A", "Auditorium", "Common", 150,
                 "Projector, sound system, seating",
                 "Keep the hall clean."),
                ("Main Auditorium", "Auditorium", "Common", 500,
                 "Stage, microphone, projector, seating",
                 "Bookings may require staff supervision."),
                ("Discussion Room 1", "Room", "Common", 10,
                 "Table, chairs, whiteboard",
                 "Leave the room clean."),
                ("Discussion Room 2", "Room", "Common", 12,
                 "Table, chairs, display",
                 "Avoid disturbing other students."),
                ("Project Room 1", "Room", "Common", 20,
                 "Project tables and power sockets",
                 "Use only for academic projects."),
                ("GPU Server", "Equipment", "AI & Data Science", 1,
                 "GPU computing resource",
                 "Provide project details and expected usage."),
                ("Arduino Kit", "Equipment", "Electrical Engineering", 5,
                 "Microcontroller and electronic components",
                 "Return all components after use."),
                ("Robotics Kit", "Equipment", "Mechanical Engineering", 3,
                 "Motors, controller and sensors",
                 "Report damaged components."),
                ("Chemistry Apparatus Kit", "Equipment", "Chemistry", 5,
                 "Basic laboratory apparatus",
                 "Follow safety guidelines."),
                ("Physics Instrument Kit", "Equipment", "Physics", 5,
                 "Physics measurement instruments",
                 "Handle instruments carefully."),
                ("MATLAB Workstation", "Equipment", "AI & Data Science", 10,
                 "MATLAB-enabled workstation",
                 "Use for authorized academic tasks."),
                ("Projector", "Equipment", "Common", 4,
                 "Portable multimedia projector",
                 "Return to the designated office.")
            ]

            conn.executemany("""
                INSERT INTO resources
                (name, category, department, capacity,
                 specifications, guidelines)
                VALUES (?, ?, ?, ?, ?, ?)
            """, resources)


def get_resources(category=None, department=None):
    query = "SELECT * FROM resources WHERE 1=1"
    params = []

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)

    if department and department != "All":
        query += " AND department = ?"
        params.append(department)

    query += " ORDER BY category, name"

    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def get_departments():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT DISTINCT department FROM resources
            ORDER BY department
        """).fetchall()
    return [row["department"] for row in rows]


def get_resource(resource_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM resources WHERE id = ?",
            (resource_id,)
        ).fetchone()


def get_booking(booking_id):
    with get_connection() as conn:
        return conn.execute("""
            SELECT b.*, r.name AS resource_name, r.category
            FROM bookings b
            JOIN resources r ON r.id = b.resource_id
            WHERE b.id = ?
        """, (booking_id,)).fetchone()


def has_conflict(resource_id, booking_date, start_time,
                 end_time, exclude_booking_id=None,
                 approved_only=False):
    query = """
        SELECT COUNT(*) FROM bookings
        WHERE resource_id = ?
          AND booking_date = ?
          AND start_time < ?
          AND end_time > ?
          AND status IN ('Pending', 'Approved')
    """
    params = [resource_id, booking_date, end_time, start_time]

    if approved_only:
        query = query.replace(
            "status IN ('Pending', 'Approved')",
            "status = 'Approved'"
        )

    if exclude_booking_id is not None:
        query += " AND id != ?"
        params.append(exclude_booking_id)

    with get_connection() as conn:
        count = conn.execute(query, params).fetchone()[0]

    return count > 0


def log_history(booking_id, action, note=""):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO history
            (booking_id, action, note, changed_at)
            VALUES (?, ?, ?, ?)
        """, (
            booking_id, action, note,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))


def create_booking(data):
    if data["start_time"] >= data["end_time"]:
        return False, "End time must be later than start time."

    if has_conflict(
        data["resource_id"], data["booking_date"],
        data["start_time"], data["end_time"]
    ):
        return False, (
            "This resource already has a pending or approved "
            "booking during the selected time."
        )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO bookings (
                student_name, roll_number, section, year,
                mobile, email, description, resource_id,
                booking_date, start_time, end_time, status,
                admin_note, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending',
                    '', ?, ?)
        """, (
            data["student_name"], data["roll_number"],
            data["section"], data["year"], data["mobile"],
            data["email"], data["description"],
            data["resource_id"], data["booking_date"],
            data["start_time"], data["end_time"], now, now
        ))

        booking_id = cursor.lastrowid

        conn.execute("""
            INSERT INTO history
            (booking_id, action, note, changed_at)
            VALUES (?, 'Request Submitted', '', ?)
        """, (booking_id, now))

    return True, f"Request submitted successfully. Booking ID: {booking_id}"


def get_student_bookings(roll_number):
    with get_connection() as conn:
        return conn.execute("""
            SELECT b.*, r.name AS resource_name, r.category
            FROM bookings b
            JOIN resources r ON r.id = b.resource_id
            WHERE LOWER(b.roll_number) = LOWER(?)
            ORDER BY b.booking_date DESC, b.start_time DESC
        """, (roll_number.strip(),)).fetchall()


def get_all_bookings(status=None):
    query = """
        SELECT b.*, r.name AS resource_name, r.category
        FROM bookings b
        JOIN resources r ON r.id = b.resource_id
    """
    params = []

    if status and status != "All":
        query += " WHERE b.status = ?"
        params.append(status)

    query += " ORDER BY b.created_at DESC"

    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def update_booking_status(booking_id, status, note=""):
    if status not in ("Approved", "Rejected", "Cancelled"):
        return False, "Invalid status."

    booking = get_booking(booking_id)

    if not booking:
        return False, "Booking not found."

    if booking["status"] != "Pending":
        return False, "Only pending requests can be updated."

    if status == "Approved":
        if has_conflict(
            booking["resource_id"], booking["booking_date"],
            booking["start_time"], booking["end_time"],
            exclude_booking_id=booking_id,
            approved_only=True
        ):
            return False, (
                "Cannot approve: another approved booking "
                "already overlaps this time slot."
            )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        conn.execute("""
            UPDATE bookings
            SET status = ?, admin_note = ?, updated_at = ?
            WHERE id = ? AND status = 'Pending'
        """, (status, note.strip(), now, booking_id))

        if conn.total_changes == 0:
            return False, "Booking status could not be updated."

        conn.execute("""
            INSERT INTO history
            (booking_id, action, note, changed_at)
            VALUES (?, ?, ?, ?)
        """, (booking_id, status, note.strip(), now))

    return True, f"Booking #{booking_id} marked {status}."


def cancel_booking(booking_id, roll_number):
    booking = get_booking(booking_id)

    if not booking:
        return False, "Booking not found."

    if booking["roll_number"].strip().lower() != roll_number.strip().lower():
        return False, "This booking does not belong to this roll number."

    if booking["status"] not in ("Pending", "Approved"):
        return False, "This booking cannot be cancelled."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        conn.execute("""
            UPDATE bookings
            SET status = 'Cancelled', updated_at = ?
            WHERE id = ? AND status IN ('Pending', 'Approved')
        """, (now, booking_id))

        conn.execute("""
            INSERT INTO history
            (booking_id, action, note, changed_at)
            VALUES (?, 'Cancelled', 'Cancelled by student', ?)
        """, (booking_id, now))

    return True, "Booking cancelled successfully."


def get_history():
    with get_connection() as conn:
        return conn.execute("""
            SELECT h.*, b.student_name, b.roll_number,
                   r.name AS resource_name
            FROM history h
            JOIN bookings b ON b.id = h.booking_id
            JOIN resources r ON r.id = b.resource_id
            ORDER BY h.changed_at DESC
        """).fetchall()


def add_resource(name, category, department, capacity,
                 specifications, guidelines):
    name = name.strip()

    if not name:
        return False, "Resource name is required."

    if capacity < 1:
        return False, "Capacity must be at least 1."

    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO resources
                (name, category, department, capacity,
                 specifications, guidelines)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name, category, department.strip(), capacity,
                specifications.strip(), guidelines.strip()
            ))

        return True, f"{name} added successfully!"

    except sqlite3.IntegrityError:
        return False, "A resource with this name already exists."

    except sqlite3.Error as e:
        return False, f"Database error: {e}"


def update_resource(resource_id, name, category, department,
                    capacity, specifications, guidelines):
    name = name.strip()

    if not name or not department.strip():
        return False, "Name and department are required."

    if capacity < 1:
        return False, "Capacity must be at least 1."

    try:
        with get_connection() as conn:
            cursor = conn.execute("""
                UPDATE resources
                SET name = ?, category = ?, department = ?,
                    capacity = ?, specifications = ?, guidelines = ?
                WHERE id = ?
            """, (
                name, category, department.strip(), capacity,
                specifications.strip(), guidelines.strip(),
                resource_id
            ))

            if cursor.rowcount == 0:
                return False, "Resource not found."

        return True, "Resource updated successfully!"

    except sqlite3.IntegrityError:
        return False, "Another resource already uses this name."

    except sqlite3.Error as e:
        return False, f"Database error: {e}"


def delete_resource(resource_id):
    try:
        with get_connection() as conn:
            booking_count = conn.execute("""
                SELECT COUNT(*)
                FROM bookings
                WHERE resource_id = ?
            """, (resource_id,)).fetchone()[0]

            if booking_count > 0:
                return (
                    False,
                    "This resource has booking records and cannot be deleted."
                )

            cursor = conn.execute(
                "DELETE FROM resources WHERE id = ?",
                (resource_id,)
            )

            if cursor.rowcount == 0:
                return False, "Resource not found."

        return True, "Resource deleted successfully!"

    except sqlite3.Error as e:
        return False, f"Database error: {e}"
