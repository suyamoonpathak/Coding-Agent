import logging
from docker.errors import DockerException
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from runner_service import RunnerService
from schemas import RunRequest


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

service = RunnerService()


@app.get("/healthz")
async def healthz():
    try:
        service.client.ping()
        return {"ok": True}
    except DockerException:
        raise HTTPException(status_code=503, detail="docker unavailable")


@app.get("/readyz")
async def readyz():
    # Ready when docker socket is reachable
    try:
        service.client.ping()
        return {"ready": True}
    except DockerException:
        return {"ready": False}


@app.get("/metrics")
async def metrics():
    try:
        service.client.ping()
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
    try:
        return service.run_once(
            code=req.code,
            language=req.language,
            timeout_seconds=req.timeout_seconds,
            memory_mb=req.memory_mb,
            cpu_millis=req.cpu_millis,
        )
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run_stream")
async def run_stream(req: RunRequest):
    def generate():
        for chunk in service.stream(
            code=req.code,
            language=req.language,
            timeout_seconds=req.timeout_seconds,
            memory_mb=req.memory_mb,
            cpu_millis=req.cpu_millis,
        ):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")


