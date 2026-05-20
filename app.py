import sqlite3
import customtkinter as ctk
from tkinter import ttk

# ضبط المظهر العام للجيل الجديد
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- 1. قسم دالات قاعدة البيانات والمنطق البرمجي ---
def init_db():
    conn = sqlite3.connect("institute_v2.db")
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()

def refresh_table():
    for row in table.get_children():
        table.delete(row)
    conn = sqlite3.connect("institute_v2.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, course, remaining_fee FROM students ORDER BY id DESC")
    rows = cursor.fetchall()
    for row in rows:
        table.insert("", ctk.END, values=row)
    conn.close()

def add_student_logic():
    name = entry_name.get()
    course = entry_course.get()
    total = entry_total.get()
    paid = entry_paid.get()
    
    if not name or not course or not total or not paid:
        lbl_status_add.configure(text="⚠️ الرجاء ملء جميع الخانات!", text_color="#e74c3c")
        return
    try:
        total_val = float(total)
        paid_val = float(paid)
        if total_val < 0 or paid_val < 0 or paid_val > total_val:
            lbl_status_add.configure(text="⚠️ أرقام الرسوم غير منطقية!", text_color="#e74c3c")
            return
            
        remaining_val = total_val - paid_val
        conn = sqlite3.connect("institute_v2.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students (name, course, total_fee, paid_fee, remaining_fee)
            VALUES (?, ?, ?, ?, ?)
        """, (name, course, total_val, paid_val, remaining_val))
        conn.commit()
        conn.close()
        
        # إشعار خفيف على الجنب بدون نوافذ منبثقة
        lbl_status_add.configure(text=f"✓ تم إضافة الطالب {name} بنجاح", text_color="#2ecc71")
        
        entry_name.delete(0, ctk.END); entry_course.delete(0, ctk.END)
        entry_total.delete(0, ctk.END); entry_paid.delete(0, ctk.END)
        refresh_table()
    except ValueError:
        lbl_status_add.configure(text="⚠️ أدخل أرقاماً صحيحة!", text_color="#e74c3c")

def pay_installment_logic():
    student_id = entry_id.get()
    amount = entry_amount.get()
    if not student_id or not amount:
        lbl_status_pay.configure(text="⚠️ املأ خانات القسط!", text_color="#e74c3c")
        return
    try:
        s_id = int(student_id); pay_val = float(amount)
        if pay_val <= 0: return
        conn = sqlite3.connect("institute_v2.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, paid_fee, remaining_fee FROM students WHERE id = ?", (s_id,))
        student = cursor.fetchone()
        if student:
            if pay_val > student[2]:
                lbl_status_pay.configure(text="⚠️ المبلغ أكبر من المتبقي!", text_color="#e74c3c")
                conn.close(); return
            cursor.execute("UPDATE students SET paid_fee = ?, remaining_fee = ? WHERE id = ?", (student[1]+pay_val, student[2]-pay_val, s_id))
            conn.commit()
            
            lbl_status_pay.configure(text=f"✓ تم دفع قسط {student[0]} بنجاح", text_color="#2ecc71")
            entry_id.delete(0, ctk.END); entry_amount.delete(0, ctk.END)
            refresh_table()
        else:
            lbl_status_pay.configure(text="⚠️ رقم الطالب غير موجود!", text_color="#e74c3c")
        conn.close()
    except ValueError:
        lbl_status_pay.configure(text="⚠️ أدخل بيانات رقمية!", text_color="#e74c3c")

def update_reports_page():
    """دالة تقوم بجلب التقارير وحقنها داخل الصفحة الثانية مباشرة دون فتح نافذة جديدة"""
    conn = sqlite3.connect("institute_v2.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, remaining_fee FROM students WHERE remaining_fee > 0 ORDER BY name ASC")
    debtors = cursor.fetchall()
    
    debtors_text = "".join([f"👤 {r[0]}  <- المتبقي عليه: {r[1]} جنيه\n" for r in debtors]) if debtors else "🎉 لا يوجد طلاب متأخرين! الخزنة مستقرة.\n"
    
    cursor.execute("SELECT SUM(paid_fee) FROM students")
    total_in_safe = cursor.fetchone()[0] or 0
    conn.close()
    
    # تحديث النصوص داخل صفحة الجرد الحالية هسي
    lbl_safe_amount.configure(text=f"💰 إجمالي الأموال في الخزينة حالياً: {total_in_safe} جنيه")
    txt_debtors.configure(state="normal")
    txt_debtors.delete("1.0", ctk.END)
    txt_debtors.insert("1.0", debtors_text)
    txt_debtors.configure(state="disabled")

# --- 2. بناء الواجهة بنظام التبويب والصفحات المتنقلة ---
init_db()
root = ctk.CTk()
root.title("🏢 نظام إدارة المعهد الذكي - نسخة الصفحات الاحترافية")
root.geometry("850x450")  # الأبعاد الآمنة تماماً لنصف شاشتك الشغال
root.resizable(False, False)

# 📑 استخدام أداة CTkTabview لصنع الصفحات في نفس المكان
tabview = ctk.CTkTabview(root, width=830, height=390)
tabview.pack(pady=5, padx=10, fill="both", expand=True)

# إضافة الصفحات
page_main = tabview.add("📊 لوحة التحكم والطلاب")
page_reports = tabview.add("📊 جرد الخزنة والتقرير الحالي")

# تفعيل تحديث صفحة التقارير تلقائياً هسي عندما يضغط المستخدم على تبويب الجرد
def on_tab_change():
    if tabview.get() == "📊 جرد الخزنة والتقرير الحالي":
        update_reports_page()

tabview.configure(command=on_tab_change)


# ==================== [ الصفحة الأولى: إدارة الطلاب ] ====================
top_frame = ctk.CTkFrame(page_main, fg_color="transparent")
top_frame.pack(pady=5, fill="x")

# مربع التسجيل (يمين)
f_registration = ctk.CTkFrame(top_frame, width=400, corner_radius=10)
f_registration.pack(side="right", padx=5, fill="both", expand=True)
ctk.CTkLabel(f_registration, text="➕ تسجيل طالب جديد", font=("Arial", 12, "bold"), text_color="#2ecc71").grid(row=0, column=0, columnspan=2, pady=2)
entry_name = ctk.CTkEntry(f_registration, placeholder_text="الاسم الكامل", width=180, justify="right")
entry_name.grid(row=1, column=1, padx=5, pady=2)
entry_course = ctk.CTkEntry(f_registration, placeholder_text="الكورس", width=180, justify="right")
entry_course.grid(row=1, column=0, padx=5, pady=2)
entry_total = ctk.CTkEntry(f_registration, placeholder_text="إجمالي الرسوم", width=180, justify="right")
entry_total.grid(row=2, column=1, padx=5, pady=2)
entry_paid = ctk.CTkEntry(f_registration, placeholder_text="المدفوع حالياً", width=180, justify="right")
entry_paid.grid(row=2, column=0, padx=5, pady=2)

# زر الحفظ ومعه إشعار خفيف على الجنب هسي بنفس الواجهة
ctk.CTkButton(f_registration, text="حفظ الطالب", fg_color="#2ecc71", hover_color="#27ae60", height=22, command=add_student_logic).grid(row=3, column=1, pady=4)
lbl_status_add = ctk.CTkLabel(f_registration, text="", font=("Arial", 11, "bold"))
lbl_status_add.grid(row=3, column=0, pady=4, padx=5)

# مربع الأقساط (يسار)
f_installments = ctk.CTkFrame(top_frame, width=400, corner_radius=10)
f_installments.pack(side="left", padx=5, fill="both", expand=True)
ctk.CTkLabel(f_installments, text="💵 إدارة الأقساط", font=("Arial", 12, "bold"), text_color="#3498db").grid(row=0, column=0, columnspan=2, pady=2)
entry_id = ctk.CTkEntry(f_installments, placeholder_text="رقم الطالب ID", width=180, justify="right")
entry_id.grid(row=1, column=1, padx=5, pady=5)
entry_amount = ctk.CTkEntry(f_installments, placeholder_text="مبلغ القسط", width=180, justify="right")
entry_amount.grid(row=1, column=0, padx=5, pady=5)

ctk.CTkButton(f_installments, text="تسجيل القسط", fg_color="#3498db", hover_color="#2980b9", height=22, command=pay_installment_logic).grid(row=2, column=1, pady=5)
lbl_status_pay = ctk.CTkLabel(f_installments, text="", font=("Arial", 11, "bold"))
lbl_status_pay.grid(row=2, column=0, pady=5, padx=5)

# الجدول الحي في المنتصف
table_frame = ctk.CTkFrame(page_main, height=150, fg_color="#2b2b2b")
table_frame.pack(pady=5, padx=5, fill="both", expand=True)

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=22, font=("Arial", 10))
style.configure("Treeview.Heading", background="#1f1f1f", foreground="white", font=("Arial", 11, "bold"))

table = ttk.Treeview(table_frame, columns=("id", "name", "course", "remaining"), show="headings")
table.heading("id", text="ID")
table.heading("name", text="اسم الطالب")
table.heading("course", text="الكورس")
table.heading("remaining", text="المتبقي")
table.column("id", anchor="center", width=50)
table.column("name", anchor="center", width=250)
table.column("course", anchor="center", width=180)
table.column("remaining", anchor="center", width=100)
table.pack(fill="both", expand=True, padx=5, pady=5)


# ==================== [ الصفحة الثانية: جرد الخزنة والتقارير ] ====================
lbl_report_title = ctk.CTkLabel(page_reports, text="📊 لوحة التقارير المالية الحية (بدون نوافذ منبثقة)", font=("Arial", 14, "bold"), text_color="#f1c40f")
lbl_report_title.pack(pady=5)

# مربع عرض أموال الخزنة ثابت في الواجهة
lbl_safe_amount = ctk.CTkLabel(page_reports, text="💰 إجمالي الأموال في الخزينة حالياً: 0 جنيه", font=("Arial", 14, "bold"), fg_color="#1f1f1f", corner_radius=8, height=35)
lbl_safe_amount.pack(pady=5, fill="x", padx=20)

lbl_debtor_title = ctk.CTkLabel(page_reports, text="⚠️ قائمة الطلاب المتأخرين عن السداد:", font=("Arial", 12, "bold"))
lbl_debtor_title.pack(pady=2, anchor="e", padx=20)

# صندوق نصي كبير داخل الصفحة لعرض قائمة المتأخرين
txt_debtors = ctk.CTkTextbox(page_reports, height=150, font=("Arial", 12), fg_color="#2b2b2b", text_color="white", justify="right")
txt_debtors.pack(pady=5, fill="both", expand=True, padx=20)


# --- شريط الإغلاق السفلي المشترك ---
btn_exit = ctk.CTkButton(root, text="❌ إغلاق النظام بأمان", fg_color="#e74c3c", hover_color="#c0392b", height=25, command=root.quit)
btn_exit.pack(pady=5)

refresh_table()
root.mainloop()
