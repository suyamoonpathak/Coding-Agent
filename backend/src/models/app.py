from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can be more restrictive by specifying URLs)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Load the model (Qwen2.5-Coder-1.5B-Instruct as an example)
cache_dir = "./model_cache"
model_name = "Qwen/Qwen2.5-Coder-1.5B"
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir, device_map="cpu")
model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=cache_dir)

print("Model and tokenizer loaded successfully.")

# Pydantic model to handle the input body
class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
async def hello():
    return {"message": "Hello, 8000 World!"}

@app.post("/generate_code/")
async def generate_code(request: PromptRequest):
    prompt = request.prompt  # Get the prompt from the request body

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    # Generate code from the model
    outputs = model.generate(**inputs, max_new_tokens=400)
    
    # Decode the output back to text
    code = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return {"generated_code": code}
