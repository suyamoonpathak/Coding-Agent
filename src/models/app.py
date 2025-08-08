from fastapi import FastAPI
from transformers import AutoTokenizer, AutoModelForCausalLM

app = FastAPI()

# # Load the model (Qwen2.5-Coder-3B-Instruct as an example)
cache_dir = "./model_cache"
model_name = "Qwen/Qwen2.5-Coder-3B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=cache_dir)

print("Model and tokenizer loaded successfully.2")

@app.get("/")
async def hello():
    return {"message": "Hello, World!"}

@app.post("/generate_code/")
async def generate_code(prompt: str):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs)
    code = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"generated_code": code}
    return {"generated_code": "hello world"} 
    
