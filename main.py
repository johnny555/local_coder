from fastapi import FastAPI
from fastapi.websockets import WebSocket
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

from pydantic import BaseModel
import builtins
GLOBAL_NS = {
    '__builtins__': builtins,
    '__name__': '__main__',
}

def execute_code(code: str) -> dict:
    stdout = io.StringIO()
    stderr = io.StringIO()
    result = None
    
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            # Use the global namespace for persistence
            exec(code, GLOBAL_NS)
            # Get the last expression's value if any
            if '_' in GLOBAL_NS:
                result = GLOBAL_NS['_']
                
        return {
            "success": True,
            "stdout": stdout.getvalue(),
            "stderr": stderr.getvalue(),
            "result": result,
            "variables": {k: str(v) for k, v in GLOBAL_NS.items() 
                        if not k.startswith('__') and not callable(v)}
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "stdout": stdout.getvalue(),
            "stderr": stderr.getvalue()
        }


class CodeRequest(BaseModel):
    code: str


app = FastAPI()


@app.post("/execute")
async def execute(code_request: CodeRequest):
    return execute_code(code_request.code)


@app.get("/")
async def root():
    return {"message": "Hello from your local server!"}
