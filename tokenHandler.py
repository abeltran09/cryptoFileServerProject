import jwt
import hmac
import hashlib
import json
from datetime import datetime, timedelta

KEY = "2LCoB-TMyw4iiQqXoZr6ieml4V4HcuvsV4DltRul_ubqQAijbxZWL6CH_KSKjp6zGU1pdEy5vrX8ySKAmf5evA"
ALGORITHM = "HS256"


def generateToken(payload, key=KEY, algorithm=ALGORITHM):
    token = jwt.encode(payload, key, algorithm=algorithm)
    return token

def decodeToken(token, key=KEY, algorithm=ALGORITHM):
    try:
        payload = jwt.decode(token, key, algorithms=algorithm)
        if payload.get("iss") != "GroupServer":
            raise Exception("Invalid token Issuer")
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has Expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid Token")

def createTokenPayload(username,role="user", permissions=[]):
    expire_date = datetime.utcnow() + timedelta(minutes=30)
    payload = {
            "iss": "GroupServer", #trusted issuer
            "username": username,
            "roles": role,
            "groups": [],
            "permissions": permissions,
            "file_server_ids": [],
            "exp": expire_date
            }
    return payload

def updateTokenExpiration(token):
    decoded_token = decodeToken(token)
    new_expire_date = datetime.utcnow() + timedelta(minutes=30)
    decoded_token["exp"] = new_expire_date
    encoded_token = generateToken(decoded_token)
    return encoded_token

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

