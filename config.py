"""
ملف الإعدادات العامة لنظام CodeMind Enterprise
يحتوي على الثوابت، مسارات الذاكرة، إعدادات الخادم، وسجلات التتبع.
"""

import os
import logging

# إعدادات السجلات العامة (Logging Configuration)
LOG_FORMAT = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("CodeMindEnterprise")

# ثوابت وإعدادات النظام الأساسية
CONFIG = {
    "system_name": "CodeMind Enterprise AI & Agent",
    "version": "3.0.0-stable",
    "server_host": "0.0.0.0",
    "server_port": 8080,
    "checkpoint_file": "codemind_checkpoint.json",
    "dataset_dir": "./dataset",
    "context_window_size": 3,
    "max_response_generation_words": 200,
    "background_training_interval_seconds": 30, # 1 دقيقة
    "supported_extensions": (".py", ".js", ".html", ".css", ".json", ".md", ".txt")
}