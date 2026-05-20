def init_db():
    conn = sqlite3.connect("institute_v2.db")
    cursor = conn.cursor()
    # 1. جدول الطلاب الأساسي
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            total_fee REAL NOT NULL,
            paid_fee REAL NOT NULL,
            remaining_fee REAL NOT NULL
        )
    """)
    # 2. الجدول الجديد: سجل الدفعات والأقساط التاريخي المطور
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            student_name TEXT,
            amount_paid REAL,
            payment_date TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)
    conn.commit()
    conn.close()
    
