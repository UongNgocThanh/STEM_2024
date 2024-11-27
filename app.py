from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Đặt secret key để sử dụng flash messages

# Kết nối cơ sở dữ liệu SQLite
def get_db_connection():
    conn = sqlite3.connect('student.db')  # Thay 'student.db' thành tên cơ sở dữ liệu của bạn
    conn.row_factory = sqlite3.Row
    return conn

# Route để hiển thị danh sách học sinh
@app.route("/")
def list_students():
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template('index.html', students=students)

# Route để thêm học sinh
@app.route("/students/create", methods=["POST"])
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
            "INSERT INTO students (age, gender, economic_status, gpa, credits_completed, days_absent, part_time_job, health_status, result) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (age, gender, economic_status, gpa, credits_completed, days_absent, part_time_job, health_status, result),
        )
        conn.commit()
        conn.close()

        flash("Student added successfully!",'success')
        return redirect(url_for('list_students'))

# Route để sửa thông tin học sinh
@app.route("/students/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    conn = get_db_connection()
    student = conn.execute("SELECT * FROM students WHERE student_id = ?", (id,)).fetchone()
    conn.close()

    if request.method == "POST":
        # Lấy dữ liệu từ form gửi lên
        age = request.form["age"]
        gender = request.form["gender"]
        economic_status = request.form["economic_status"]
        gpa = request.form["gpa"]
        credits_completed = request.form["credits_completed"]
        days_absent = request.form["days_absent"]
        part_time_job = request.form["part_time_job"]
        health_status = request.form["health_status"]
        result = request.form["result"]

        # Cập nhật thông tin học sinh vào cơ sở dữ liệu
        conn = get_db_connection()
        conn.execute(
            "UPDATE students SET age = ?, gender = ?, economic_status = ?, gpa = ?, credits_completed = ?, days_absent = ?, part_time_job = ?, health_status = ?, result = ? WHERE student_id = ?",
            (age, gender, economic_status, gpa, credits_completed, days_absent, part_time_job, health_status, result, id),
        )
        conn.commit()
        conn.close()

        flash('Student updated successfully!','success')
        return redirect(url_for('list_students'))  # Redirect về danh sách học sinh

    # Nếu là GET request, trả về form để sửa thông tin học sinh


# Route để xóa học sinh
@app.route("/students/delete/<int:id>", methods=["POST"])
def delete_student(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE student_id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Student deleted successfully!",'success')
    return redirect(url_for('list_students'))

if __name__ == '__main__':
    app.run(debug=True)
