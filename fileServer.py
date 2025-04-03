import socket
import threading
import json
import os
from tokenHandler import decodeToken
from dataHandler import load_data
from datetime import datetime

FILE_STORAGE = "server_files/" #folder for the file uploads

class FileServer(threading.Thread):
    def __init__(self, conn, addr):

        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.data = load_data()
        print(f"New File Server connection from {addr}")

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
        token = request.get("token")

        #decodes tokenget
        user_data = decodeToken(token)
        if datetime.fromisoformat(user_data["expires_at"]) < datetime.utcnow():
            return {"status": "failed", "message": "User Token Expired"}
        elif "status" in user_data and user_data["status"] == "error":
            return {"status": "error", "message": user_data["message"]}

        #handles different file server actions
        if action == "list_files":
            return self.list_files(user_data)
        elif action == "upload":
            return self.upload_file(request, user_data)
        elif action == "download":
            return self.download_file(request, user_data)

        return {"status": "error", "message": "Invalid action"}
    def list_files(self, user_data):
    #lists all files accessible to user groups
        try:
            groups = user_data.get("groups")
            files_map = {}
            for group in groups:
                dir_path = group.lstrip("./")
                if os.path.isdir(dir_path):
                    txt_files = [f for f in os.listdir(dir_path)]
                    files_map[dir_path] = txt_files

            return {"status": "success", "files":files_map}
        except Exception as e:
            return {"status": "error", "message": f"Failed to list files: {e}"}
    def upload_file(self, request ,user_data ):
    #uploads the file to the server if the user belongs to the group
        group = request.get("group")
        dest_group = group.lstrip('./')
        if group not in user_data["groups"]:
            return {"status": "error", "message": "group entered does not exist"}

        try:
            source_file = request.get("source_file")
            filename = request.get("filename")
            dest_file = f"{dest_group}/{filename}"

            with open(dest_file, "wb") as f:
                f.write(request.get("file_data").encode())

            return {"status":"success", "message": f"File '{source_file}' uploaded"}
        except Exception as e:
            return {"status": "error", "message": f"Upload Failed: {e}"}
    def download_file(self,request, user_data):
    #download a file if user is in group
        source_file = request.get("source_file")
        group = source_file.split("_")[0]

        if group not in user_data["groups"]:
            return {"status": "error", "message": "You don't have permission to download this file"}

        try:
            with open(f"{FILE_STORAGE}{source_file}", "rb") as f:
                file_data = f.read().decode()
            return {"status": "success", "file_data": file_data}
        except Exception as e:
            return {"status": "error", "message": f"Download failed: {e}"}
def start_file_server():
#starts the file server
    if not os.path.exists(FILE_STORAGE):
        os.makedirs(FILE_STORAGE)
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind(("0.0.0.0",6000))
    server.listen(5)
    print("File Server running on port 6000...")

    while True:
        conn, addr = server.accept()
        handler = FileServer(conn,addr)
        handler.start()


if __name__=="__main__":
    start_file_server()