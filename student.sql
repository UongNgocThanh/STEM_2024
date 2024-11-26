CREATE TABLE students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Mã SV, sử dụng tự động tăng cho ID
    age INTEGER,                                   -- Tuổi
    gender TEXT,                                   -- Giới tính
    economic_status TEXT,                          -- Tình hình kinh tế
    gpa REAL,                                      -- GPA
    credits_completed INTEGER,                     -- Số tín chỉ hoàn thành
    days_absent INTEGER,                           -- Số ngày vắng (Không phép)
    part_time_job TEXT,                            -- Làm thêm (TEXT để lưu thông tin về công việc)
    health_status TEXT,                            -- Tình hình sức khỏe
    result TEXT                                     -- Kết quả
);
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
