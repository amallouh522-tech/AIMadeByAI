# llm_core.py - واجهة نموذج اللغة الكبير
from codemind_engine import LLMCoreEngine

class PureLLM(LLMCoreEngine):
    def __init__(self):
        super().__init__()
        print("[🧠 LLM Core] عقل النموذج اللغوي جاهز ويعمل بكفاءة.")

if __name__ == "__main__":
    llm = PureLLM()
    print("تجربة توليد:", llm.generate("مرحباً بك"))