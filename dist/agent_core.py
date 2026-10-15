# agent_core.py - واجهة الوكيل الذكي المستقل
from codemind_engine import LLMCoreEngine, CodeMindAgent

class AgentInterface:
    def __init__(self):
        self.llm = LLMCoreEngine()
        self.agent = CodeMindAgent(self.llm)
        print("[🤖 Agent Core] الوكيل الذكي والأدوات جاهزة للعمل.")

    def run_goal(self, goal):
        return self.agent.process_goal(goal)

if __name__ == "__main__":
    agent_sys = AgentInterface()
    result = agent_sys.run_goal("فحص المشروع")
    print(result)