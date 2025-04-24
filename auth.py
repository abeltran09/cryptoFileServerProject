import bcrypt
import base64

def hash_password(password):
    if isinstance(password, str):
        password = password.encode('utf-8')

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return base64.b64encode(hashed).decode('utf-8')


def verify_password(entered_password, hashed_password):
    if isinstance(entered_password, str):
        entered_password = entered_password.encode('utf-8')

    hashed_password_bytes = base64.b64decode(hashed_password)
    if bcrypt.checkpw(entered_password, hashed_password_bytes):
        return True
    else:
        return False