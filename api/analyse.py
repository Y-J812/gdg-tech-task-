from http.server import BaseHTTPRequestHandler
import json
from engine import analyse
class handler(BaseHTTPRequestHandler):
 def do_POST(self):
  try:
   n=int(self.headers.get("Content-Length","0")); d=json.loads(self.rfile.read(n).decode())
   out=analyse(str(d.get("questions","")),str(d.get("syllabus","")),d.get("hours",10))
   self.send_response(200);self.send_header("Content-Type","application/json; charset=utf-8");self.end_headers();self.wfile.write(json.dumps(out).encode())
  except Exception as e:
   self.send_response(400);self.send_header("Content-Type","application/json; charset=utf-8");self.end_headers();self.wfile.write(json.dumps({"error":str(e)}).encode())
