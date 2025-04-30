import json
from tokenHandler import decodeToken
from datetime import datetime

DATA_FILE = "groupServerData.json"
START_FILE = "dataexample.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        with open(START_FILE, "r") as f:
            data=json.load(f)
        save_data(data)
        return json.load(f)
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def createUserPayload(username, email, admin):
    payload = {
        username: {
            "username": username,
            "email": email,
            "role": "user",
            "hashed_password": "",
            "token": "",
            "temp_token": "",
            "created_by": admin,
            "created_at": datetime.utcnow().isoformat()
            #"iss":"GroupServer"
        }
    }
    return payload


def createGroupPayload(groupname, usertoken):
    decoded_token = decodeToken(usertoken)
    username = decoded_token.get("username")
    payload = {
        groupname: {
            "name": groupname,
            "owner": username,
            "members": [username],
            "file_server_ids": []
        }
    }
    return payload

def addGroupToToken(token, group_name):
    token["groups"].append(group_name)
    return token