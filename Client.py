import socket
import ssl
import json
import threading
import logging

# Global variables to track connection states
connected_to_group_server = False
client_socket = None
connected_to_file_server = False
file_socket = None  # Different socket for file server

# Set up logging for better error tracking
logging.basicConfig(level=logging.INFO)


def connect_to_group_server():
    global connected_to_group_server, client_socket
    try:
        # Create the raw socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Wrap the socket with TLS/SSL using SSLContext and the server's certs
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # Force TLSv1.2 for compatibility
        context.load_cert_chain(certfile="server.crt", keyfile="server.key")  # Adjust to your cert path
        client_socket = context.wrap_socket(client_socket, server_side=False)  # Secure the socket

        client_socket.connect(("localhost", 5000))  # Connect to the Group Server (port 5000)
        connected_to_group_server = True
        logging.info("Connected to Group Server")
        return {"status": "success", "message": "Connected to Group Server"}
    except Exception as e:
        logging.error(f"Group Server connection failed: {e}")
        return {"status": "error", "message": f"Connection failed: {e}"}


def send_request(request):
    global connected_to_group_server, client_socket
    if not connected_to_group_server:
        return {"status": "error", "message": "Not connected to Group Server"}

    try:
        # Send the request to the server
        client_socket.send(json.dumps(request).encode())
        response = json.loads(client_socket.recv(1024).decode())  # Wait for the server's response
        return response
    except Exception as e:
        connected_to_group_server = False
        client_socket.close()
        logging.error(f"Request failed: {e}")
        return {"status": "error", "message": f"Request failed: {e}"}


def disconnect_from_group_server():
    global connected_to_group_server, client_socket
    if connected_to_group_server:
        client_socket.close()
        connected_to_group_server = False
        logging.info("Disconnected from Group Server")
    return {"status": "success", "message": "Disconnected from Group Server"}


def groupServerMenu():
    global connected_to_group_server

    print("Welcome to the Group Server Client!")

    while True:
        print("\nOptions:")
        print("1. Connect to Group Server" if not connected_to_group_server else "1. Disconnect from Group Server")
        if connected_to_group_server:
            print("2. Get Token")
            print("3. Create User (Admin Only)")
            print("4. Create Group")
            print("5. Add User to Group")
            print("6. List Members of Group")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            if not connected_to_group_server:
                response = connect_to_group_server()
            else:
                response = disconnect_from_group_server()
        elif choice == "2" and connected_to_group_server:
            username = input("Enter your username: ")
            response = send_request({"action": "get_token", "username": username})
        elif choice == "3" and connected_to_group_server:
            username = input("Enter new username: ")
            token = input("Enter admin token: ")
            response = send_request({"action": "create_user", "username": username, "token": token})
        elif choice == "4" and connected_to_group_server:
            group_name = input("Enter group name: ")
            token = input("Enter your token: ")
            response = send_request({"action": "create_group", "group_name": group_name, "token": token})
        elif choice == "5" and connected_to_group_server:
            username = input("Enter username to add: ")
            group_name = input("Enter group name: ")
            token = input("Enter your token: ")
            response = send_request(
                {"action": "add_user_to_group", "username": username, "group_name": group_name, "token": token})
        elif choice == "6" and connected_to_group_server:
            group_name = input("Enter group name: ")
            token = input("Enter your token: ")
            response = send_request({"action": "list_members", "group_name": group_name, "token": token})
        elif choice == "7":
            if connected_to_group_server:
                disconnect_from_group_server()
            print("Exiting Group Server")
            break
        elif not connected_to_group_server and choice in ["2", "3", "4", "5", "6"]:
            response = {"status": "error", "message": "Please connect to the Group Server first"}
        else:
            print("Invalid choice. Please try again.")
            continue

        print("Response:", response.get("message", response))


def connect_to_file_server():
    global connected_to_file_server, file_socket
    try:
        # Create the raw socket for the File Server
        file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Wrap the socket with TLS/SSL using SSLContext and the server's certs
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # Force TLSv1.2 for compatibility
        context.load_cert_chain(certfile="server.crt", keyfile="server.key")  # Adjust to your cert path
        file_socket = context.wrap_socket(file_socket, server_side=False)  # Secure the socket

        file_socket.connect(("localhost", 6000))  # Connect to the File Server (port 6000)
        connected_to_file_server = True
        logging.info("Connected to File Server")
        return {"status": "success", "message": "Connected to File Server"}
    except Exception as e:
        logging.error(f"File Server connection failed: {e}")
        return {"status": "error", "message": f"File Server connection failed: {e}"}


def disconnect_from_file_server():
    global connected_to_file_server, file_socket
    if connected_to_file_server:
        file_socket.close()
        connected_to_file_server = False
        logging.info("Disconnected from File Server")
    return {"status": "success", "message": "Disconnected from File Server"}


def send_file_request(request):
    global connected_to_file_server, file_socket
    if not connected_to_file_server:
        return {"status": "error", "message": "Not connected to File Server"}

    try:
        file_socket.send(json.dumps(request).encode())
        response = json.loads(file_socket.recv(1024).decode())
        return response
    except Exception as e:
        connected_to_file_server = False
        file_socket.close()
        logging.error(f"File Server request failed: {e}")
        return {"status": "error", "message": f"File Server request failed: {e}"}


def fileServerMenu():
    print("Welcome to the File Server Client!")

    while True:
        print("\nOptions:")
        print("1. Connect to File Server" if not connected_to_file_server else "1. Disconnect from File Server")
        if connected_to_file_server:
            print("2. List Files")
            print("3. Upload File")
            print("4. Download File")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            if not connected_to_file_server:
                response = connect_to_file_server()
            else:
                response = disconnect_from_file_server()
        elif choice == "2" and connected_to_file_server:
            token = input("Enter your token: ")
            response = send_file_request({"action": "list_files", "token": token})
        elif choice == "3" and connected_to_file_server:
            source_file = input("Enter the file to upload: ")
            filename = input("Enter filename: ")
            group = input("Enter group to share with: ")
            token = input("Enter your token: ")
            try:
                with open(source_file, "rb") as f:
                    file_data = f.read().decode()
                response = send_file_request({
                    "action": "upload",
                    "source_file": source_file,
                    "filename": filename,
                    "file_data": file_data,
                    "group": group,
                    "token": token
                })
            except FileNotFoundError:
                response = {"status": "error", "message": "File not found"}
        elif choice == "4" and connected_to_file_server:
            source_file = input("Enter the file to download: ")
            dest_file = input("Enter destination filename: ")
            token = input("Enter your token: ")
            response = send_file_request({
                "action": "download",
                "source_file": source_file,
                "dest_file": dest_file,
                "token": token
            })
            if response.get("status") == "success":
                with open(dest_file, "wb") as f:
                    f.write(response["file_data"].encode())
        elif choice == "5":
            print("Exiting File Server Client")
            break
        else:
            print("Invalid Choice. Try again.")
            continue

        print("Response:", response.get("message", response))


def main():
    print("Connect To Group Server or File Server")
    while True:
        print("1. Group Server")
        print("2. File Server")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            print()
            groupServerMenu()
        elif choice == "2":
            print()
            fileServerMenu()
        elif choice == "3":
            print("Exiting....")
            break
        else:
            print("Invalid Option")


if __name__ == "__main__":
    main()
