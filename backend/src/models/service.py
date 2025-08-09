import logging
import threading
import time
from typing import Optional

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextIteratorStreamer,
)


logger = logging.getLogger("model-service")


class ModelService:
    def __init__(self, model_name: str, cache_dir: str = "./model_cache") -> None:
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.tokenizer = None
        self.model = None
        self.ready = False

    def load(self) -> None:
        start = time.time()
        logger.info("Loading tokenizer %s", self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, cache_dir=self.cache_dir)
        logger.info("Loading model %s", self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name, cache_dir=self.cache_dir)
        self.model.to("cpu")
        self.model.eval()
        self.ready = True
        logger.info("Model loaded in %.2fs", time.time() - start)

    def start_background_load(self) -> None:
        thread = threading.Thread(target=self._safe_load, daemon=True)
        thread.start()

    def _safe_load(self) -> None:
        try:
            self.load()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load model: %s", exc)
            self.ready = False

    def build_prompt(self, user_prompt: str, system_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    def generate(self, prompt_text: str, *, max_new_tokens: int, temperature: float, top_p: float) -> str:
        inputs = self.tokenizer(prompt_text, return_tensors="pt")
        outputs = self.model.generate(
            input_ids=inputs["input_ids"],
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            eos_token_id=self.tokenizer.eos_token_id,
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def stream(self, prompt_text: str, *, max_new_tokens: int, temperature: float, top_p: float):
        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
        inputs = self.tokenizer(prompt_text, return_tensors="pt")
        kwargs = dict(
            input_ids=inputs["input_ids"],
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            eos_token_id=self.tokenizer.eos_token_id,
            streamer=streamer,
        )
        thread = threading.Thread(target=self.model.generate, kwargs=kwargs)
        thread.start()
        for chunk in streamer:
            yield chunk


