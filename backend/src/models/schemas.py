from typing import Optional

from pydantic import BaseModel


class PromptRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 256
    temperature: float = 0.2
    top_p: float = 0.95
    stop: Optional[list[str]] = None
    system_prompt: str = (
        "You are a helpful coding assistant. When returning code, output it as fenced markdown with the appropriate language tag (for example ```python ...```). Prefer concise explanations followed by a single complete code block."
    )


class GenerateCodeResponse(BaseModel):
    generated_code: str


