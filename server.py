"""
خادم الـ API المحلي (HTTP API Server)
يستقبل طلبات الـ POST للدردشة والـ GET للإحصائيات بطريقة رسمية ومتكاملة.
"""

import json
import http.server
import socketserver
from config import CONFIG, logger
from llm_core import CoreLLMEngine
from agent_tools import CodeMindAgentSystem

# تهيئة المحركات المركزية للخادم
server_llm_engine = CoreLLMEngine()
server_agent_system = CodeMindAgentSystem(server_llm_engine)

class EnterpriseAPIRequestHandler(http.server.BaseHTTPRequestHandler):
    def _send_response_headers(self, status_code: int = 200, content_type: str = "application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._send_response_headers(200)

    def do_GET(self):
        if self.path == "/" or self.path == "/health":
            self._send_response_headers(200, "text/html")
            dashboard_html = f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head>
                <meta charset="UTF-8">
                <title>{CONFIG["system_name"]}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; }}
                    .box {{ background: #1e293b; border-radius: 10px; padding: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }}
                    h1 {{ color: #38bdf8; }}
                    .num {{ color: #4ade80; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="box">
                    <h1>🚀 نظام CodeMind Enterprise يعمل بكفاءة تامة</h1>
                    <p>خادم الـ API والتعلم المستمر في وضع التشغيل النشط.</p>
                    <hr style="border-color: #334155;">
                    <p>إجمالي الأنماط البرمجية المتعلمة: <span class="num">{len(server_llm_engine.model_graph)}</span></p>
                    <p>إجمالي الرموز المعالجة: <span class="num">{server_llm_engine.statistics['total_tokens_processed']}</span></p>
                    <p>نقطة النهاية للتفاعل (POST): <code>/v1/chat</code></p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(dashboard_html.encode('utf-8'))

        elif self.path == "/v1/stats":
            self._send_response_headers(200)
            payload = {
                "system": CONFIG["system_name"],
                "version": CONFIG["version"],
                "patterns_count": len(server_llm_engine.model_graph),
                "vocabulary_size": len(server_llm_engine.vocabulary),
                "statistics": server_llm_engine.statistics
            }
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))
        else:
            self._send_response_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode('utf-8'))

    def do_POST(self):
        if self.path == "/v1/chat":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_length)
                request_json = json.loads(raw_body.decode("utf-8"))

                user_message = request_json.get("message", "")
                if not user_message:
                    self._send_response_headers(400)
                    self.wfile.write(json.dumps({"error": "رسالة المستخدم فارغة."}).encode('utf-8'))
                    return

                # تنفيذ المهمة عبر الوكيل والنظام الذكي
                result_output = server_agent_system.execute_user_objective(user_message)

                response_payload = {
                    "status": "success",
                    "data": result_output,
                    "memory_patterns": len(server_llm_engine.model_graph)
                }

                self._send_response_headers(200)
                self.wfile.write(json.dumps(response_payload, ensure_ascii=False).encode('utf-8'))

            except Exception as e:
                logger.error(f"خطأ في معالجة طلب POST: {e}")
                self._send_response_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self._send_response_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode('utf-8'))

def run_enterprise_server():
    port = CONFIG["server_port"]
    with socketserver.TCPServer(("", port), EnterpriseAPIRequestHandler) as httpd:
        logger.info(f"==================================================")
        logger.info(f"🚀 خادم CodeMind Enterprise يعمل على المنفذ: {port}")
        logger.info(f"📡 نقطة المحادثة: http://localhost:{port}/v1/chat")
        logger.info(f"==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("جاري إيقاف الخادم وحفظ الذاكرة نهائياً...")
            server_llm_engine.save_model_checkpoint()