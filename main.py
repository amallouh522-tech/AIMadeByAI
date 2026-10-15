"""
نقطة الدخول الرئيسية للنظام (Main Orchestrator)
مسؤول عن تشغيل خادم الـ API وخيط التدريب التلقائي المستمر الذي يجلب المعرفة من ويكيبيديا والملفات المحلية.
"""

import time
import random
import threading
from config import CONFIG, logger
from llm_core import CoreLLMEngine
from agent_tools import AgentToolbox
from server import run_enterprise_server

def background_continuous_training_worker():
    """
    خلفية النظام الذكية (Autonomous Background Learner):
    تقوم تلقائياً وبشكل دوري بـ:
    1. فحص مجلد الـ dataset المحلي وسحب الأكواد.
    2. سحب مقالات تقنية وبرمجية متجددة من ويكيبيديا وتغذية ذاكرة الـ LLM بها.
    3. حفظ التقدم تلقائياً في ملف الذاكرة.
    """
    logger.info("بدء خيط التدريب التلقائي المستمر في الخلفية (Autonomous Learner)...")
    engine_instance = CoreLLMEngine()

    # قائمة المواضيع والمصطلحات التقنية التي يبحث عنها النظام تلقائياً من ويكيبيديا
    wiki_topics_pool = [
        "برمجة الحاسوب",
        "لغة بايثون",
        "ذكاء اصطناعي",
        "تعلم عميق",
        "خوارزمية البحث الثنائي",
        "هيكل بيانات",
        "جافا سكريبت",
        "قاعدة بيانات",
        "هندسة البرمجيات",
        "شبكة عصبية حيوية"
    ]

    while True:
        try:
            logger.info("[🔄 Autonomous Training] بدء دورة التدريب والتحديث التلقائي...")

            # 1. التعلم التلقائي من الملفات المحلية في مجلد dataset
            local_files = AgentToolbox.scan_project_files(CONFIG["dataset_dir"])
            local_learned = 0
            for file_path in local_files:
                file_content = AgentToolbox.read_target_file(file_path)
                if file_content:
                    engine_instance.train_on_text(file_content)
                    local_learned += 1
            
            if local_learned > 0:
                logger.info(f"[📁 Local Dataset] تم تدريب النظام على {local_learned} ملفاً محلياً.")

            # 2. التعلم التلقائي من ويكيبيديا (اختيار موضوع عشوائي في كل دورة)
            selected_topic = random.choice(wiki_topics_pool)
            logger.info(f"[🌐 Wikipedia Auto-Sync] جاري البحث وجلب مقالة '{selected_topic}' من ويكيبيديا...")
            
            wiki_content = AgentToolbox.fetch_wikipedia_article(selected_topic)
            if wiki_content:
                engine_instance.train_on_text(wiki_content)
                logger.info(f"[✨ Wikipedia Success] تمت إضافة معارف مقالة '{selected_topic}' إلى ذاكرة النموذج بنجاح!")
            
            # 3. حفظ نقطة التقدم والذاكرة محلياً بأمان
            engine_instance.save_model_checkpoint()
            logger.info("[💾 Checkpoint] تم حفظ الذاكرة والأنماط المحدثة بنجاح.")

        except Exception as e:
            logger.error(f"خطأ في دورة التدريب التلقائي الخلفية: {e}")

        # الانتظار للفترة المحددة في الإعدادات قبل الدورة التالية (مثلاً كل 5 دقائق أو حسب رغبتك)
        # يمكنك تعديل الفترة في config.py أو هنا مباشرة (بالثواني)
        sleep_interval = CONFIG.get("background_training_interval_seconds", 300)
        time.sleep(sleep_interval)

def main():
    logger.info("=" * 60)
    logger.info(f"🧠 إطلاق نظام {CONFIG['system_name']} الإصدار {CONFIG['version']}")
    logger.info("=" * 60)

    # 1. إطلاق مسار التدريب والتعلم الذاتي المستمر في الخلفية
    training_thread = threading.Thread(target=background_continuous_training_worker, daemon=True)
    training_thread.start()

    # 2. تشغيل خادم الـ API الرئيسي في الواجهة لاستقبال طلباتك
    try:
        run_enterprise_server()
    except KeyboardInspector if "KeyboardInterrupt" in globals() else Exception:
        pass
    except KeyboardInterrupt:
        logger.info("[🛑] تم إيقاف النظام الرئيسي بأمان بواسطة المستخدم.")

if __name__ == "__main__":
    main()