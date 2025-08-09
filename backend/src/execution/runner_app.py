import io
import json
import logging
import os
import shutil
import tempfile
import time
import uuid
from typing import Literal

import docker
from docker.errors import DockerException
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field


logger = logging.getLogger("runner")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="Code Runner")

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

docker_client = docker.from_env()


class RunRequest(BaseModel):
    code: str = Field(..., description="Source code to execute")
    language: Literal["python"] = "python"
    timeout_seconds: int = Field(10, ge=1, le=120)
    memory_mb: int = Field(256, ge=64, le=2048)
    cpu_millis: int = Field(500, ge=100, le=2000)


@app.get("/healthz")
async def healthz():
    try:
        docker_client.ping()
        return {"ok": True}
    except DockerException:
        raise HTTPException(status_code=503, detail="docker unavailable")


@app.get("/readyz")
async def readyz():
    # Ready when docker socket is reachable
    try:
        docker_client.ping()
        return {"ready": True}
    except DockerException:
        return {"ready": False}


@app.get("/metrics")
async def metrics():
    try:
        docker_client.ping()
        up = 1
    except DockerException:
        up = 0
    lines = [
        "# HELP runner_docker_up 1 if docker is reachable",
        "# TYPE runner_docker_up gauge",
        f"runner_docker_up {{}} {up}",
    ]
    return "\n".join(lines) + "\n"


def _image_for_language(language: str) -> str:
    if language == "python":
        return os.environ.get("RUNNER_IMAGE_PYTHON", "python:3.11-slim")
    raise ValueError(f"Unsupported language: {language}")


def _write_temp_program(language: str, code: str) -> tuple[str, str]:
    job_id = str(uuid.uuid4())
    temp_dir = os.path.join(tempfile.gettempdir(), "runner_jobs", job_id)
    os.makedirs(temp_dir, exist_ok=True)
    if language == "python":
        program_path = os.path.join(temp_dir, "main.py")
    else:
        raise ValueError(f"Unsupported language: {language}")
    with open(program_path, "w", encoding="utf-8") as f:
        f.write(code)
    return temp_dir, program_path


def _container_command(language: str, program_mount_path: str) -> list[str]:
    if language == "python":
        return ["python", program_mount_path]
    raise ValueError(f"Unsupported language: {language}")


def _nano_cpus(cpu_millis: int) -> int:
    # 1000 millis = 1 CPU = 1e9 nano_cpus
    return int(cpu_millis * 1_000_000)


@app.post("/run")
async def run_once(req: RunRequest):
    start = time.time()
    temp_dir, _ = _write_temp_program(req.language, req.code)
    volumes = {temp_dir: {"bind": "/workspace", "mode": "ro"}}
    image = _image_for_language(req.language)
    cmd = _container_command(req.language, "/workspace/main.py")

    container = None
    try:
        container = docker_client.containers.run(
            image=image,
            command=cmd,
            detach=True,
            network_disabled=True,
            read_only=True,
            user="65534:65534",  # nobody
            volumes=volumes,
            mem_limit=f"{req.memory_mb}m",
            nano_cpus=_nano_cpus(req.cpu_millis),
            security_opt=["no-new-privileges:true"],
            pids_limit=128,
        )

        result = container.wait(timeout=req.timeout_seconds)
        exit_code = result.get("StatusCode", 124)
        logs = container.logs(stdout=True, stderr=True).decode("utf-8", errors="ignore")
        duration_ms = int((time.time() - start) * 1000)
        return {
            "exit_code": exit_code,
            "logs": logs,
            "duration_ms": duration_ms,
        }
    except docker.errors.APIError as e:
        raise HTTPException(status_code=500, detail=f"docker error: {e.explanation}")
    except docker.errors.ContainerError as e:
        raise HTTPException(status_code=500, detail=f"container error: {str(e)}")
    except docker.errors.DockerException as e:
        raise HTTPException(status_code=500, detail=f"docker exception: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"runner error: {str(e)}")
    finally:
        try:
            if container is not None:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@app.post("/run_stream")
async def run_stream(req: RunRequest):
    start = time.time()
    temp_dir, _ = _write_temp_program(req.language, req.code)
    volumes = {temp_dir: {"bind": "/workspace", "mode": "ro"}}
    image = _image_for_language(req.language)
    cmd = _container_command(req.language, "/workspace/main.py")

    def generate():
        container = None
        try:
            container = docker_client.containers.run(
                image=image,
                command=cmd,
                detach=True,
                network_disabled=True,
                read_only=True,
                user="65534:65534",
                volumes=volumes,
                mem_limit=f"{req.memory_mb}m",
                nano_cpus=_nano_cpus(req.cpu_millis),
                security_opt=["no-new-privileges:true"],
                pids_limit=128,
            )

            for chunk in container.logs(stream=True, stdout=True, stderr=True, follow=True):
                yield chunk

            result = container.wait(timeout=req.timeout_seconds)
            exit_code = result.get("StatusCode", 124)
            duration_ms = int((time.time() - start) * 1000)
            tail = json.dumps({"exit_code": exit_code, "duration_ms": duration_ms})
            yield ("\n" + tail + "\n").encode("utf-8")
        except Exception as e:
            yield ("ERROR: " + str(e) + "\n").encode("utf-8")
        finally:
            try:
                if container is not None:
                    try:
                        container.remove(force=True)
                    except Exception:
                        pass
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

    return StreamingResponse(generate(), media_type="text/plain")


