import http.server
import socketserver
import json
from llm_core import UltimateLLMCore

PORT = 8080
llm_engine = UltimateLLMCore()

class ChatAPIHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/v1/chat":
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                req_json = json.loads(post_data.decode('utf-8'))
                
                user_message = req_json.get("message", "")
                print(f"[💬 رسالة مستلمة]: {user_message}")

                # توليد الرد والحلول الذكية عبر عقل الـ LLM
                ai_reply = llm_engine.generate_response(user_message, max_words=180)

                response_data = {
                    "status": "success",
                    "reply": ai_reply,
                    "memory_patterns": len(llm_engine.model)
                }

                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """
            <html>
            <head><title>Ultimate CodeMind LLM</title></head>
            <body style="font-family: Arial; padding: 30px; background: #0f172a; color: #f8fafc;">
                <h2>🚀 Ultimate CodeMind LLM & Agent Server is Active!</h2>
                <p>الخادم يعمل بأقصى طاقة للتعلم المستمر والدردشة.</p>
                <p>أرسل طلبات <b>POST</b> إلى نقطة النهاية: <code>/v1/chat</code></p>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))

def run_server():
    with socketserver.TCPServer(("", PORT), ChatAPIHandler) as httpd:
        print(f"[🚀] خادم الدردشة والـ API يعمل الآن على: http://localhost:{PORT}/v1/chat")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[🛑] تم إيقاف الخادم.")

if __name__ == "__main__":
    run_server()