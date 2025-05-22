import http.server
import json
import os

PORT = 8000
NOTES_FILE = "notes.json"
USERS_FILE = "users.json"

def load_json(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/notes":
            notes = load_json(NOTES_FILE, [])
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(notes).encode("utf-8"))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/add_note":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            note = json.loads(post_data.decode("utf-8"))
            notes = load_json(NOTES_FILE, [])
            notes.append(note)
            save_json(NOTES_FILE, notes)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        elif self.path == "/remove_note":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))
            notes = load_json(NOTES_FILE, [])
            notes = [n for n in notes if not (
                n.get("x") == data.get("x") and
                n.get("y") == data.get("y") and
                n.get("user") == data.get("user")
            )]
            save_json(NOTES_FILE, notes)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        elif self.path == "/update_note":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            note = json.loads(post_data.decode("utf-8"))
            notes = load_json(NOTES_FILE, [])
            for n in notes:
                if n.get("x") == note.get("x") and n.get("y") == note.get("y") and n.get("user") == note.get("user"):
                    n["text"] = note.get("text", "")
            save_json(NOTES_FILE, notes)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        elif self.path == "/signup":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))
            users = load_json(USERS_FILE, {})
            if data["username"] in users:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": "Username already exists"}).encode("utf-8"))
            else:
                users[data["username"]] = data["password"]
                save_json(USERS_FILE, users)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
        elif self.path == "/login":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))
            users = load_json(USERS_FILE, {})
            if users.get(data["username"]) == data["password"]:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
            else:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": "Invalid username or password"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    # Ensure notes.json and users.json exist
    if not os.path.exists(NOTES_FILE):
        save_json(NOTES_FILE, [])
    if not os.path.exists(USERS_FILE):
        save_json(USERS_FILE, {})
    from http.server import ThreadingHTTPServer
    server_address = ("", PORT)
    httpd = ThreadingHTTPServer(server_address, Handler)
    print(f"Serving at http://localhost:{PORT}/index.html")
    httpd.serve_forever()