import json
import os
import shutil
import tempfile
import time
import uuid
from typing import Dict

import docker


class RunnerService:
    def __init__(self) -> None:
        self.client = docker.from_env()

    def _image_for_language(self, language: str) -> str:
        if language == "python":
            return os.environ.get("RUNNER_IMAGE_PYTHON", "python:3.11-slim")
        raise ValueError(f"Unsupported language: {language}")

    def _write_temp_program(self, language: str, code: str) -> str:
        job_id = str(uuid.uuid4())
        temp_dir = os.path.join(tempfile.gettempdir(), "runner_jobs", job_id)
        os.makedirs(temp_dir, exist_ok=True)
        filename = "main.py" if language == "python" else "main.txt"
        with open(os.path.join(temp_dir, filename), "w", encoding="utf-8") as f:
            f.write(code)
        return temp_dir

    def _command(self, language: str) -> list[str]:
        if language == "python":
            return ["python", "/workspace/main.py"]
        raise ValueError(f"Unsupported language: {language}")

    @staticmethod
    def _nano_cpus(cpu_millis: int) -> int:
        return int(cpu_millis * 1_000_000)

    def run_once(self, *, code: str, language: str, timeout_seconds: int, memory_mb: int, cpu_millis: int) -> Dict:
        start = time.time()
        temp_dir = self._write_temp_program(language, code)
        volumes = {temp_dir: {"bind": "/workspace", "mode": "ro"}}
        image = self._image_for_language(language)
        cmd = self._command(language)
        container = None
        try:
            container = self.client.containers.run(
                image=image,
                command=cmd,
                detach=True,
                network_disabled=True,
                read_only=True,
                user="65534:65534",
                volumes=volumes,
                mem_limit=f"{memory_mb}m",
                nano_cpus=self._nano_cpus(cpu_millis),
                security_opt=["no-new-privileges:true"],
                pids_limit=128,
            )
            result = container.wait(timeout=timeout_seconds)
            code_ = result.get("StatusCode", 124)
            logs = container.logs(stdout=True, stderr=True).decode("utf-8", errors="ignore")
            return {"exit_code": code_, "logs": logs, "duration_ms": int((time.time() - start) * 1000)}
        finally:
            try:
                if container is not None:
                    container.remove(force=True)
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

    def stream(self, *, code: str, language: str, timeout_seconds: int, memory_mb: int, cpu_millis: int):
        start = time.time()
        temp_dir = self._write_temp_program(language, code)
        volumes = {temp_dir: {"bind": "/workspace", "mode": "ro"}}
        image = self._image_for_language(language)
        cmd = self._command(language)
        container = None
        try:
            container = self.client.containers.run(
                image=image,
                command=cmd,
                detach=True,
                network_disabled=True,
                read_only=True,
                user="65534:65534",
                volumes=volumes,
                mem_limit=f"{memory_mb}m",
                nano_cpus=self._nano_cpus(cpu_millis),
                security_opt=["no-new-privileges:true"],
                pids_limit=128,
            )
            for chunk in container.logs(stream=True, stdout=True, stderr=True, follow=True):
                yield chunk
            result = container.wait(timeout=timeout_seconds)
            code_ = result.get("StatusCode", 124)
            tail = json.dumps({"exit_code": code_, "duration_ms": int((time.time() - start) * 1000)})
            yield ("\n" + tail + "\n").encode("utf-8")
        finally:
            try:
                if container is not None:
                    container.remove(force=True)  # type: ignore[arg-type]
            except Exception:
                pass
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)


