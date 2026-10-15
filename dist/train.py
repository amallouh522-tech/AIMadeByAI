import os
import glob
import subprocess
import urllib.request
import json
from pathlib import Path

class CodeTrainer:
    def __init__(self, order=4, model_file="codemind_checkpoint.json"):
        self.order = order
        self.model = {}
        self.model_file = model_file
        self.load_checkpoint()

    def save_checkpoint(self):
        """حفظ نقاط التقدم والنموذج لحمايته من انقطاع الكهرباء"""
        try:
            data_to_save = {
                "order": self.order,
                "model": {k: list(v) for k, v in self.model.items()}
            }
            with open(self.model_file, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False)
            print("[💾] تم حفظ وتحديث نقاط التقدم بنجاح في الذاكرة.")
        except Exception as e:
            print(f"[!] خطأ أثناء حفظ التقدم: {e}")

    def load_checkpoint(self):
        """استرجاع التقدم السابق"""
        if os.path.exists(self.model_file):
            try:
                with open(self.model_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.order = data.get("order", 4)
                    self.model = data.get("model", {})
                print(f"[+] تم تحميل الذاكرة بنجاح! إجمالي الأنماط المحفوظة: {len(self.model)}")
            except Exception as e:
                print(f"[!] لم يتم قراءة الذاكرة القديمة: {e}")

    def update_from_github(self, target_dir="./dataset"):
        """جلب مشاريع من GitHub (يتخطى تلقائياً عند انقطاع الإنترنت)"""
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)

        languages = ["python", "javascript", "html", "cpp"]
        print("[*] فحص وتحديث المشاريع من GitHub...")

        for lang in languages:
            try:
                url = f"https://api.github.com/search/repositories?q=language:{lang}&sort=stars&order=desc"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    items = data.get("items", [])[:1]
                    
                    for repo in items:
                        repo_url = repo["clone_url"]
                        repo_name = repo["name"]
                        repo_path = os.path.join(target_dir, f"{lang}_{repo_name}")

                        if not os.path.exists(repo_path):
                            print(f"[-] جاري تحميل مشروع ({lang}): {repo_name} ...")
                            try:
                                subprocess.run(["git", "clone", "--depth", "1", repo_url, repo_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            except Exception:
                                pass
            except Exception:
                print("[!] وضع التشغيل بدون إنترنت: سيتم الاعتماد على الأكواد المخزنة محلياً.")
                break

    def load_dataset(self, folder_path="./dataset"):
        """قراءة الملفات البرمجية"""
        code_text = ""
        extensions = ["*.py", "*.js", "*.html", "*.css", "*.ts", "*.cpp", "*.json"]

        for ext in extensions:
            pattern = os.path.join(folder_path, "**", ext)
            for filepath in glob.glob(pattern, recursive=True):
                if ".git" in filepath or "node_modules" in filepath:
                    continue
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        code_text += f.read() + "\n"
                except Exception:
                    pass
        return code_text

    def train(self):
        """عملية التدريب الشاملة"""
        self.update_from_github()
        text = self.load_dataset()

        if len(text) < self.order:
            print("[!] البيانات قليلة جداً للتدريب.")
            return

        print("[*] جاري تدريب النموذج على الأكواد...")
        total = len(text) - self.order
        for i in range(total):
            context = text[i : i + self.order]
            next_char = text[i + self.order]
            
            if context not in self.model:
                self.model[context] = []
            if next_char not in self.model[context]:
                self.model[context].append(next_char)

            if i > 0 and i % 50000 == 0:
                self.save_checkpoint()

        self.save_checkpoint()
        print(f"[+] اكتمل التدريب بنجاح! الإجمالي النهائي: {len(self.model)} نمط.")

if __name__ == "__main__":
    trainer = CodeTrainer()
    trainer.train()