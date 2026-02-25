import requests
import threading
from cryptography.fernet import Fernet

def startPCS(host="0.0.0.0", port=5000, user_passkey=""):
    """
    Connects to the server, fetches the encrypted passkey, decrypts it,
    and checks if the user-provided key matches.
    If correct, starts an interactive shell.
    """
    if not user_passkey:
        print("Error: You must provide a passkey!")
        return

    # Step 1: Fetch encrypted passkey from server
    try:
        resp = requests.get(f"http://{host}:{port}/secretPasskey", timeout=10).json()
        encrypted_pass = resp["encrypted_passkey"].encode()
        encryption_key = resp["encryption_key"].encode()
    except Exception as e:
        print(f"Failed to fetch encrypted passkey: {e}")
        return

    # Step 2: Decrypt the server passkey
    try:
        fernet = Fernet(encryption_key)
        server_passkey = fernet.decrypt(encrypted_pass).decode()
    except Exception as e:
        print(f"Failed to decrypt server passkey: {e}")
        return

    # Step 3: Check if user-provided key matches
    if user_passkey != server_passkey:
        print("Error: Provided passkey does not match the server's key.")
        return
    else:
        print("Passkey verified. Connecting to server...")

    # Step 4: Start interactive shell
    BASE_URL = f"http://{host}:{port}/run"
    cwd = "unknown"
    lock = threading.Lock()

    def send_command(command):
        nonlocal cwd
        try:
            response = requests.post(
                BASE_URL,
                json={"command": command, "passkey": server_passkey},
                timeout=10
            )
            data = response.json()
            cwd = data.get("cwd", cwd)
            output = data.get("output", "")
            with lock:
                if output:
                    print(f"\n{output}")
                print(f"{cwd}> ", end="", flush=True)
        except Exception as e:
            with lock:
                print(f"\nError: {e}")
                print(f"{cwd}> ", end="", flush=True)

    # Get initial cwd from server
    try:
        cwd = requests.post(
            BASE_URL,
            json={"command": "", "passkey": server_passkey},
            timeout=10
        ).json().get("cwd", "unknown")
    except Exception as e:
        print(f"Connection error: {e}")
        return

    # Interactive loop
    while True:
        command = input(f"{cwd}> ").strip()
        if command.lower() in ("exit", "quit"):
            print("Exiting...")
            break
        if not command:
            continue
        thread = threading.Thread(target=send_command, args=(command,), daemon=True)
        thread.start()
