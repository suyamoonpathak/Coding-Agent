import logging
import os
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from schemas import CodeRequest


logger = logging.getLogger("execution-service")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

RUNNER_BASE_URL = os.environ.get("RUNNER_BASE_URL", "http://runner:5100")

app = FastAPI(title="Execution API")

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


"""
Request/response models are defined in schemas.py to keep this file small.
"""


@app.get("/")
async def root():
    return {"message": "Execution service up"}


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.get("/readyz")
async def readyz():
    # This service is stateless and ready if process is up
    return {"ready": True}


@app.get("/metrics")
async def metrics():
    lines = [
        "# HELP execution_gateway_up 1 if service is up",
        "# TYPE execution_gateway_up gauge",
        "execution_gateway_up {} 1",
    ]
    return "\n".join(lines) + "\n"


@app.post("/execute_code/")
async def execute_code(request: CodeRequest):
    # Forward to runner synchronously and capture full output
    url = f"{RUNNER_BASE_URL}/run"
    try:
        async with httpx.AsyncClient(timeout=request.timeout_seconds + 5) as client:
            resp = await client.post(url, json=request.model_dump())
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            return resp.json()
    except httpx.RequestError as exc:
        logger.exception("Runner request failed: %s", exc)
        raise HTTPException(status_code=502, detail="runner unavailable")


@app.post("/execute_code_stream/")
async def execute_code_stream(request: CodeRequest):
    url = f"{RUNNER_BASE_URL}/run_stream"

    async def stream():
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", url, json=request.model_dump()) as resp:
                    if resp.status_code != 200:
                        text = await resp.aread()
                        raise HTTPException(status_code=resp.status_code, detail=text.decode("utf-8"))
                    async for chunk in resp.aiter_bytes():
                        yield chunk
        except httpx.RequestError as exc:
            logger.exception("Runner stream failed: %s", exc)
            yield b"ERROR: runner unavailable\n"

    return StreamingResponse(stream(), media_type="text/plain")

