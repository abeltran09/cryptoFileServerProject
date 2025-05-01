from dataHandler import load_data

def getAdminToken():
    # Load user data
    data = load_data()

    # Check if the admin exists
    if "admin" not in data["users"]:
        print("Admin user not found.")
        return None

    # Retrieve the admin token
    admin_token = data["users"]["admin"]["token"]
    return admin_token

# Get the admin token
token = getAdminToken()
if token:
    print("Admin Token:", token)
