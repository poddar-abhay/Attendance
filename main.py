from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Google Sheets API setup
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_json = os.getenv('GOOGLE_CREDS')
creds_dict = json.loads(creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open sheets
students_sheet = client.open("Attendance").worksheet("Students")
attendance_sheet = client.open("Attendance").worksheet("Attendance")

@app.route('/')
def index():
    # Render the main attendance page
    return render_template('attendance.html')

@app.route('/view')
def view_attendance():
    # Render the attendance viewing page
    return render_template('view.html')

@app.route('/get-students', methods=['GET'])
def get_students():
    # Fetch student names from the Students sheet
    students = students_sheet.col_values(1)
    return jsonify(students)

@app.route('/submit-attendance', methods=['POST'])
def submit_attendance():
    # Get attendance data from the frontend
    data = request.json
    attendance = data['attendance']  # List of {"name": "Student", "status": "Present/Absent"}

    # Get the current date and time
    now = datetime.now()
    today_date = now.strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
    current_time = now.strftime("%H:%M:%S")  # Format: HH:MM:SS

    # Prepare the list of students marked present
    present_students = [
        entry['name'] for entry in attendance if entry['status'] == 'Present'
    ]
    present_students_str = ", ".join(present_students)  # Convert to comma-separated string

    # Append the entry to the Attendance sheet
    attendance_sheet.append_row([today_date, current_time, present_students_str])

    return jsonify({"status": "success"}), 200

@app.route('/get-attendance', methods=['GET'])
def get_attendance():
    """Fetch attendance data and split comma-separated names into individual rows."""
    all_records = attendance_sheet.get_all_records()

    # Group records by date
    grouped_records = {}
    for record in all_records:
        date = record["Date"]
        time = record["Time"]
        present = record["Present"]

        # Split the comma-separated names into individual student names
        present_students = present.split(", ")

        # Store the date with the student names as separate rows
        if date not in grouped_records:
            grouped_records[date] = []

        for student in present_students:
            grouped_records[date].append({"time": time, "student": student})

    return jsonify(grouped_records)

@app.route('/get-attendance-by-date', methods=['GET'])
def get_attendance_by_date():
    """Fetch attendance data for a specific date."""
    date = request.args.get('date')
    all_records = attendance_sheet.get_all_records()

    # Filter records by date
    filtered_records = [
        {"student": name}  # Return each name individually
        for record in all_records if record["Date"] == date
        for name in record["Present"].split(", ")
    ]

    return jsonify({date: filtered_records})

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)), debug=True)
