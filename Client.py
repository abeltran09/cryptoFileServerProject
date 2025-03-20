import socket
import json


def send_request(request):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(("localhost", 5000))
        client.send(json.dumps(request).encode())
        response = json.loads(client.recv(1024).decode())
        return response

def groupServerMenu():
    print("Welcome to the Group Server Client!")
    while True:
        print("\nOptions:")
        print("1. Connect to Group Server")
        print("2. Get Token")
        print("3. Create User (Admin Only)")
        print("4. Create Group")
        print("5. Add User to Group")
        print("6. List Members of Group")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            response = send_request({"action": "connect"})
        elif choice == "2":
            username = input("Enter your username: ")
            response = send_request({"action": "get_token", "username": username})
            if response.get("status") == "success":
                token = response.get("token")
                print(f"Your token: {token}")
        elif choice == "3":
            username = input("Enter new username: ")
            password = input("Enter new password: ")
            token = input("Enter admin token: ")
            response = send_request(
                {"action": "create_user", "username": username, "password": password, "token": token})
        elif choice == "4":
            group_name = input("Enter group name: ")
            token = input("Enter your token: ")
            response = send_request({"action": "create_group", "group_name": group_name, "token": token})
        elif choice == "5":
            username = input("Enter username to add: ")
            group_name = input("Enter group name: ")
            token = input("Enter your token: ")
            response = send_request(
                {"action": "add_user_to_group", "username": username, "group_name": group_name, "token": token})
        elif choice == "6":
            group_name = input("Enter group name: ")
            token = input("Enter your token: ")
            response = send_request({"action": "list_members", "group_name": group_name, "token": token})
        elif choice == "7":
            print("Exiting Group Server")
            main()
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
