"""
أدوات الوكيل الذكي (Autonomous Agent Tools) المحدثة
تتيح للوكيل قراءة الملفات المحلية، جلب المقالات من ويكيبيديا، وتحميل وفحص المستودعات من GitHub.
"""

import os
import glob
import urllib.request
import urllib.parse
import json
from typing import List, Optional
from config import CONFIG, logger
from llm_core import CoreLLMEngine

class AgentToolbox:
    @staticmethod
    def scan_project_files(target_dir: str = CONFIG["dataset_dir"]) -> List[str]:
        """فحص المجلدات المحلية واستخراج المسارات البرمجية"""
        discovered_files = []
        for root, _, files in os.walk(target_dir):
            if any(excluded in root for excluded in ['.venv', '__pycache__', '.git']):
                continue
            for file in files:
                if file.endswith(CONFIG["supported_extensions"]):
                    discovered_files.append(os.path.join(root, file))
        return discovered_files

    @staticmethod
    def read_target_file(file_path: str) -> Optional[str]:
        """قراءة محتوى ملف برمجي محلي"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            logger.error(f"خطأ أثناء قراءة الملف {file_path}: {e}")
            return None

    @staticmethod
    def fetch_wikipedia_article(query: str) -> Optional[str]:
        """أداة جديدة: جلب ملخص مقالة من ويكيبيديا (عربي أو إنجليزي) لتدريب النموذج"""
        try:
            encoded_query = urllib.parse.quote(query)
            # استخدام واجهة ويكيبيديا البرمجية المفتوحة
            url = f"https://ar.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles={encoded_query}&format=json"
            
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'CodeMindEnterpriseBot/3.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                pages = data.get("query", {}).get("pages", {})
                for page_id, page_info in pages.items():
                    if page_id != "-1" and "extract" in page_info:
                        logger.info(f"[🌐 Wikipedia] تم بنجاح جلب محتوى المقالة: {query}")
                        return page_info["extract"]
            return None
        except Exception as e:
            logger.error(f"فشل جلب ويكيبيديا لـ {query}: {e}")
            return None

    @staticmethod
    def clone_or_fetch_github_repo(repo_owner: str, repo_name: str) -> List[str]:
        """أداة جديدة: جلب قائمة الملفات وأكواد سورس من مستودع عام على GitHub وفحصها"""
        fetched_contents = []
        try:
            api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents"
            req = urllib.request.Request(
                api_url, 
                headers={'User-Agent': 'CodeMindEnterpriseBot/3.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                items = json.loads(response.read().decode('utf-8'))
                for item in items:
                    if item['type'] == 'file' and item['name'].endswith(('.py', '.js', '.html', '.md')):
                        # تحميل محتوى كل ملف برمجي من المستودع مباشرة
                        file_download_url = item['download_url']
                        with urllib.request.urlopen(file_download_url, timeout=10) as file_resp:
                            code_content = file_resp.read().decode('utf-8', errors='ignore')
                            fetched_contents.append(code_content)
                            logger.info(f"[🐙 GitHub] تم سحب الملف بنجاح: {item['name']}")
        except Exception as e:
            logger.error(f"فشل الاتصال بـ GitHub للمستودع {repo_owner}/{repo_name}: {e}")
        
        return fetched_contents

    @staticmethod
    def write_solution_to_file(file_path: str, content: str) -> bool:
        """كتابة وحفظ الأكواد في ملف محلي"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"تم إنشاء وتخزين الملف بنجاح: {file_path}")
            return True
        except Exception as e:
            logger.error(f"فشل حفظ الملف {file_path}: {e}")
            return False

class CodeMindAgentSystem:
    def __init__(self, llm_engine: CoreLLMEngine):
        logger.info("جاري تهيئة الوكيل الذكي المستقل (CodeMindAgentSystem) مع أدوات الإنترنت والـ GitHub...")
        self.llm = llm_engine
        self.toolbox = AgentToolbox()

    def execute_user_objective(self, objective: str) -> dict:
        """تحليل الهدف الموجه للوكيل وتنفيذه باستخدام الأدوات المتقدمة"""
        logger.info(f"الوكيل يستلم الهدف: {objective}")

        # 1. حالة طلب التعلم من ويكيبيديا (مثال: "تعلم عن الذكاء الاصطناعي من ويكيبيديا")
        if "ويكيبيديا" in objective or "wikipedia" in objective.lower():
            # استخراج الكلمة المراد البحث عنها بعد كلمة ويكيبيديا
            query = objective.replace("ويكيبيديا", "").replace("wikipedia", "").strip()
            if not query:
                query = "برمجة الحاسوب"
            
            wiki_text = self.toolbox.fetch_wikipedia_article(query)
            if wiki_text:
                self.llm.train_on_text(wiki_text)
                self.llm.save_model_checkpoint()
                return {
                    "status": "success",
                    "action": "wikipedia_learning",
                    "message": f"تم جلب مقالة '{query}' من ويكيبيديا بنجاح وتدريب نموذج الـ LLM عليها وتحديث الذاكرة!"
                }
            else:
                return {
                    "status": "error",
                    "action": "wikipedia_learning",
                    "message": f"عذراً، لم أتمكن من العثور على مقالة مطابقة لـ '{query}' في ويكيبيديا."
                }

        # 2. حالة طلب سحب مشروع من جيت هب (مثال: "اسحب مشروع من github username/repo")
        elif "github" in objective.lower() or "جيت هب" in objective:
            # افتراضياً نجرب سحب مستودع تجريبي أو استخراج اسم المستخدم والمستودع إذا تم كتابتهما
            # مثال افتراضي مستودع شهير أو يمكن تخصيصه
            owner, repo = "octocat", "Hello-World" # افتراضي للاختبار
            if "/" in objective:
                parts = [p for p in objective.split() if "/" in p]
                if parts:
                    repo_path = parts[0].split("/")
                    if len(repo_path) == 2:
                        owner, repo = repo_path[0], repo_path[1]

            repo_files = self.toolbox.clone_or_fetch_github_repo(owner, repo)
            trained_count = 0
            for code_text in repo_files:
                self.llm.train_on_text(code_text)
                trained_count += 1
            
            if trained_count > 0:
                self.llm.save_model_checkpoint()
                return {
                    "status": "success",
                    "action": "github_sync",
                    "message": f"تم بنجاح جلب وفحص {trained_count} ملفات برمجية من المستودع {owner}/{repo} وتدريب الذاكرة عليها!"
                }
            else:
                return {
                    "status": "error",
                    "action": "github_sync",
                    "message": f"فشل سحب الملفات من المستودع {owner}/{repo}. تأكد من أن الرابط صحيح أو أن المستودع عام."
                }

        # 3. حالة فحص الملفات المحلية التقليدية
        elif any(w in objective for w in ["فحص", "مراجعة", "scan"]):
            files = self.toolbox.scan_project_files()
            learned_count = 0
            for f_path in files[:15]:
                content = self.toolbox.read_target_file(f_path)
                if content:
                    self.llm.train_on_text(content)
                    learned_count += 1
            
            self.llm.save_model_checkpoint()
            return {
                "status": "success",
                "action": "project_scan",
                "message": f"تم فحص المجلد المحلي وقراءة {learned_count} ملفاً برمجياً وتحديث الذاكرة."
            }

        # 4. طلب كتابة كود برمجي
        elif any(w in objective for w in ["اكتب", "أنشئ", "صمم", "حل"]):
            generated_code = self.llm.generate_response(objective)
            output_filename = "agent_solution_output.py"
            success = self.toolbox.write_solution_to_file(output_filename, generated_code)
            
            if success:
                return {
                    "status": "success",
                    "action": "code_generation",
                    "message": f"تم توليد الحل بنجاح وحفظه في الملف: {output_filename}"
                }
            else:
                return {"status": "error", "action": "code_generation", "message": "فشل حفظ الملف."}

        # 5. محادثة عامة
        else:
            response_text = self.llm.generate_response(objective)
            return {
                "status": "success",
                "action": "general_chat",
                "message": response_text
            }