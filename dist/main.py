# main.py - نقطة الدخول الرسمية للنظام
from codemind_engine import start_server

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 جاري تهيئة وتشغيل نظام CodeMind Enterprise الرسمي...")
    print("=" * 60)
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[🛑] تم إيقاف النظام بأمان بواسطة المستخدم.")