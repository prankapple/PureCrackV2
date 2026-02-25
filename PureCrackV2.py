import os
import sys
import time
import socket
import secrets
import string

def generate_passkey(length=10):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # The IP here doesn't need to be reachable. Used to get your LAN IP.
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"  # fallback
    finally:
        s.close()
    return ip

local_ip = get_local_ip()


sys.path.append("assets")
time.sleep(1)

import Server
import Connect

def is_number(val):
    try:
        float(val)
        return True
    except ValueError:
        return False
def clear():
    os.system("cls")

clear()
file_path = "assets/banner.txt"  # replace with your file

def banner():
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            contents = f.read()
            print(contents)  # prints the full content to console
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"Error reading file: {e}")

banner()

print("                 PureCrackV2 Menu")
print(" 1. Start Server")
print(" 2. Connect")
print()

num = input("Enter the desired option > ")

if is_number(num):
    print()
else:
    print("Please enter a valid option!")
    sys.exit()

if int(num) == 1:
    print("Server started on > " + local_ip + ", port > 5000")
    secretKey = generate_passkey()
    print("Secret Password > " + secretKey)
    Server.startServer(secretKey, port=5000, host="0.0.0.0")
elif int(num) == 2:
    conHost = input("Enter the host to connect to > ")
    conPort = input("Enter the port to connect to > ")
    user_passkey = input("Enter the secret key for the conection > ")
    clear()
    banner()
    print()
    Connect.startPCS(str(conHost), int(conPort), str(user_passkey))