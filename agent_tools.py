"""
أدوات الوكيل الذكي (Autonomous Agent Tools) المحدثة والمحصنة ضد التخبط البرمجي
"""

import os
import urllib.request
import urllib.parse
import json
import re
from typing import List, Optional
from config import CONFIG, logger
from llm_core import CoreLLMEngine

class AgentToolbox:
    @staticmethod
    def scan_project_files(target_dir: str = CONFIG["dataset_dir"]) -> List[str]:
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
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            logger.error(f"خطأ أثناء قراءة الملف {file_path}: {e}")
            return None

    @staticmethod
    def live_web_search(query: str) -> Optional[str]:
        """أداة بحث حية في الإنترنت"""
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                abstract = data.get("AbstractText", "")
                if abstract:
                    return abstract
                
                related = data.get("RelatedTopics", [])
                for topic in related:
                    if isinstance(topic, dict) and "Text" in topic:
                        return topic["Text"]
                        
            return None
        except Exception as e:
            logger.error(f"فشل البحث المباشر في الويب عن '{query}': {e}")
            return None

    @staticmethod
    def search_specific_platforms(query: str, platform: str = "reddit") -> Optional[str]:
        """بحث موجه داخل منصات مثل Reddit"""
        try:
            domain_query = f"site:{platform}.com {query}"
            return AgentToolbox.live_web_search(domain_query)
        except Exception as e:
            logger.error(f"فشل البحث في منصة {platform}: {e}")
            return None

    @staticmethod
    def fetch_wikipedia_article(query: str) -> Optional[str]:
        """جلب مقالات ويكيبيديا مع تنظيف الكلمات المفتاحية"""
        try:
            # استخراج الكلمات الأساسية للبحث في ويكيبيديا (إزالة أدوات الاستفهام والأفعال الزائدة)
            clean_q = query
            for word in ["كم", "عمر", "لما", "مات", "توفي", "من هو", "ما هو", "ما هي", "أين", "متى", "في"]:
                clean_q = clean_q.replace(word, "")
            clean_q = clean_q.strip()
            
            encoded_query = urllib.parse.quote(clean_q if len(clean_q) > 2 else query)
            url = f"https://ar.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles={encoded_query}&format=json"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                pages = data.get("query", {}).get("pages", {})
                for page_id, page_info in pages.items():
                    if page_id != "-1" and "extract" in page_info:
                        return page_info["extract"]
            return None
        except Exception as e:
            logger.error(f"فشل جلب ويكيبيديا لـ {query}: {e}")
            return None

    @staticmethod
    def search_and_fetch_github_repos(query_keyword: str) -> List[str]:
        """أداة البحث في جيت هب وسحب الأكواد للتدريب الخلفي"""
        fetched_contents = []
        try:
            encoded_query = urllib.parse.quote(query_keyword)
            api_url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars&order=desc"
            
            headers = {'User-Agent': 'CodeMindBot/3.0'}
            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                search_data = json.loads(response.read().decode('utf-8'))
                items = search_data.get("items", [])
                if items:
                    top_repo = items[0]
                    owner, repo_name = top_repo['owner']['login'], top_repo['name']
                    contents_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"
                    contents_req = urllib.request.Request(contents_url, headers=headers)
                    with urllib.request.urlopen(contents_req, timeout=10) as contents_resp:
                        file_items = json.loads(contents_resp.read().decode('utf-8'))
                        for item in file_items:
                            if item['type'] == 'file' and item['name'].endswith(('.py', '.js', '.html', '.md', '.json')):
                                with urllib.request.urlopen(item['download_url'], timeout=10) as f_resp:
                                    fetched_contents.append(f_resp.read().decode('utf-8', errors='ignore'))
        except Exception as e:
            logger.error(f"فشل البحث في GitHub عن '{query_keyword}': {e}")
        return fetched_contents


class CodeMindAgentSystem:
    def __init__(self, llm_engine: CoreLLMEngine):
        self.llm = llm_engine
        self.toolbox = AgentToolbox()

    def generate_chat_title(self, user_message: str) -> str:
        """توليد عنوان ذكي ومختصر للشات"""
        clean_msg = re.sub(r'[^\w\s]', '', user_message).strip()
        words = clean_msg.split()
        if len(words) <= 4:
            return clean_msg.title() if clean_msg else "محادثة جديدة"
        return " ".join(words[:4]).title() + "..."

    def search_local_memory(self, query: str) -> Optional[str]:
        """فحص الذاكرة المحلية بحثاً عن إجابة قوية متطابقة"""
        tokens = self.llm.tokenizer.tokenize(query)
        
        for context_key, next_words in self.llm.model_graph.items():
            if any(token in context_key for token in tokens if len(token) > 3):
                if next_words:
                    return f"{context_key} " + " ".join(next_words[:10])
        return None

    def execute_user_objective(self, objective: str) -> dict:
        """
        منطق موجه وحاسم:
        1. فحص الذاكرة المحلية أولاً.
        2. البحث الحي في الويب، ويكيبيديا، والمنصات الخارجية للأسئلة العامة.
        3. منع إعطاء ردود برمجية عشوائية (Fallback) للأسئلة العامة نهائياً.
        """
        title = self.generate_chat_title(objective)
        lower_obj = objective.lower()

        # الكلمات المفتاحية للأسئلة الخارجية
        external_triggers = ["كم", "من هو", "متى", "عمر", "أين", "ما هو", "ما هي", "تاريخ", "وفاة", "مات", "مايكل", "michael", "كيف"]
        is_external_query = any(trigger in lower_obj for trigger in external_triggers)

        # الخطوة 1: فحص الذاكرة المحلية إذا لم يكن استعلاماًexternal صريحاً
        local_memory_result = self.search_local_memory(objective)
        if local_memory_result and not is_external_query:
            return {
                "title": title,
                "response": local_memory_result,
                "source": "llm_core_memory"
            }

        # الخطوة 2: البحث الخارجي (ويب، ويكيبيديا، ريديت)
        web_result = self.toolbox.live_web_search(objective)
        
        if not web_result:
            web_result = self.toolbox.search_specific_platforms(objective, "reddit")

        if not web_result:
            web_result = self.toolbox.fetch_wikipedia_article(objective)

        if web_result:
            self.llm.train_on_text(web_result)
            return {
                "title": title,
                "response": web_result,
                "source": "live_web_search"
            }

        # الخطوة 3: التعامل الذكي بدلاً من الـ Fallback العشوائي للأسئلة العامة
        if is_external_query:
            return {
                "title": title,
                "response": "عذراً، لم أتمكن من جلب معلومات كافية حول هذا السؤال من الإنترنت حالياً. يرجى التأكد من الاتصال أو إعادة المحاولة.",
                "source": "web_search_failed"
            }

        # التراجع البرمجي فقط إذا كان السؤال برمجياً بحتاً
        fallback_response = self.llm.generate_response(objective)
        return {
            "title": title,
            "response": fallback_response,
            "source": "llm_core_fallback"
        }