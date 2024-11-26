from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import sqlite3
# from flask_login import login_required

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('student.db')  # Thay 'stem.db' thành tên cơ sở dữ liệu của bạn
    conn.row_factory = sqlite3.Row
    return conn

# Route để thêm học sinh
@app.route("/students/create", methods=["POST"])
# @login_required
def create_student():
    if request.method == "POST":
        age = request.form["age"]
        gender = request.form["gender"]
        economic_status = request.form["economic_status"]
        gpa = request.form["gpa"]
        credits_completed = request.form["credits_completed"]
        days_absent = request.form["days_absent"]
        part_time_job = request.form["part_time_job"]
        health_status = request.form["health_status"]
        result = request.form["result"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO students ( age, gender, economic_status, gpa, credits_completed, days_absent, part_time_job, health_status, result) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ( age, gender, economic_status, gpa, credits_completed, days_absent, part_time_job, health_status, result),
        )
        conn.commit()
        conn.close()

        flash("Student added successfully!")
        return jsonify({"message": "Student added successfully!"})

# Route để sửa thông tin học sinh
@app.route("/students/update/<int:id>", methods=["POST"])
# @login_required
def update_student(id):
    if request.method == "POST":
        age = request.form["age"]
        gender = request.form["gender"]
        economic_status = request.form["economic_status"]
        gpa = request.form["gpa"]
        credits_completed = request.form["credits_completed"]
        days_absent = request.form["days_absent"]
        part_time_job = request.form["part_time_job"]
        health_status = request.form["health_status"]
        result = request.form["result"]

        conn = get_db_connection()
        conn.execute(
            "UPDATE students SET  age = ?, gender = ?, economic_status = ?, gpa = ?, credits_completed = ?, days_absent = ?, part_time_job = ?, health_status = ?, result = ? WHERE student_id = ?",
            ( age, gender, economic_status, gpa, credits_completed, days_absent, part_time_job, health_status, result, id),
        )
        conn.commit()
        conn.close()

        flash("Student updated successfully!")
        return jsonify({"message": "Student updated successfully!"})

# Route để xóa học sinh
@app.route("/students/delete/<int:id>", methods=["POST"])
# @login_required
def delete_student(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE student_id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Student deleted successfully!")
    return jsonify({"message": "Student deleted successfully!"})

# Route để hiển thị danh sách học sinh
@app.route("/students")
# @login_required
def list_students():
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template('index.html', students=students)

if __name__ == '__main__':
    app.run(debug=True)
