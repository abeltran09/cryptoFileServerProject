import socket
import ssl
import json
import threading
import logging
from dataHandler import load_data, save_data, createUserPayload, createGroupPayload, addGroupToToken
from tokenHandler import generateToken, decodeToken, createTokenPayload, updateTokenExpiration
from datetime import datetime
import os
import signal
import sys

# Set up logging for better error tracking
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
                logging.error(f"Error in receiving or processing data: {e}")
                break
        self.conn.close()

    def handle_request(self, request):
        try:
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
        except Exception as e:
            logging.error(f"Error handling request: {e}")
            return {"status": "error", "message": "An error occurred while handling the request"}

    def get_token(self, username):
        try:
            if username not in self.data["users"]:
                return {"status": "failed", "message": "Username entered does not exist."}
            if self.data["users"][username]["token"] != "":
                token = self.data["users"][username]["token"]
                new_token = updateTokenExpiration(token)
                self.data["users"][username]["token"] = new_token
                save_data(self.data)
                return {"status": "success", "token": self.data["users"][username].get("token")}
            else:
                token_payload = createTokenPayload(username)
                token_payload["iss"] = "GroupServer"
                token = generateToken(token_payload)
                self.data["users"][username]["token"] = token
                save_data(self.data)
                return {"status": "success", "token": self.data["users"][username].get("token")}
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {"status": "failed", "message": "Failed to get token"}

    def create_user(self, username, userToken):
        try:
            decoded_token = decodeToken(userToken)
            if datetime.fromisoformat(decoded_token["expires_at"]) < datetime.utcnow():
                return {"status": "failed", "message": "Token has expired"}
            elif "./ADMIN" not in decoded_token["groups"]:
                return {"status": "failed", "message": f"User: {decoded_token['username']} needs to be in ./ADMIN group"}
            user_payload = createUserPayload(username)
            self.data["users"].update(user_payload)
            save_data(self.data)
            return {"status": "success", "message": f"User: {username} has been created by {decoded_token.get('username')}"}
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {"status": "failed", "message": "Failed to create user"}

    def create_group(self, group_name, token):
        decoded_token = decodeToken(token)
        if datetime.fromisoformat(decoded_token["expires_at"]) < datetime.utcnow():
            return {"status": "failed", "message": "Token has expired, generate new token"}
        elif group_name in self.data["group_servers"]:
            return {"status": "failed", "message": "Group already exists, try another name"}
        group_payload = createGroupPayload(group_name, token)
        self.data["group_servers"].update(group_payload)
        updated_token = addGroupToToken(decoded_token, group_name)
        encoded_updated_token = generateToken(updated_token)
        self.data["users"][decoded_token["username"]]["token"] = encoded_updated_token
        save_data(self.data)
        try:
            os.makedirs(group_name)
            print(f"{group_name} created successfully")
        except FileExistsError:
            print(f"{group_name} already exists")
        except FileNotFoundError:
            print("Parent directory not found")
        return {"status": "success", "message": f"Group: {group_name} has been created by group owner {decoded_token.get('username')}"}

    def add_user_to_group(self, username, group_name, token):
        decoded_token = decodeToken(token)
        if datetime.fromisoformat(decoded_token["expires_at"]) < datetime.utcnow():
            return {"status": "failed", "message": "Token has expired"}
        elif self.data["group_servers"][group_name]["owner"] != decoded_token.get("username"):
            return {"status": "failed", "message": "Owner of token and group server owner don't match"}
        elif group_name not in self.data["group_servers"]:
            return {"status": "failed", "message": "Group does not exist"}
        elif username not in self.data["users"]:
            return {"status": "failed", "message": f"User: {username} does not exist, create user first"}
        elif username in self.data["group_servers"][group_name]["members"]:
            return {"status": "failed", "message": f"User: {username} already in group {group_name}"}
        self.data["group_servers"][group_name]["members"].append(username)
        user_token = self.data["users"][username]["token"]
        user_decoded_token = decodeToken(user_token)
        updated_token = addGroupToToken(user_decoded_token, group_name)
        encoded_updated_token = generateToken(updated_token)
        self.data["users"][user_decoded_token["username"]]["token"] = encoded_updated_token
        save_data(self.data)
        return {"status": "success", "message": f"User: {username} added to group {group_name}"}

    def list_members(self, group_name, token):
        decoded_token = decodeToken(token)
        if datetime.fromisoformat(decoded_token["expires_at"]) < datetime.utcnow():
            return {"status": "failed", "message": "Token has expired"}
        elif group_name not in self.data["group_servers"]:
            return {"status": "failed", "message": f"Group name: {group_name} does not exist"}
        elif self.data["group_servers"][group_name]["owner"] != decoded_token.get("username"):
            return {"status": "failed", "message": "Owner of token and group server owner don't match"}
        member_list = self.data["group_servers"][group_name]["members"]
        return {"status": "success", "message": f"{group_name} member list: {member_list}"}

# Wrap the server socket to use TLS encryption
def start_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # Force TLSv1.2
    context.load_cert_chain(certfile="server.crt", keyfile="server.key") # Make sure these files exist
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5000))  # Ensure port 5000 is free
    server.listen(5)
    print("Group Server is running on port 5000 with TLS...")

    try:
        while True:
            conn, addr = server.accept()
            secure_conn = context.wrap_socket(conn, server_side=True)  # Wrap the connection with TLS
            handler = GroupServer(secure_conn, addr)
            handler.start()
    except KeyboardInterrupt:
        print("Shutting down the server gracefully...")
        server.close()

if __name__ == "__main__":
    start_server()
