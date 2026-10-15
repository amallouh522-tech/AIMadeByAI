"""
محرك الـ LLM الأساسي (LLM Core Engine)
يدير الذاكرة، الخوارزميات الاحتمالية للسياق، التعلم التراكمي، والحفظ الآمن.
"""

import os
import json
import time
import random
import threading
from typing import List, Dict, Any
from config import CONFIG, logger
from tokenizer import AdvancedTokenizer

class CoreLLMEngine:
    def __init__(self):
        logger.info("جاري إطلاق عقل نموذج الـ LLM التراكمي...")
        self.tokenizer = AdvancedTokenizer()
        self.checkpoint_path = CONFIG["checkpoint_file"]
        self.context_window = CONFIG["context_window_size"]
        
        self.model_graph: Dict[str, List[str]] = {}
        self.vocabulary = set()
        self.statistics = {
            "total_tokens_processed": 0,
            "training_sessions": 0,
            "created_at": time.time(),
            "last_updated": time.time()
        }
        self.thread_lock = threading.Lock()
        self.load_model_checkpoint()

    def load_model_checkpoint(self) -> bool:
        """تحميل الذاكرة السابقة للنموذج من الملف المحلي بأمان"""
        if not os.path.exists(self.checkpoint_path):
            logger.info("لم يُعثر على ملف ذاكرة سابق، تم تهيئة نموذج جديد كلياً.")
            return False

        with self.thread_lock:
            try:
                with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.model_graph = data.get("model", {})
                    self.vocabulary = set(data.get("vocabulary", []))
                    self.statistics = data.get("statistics", self.statistics)
                logger.info(f"تم تحميل الذاكرة بنجاح! إجمالي الأنماط البرمجية والمعرفية: {len(self.model_graph)}")
                return True
            except Exception as e:
                logger.error(f"حدث خطأ فادح أثناء قراءة ملف الذاكرة: {e}")
                return False

    def save_model_checkpoint(self) -> bool:
        """حفظ الحالة الحالية للنموذج لمنع فقدان البيانات عند انقطاع الكهرباء"""
        with self.thread_lock:
            try:
                payload = {
                    "model": self.model_graph,
                    "vocabulary": list(self.vocabulary),
                    "statistics": self.statistics,
                    "engine_version": CONFIG["version"]
                }
                tmp_filename = f"{self.checkpoint_path}.tmp"
                with open(tmp_filename, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False)
                os.replace(tmp_filename, self.checkpoint_path)
                logger.info("[💾] تم حفظ تقدم الذاكرة والأنماط محلياً بنجاح.")
                return True
            except Exception as e:
                logger.error(f"فشل حفظ نقطة التقدم: {e}")
                return False

    def train_on_text(self, raw_text: str):
        """تدريب النموذج تدريجياً وتحديث شبكة السياق والكلمات"""
        tokens = self.tokenizer.tokenize(raw_text)
        if len(tokens) <= self.context_window:
            return

        with self.thread_lock:
            self.statistics["total_tokens_processed"] += len(tokens)
            self.statistics["last_updated"] = time.time()

            for token in tokens:
                self.vocabulary.add(token)

            for i in range(len(tokens) - self.context_window):
                context_key = " ".join(tokens[i : i + self.context_window])
                next_word = tokens[i + self.context_window]

                if context_key not in self.model_graph:
                    self.model_graph[context_key] = []

                if next_word not in self.model_graph[context_key]:
                    self.model_graph[context_key].append(next_word)

    def generate_response(self, prompt: str, word_limit: int = CONFIG["max_response_generation_words"]) -> str:
        """توليد الإجابات، الحلول، والأكواد بناءً على الذاكرة التراكمية وسياق المستخدم"""
        # يتعلم النظام فوراً من السؤال المطروح لضمان التطور المستمر
        self.train_on_text(prompt)
        tokens = self.tokenizer.tokenize(prompt)

        if not self.model_graph:
            return "الذاكرة لا تحتوي على بيانات كافية بعد. أضف نصوصاً أو ملفات لمجلد dataset ليصبح أذكى."

        if len(tokens) >= self.context_window:
            current_context = " ".join(tokens[-self.context_window:])
        else:
            current_context = " ".join(tokens)

        generated_tokens = list(tokens)

        for _ in range(word_limit):
            if current_context not in self.model_graph:
                all_keys = list(self.model_graph.keys())
                if not all_keys:
                    break
                current_context = random.choice(all_keys)

            possible_next_words = self.model_graph[current_context]
            selected_word = random.choice(possible_next_words)
            generated_tokens.append(selected_word)

            context_words = current_context.split()
            if len(context_words) >= self.context_window:
                current_context = " ".join(context_words[1:]) + " " + selected_word
            else:
                current_context = current_context + " " + selected_word

        final_response = " ".join(generated_tokens)
        # يتعلم أيضاً من الرد المتولد لرفع دقة الجودة لاحقاً
        self.train_on_text(final_response)
        return final_response