import logging
import threading
import time
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextIteratorStreamer,
)


logger = logging.getLogger("model-service")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="Model Inference Service")

ALLOWED_ORIGINS = [
    # Replace with specific origins via env in production
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:9000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global lazy state
cache_dir = "./model_cache"
model_name = "Qwen/Qwen2.5-Coder-1.5B"
tokenizer = None
model = None
model_ready = False


def _load_model_blocking() -> None:
    global tokenizer, model, model_ready
    try:
        start = time.time()
        logger.info("Loading tokenizer %s", model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        logger.info("Loading model %s", model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=cache_dir)
        model.to("cpu")
        model.eval()
        model_ready = True
        logger.info("Model loaded in %.2fs", time.time() - start)
    except Exception as exc:
        logger.exception("Failed to load model: %s", exc)
        model_ready = False


@app.on_event("startup")
async def startup_load():
    # Lazy background load so healthz is fast and readyz flips when done
    thread = threading.Thread(target=_load_model_blocking, daemon=True)
    thread.start()

# Pydantic model to handle the input body
class PromptRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 256
    temperature: float = 0.2
    top_p: float = 0.95
    stop: Optional[list[str]] = None

@app.get("/")
async def root():
    return {"message": "Model service up"}


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.get("/readyz")
async def readyz():
    return {"ready": bool(model_ready)}


@app.get("/metrics")
async def metrics():
    # Minimal Prometheus text format
    lines = [
        "# HELP model_ready 1 if model is loaded",
        "# TYPE model_ready gauge",
        f"model_ready {{}} {1 if model_ready else 0}",
    ]
    return "\n".join(lines) + "\n"

@app.post("/generate_code/")
async def generate_code(request: PromptRequest):
    if not model_ready:
        return {"error": "model not ready"}

    inputs = tokenizer(request.prompt, return_tensors="pt")
    outputs = model.generate(
        input_ids=inputs["input_ids"],
        max_new_tokens=min(max(1, request.max_new_tokens), 1024),
        do_sample=True,
        temperature=max(0.0, request.temperature),
        top_p=min(max(0.0, request.top_p), 1.0),
    )
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"generated_code": generated_text}


@app.post("/generate_code_stream")
async def generate_code_stream(request: PromptRequest):
    if not model_ready:
        return {"error": "model not ready"}

    def token_stream():
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        inputs = tokenizer(request.prompt, return_tensors="pt")

        generation_kwargs = dict(
            input_ids=inputs["input_ids"],
            max_new_tokens=min(max(1, request.max_new_tokens), 1024),
            do_sample=True,
            temperature=max(0.0, request.temperature),
            top_p=min(max(0.0, request.top_p), 1.0),
            streamer=streamer,
        )

        thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()

        for new_text in streamer:
            yield new_text

    return StreamingResponse(token_stream(), media_type="text/plain")
