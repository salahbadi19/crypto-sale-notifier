import os
import sqlite3
import time
import subprocess

# اسم قاعدة البيانات
DB_FILE = "timer.db"

# مدة التشغيل بالثواني (6 ساعات)
TOTAL_SECONDS = 6 * 60 * 60  

# الملفات المراد حذفها بعد انتهاء الوقت
FILES_TO_DELETE = ["bot_guard.py", "main.py"]

# تهيئة قاعدة البيانات وتسجيل الوقت
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time REAL
        )
    """)
    conn.commit()
    conn.close()

# تسجيل وقت بدء التشغيل
def log_start_time():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO timer (start_time) VALUES (?)", (time.time(),))
    conn.commit()
    conn.close()

# تشغيل bot_guard.py
def run_bot_guard():
    # هذا سيشغل الملف في عملية فرعية
    subprocess.Popen(["python3", "bot_guard.py"])
    print("تم تشغيل bot_guard.py")

# حذف الملفات بعد انتهاء الوقت
def delete_files():
    for file in FILES_TO_DELETE:
        if os.path.exists(file):
            os.remove(file)
            print(f"تم حذف {file}")
        else:
            print(f"{file} غير موجود")

# البرنامج الرئيسي
def main():
    init_db()
    log_start_time()
    run_bot_guard()
    print(f"سيتم حذف الملفات بعد {TOTAL_SECONDS / 3600} ساعات...")
    time.sleep(TOTAL_SECONDS)
    delete_files()

if __name__ == "__main__":
    main()
