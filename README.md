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

## Setting up on remote. 

We are going to be assuming you're on a solveit instance, and so there is a sqlite db with your messages. 

To pass a message to the local interpreter, you'll need to tag the cell in the following format 

`# tag = TAGNAME`

These tags are global accross all dialogs, so make sure its unique. 

Add the following code to a code cell 


```
import sqlite3
import requests

NGROK_ADDRESS='https://somengrok.free.app/'
def get_call_by_tag(tag_name):
    # Find the code block
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        search_pattern = f"# tag = {tag_name}"
        cursor.execute("""
            SELECT content 
            FROM message 
            WHERE content LIKE ?
            ORDER BY time_run DESC
        """, (f'%{search_pattern}%',))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Get the code, skipping the tag line
            code_lines = result[0].split('\n')
            code = '\n'.join(line for line in code_lines if not line.startswith('# tag ='))
            
            # Send to your local server
            response = requests.post(f'{NGROK_ADDRESS}/execute', 
                                  json={'code': code})
            if stdout.getvalue():
                return stdout.getvalue()
            elif stderr.getvalue():
                return stderr.getvalue()
            return "success=True"
        else:
            return f"No code block found with tag '{tag_name}'"
            
    except Exception as e:
        return f"Error: {e}"
```        

Now, any cell you want to pass to your local, you can simple run

`get_call_by_tag("TAGNAME")` and it will pass that code to your local interpreter. 
