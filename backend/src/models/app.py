import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from schemas import PromptRequest
from service import ModelService


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


service = ModelService(model_name="Qwen/Qwen2.5-Coder-0.5B-Instruct")


@app.on_event("startup")
async def startup_load():
    service.start_background_load()

@app.get("/")
async def root():
    return {"message": "Model service up"}


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.get("/readyz")
async def readyz():
    return {"ready": bool(service.ready)}


@app.get("/metrics")
async def metrics():
    # Minimal Prometheus text format
    lines = [
        "# HELP model_ready 1 if model is loaded",
        "# TYPE model_ready gauge",
        f"model_ready {{}} {1 if service.ready else 0}",
    ]
    return "\n".join(lines) + "\n"

@app.post("/generate_code/")
async def generate_code(request: PromptRequest):
    if not service.ready:
        return {"error": "model not ready"}
    prompt_text = service.build_prompt(request.prompt, request.system_prompt)
    generated_text = service.generate(
        prompt_text,
        max_new_tokens=min(max(1, request.max_new_tokens), 1024),
        temperature=max(0.0, request.temperature),
        top_p=min(max(0.0, request.top_p), 1.0),
    )
    return {"generated_code": generated_text}


@app.post("/generate_code_stream")
async def generate_code_stream(request: PromptRequest):
    if not service.ready:
        return {"error": "model not ready"}

    def token_stream():
        prompt_text = service.build_prompt(request.prompt, request.system_prompt)
        for chunk in service.stream(
            prompt_text,
            max_new_tokens=min(max(1, request.max_new_tokens), 1024),
            temperature=max(0.0, request.temperature),
            top_p=min(max(0.0, request.top_p), 1.0),
        ):
            yield chunk

    return StreamingResponse(token_stream(), media_type="text/plain")
