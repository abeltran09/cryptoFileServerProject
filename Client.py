import socket
import json

# Global variable to track connection state
connected_to_group_server = False
client_socket = None


def connect_to_group_server():
    global connected_to_group_server, client_socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", 5000))
        connected_to_group_server = True
        return {"status": "success", "message": "Connected to Group Server"}
    except Exception as e:
        return {"status": "error", "message": f"Connection failed: {e}"}


def send_request(request):
    global connected_to_group_server, client_socket
    if not connected_to_group_server:
        return {"status": "error", "message": "Not connected to Group Server"}

    try:
        client_socket.send(json.dumps(request).encode())
        response = json.loads(client_socket.recv(1024).decode())
        return response
    except Exception as e:
        connected_to_group_server = False
        client_socket.close()
        return {"status": "error", "message": f"Request failed: {e}"}


def disconnect_from_group_server():
    global connected_to_group_server, client_socket
    if connected_to_group_server:
        client_socket.close()
        connected_to_group_server = False
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
            response = send_request(
                {"action": "create_user", "username": username, "token": token})
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


def fileServerMenu():
    pass


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