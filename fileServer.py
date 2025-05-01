import socket
import threading
import json
import os
from tokenHandler import decodeToken
from dataHandler import load_data
import logging

logging.basicConfig(filename="file_server.log",level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

FILE_STORAGE = "server_files/" #folder for the file uploads

class FileServer(threading.Thread):
    def __init__(self, conn, addr):

        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.data = load_data()
        print(f"New Connection from {addr}")
        logging.info(f"New File Server connection from {addr}")

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
                logging.error(f"Error: {e}")
                break
        self.conn.close()

    def handle_request(self, request):
        action = request.get("action")
        token = request.get("token")

        try:
            user_data = decodeToken(token)  # decodeToken already checks expiration and issuer
        except Exception as e:
            return {"status": "error", "message": str(e)}

        # Handle file server actions
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
            groups = user_data.get("groups", [])
            files_map = {}
            for group in groups:
                dir_path = os.path.join(FILE_STORAGE, group.lstrip("./"))
                if os.path.isdir(dir_path):
                    files = os.listdir(dir_path)
                    files_map[group] = files

            return {"status": "success", "files":files_map}
        except Exception as e:
            logging.error(f"Failed to list files: {e}")
            return {"status": "error", "message": f"Failed to list files: {e}"}
    def upload_file(self, request ,user_data ):
    #uploads the file to the server if the user belongs to the group
        group = request.get("group")
        if group not in user_data.get("groups",[]):
            return {"status": "error", "message": "group entered does not exist"}

        dest_group = group.lstrip("./")
        dest_dir = os.path.join(FILE_STORAGE, dest_group)
        os.makedirs(dest_dir, exist_ok=True)

        try:
            source_file = request.get("source_file")
            filename = request.get("filename")
            file_data = request.get("file_data").encode()

            dest_file=os.path.join(dest_dir, filename)

            with open(dest_file, "wb") as f:
                f.write(file_data)
            logging.info(f"File '{filename}' uploaded by {user_data.get('username')}")
            return {"status":"success", "message": f"File '{source_file}' uploaded"}
        except Exception as e:
            logging.error(f"Upload Failed: {e}")
            return {"status": "error", "message": f"Upload Failed: {e}"}

    def download_file(self, request, user_data):
        # download a file if user is in group
        source_file = request.get("source_file")
        group = request.get("group")

        if group not in user_data("groups",[]):
            return {"status": "error", "message": "You don't have permission to download this file"}

        try:
            file_path = os.path.join(FILE_STORAGE, group.lstrip("./"), source_file)

            with open(file_path, "rb") as f:
                file_data = f.read()

            return {"status": "success", "file_data": file_data.decode()}
        except Exception as e:
            logging.error(f"Download failed: {e}")
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