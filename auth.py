import bcrypt
import base64
import yagmail
import random

otp_storage = {}

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

def send_otp_email(email, otp):
    yag = yagmail.SMTP('pcrypto43@gmail.com', 'jesv fgwl opww geee')
    yag.send(to=email, subject="Your OTP Code", contents=f"Your one-time passcode is: {otp}")

def MFA(email):
    otp = str(random.randint(100000, 999999))
    otp_storage[email] = otp
    send_otp_email(email, otp)
    print("An OTP had been sent, verify it to connect to group server")

    for attempt in range(3):
        input_otp = input("Enter Your OTP: ")
        if input_otp == otp_storage[email]:
            print("MFA Verified")
            return True
        else:
            print("Incorrect OTP. Try again")
    print("Failed MFA verification")
    return False
