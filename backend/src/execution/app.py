from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from execute_code import execute_code_in_container
# FastAPI instance
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can be more restrictive by specifying URLs)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

    
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

