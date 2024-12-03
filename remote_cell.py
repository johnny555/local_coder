from pydantic import BaseModel
import requests
import builtins
import io, base64, secrets, hashlib
from hashlib import sha256
from secrets import token_bytes
from contextlib import redirect_stdout, redirect_stderr


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
    
from IPython.core.magic import register_cell_magic
import requests, base64, secrets, hashlib, json

@register_cell_magic
def local(line, cell):
    with open('server_secret.key') as f:
        secret_key = f.read().strip()
    
    try:
        signature = create_signature(generate_code_hash(cell), secret_key)
        encrypted_code = encrypt_message(cell, secret_key)
        
        response = requests.post(
            f'{NGROK_ADDRESS}/execute', 
            json={
                'encrypted_code': encrypted_code,
                'signature': signature
            }
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return
        
        # Decrypt the response and parse JSON
        decrypted_response = decrypt_message(response.text, secret_key)
        data = json.loads(decrypted_response)
        
        if data.get('stdout'):
            print(data['stdout'], end='')
        elif data.get('stderr'):
            print(data['stderr'], end='')
        elif data.get('error'):
            print(f"Error: {data['error']}")
        else:
            print("success=True")
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        raise