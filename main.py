"""
نقطة الدخول الرئيسية للنظام (Main Orchestrator)
مسؤول عن إطلاق الخادم وخيط التدريب الذاتي المستمر في الخلفية (Autonomous Sync & Training).
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
    تبحث تلقائياً وبشكل دوري في ويكيبيديا وتجري عمليات بحث ذاتية في GitHub لسحب الأكواد وتطوير الذاكرة.
    """
    logger.info("بدء خيط التدريب التلقائي المستمر في الخلفية (Autonomous Learner)...")
    engine_instance = CoreLLMEngine()

    wiki_topics_pool = [
        "برمجة الحاسوب", "لغة بايثون", "ذكاء اصطناعي", "تعلم عميق",
        "خوارزمية البحث الثنائي", "هيكل بيانات", "جافا سكريبت", "هندسة البرمجيات"
    ]

    github_search_keywords = [
        "python AI agent", "javascript framework", "python algorithms", "fastapi backend"
    ]

    while True:
        try:
            logger.info("[🔄 Autonomous Training] بدء دورة التدريب والتحديث الذاتي في الخلفية...")

            # 1. التدريب على الملفات المحلية
            local_files = AgentToolbox.scan_project_files(CONFIG["dataset_dir"])
            for f_path in local_files:
                content = AgentToolbox.read_target_file(f_path)
                if content:
                    engine_instance.train_on_text(content)

            # 2. البحث الذاتي وسحب مقالة من ويكيبيديا
            selected_topic = random.choice(wiki_topics_pool)
            wiki_content = AgentToolbox.fetch_wikipedia_article(selected_topic)
            if wiki_content:
                engine_instance.train_on_text(wiki_content)
                logger.info(f"[🌐 Auto-Wiki] تمت إضافة معارف مقالة '{selected_topic}' للذاكرة.")

            # 3. البحث الذاتي وسحب الأكواد من GitHub بناءً على كلمات مفتاحية
            selected_kw = random.choice(github_search_keywords)
            logger.info(f"[🐙 Auto-GitHub Search] البحث في جيت هب عن: '{selected_kw}'...")
            repo_files = AgentToolbox.search_and_fetch_github_repos(selected_kw)
            
            github_count = 0
            for code_text in repo_files:
                engine_instance.train_on_text(code_text)
                github_count += 1
            
            if github_count > 0:
                logger.info(f"[✨ GitHub Success] تم جلب وتدريب الذاكرة على {github_count} ملفاً من بحث جيت هب!")

            # 4. حفظ نقطة التقدم والذاكرة محلياً
            engine_instance.save_model_checkpoint()
            logger.info("[💾 Checkpoint] تم حفظ الذاكرة والأنماط المحدثة بنجاح.")

        except Exception as e:
            logger.error(f"خطأ في دورة التدريب الذاتي: {e}")

        # الانتظار للفترة المحددة في الإعدادات قبل الدورة التالية (افتراضياً 300 ثانية أو 60 ثانية)
        sleep_interval = CONFIG.get("background_training_interval_seconds", 300)
        time.sleep(sleep_interval)

def main():
    logger.info("=" * 60)
    logger.info(f"🧠 إطلاق نظام {CONFIG['system_name']} الإصدار {CONFIG['version']}")
    logger.info("=" * 60)

    # 1. تشغيل مسار التدريب والبحث الذاتي المستمر في الخلفية
    training_thread = threading.Thread(target=background_continuous_training_worker, daemon=True)
    training_thread.start()

    # 2. تشغيل خادم الـ API الرئيسي في الواجهة
    try:
        run_enterprise_server()
    except KeyboardInterrupt:
        logger.info("[🛑] تم إيقاف النظام الرئيسي بأمان بواسطة المستخدم.")

if __name__ == "__main__":
    main()