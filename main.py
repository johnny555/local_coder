import builtins

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import io, base64, secrets, hashlib
from contextlib import redirect_stdout, redirect_stderr
from hashlib import sha256
from secrets import token_bytes

# Encryption functions
def encrypt_message(message: str, key: str) -> str:
    key_bytes = base64.b64decode(key)
    derived_key = sha256(key_bytes).digest()
    iv = token_bytes(16)
    message_bytes = message.encode()
    keystream = derived_key * (len(message_bytes) // len(derived_key) + 1)
    encrypted = bytes(a ^ b for a, b in zip(message_bytes, keystream))
    final = iv + encrypted
    return base64.b64encode(final).decode()

def decrypt_message(encrypted: str, key: str) -> str:
    key_bytes = base64.b64decode(key)
    derived_key = sha256(key_bytes).digest()
    data = base64.b64decode(encrypted)
    iv, encrypted_message = data[:16], data[16:]
    keystream = derived_key * (len(encrypted_message) // len(derived_key) + 1)
    decrypted = bytes(a ^ b for a, b in zip(encrypted_message, keystream))
    return decrypted.decode()

# FastAPI setup
app = FastAPI()
GLOBAL_NS = {'__builtins__': builtins, '__name__': '__main__'}

class EncryptedRequest(BaseModel):
    encrypted_code: str

def execute_code(code: str) -> dict:
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exec(code, GLOBAL_NS)
        return {
            "success": True,
            "stdout": stdout.getvalue(),
            "stderr": stderr.getvalue()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "stdout": stdout.getvalue(),
            "stderr": stderr.getvalue()
        }

@app.post("/execute")
async def execute(request: EncryptedRequest):
    try:
        with open('server_secret.key') as f:
            secret_key = f.read().strip()
        try:
            code = decrypt_message(request.encrypted_code, secret_key)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Decryption failed - invalid key")
        return execute_code(code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))