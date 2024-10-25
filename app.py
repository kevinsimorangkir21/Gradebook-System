import os
from datetime import datetime
from flask import Flask, jsonify, render_template, abort

app = Flask(__name__)
# Set the CSV directory to 'static' folder
CSV_DIRECTORY = 'static'


@app.route('/')
def index():
    courses = get_courses()
    return render_template('index.html', courses=courses)


@app.route('/last_modified/<course>')
def get_last_modified(course):
    try:
        last_modified_date = get_last_modified_date(course)
        return jsonify({'last_modified_date': last_modified_date})
    except FileNotFoundError:
        return jsonify({'error': 'Course not found'}), 404


@app.route('/grades/<course>/<student_id>')
def get_grades(course, student_id):
    try:
        grades = read_grades_from_csv(f'{course}.csv')
        student_grades = grades.get(student_id)

        if student_grades:
            return jsonify(student_grades)
        else:
            return jsonify({'error': 'Student ID not found'}), 404
    except FileNotFoundError:
        return jsonify({'error': 'Course not found'}), 404


def get_courses():
    """Returns a list of courses by extracting .csv files from the 'static' folder."""
    try:
        csv_files = [file for file in os.listdir(
            CSV_DIRECTORY) if file.endswith('.csv')]
        if not csv_files:
            return []
        return [file.rsplit('.', 1)[0] for file in csv_files]
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return []


def get_last_modified_date(course):
    """Gets the last modified date of a course's CSV file."""
    csv_file = os.path.join(CSV_DIRECTORY, f'{course}.csv')
    if not os.path.exists(csv_file):
        raise FileNotFoundError
    last_modified = os.path.getmtime(csv_file)
    return datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')


def read_grades_from_csv(file_path):
    """Reads grades from a CSV file and returns a dictionary of student grades."""
    full_path = os.path.join(CSV_DIRECTORY, file_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError

    grades = {}
    try:
        with open(full_path, 'r') as file:
            lines = file.readlines()
            headers = lines[0].strip().split(',')
            for line in lines[1:]:
                values = line.strip().split(',')
                student_id = values[0]
                student_grades = {header: value for header,
                                  value in zip(headers[1:], values[1:])}
                grades[student_id] = student_grades
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return {}

    return grades


if __name__ == '__main__':
    app.run(debug=True)
