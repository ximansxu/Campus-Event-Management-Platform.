pip install flask
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = 'campus_events.db'

def init_db():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        # Create tables
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Colleges(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Students(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                college_id INTEGER,
                name TEXT,
                email TEXT UNIQUE,
                FOREIGN KEY(college_id) REFERENCES Colleges(id)
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Events(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                college_id INTEGER,
                name TEXT,
                type TEXT,
                date TEXT,
                status TEXT DEFAULT 'active',
                FOREIGN KEY(college_id) REFERENCES Colleges(id)
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Registrations(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                event_id INTEGER,
                registration_time TEXT,
                UNIQUE(student_id, event_id),
                FOREIGN KEY(student_id) REFERENCES Students(id),
                FOREIGN KEY(event_id) REFERENCES Events(id)
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Attendance(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registration_id INTEGER,
                check_in_time TEXT,
                FOREIGN KEY(registration_id) REFERENCES Registrations(id)
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Feedback(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registration_id INTEGER,
                rating INTEGER CHECK(rating BETWEEN 1 AND 5),
                comments TEXT,
                FOREIGN KEY(registration_id) REFERENCES Registrations(id)
            )
        ''')
        con.commit()

@app.route('/register_student', methods=['POST'])
def register_student():
    data = request.json
    student_id = data['student_id']
    event_id = data['event_id']
    import datetime
    reg_time = datetime.datetime.utcnow().isoformat()
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        try:
            cur.execute('INSERT INTO Registrations(student_id, event_id, registration_time) VALUES(?,?,?)', 
                       (student_id, event_id, reg_time))
            con.commit()
            return jsonify({"status": "success", "message": "Student registered successfully"}), 200
        except sqlite3.IntegrityError:
            return jsonify({"status": "error", "message": "Student already registered for this event"}), 400

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    registration_id = data['registration_id']
    import datetime
    checkin_time = datetime.datetime.utcnow().isoformat()
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute('SELECT id FROM Attendance WHERE registration_id = ?', (registration_id,))
        if cur.fetchone():
            return jsonify({"status": "error", "message": "Attendance already marked"}), 400
        cur.execute('INSERT INTO Attendance(registration_id, check_in_time) VALUES (?, ?)', (registration_id, checkin_time))
        con.commit()
        return jsonify({"status": "success", "message": "Attendance marked successfully"}), 200

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    registration_id = data['registration_id']
    rating = data['rating']
    comments = data.get('comments', '')
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute('SELECT id FROM Feedback WHERE registration_id = ?', (registration_id,))
        if cur.fetchone():
            return jsonify({"status": "error", "message": "Feedback already submitted"}), 400
        cur.execute('INSERT INTO Feedback(registration_id, rating, comments) VALUES (?, ?, ?)', 
                    (registration_id, rating, comments))
        con.commit()
        return jsonify({"status": "success", "message": "Feedback submitted successfully"}), 200

@app.route('/report/registrations_per_event', methods=['GET'])
def registrations_per_event():
    with sqlite3.connect(DATABASE) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('''
            SELECT Events.id, Events.name, COUNT(Registrations.id) AS total_registrations
            FROM Events LEFT JOIN Registrations ON Events.id = Registrations.event_id
            GROUP BY Events.id ORDER BY total_registrations DESC
        ''')
        rows = cur.fetchall()
        results = [dict(row) for row in rows]
        return jsonify(results)

@app.route('/report/attendance_percentage', methods=['GET'])
def attendance_percentage():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute('''
            SELECT Events.id, Events.name,
            (CAST(COUNT(DISTINCT Attendance.id) AS FLOAT) * 100.0 / NULLIF(COUNT(DISTINCT Registrations.id),0)) AS attendance_percentage
            FROM Events
            LEFT JOIN Registrations ON Events.id = Registrations.event_id
            LEFT JOIN Attendance ON Registrations.id = Attendance.registration_id
            GROUP BY Events.id
        ''')
        rows = cur.fetchall()
        results = [{"event_id": row[0], "event_name": row[1], "attendance_percentage": row[2]} for row in rows]
        return jsonify(results)

@app.route('/report/average_feedback_score', methods=['GET'])
def average_feedback_score():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute('''
            SELECT Events.id, Events.name, AVG(Feedback.rating) AS avg_rating
            FROM Events
            LEFT JOIN Registrations ON Events.id = Registrations.event_id
            LEFT JOIN Feedback ON Registrations.id = Feedback.registration_id
            GROUP BY Events.id
        ''')
        rows = cur.fetchall()
        results = [{"event_id": row[0], "event_name": row[1], "average_rating": row[2]} for row in rows]
        return jsonify(results)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
