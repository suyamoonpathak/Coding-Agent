from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM

app = FastAPI()

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
    return {"message": "Hello, World!"}

@app.post("/generate_code/")
async def generate_code(request: PromptRequest):
    prompt = request.prompt  # Get the prompt from the request body

    messages = [
        {"role": "user", "content": prompt},
    ]
    
    # Prepare the input for the model
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)
    
    # Generate code from the model
    outputs = model.generate(**inputs, max_new_tokens=400)
    
    # Decode the output back to text
    code = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:])
    
    return {"generated_code": code}
