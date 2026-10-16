"""
متحكم التشغيل السريع لنظام CodeMind Enterprise
يسمح بتشغيل النظام عبر أوامر مباشرة مثل: python run.py ai
"""

import sys
import os
import subprocess

def main():
    if len(sys.argv) < 2:
        print("❌ الرجاء تحديد الأمر المطلوب. مثال:")
        print("   python run.py ai      (لتشغيل الخادم والذكاء الاصطناعي)")
        print("   python run.py stats   (لعرض إحصائيات الذاكرة)")
        return

    command = sys.argv[1].lower()

    if command == "ai" or command == "server":
        print("🚀 جاري تشغيل عقل CodeMind Enterprise بالكامل...")
        os.system("python3 main.py")
        
    elif command == "stats":
        print("📊 جاري جلب الإحصائيات الحية للذاكرة...")
        import urllib.request
        import json
        try:
            with urllib.request.urlopen("http://localhost:8080/v1/stats") as response:
                data = json.loads(response.read().decode('utf-8'))
                print(json.dumps(data, indent=4, ensure_ascii=False))
        except Exception as e:
            print(f"⚠️ الخادم غير متصل أو لا يعمل حالياً: {e}")
            
    else:
        print(f"❌ الأمر '{command}' غير معروف. استخدم 'ai' أو 'stats'.")

if __name__ == "__main__":
    main()