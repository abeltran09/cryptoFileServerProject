import socket
import json
import threading
import time
import uuid
from dataHandler import load_data, save_data


class GroupServer(threading.Thread):
    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        print(f"New Connection from {addr}")

    def run(self):
        while True:
            try:
                data = self.conn.recv(1024).decode()
                if not data:
                    break
                request = json.loads(data)
                response = self.handle_request(request)
                self.conn.send(json.dumps(response).encode())
            except Exception as e:
                print(f"Error: {e}")
                break
        self.conn.close()

    def handle_request(self, request):
        action = request.get("action")
        if action == "connect":
            return {"status": "success", "message": "Connected to Group Server"}
        elif action == "get_token":
            return self.get_token(request.get("username"))
        elif action == "create_user":
            return self.create_user(request.get("username"), request.get("password"), request.get("token"))
        elif action == "create_group":
            return self.create_group(request.get("group_name"), request.get("token"))
        elif action == "add_user_to_group":
            return self.add_user_to_group(request.get("username"), request.get("group_name"), request.get("token"))
        elif action == "list_members":
            return self.list_members(request.get("group_name"), request.get("token"))
        return {"status": "error", "message": "Invalid action"}

    def get_token(self, username):
        pass

    def create_user(self, username, password, token):
        pass

    def create_group(self, group_name, token):
        pass

    def add_user_to_group(self, username, group_name, token):
        pass

    def list_members(self, group_name, token):
        pass

# Start the server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5000))
    server.listen(5)
    print("Group Server is running on port 5000...")
    while True:
        conn, addr = server.accept()
        handler = GroupServer(conn, addr)
        handler.start()

if __name__ == "__main__":
    start_server()

        