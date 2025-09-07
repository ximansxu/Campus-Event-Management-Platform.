# Campus-Event-Management-Platform.
Backend prototype for Campus Event Management platform. Built with Python Flask and SQLite, it handles student registrations, attendance tracking, feedback collection, and detailed event reports. Designed for scalability, tested via Postman, and includes API endpoints for key campus event workflows.
This backend API prototype enables campuses to manage student participation in various events efficiently. It supports registration, attendance tracking, feedback collection, and multiple reporting endpoints to analyze participation and satisfaction.

How to Run
Ensure Python 3 is installed.

Install dependencies using:

text
pip install flask
Run the app with:

text
python app.py
The API server runs locally at http://127.0.0.1:5000.

API Endpoints
POST /register_student: Registers a student for an event. Requires student_id & event_id.

POST /mark_attendance: Marks attendance for a student’s event registration.

POST /submit_feedback: Allows students to submit rating and comments.

GET /report/registrations_per_event: Returns total registrations for each event.

GET /report/attendance_percentage: Shows attendance percentages per event.

GET /report/average_feedback_score: Provides average feedback ratings per event.

Assumptions & Notes
Student-event combination must be unique in registrations.

Attendance and feedback can only be recorded once per registration.

The system uses a shared dataset for all colleges but can scale easily.

Responses are JSON formatted for easy integration.

Minimal frontend/UI was planned as part of bonus (wireframes/sketches included).

AI Assistance
AI tools like ChatGPT were used to brainstorm ideas, troubleshoot code, and generate some snippets, but the final design decisions and coding were done manually to maintain full control and learning.

