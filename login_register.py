from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import re  # Import thư viện re để kiểm tra biểu thức chính quy

login_register = Flask(__name__)
login_register.secret_key = 'a_random_secret_key_here'  # Cần thay đổi thành một secret key bảo mật

# Kết nối cơ sở dữ liệu
def get_db_connection():
    conn = sqlite3.connect('student.db')
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

@login_register.route('/', methods=['GET', 'POST'])
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

@login_register.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
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
    return render_template("register.html")

@login_register.route('/index')
def index():
    if 'user_id' not in session:
        flash("Vui lòng đăng nhập để truy cập trang này", "danger")
        return redirect(url_for('login'))
    
    # Thực hiện các thao tác cần thiết để lấy dữ liệu cho dashboard nếu có
    return render_template('index.html')  # Thay 'index.html' bằng tên template của bạn

if __name__ == "__main__":
    login_register.run(debug=True)
