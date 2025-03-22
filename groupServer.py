import socket
import json
import threading
import time
import uuid
import logging
from dataHandler import load_data, save_data, createUserPayload, createGroupPayload
from tokenHandler import generateToken, decodeToken, createTokenPayload

logging.basicConfig(level=logging.ERROR)

class GroupServer(threading.Thread):
    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.data = load_data()
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
            return self.create_user(request.get("username"), request.get("token"))
        elif action == "create_group":
            return self.create_group(request.get("group_name"), request.get("token"))
        elif action == "add_user_to_group":
            return self.add_user_to_group(request.get("username"), request.get("group_name"), request.get("token"))
        elif action == "list_members":
            return self.list_members(request.get("group_name"), request.get("token"))
        return {"status": "error", "message": "Invalid action"}

    def get_token(self, username):
        try:
            if username not in self.data["users"]:
                return {"status": "failed", "message": "username Entered Does not exist"}
            elif username in self.data["users"] and self.data["users"][username].get("token"):
                return {"status": "success", "token": self.data["users"][username].get("token")}
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {"status": "failed", "message": "failed to get token"}

    def create_user(self, username, userToken):
        try:
            decoded_token = decodeToken(userToken)
            if "./ADMIN" not in decoded_token["groups"]:
                return {"status": "failed", "message": f"User: {decoded_token['username']} is not in the ./ADMIN group"}

            token_payload = createTokenPayload(username)
            token = generateToken(token_payload)

            user_payload = createUserPayload(username, token)

            self.data["users"].update(user_payload)
            save_data(self.data)
            return {"status": "success", "message": f"User: {username} has been created by {decoded_token.get('username')}"}
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {"status": "failed", "message": "failed to create user"}


    def create_group(self, group_name, token):
        decoded_token = decodeToken(token)
        if group_name in self.data["group_servers"]:
            return {"status": "failed", "message": f"group already exist try another name"}
        group_payload = createGroupPayload(group_name, token)
        self.data["group_servers"].update(group_payload)
        save_data(self.data)
        return {"status": "success", "message": f"Group: {group_name} has been created by group owner {decoded_token.get('username')}"}



    def add_user_to_group(self, username, group_name, token):
        decoded_token = decodeToken(token)
        if self.data["group_servers"][group_name]["owner"] != decoded_token.get("username"):
            return {"status": "failed", "message": f"Owner of token and group server owner don't match"}
        elif group_name not in self.data["group_servers"]:
            return {"status": "failed", "message": f"Group does not exist"}
        elif username not in self.data["users"]:
            return {"status": "failed", "message": f"User: {username} does not exist, create user first"}
        elif username in self.data["group_servers"][group_name]["members"]:
            return {"status": "failed", "message": f"User: {username} already in group {group_name}"}

        self.data["group_servers"][group_name]["members"].append(username)
        save_data(self.data)
        return {"status": "success", "message": f"User: {username} added to group {group_name}"}


    def list_members(self, group_name, token):
        decoded_token = decodeToken(token)
        if group_name not in self.data["group_servers"]:
            return {"status": "failed", "message": f"group name: {group_name} does not exist"}
        elif self.data["group_servers"][group_name]["owner"] != decoded_token.get("username"):
            return {"status": "failed", "message": f"Owner of token and group server owner don't match"}
        member_list = self.data["group_servers"][group_name]["members"]
        return {"status": "success", "message": f"{group_name} member list: {member_list}"}




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

        