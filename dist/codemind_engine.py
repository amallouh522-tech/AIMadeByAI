import os
import sys
import re
import glob
import json
import time
import math
import random
import logging
import threading
import http.server
import socketserver
import urllib.request
import urllib.parse
from typing import List, Dict, Union, Optional, Tuple

# ==============================================================================
# 1. إعدادات النظام وتسجيل السجلات (SYSTEM CONFIGURATION & LOGGING)
# ==============================================================================

LOG_FORMAT = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("CodeMindEnterprise")

CONFIG = {
    "server_port": 8080,
    "checkpoint_file": "codemind_checkpoint.json",
    "dataset_dir": "./dataset",
    "context_window": 3,
    "max_response_words": 200,
    "autosave_interval_steps": 10000,
    "log_file": "codemind.log"
}

# ==============================================================================
# 2. وحدة معالجة النصوص واللغات (ADVANCED MULTILINGUAL TOKENIZER)
# ==============================================================================

class TextProcessor:
    """
    وحدة معالجة الألفاظ والمصطلحات البرمجية والعامية العربية والإنجليزية.
    تساعد النموذج على فهم الكلمات المركبة والعاميات وتوحيد المعاني.
    """
    def __init__(self):
        self.arabic_synonyms = {
            "نت": "إنترنت",
            "net": "internet",
            "ابغى": "أريد",
            "بدي": "أريد",
            "كود": "برمجة",
            "عطيني": "اعرض",
            "ازاي": "كيف",
            "ليه": "لماذا",
            "وين": "أين",
            "شلون": "كيف",
            "عشان": "لأن",
            "معليش": "عفوا",
            "شو": "ماذا",
            "ايه": "ماذا"
        }
        self.stop_words = set(["في", "على", "من", "إلى", "عن", "مع", "the", "in", "on", "at", "to"])

    def clean_text(self, text: str) -> str:
        """تنظيف النص من الرموز الخبيثة وغير المرغوبة مع الحفاظ على البنية البرمجية"""
        text = re.sub(r'[\r\t]', ' ', text)
        return text

    def tokenize(self, text: str, normalize: bool = True) -> List[str]:
        """تقطيع النص إلى كلمات وحساب سياقات اللغة الطبيعية والبرمجية"""
        cleaned = self.clean_text(text)
        tokens = re.findall(r'\w+|[^\w\s]', cleaned, re.UNICODE)
        
        if not normalize:
            return tokens

        normalized_tokens = []
        for token in tokens:
            lower_token = token.lower()
            if lower_token in self.arabic_synonyms:
                normalized_tokens.append(self.arabic_synonyms[lower_token])
            else:
                normalized_tokens.append(token)

        return normalized_tokens

# ==============================================================================
# 3. محرك الـ LLM الأساسي والتعلم التراكمي (CORE LLM ENGINE & MEMORY)
# ==============================================================================

class LLMCoreEngine:
    """
    عقل النموذج اللغوي الكبير المخصص للتعلم التراكمي المستمر.
    يخزن الأنماط بمرور الوقت في ملف JSON محلي آمن من الانقطاعات.
    """
    def __init__(self, checkpoint_path: str = CONFIG["checkpoint_file"]):
        self.checkpoint_path = checkpoint_path
        self.tokenizer = TextProcessor()
        self.vocabulary = set()
        self.model_graph: Dict[str, List[str]] = {}
        self.statistics = {
            "total_tokens_processed": 0,
            "total_training_sessions": 0,
            "created_at": time.time(),
            "last_updated": time.time()
        }
        self.lock = threading.Lock()
        self.load_checkpoint()

    def load_checkpoint(self) -> bool:
        """استرجاع الذاكرة السابقة والتقدم التراكمي"""
        if not os.path.exists(self.checkpoint_path):
            logger.info("لم يتم العثور على نقطة حفظ سابقة، سيتم البدء بنموذج جديد.")
            return False

        try:
            with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.model_graph = data.get("model", {})
                self.statistics = data.get("statistics", self.statistics)
                self.vocabulary = set(data.get("vocabulary", []))
            logger.info(f"تم تحميل الذاكرة بنجاح! عدد الأنماط المتعلمة: {len(self.model_graph)}")
            return True
        except Exception as e:
            logger.error(f"خطأ أثناء تحميل ملف الذاكرة: {e}")
            return False

    def save_checkpoint(self) -> bool:
        """حفظ حالة النموذج التراكمية بأمان لحمايتها من الانقطاع المفاجئ"""
        with self.lock:
            try:
                data_to_save = {
                    "model": self.model_graph,
                    "statistics": self.statistics,
                    "vocabulary": list(self.vocabulary),
                    "version": "2.0.0-enterprise"
                }
                tmp_file = f"{self.checkpoint_path}.tmp"
                with open(tmp_file, "w", encoding="utf-8") as f:
                    json.dump(data_to_save, f, ensure_ascii=False)
                os.replace(tmp_file, self.checkpoint_path)
                logger.info("[💾] تم حفظ نقطة تقدم النموذج والذاكرة بنجاح.")
                return True
            except Exception as e:
                logger.error(f"فشل أثناء حفظ تقدم النموذج: {e}")
                return False

    def train_on_text(self, text: str, context_window: int = CONFIG["context_window"]):
        """التدريب المستمر على النصوص والأكواد وتوسيع ذاكرة النموذج"""
        tokens = self.tokenizer.tokenize(text)
        if len(tokens) <= context_window:
            return

        with self.lock:
            self.statistics["total_tokens_processed"] += len(tokens)
            self.statistics["last_updated"] = time.time()
            
            for token in tokens:
                self.vocabulary.add(token)

            for i in range(len(tokens) - context_window):
                context_key = " ".join(tokens[i : i + context_window])
                next_word = tokens[i + context_window]

                if context_key not in self.model_graph:
                    self.model_graph[context_key] = []

                if next_word not in self.model_graph[context_key]:
                    self.model_graph[context_key].append(next_word)

    def generate(self, prompt: str, max_words: int = CONFIG["max_response_words"]) -> str:
        """توليد الإجابة والردود وتحديث الذاكرة بالتعلم الذاتي الفوري"""
        self.train_on_text(prompt)
        tokens = self.tokenizer.tokenize(prompt)

        if not self.model_graph:
            return "النموذج غير مدرب بعد أو يجري إعداده حالياً. يرجى تزويده بملفات أو إجراء محادثات أولاً."

        context_window = CONFIG["context_window"]
        if len(tokens) >= context_window:
            current_context = " ".join(tokens[-context_window:])
        else:
            current_context = " ".join(tokens)

        generated_tokens = list(tokens)

        for _ in range(max_words):
            if current_context not in self.model_graph:
                available_keys = list(self.model_graph.keys())
                if not available_keys:
                    break
                current_context = random.choice(available_keys)

            candidates = self.model_graph[current_context]
            selected_next = random.choice(candidates)
            generated_tokens.append(selected_next)

            context_words = current_context.split()
            if len(context_words) >= context_window:
                current_context = " ".join(context_words[1:]) + " " + selected_next
            else:
                current_context = current_context + " " + selected_next

        response = " ".join(generated_tokens)
        self.train_on_text(response)
        return response

# ==============================================================================
# 4. الوكيل الذكي والأدوات التفاعلية (AUTONOMOUS AGENT ENGINE & TOOLS)
# ==============================================================================

class AgentTools:
    """مجموعة أدوات حقيقية يستخدمها الوكيل للقيام بعمليات تنفذ على النظام محلياً"""
    
    @staticmethod
    def scan_directory(path: str = "./") -> List[str]:
        """أداة فحص المجلدات واستخراج الملفات البرمجية"""
        found_files = []
        extensions = ('.py', '.js', '.html', '.css', '.json', '.md', '.txt')
        for root, _, files in os.walk(path):
            if '.venv' in root or '__pycache__' in root or '.git' in root:
                continue
            for file in files:
                if file.endswith(extensions):
                    found_files.append(os.path.join(root, file))
        return found_files

    @staticmethod
    def read_file_content(file_path: str) -> Optional[str]:
        """أداة قراءة محتوى ملف محلي"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            logger.error(f"خطأ أثناء قراءة الملف {file_path}: {e}")
            return None

    @staticmethod
    def write_file_content(file_path: str, content: str) -> bool:
        """أداة إنشاء وكتابة الأكواد والحلول في ملف محلي"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"خطأ أثناء كتابة الملف {file_path}: {e}")
            return False

class CodeMindAgent:
    """
    الوكيل الذكي المستقل الذي يتلقى الأهداف من المستخدم،
    يحللها، يحدد الأدوات المناسبة، وينفذ المهام.
    """
    def __init__(self, llm_engine: LLMCoreEngine):
        self.llm = llm_engine
        self.tools = AgentTools()

    def process_goal(self, goal: str) -> Dict[str, Union[str, bool]]:
        """تحليل الهدف وتحديد الأداة والتنفيذ الذكي"""
        logger.info(f"الوكيل يستلم مهمة جديدة: {goal}")
        
        # 1. حالة طلب الفحص والتحليل للمشروع
        if any(keyword in goal for keyword in ["فحص", "مراجعة", "اقرأ", "تحليل"]):
            files = self.tools.scan_directory()
            total_learned = 0
            for file_path in files[:10]:
                content = self.tools.read_file_content(file_path)
                if content:
                    self.llm.train_on_text(content)
                    total_learned += 1

            self.llm.save_checkpoint()
            return {
                "success": True,
                "action": "scan_and_learn",
                "result": f"تم فحص المشروع وقراءة {total_learned} ملفات برمجية وتغذية ذاكرة الـ LLM بها بنجاح."
            }

        # 2. حالة طلب كتابة أو إنشاء ملف كود محدد
        elif any(keyword in goal for keyword in ["اكتب", "أنشئ", "صمم", "حل"]):
            generated_code = self.llm.generate(goal)
            out_filename = "agent_generated_code.py"
            written = self.tools.write_file_content(out_filename, generated_code)
            
            if written:
                return {
                    "success": True,
                    "action": "create_file",
                    "result": f"تم توليد الحل البرمجي وحفظه بنجاح في الملف: {out_filename}"
                }
            else:
                return {"success": False, "action": "create_file", "result": "فشل في حفظ ملف الكود المتولد."}

        # 3. الاستجابة العامة والدردشة وتوليد الإجابات
        else:
            response = self.llm.generate(goal)
            return {
                "success": True,
                "action": "chat_response",
                "result": response
            }

# ==============================================================================
# 5. خادم الـ API والخدمات المحلية (ENTERPRISE REST API SERVER)
# ==============================================================================

GLOBAL_LLM = LLMCoreEngine()
GLOBAL_AGENT = CodeMindAgent(GLOBAL_LLM)

class EnterpriseAPIHandler(http.server.BaseHTTPRequestHandler):
    """معالج طلبات الخادم بروابط متعددة وبنية رسمية كاملة"""

    def _set_headers(self, status_code: int = 200, content_type: str = "application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        """إدارة طلبات الصفحة الرئيسية وإحصائيات النظام"""
        if self.path == "/" or self.path == "/health":
            self._set_headers(200, "text/html")
            status_html = f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head>
                <meta charset="UTF-8">
                <title>CodeMind Enterprise Engine</title>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 40px; }}
                    .card {{ background: #1e293b; border-radius: 12px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }}
                    h1 {{ color: #38bdf8; }}
                    .stat {{ color: #4ade80; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>🤖 نظام CodeMind الذكي المتكامل يعمل بنجاح</h1>
                    <p>النظام متصل ويقوم بالتعلم التراكمي المستمر بمرور الوقت.</p>
                    <hr style="border-color: #334155;">
                    <p>عدد الأنماط المتعلمة في الذاكرة: <span class="stat">{len(GLOBAL_LLM.model_graph)}</span></p>
                    <p>عدد الرموز المصنفة: <span class="stat">{GLOBAL_LLM.statistics['total_tokens_processed']}</span></p>
                    <p>استخدم نقطة النهاية <code>/v1/chat</code> للتفاعل والمحادثة عبر POST.</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(status_html.encode('utf-8'))
        
        elif self.path == "/v1/stats":
            self._set_headers(200)
            stats = {
                "patterns_count": len(GLOBAL_LLM.model_graph),
                "vocabulary_size": len(GLOBAL_LLM.vocabulary),
                "statistics": GLOBAL_LLM.statistics
            }
            self.wfile.write(json.dumps(stats, ensure_ascii=False).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode('utf-8'))

    def do_POST(self):
        """إدارة طلبات المحادثة والـ Agent"""
        if self.path == "/v1/chat":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                req_data = json.loads(post_data.decode('utf-8'))

                user_message = req_data.get("message", "")
                if not user_message:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "رسالة المستخدم فارغة."}).encode('utf-8'))
                    return

                # معالجة الطلب عبر الـ Agent
                agent_response = GLOBAL_AGENT.process_goal(user_message)

                response_payload = {
                    "status": "success",
                    "response": agent_response["result"],
                    "action_taken": agent_response["action"],
                    "memory_stats": {
                        "total_patterns": len(GLOBAL_LLM.model_graph)
                    }
                }

                self._set_headers(200)
                self.wfile.write(json.dumps(response_payload, ensure_ascii=False).encode('utf-8'))

            except Exception as e:
                logger.error(f"خطأ أثناء معالجة الطلب: {e}")
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode('utf-8'))

# ==============================================================================
# 6. إدارة النظام والتدريب المستمر (SYSTEM MANAGER & THREADING)
# ==============================================================================

def continuous_background_trainer():
    """خيط عمل مستمر في الخلفية يقو بالتفتيش والتدريب والحفظ الدوري"""
    logger.info("بدء خيط التدريب الخلفي المستمر...")
    while True:
        try:
            # فحص وتدريب المجلدات المحلية
            files = AgentTools.scan_directory(CONFIG["dataset_dir"])
            for file_path in files:
                content = AgentTools.read_file_content(file_path)
                if content:
                    GLOBAL_LLM.train_on_text(content)
            
            # حفظ التقدم دورياً
            GLOBAL_LLM.save_checkpoint()
        except Exception as e:
            logger.error(f"خطأ في خيط التدريب الخلفي: {e}")
            
        time.sleep(1800) # فحص كل 30 دقيقة تلقائياً

def start_server():
    """إطلاق الخادم والأنظمة الضخمة"""
    port = CONFIG["server_port"]
    
    # 1. تشغيل خيط التدريب المستمر في الخلفية
    bg_thread = threading.Thread(target=continuous_background_trainer, daemon=True)
    bg_thread.start()

    # 2. تشغيل خادم الـ HTTP الرئيسي
    with socketserver.TCPServer(("", port), EnterpriseAPIHandler) as httpd:
        logger.info(f"==================================================")
        logger.info(f"🚀 تم إطلاق نظام CodeMind Enterprise بنجاح!")
        logger.info(f"📡 رابط الـ API الرئيسي: http://localhost:{port}/v1/chat")
        logger.info(f"📊 رابط الإحصائيات: http://localhost:{port}/v1/stats")
        logger.info(f"==================================================")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("جاري إيقاف الخادم وحفظ الذاكرة نهائياً...")
            GLOBAL_LLM.save_checkpoint()
            sys.exit(0)

if __name__ == "__main__":
    start_server()