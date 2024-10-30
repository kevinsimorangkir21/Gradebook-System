import os
import io
from datetime import datetime
from flask import Flask, jsonify, render_template, send_file
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

app = Flask(__name__)
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


@app.route('/export_pdf/<course>/<student_id>')
def export_pdf(course, student_id):
    try:
        # Read grades from CSV
        grades = read_grades_from_csv(f'{course}.csv')
        student_grades = grades.get(student_id)
        if not student_grades:
            return jsonify({'error': 'Student ID not found'}), 404

        # Create a PDF in memory
        pdf_buffer = io.BytesIO()
        pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        # Custom styles for better appearance
        title_style = ParagraphStyle(
            name='TitleStyle', fontSize=18, alignment=0, spaceAfter=12)  # Left align
        normal_style = ParagraphStyle(
            name='NormalStyle', fontSize=12, alignment=0, spaceAfter=6)  # Left align

        # Header
        header = Paragraph(
            "Data Nilai Tutorial Matematika Dasar 1B", title_style)

        # Student Info
        student_info = [
            ["Student ID:", student_id],
            ["Faculty:", "Teknologi Industri (FTI)"],
            ["Class:", "TPB 47"],
            ["Dosen Pengampu:", "Muhammad Suroso & Nanda Azzanina"],
            ["Asisten Tutorial:", "Kevin Simorangkir"],
        ]

        # Create a Table for student info
        student_info_table = Table(student_info)
        student_info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Left align all columns
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('GRID', (0, 0), (-1, -1), 0, colors.white),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header background
        ]))

        # Create a table for the grades
        grade_headers = ['Subject', 'Grades (X/100)']
        data = [grade_headers] + [[subject, grade]
                                  for subject, grade in student_grades.items()]

        # Create a Table for grades
        grades_table = Table(data)
        grades_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            # Left align the grades table
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Change to LEFT
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ]))

        # Add elements to the PDF document
        elements = [header, student_info_table, grades_table]

        # Build PDF
        pdf.build(elements)

        # Prepare response
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, as_attachment=True, download_name=f"{student_id}_grades.pdf", mimetype='application/pdf')

    except FileNotFoundError:
        return jsonify({'error': 'Course not found'}), 404


def get_courses():
    try:
        csv_files = [file for file in os.listdir(
            CSV_DIRECTORY) if file.endswith('.csv')]
        return [file.rsplit('.', 1)[0] for file in csv_files]
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return []


def get_last_modified_date(course):
    csv_file = os.path.join(CSV_DIRECTORY, f'{course}.csv')
    if not os.path.exists(csv_file):
        raise FileNotFoundError
    last_modified = os.path.getmtime(csv_file)
    return datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')


def read_grades_from_csv(file_path):
    full_path = os.path.join(CSV_DIRECTORY, file_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError

    grades = {}
    with open(full_path, 'r') as file:
        lines = file.readlines()
        headers = lines[0].strip().split(',')
        for line in lines[1:]:
            values = line.strip().split(',')
            student_id = values[0]
            student_grades = {header: value for header,
                              value in zip(headers[1:], values[1:])}
            grades[student_id] = student_grades
    return grades


if __name__ == '__main__':
    app.run(debug=True)
