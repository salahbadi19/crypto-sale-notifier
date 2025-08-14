import time
import subprocess

RUN_DURATION = 5 * 60  # مدة التشغيل: 5 دقائق
PAUSE_DURATION = 1     # مدة التوقف: ثانية واحدة

while True:
    try:
        # تشغيل main.py
        process = subprocess.Popen(["python3", "main.py"])
        print("🚀 main.py بدأ العمل...")
        
        # الانتظار لمدة 5 دقائق
        time.sleep(RUN_DURATION)
        
        # إيقاف العملية بعد 5 دقائق
        process.terminate()
        print("⏹ main.py توقف لمدة ثانية واحدة...")
        
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
    
    # الانتظار ثانية واحدة قبل إعادة التشغيل
    time.sleep(PAUSE_DURATION)
