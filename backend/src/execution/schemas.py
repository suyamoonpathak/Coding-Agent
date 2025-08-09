from typing import Literal

from pydantic import BaseModel, Field


class CodeRequest(BaseModel):
  code: str = Field(..., description="Source code to execute")
  language: Literal["python"] = "python"
  timeout_seconds: int = Field(10, ge=1, le=120)
  memory_mb: int = Field(256, ge=64, le=2048)
  cpu_millis: int = Field(500, ge=100, le=2000)


class ExecuteResponse(BaseModel):
  logs: str
  exit_code: int
  duration_ms: int


class RunRequest(CodeRequest):
  pass


class RunnerResponse(ExecuteResponse):
  pass


