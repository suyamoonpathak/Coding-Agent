from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from execute_code import execute_code_in_container
# FastAPI instance
app = FastAPI()

# Pydantic model for request
class CodeRequest(BaseModel):
    code: str

@app.get("/")
async def hello():
    return {"message": "Hello, 5000 World!"}

@app.post("/execute_code/")
async def execute_code(request: CodeRequest):
    code = request.code
    
    # Execute the code inside the Docker container
    result = execute_code_in_container(code)
    
    if result.startswith("Error"):
        raise HTTPException(status_code=400, detail=result)
    
    return {"output": result}

