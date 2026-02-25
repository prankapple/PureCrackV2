from flask import Flask, request, jsonify
import subprocess, os, secrets, string
from cryptography.fernet import Fernet

app = Flask(__name__)
cwd = os.getcwd()  # track current working directory

# Module-level variables
PASSKEY = None
ENCRYPTION_KEY = None
fernet = None


@app.route("/run", methods=["POST"])
def run_command():
    global cwd
    data = request.json or {}
    cmd = data.get("command", "").strip()
    key = data.get("passkey", "")

    if key != PASSKEY:
        return jsonify({"error": "Invalid passkey"}), 401

    output = ""
    try:
        if cmd.startswith("cd "):
            path = cmd[3:].strip()
            new_dir = os.path.abspath(os.path.join(cwd, path))
            if os.path.isdir(new_dir):
                os.chdir(new_dir)
                cwd = new_dir
                output = "\n".join(os.listdir(cwd))
            else:
                output = f"Directory not found: {new_dir}"
        elif cmd.lower() == "dir":
            output = "\n".join(os.listdir(cwd))
        else:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=20
            )
            output = result.stdout + result.stderr
            if output.strip() == "":
                output = "Command ran but no output detected"
    except Exception as e:
        output = str(e)

    return jsonify({"output": output, "cwd": cwd})


@app.route("/secretPasskey", methods=["GET"])
def get_passkey():
    # Encrypt the passkey before sending
    encrypted_pass = fernet.encrypt(PASSKEY.encode()).decode()
    return jsonify({
        "encrypted_passkey": encrypted_pass,
        "encryption_key": ENCRYPTION_KEY.decode()  # send key to client to decrypt
    })


def startServer(secretKey=None, port=5000, host="0.0.0.0"):
    """
    Starts the server.
    If secretKey is None, generate a random passkey automatically.
    """
    import logging
    global PASSKEY, ENCRYPTION_KEY, fernet

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)  # suppress request logs

    # Generate passkey if none provided
    PASSKEY = secretKey
    ENCRYPTION_KEY = Fernet.generate_key()  # 32-byte base64 key
    fernet = Fernet(ENCRYPTION_KEY)

    print(f"Server starting at http://{host}:{port}")
    app.run(host=host, port=port, debug=False, use_reloader=False)
