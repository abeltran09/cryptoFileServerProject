import jwt

KEY = "hvgdkvhfcvhqvwfhvqkwfvjkqv"
ALGORITHM = "HS256"


def generateToken(payload, key=KEY, algorithm=ALGORITHM):
    token = jwt.encode(payload, key, algorithm=algorithm)
    return token


def decodeToken(token, key=KEY, algorithm=ALGORITHM):
    payload = jwt.decode(token, key, algorithms=algorithm)
    return payload

def createTokenPayload(username):
    payload = {
            "username": username,
            "groups": [],
            "permissions": [],
            "file_server_ids": []
            }
    return payload


# token format:
'''
{
    "user_id": "12345678",
    "groups": ["group1", "group2"],
    "permissions": ["view", "upload", "download"],
    "file_server": "fileserver1",
    "expires_at": "2025-03-21T12:00:00Z",
    "signature": "abc123..." 
}
'''
'''
payload = {
    "username": "admin",
    "groups": ["./ADMIN"],
    "permissions": ["view", "upload", "download"],
    "file_server_ids": []
}
'''
