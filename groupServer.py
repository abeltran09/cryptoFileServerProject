import socket
import json
import threading
import time
import uuid
import logging
from dataHandler import load_data, save_data, createUserPayload, createGroupPayload, addGroupToToken
from tokenHandler import generateToken, decodeToken, createTokenPayload, updateTokenExpiration
from datetime import datetime
import os
import secrets
import yagmail
import auth

logging.basicConfig(level=logging.INFO)

class GroupServer(threading.Thread):
    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.data = load_data()
        print(f"New Connection from {addr}")
        logging.info(f"New Group Server connection from {addr}")


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
            return self.create_user(request.get("username"), request.get("email"), request.get("token"))
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
                return {"status": "failed", "message": "username Entered Does not exist."}
            if self.data["users"][username]["token"] != "":
                token = self.data["users"][username]["token"]
                new_token = updateTokenExpiration(token)
                self.data["users"][username]["token"] = new_token
                save_data(self.data)
                return {"status": "success", "token": self.data["users"][username].get("token")}

            else:
                token_payload = createTokenPayload(username)
                token_payload["iss"]="GroupServer"
                token = generateToken(token_payload)
                self.data["users"][username]["token"] = token
                save_data(self.data)
                return {"status": "success", "token": self.data["users"][username].get("token")}
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {"status": "failed", "message": "failed to get token"}

    def create_user(self, username, email, userToken):
        try:
            decoded_token = decodeToken(userToken)
            if datetime.fromisoformat(decoded_token["expires_at"]) < datetime.utcnow():
                return {"status": "failed", "message": f"token has expired"}
            elif "./ADMIN" not in decoded_token["groups"]:
                return {"status": "failed",
                        "message": f"User: {decoded_token['username']} not an admin needs to be in ./ADMIN group"}

            # Generate temporary token
            temp_token = secrets.token_urlsafe(16)

            user_payload = createUserPayload(username, email, decoded_token.get("username"))
            # Add temp token to the user payload
            user_payload[username]["temp_token"] = temp_token
            plain_temp_password = str(username+"1")
            temp_password_hash = auth.hash_password(plain_temp_password.encode('utf-8'))
            user_payload[username]["hashed_password"] = temp_password_hash

            self.data["users"].update(user_payload)
            save_data(self.data)

            password_url = f"http://localhost:8000/change-password?username={username}&temp_token={temp_token}"

            email_sent = self.send_email_to_user(email, username, plain_temp_password, password_url)

            return {
                "status": "success",
                "message": f"User: {username} has been created by {decoded_token.get('username')}",
                "password_url": password_url  # Return this URL to the admin
            }
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {"status": "failed", "message": "failed to create user"}

    def send_email_to_user(self, email, username, plain_temp_password, setup_url):
        """Send password setup email to new user using Gmail"""
        try:
            # Email body
            body = f"""
            Hello {username},

            An account has been created for you with temp password: {plain_temp_password}. Please set up your password by clicking the link below:

            {setup_url}

            This link will expire in 24 hours.

            If you did not request this account, please ignore this email.

            Thank you,
            The System Administrator
            """

            yag = yagmail.SMTP('pcrypto43@gmail.com', 'jesv fgwl opww geee')
            yag.send(to=email, subject='Password Setup', contents=body)

            logging.info(f"Password setup email sent to {email}")
            return True

        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")
            return False


    def create_group(self, group_name, token):
        decoded_token = decodeToken(token)
        if datetime.fromisoformat(decoded_token["expires_at"]) < datetime.utcnow():
            return {"status": "failed", "message": f"token has expired, generate new token"}
        elif group_name in self.data["group_servers"]:
            return {"status": "failed", "message": f"group already exist try another name"}
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
            return {"status": "failed", "message": f"token has expired"}
        elif self.data["group_servers"][group_name]["owner"] != decoded_token.get("username"):
            return {"status": "failed", "message": f"Owner of token and group server owner don't match"}
        elif group_name not in self.data["group_servers"]:
            return {"status": "failed", "message": f"Group does not exist"}
        elif username not in self.data["users"]:
            return {"status": "failed", "message": f"User: {username} does not exist, create user first"}
        elif username in self.data["group_servers"][group_name]["members"]:
            return {"status": "failed", "message": f"User: {username} already in group {group_name}"}

        self.data["group_servers"][group_name]["members"].append(username)
        # get user being added to group token
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
            return {"status": "failed", "message": f"token has expired"}
        elif group_name not in self.data["group_servers"]:
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

        