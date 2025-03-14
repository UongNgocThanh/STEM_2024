from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
import sqlite3
from datetime import datetime

# from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import re  # Import thư viện re để kiểm tra biểu thức chính quy

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

import requests


# Kết nối cơ sở dữ liệu SQLite
def get_db_connection():
    conn = sqlite3.connect('student.db') 
    conn.row_factory = sqlite3.Row
    return conn

# Route để hiển thị danh sách học sinh
@app.route("/students")
def list_students():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    total_failed_students = conn.execute("SELECT COUNT(*) FROM students WHERE result = 'Rớt môn'").fetchone()[0]
    partTime_students = conn.execute("SELECT COUNT(*) FROM students WHERE part_time_job = 'Có'").fetchone()[0]
    total_heathless_students = conn.execute("SELECT COUNT(*) FROM students WHERE health_status = 'Bị bệnh'").fetchone()[0]
    current_datetime = datetime.now().strftime('%a, %d %b %Y') 
    name = session['name']
    username = session['username']

    conn.close()
    return render_template('index.html',
                            students=students,
                            total_students=total_students,
                            total_failed_students=total_failed_students,
                            current_datetime=current_datetime,
                            partTime_students=partTime_students,
                            total_heathless_students=total_heathless_students, 
                            name = name, username=username)
# Hàm kiểm tra tính hợp lệ của email
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, email))

# Hàm kiểm tra mật khẩu mạnh
def is_strong_password(password):
    return len(password) >= 8 and any(c.isdigit() for c in password) and any(c.isalpha() for c in password)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        errors = []

        if not username:
            errors.append("Tên tài khoản không được để trống.")
        if not password:
            errors.append("Mật khẩu không được để trống.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("login.html")

        try:
            with get_db_connection() as conn:
                user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['name'] = user['name']
                session['username'] = user['username']
                return redirect(url_for('index'))
            else:
                flash("Tài khoản hoặc mật khẩu không đúng!", "danger")
        except sqlite3.Error as e:
            print(f"Lỗi SQLite: {e}")
            flash("Đã xảy ra lỗi khi kết nối cơ sở dữ liệu. Vui lòng thử lại.", "danger")

    return render_template("login.html")



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        errors = []
        if not name:
            errors.append("Họ và tên không được để trống.")
        
        if not username:
            errors.append("Tên tài khoản (email) không được để trống.")
        elif not is_valid_email(username):
            errors.append("Tên tài khoản phải là một email hợp lệ.")
        
        if not password or not confirm_password:
            errors.append("Mật khẩu và xác nhận mật khẩu không được để trống.")
        elif password != confirm_password:
            errors.append("Mật khẩu không khớp.")
        elif not is_strong_password(password):
            errors.append("Mật khẩu phải dài ít nhất 8 ký tự và chứa cả chữ cái và số.")
        
        # Dừng lại nếu có lỗi
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("register.html")
        
        try:
            conn = get_db_connection()
            existing_user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            if existing_user:
                flash("Tên tài khoản đã tồn tại.", "danger")
                return render_template("register.html")

            hashed_password = generate_password_hash(password)
            conn.execute("INSERT INTO users (name, username, password) VALUES (?, ?, ?)", (name, username, hashed_password))
            conn.commit()
            conn.close()

            flash("Đăng ký thành công! Hãy đăng nhập.", "success")
            return redirect(url_for('login'))
        except sqlite3.Error as e:
            print(f"Lỗi SQLite: {e}")
            flash("Đã xảy ra lỗi khi kết nối cơ sở dữ liệu. Vui lòng thử lại.", "danger")
    
    return render_template("register.html")


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('name', None)
    return redirect(url_for('index'))

# Route để thêm học sinh
@app.route("/students/create", methods=["POST"])
def create_student():
    if request.method == "POST":
        age = request.form["age"]
        gender = request.form["gender"]
        economic_status = request.form["economic_status"]
        gpa = float(request.form["gpa"])
        credits_completed = request.form["credits_completed"]
        days_absent = int(request.form["days_absent"])
        part_time_job = request.form["part_time_job"]
        health_status = request.form["health_status"]

        economic_status_map = {"Nghèo": 0, "Cận nghèo": 1, "Bình thường": 2, "Giàu": 3}
        part_time_job_map = {"Có": 1, "Không": 0}
        health_status_map = {"Bình thường": 0, "Bị bệnh": 1}

        economy = economic_status_map.get(economic_status, -1)
        part_time = part_time_job_map.get(part_time_job, -1)
        health_statuss = health_status_map.get(health_status, -1)

        if economy == -1 or part_time == -1 or health_statuss == -1:
            return "Dữ liệu không hợp lệ", 400

        ai_payload = {
            "economy": economy,
            "gpa": gpa,
            "absent_days": days_absent,
            "part_time": part_time,
            "health_status": health_statuss
        }
        # Gui request
        try:
            ai_response = requests.post("http://127.0.0.1:5001/predict", json=ai_payload)
            ai_response.raise_for_status()
            ai_result = ai_response.json()

            result = ai_result.get("result", 0)

        except requests.RequestException as e:
            flash(f"Lỗi khi gọi API AI: {e}", "danger")
            return redirect(url_for('list_students'))

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO students (age, gender, economic_status, gpa, credits_completed, days_absent, part_time_job, health_status, result) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (age, gender, economic_status, gpa, credits_completed, days_absent, part_time_job, health_status, result),
        )
        conn.commit()
        conn.close()

        accuracy_response = requests.get("http://127.0.0.1:5001/evaluate")
        accuracy_response.raise_for_status()

        accuracy = accuracy_response.json().get("accuracy", 0)

        flash(f"Thêm sinh viên thành công! Độ chính xác của thông tin này là {accuracy}",'success')
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
        gpa = float(request.form["gpa"])
        credits_completed = request.form["credits_completed"]
        days_absent = int(request.form["days_absent"])
        part_time_job = request.form["part_time_job"]
        health_status = request.form["health_status"]

        # Map các giá trị từ form sang giá trị API yêu cầu
        economic_status_map = {"Nghèo": 0, "Cận nghèo": 1, "Bình thường": 2, "Giàu": 3}
        part_time_job_map = {"Có": 1, "Không": 0}
        health_status_map = {"Bình thường": 0, "Bị bệnh": 1}

        # Debug log để kiểm tra các giá trị
        print("Economic Status:", economic_status)
        print("Part-time Job:", part_time_job)
        print("Health Status:", health_status)

        # Convert giá trị
        economy = economic_status_map.get(economic_status, -1)
        part_time = part_time_job_map.get(part_time_job, -1)
        health_statuss = health_status_map.get(health_status, -1)
        print(economy)
        print(part_time)
        print(health_statuss)

        # Kiểm tra lỗi nếu không có giá trị hợp lệ
        if economy == -1 or part_time == -1 or health_statuss == -1:
            return f"Dữ liệu không hợp lệ: {economic_status}, {part_time_job}, {health_statuss}", 400
        
        # Chuẩn bị payload gửi đến API
        ai_payload = {
            "economy": economy,
            "gpa": gpa,
            "absent_days": days_absent,
            "part_time": part_time,
            "health_status": health_statuss
        }

        try:
            # Gửi yêu cầu đến API để dự đoán kết quả
            ai_response = requests.post("http://127.0.0.1:5001/predict", json=ai_payload)
            ai_response.raise_for_status()
            ai_result = ai_response.json()
            result = ai_result.get("result", 0)
        except requests.RequestException as e:
            flash(f"Lỗi khi gọi API AI: {e}", "danger")
            return redirect(url_for('list_students'))

        # Cập nhật thông tin học sinh vào cơ sở dữ liệu
        conn = get_db_connection()
        conn.execute(
            "UPDATE students SET age = ?, gender = ?, economic_status = ?, gpa = ?, credits_completed = ?, days_absent = ?, part_time_job = ?, health_status = ?, result = ? WHERE student_id = ?",
            (age, gender, economic_status, gpa, credits_completed, days_absent, part_time_job, health_status, result, id),
        )
        conn.commit()
        conn.close()

        accuracy_response = requests.get("http://127.0.0.1:5001/evaluate")
        accuracy_response.raise_for_status()

        accuracy = accuracy_response.json().get("accuracy", 0)

        flash(f'Đã cập nhật thành công thông tin sinh viên! Độ chính xác của thông tin này là {accuracy}','success')
        return redirect(url_for('list_students'))  


# Route để xóa học sinh
@app.route("/students/delete/<int:id>", methods=["POST"])
def delete_student(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE student_id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Đã xóa thành công sinh viên!",'success')
    return redirect(url_for('list_students'))

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('list_students'))

if __name__ == '__main__':
    app.run(debug=True)
