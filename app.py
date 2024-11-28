from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
import sqlite3
# from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import re  # Import thư viện re để kiểm tra biểu thức chính quy
# from flask_login import login_required

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


def get_db_connection():
    conn = sqlite3.connect('student.db')  # Thay 'stem.db' thành tên cơ sở dữ liệu của bạn
    conn.row_factory = sqlite3.Row
    return conn

# Hàm kiểm tra tính hợp lệ của email
def is_valid_email(email):
    # Biểu thức chính quy để kiểm tra định dạng email hợp lệ
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, email))

# Hàm kiểm tra mật khẩu mạnh
def is_strong_password(password):
    return len(password) >= 8 and any(c.isdigit() for c in password) and any(c.isalpha() for c in password)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Kiểm tra tên người dùng (email) và mật khẩu có được nhập đúng chưa
        if not username or not password:
            flash("Tên tài khoản và mật khẩu không được để trống.", "danger")

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for('index'))
        else:
            flash("Tên tài khoản hoặc mật khẩu không đúng.", "danger")
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try: 
            name = request.form['name']
            username = request.form['username']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            # Kiểm tra tính hợp lệ của email
            if not is_valid_email(username):
                flash("Tên tài khoản phải là một email hợp lệ.", "danger")

            # Validate mật khẩu không khớp
            if password != confirm_password:
                flash("Mật khẩu không khớp.", "danger")

            # Kiểm tra độ mạnh mật khẩu
            if not is_strong_password(password):
                flash("Mật khẩu phải dài ít nhất 8 ký tự và chứa cả chữ cái và số.", "danger")

            hashed_password = generate_password_hash(password)

            try:
                conn = get_db_connection()
                # Kiểm tra xem tên người dùng (email) có tồn tại trong cơ sở dữ liệu chưa
                existing_user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
                if existing_user:
                    flash("Tên tài khoản đã tồn tại.", "danger")

                conn.execute("INSERT INTO users (name, username, password) VALUES (?, ?, ?)", (name, username, hashed_password))
                conn.commit()
                conn.close()
                flash("Đăng ký thành công! Hãy đăng nhập.", "success")
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash("Lỗi khi đăng ký tài khoản.", "danger")
        except Exception as e:
            # Xử lý lỗi, ghi log và thông báo cho người dùng
            print(f"Đã xảy ra lỗi: {e}")
            flash("Lỗi khi đăng ký tài khoản.", "danger")
    return render_template("register.html")

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash("Đăng xuất thành công!", "success")
    return redirect(url_for('index'))

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

@app.route('/')
def index():
    if 'user_id' not in session:
        flash("Vui lòng đăng nhập để truy cập trang này", "danger")
        return redirect(url_for('login'))
    
    # Thực hiện các thao tác cần thiết để lấy dữ liệu cho dashboard nếu có
    return render_template('index.html')  # Thay 'index.html' bằng tên template của bạn

if __name__ == '__main__':
    app.run(debug=True)
