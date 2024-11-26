from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('student.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/add_student', methods=['POST'])
def add_student():
    try:
        # Nhận dữ liệu từ request
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        gpa = request.form['gpa']
        credits_completed = request.form['credits_completed']
        days_absent = request.form['days_absent']
        part_time_job = request.form['part_time_job']
        health_status = request.form['health_status']
        result = request.form['result']

        # Kết nối và thêm dữ liệu vào cơ sở dữ liệu
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (name, age, gender, gpa, credits_completed, days_absent, part_time_job, health_status, result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, age, gender, gpa, credits_completed, days_absent, part_time_job, health_status, result))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Student added successfully!'})

    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
