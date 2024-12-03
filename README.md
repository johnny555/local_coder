# Local Coder 

This is a repo to enable LLM's to control your local python instance. 

It's inherently dangerous as its literally a remote code exploit ! so don't use this! 

But, if you want to, here is the code and instructions anyway. 

## Setting up local 

Clone this repo, create a venv and install fastapi 

```
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install required packages
pip install fastapi uvicorn websockets
```

Next setup a ngrok and install locally. 

make sure you add the auth token to your system

`ngrok config add-authtoken YOUR_TOKEN_HERE` 

Start the local server by running (in the root directory of this repo): 

`uvicorn main:app --reload`

Now connect it to the ngrok endpoint:

`ngrok http 8000`

Note down your enpoints address. 

## generate secret key 

You'll need to create a secret key to be shared between your local computer and solveit. 

use this code to make one:

```
import secrets
import base64

# Generate a secure random key
secret_key = secrets.token_bytes(32)  # 256 bits
# Convert to base64 for easier storage/transmission
secret_key_b64 = base64.b64encode(secret_key).decode()

print("Your secret key (save this somewhere safe):")
print(secret_key_b64)
```

and then save it to your solveit:

```
with open('server_secret.key', 'w') as f:
    f.write(secret_key_b64) 
```

You should next save the secret key as a file in the same directory that you run the local server.


## Setting up on remote. 

We are using jupyter magic to know which cells to send to the local computer.

You'll need to set an environment variable `NGROK_ADDRESS` to the endpoint that ngrok forwards your ip to.

You'll also need to put the contents of `remote_cell.py` into one of the cells.

## Usage 

Once the local server is running, and the remote_cell.py has been run, your NGROK_ADDRESS variable is set correctly and a secret is shared between the computers, you can start any cell with the magic `%%local` and it will transmit it to your server and show any output from the command (or success=True if there was no output). 
