from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from google import genai

from backend.config import settings


@dataclass(frozen=True, slots=True)
class GeminiResponse:
    text: str
    raw: object | None = None


from utils.logger import logger

class GeminiClient:
    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model_name or settings.gemini_model
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    @property
    def available(self) -> bool:
        return self.client is not None

    def generate(self, prompt: str) -> GeminiResponse:
        if self.client is None:
            return GeminiResponse(text="I could not find this information in company policies.")
        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                temperature=settings.temperature,
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )
            text = getattr(response, "text", "") or ""
            return GeminiResponse(text=text.strip(), raw=response)
        except Exception as exc:
            logger.error("Gemini API call failed: %s", exc)
            return GeminiResponse(
                text="The Gemini API service is currently experiencing high demand or is temporarily unavailable. Please try again in a few seconds.",
                raw=None
            )



@lru_cache(maxsize=1)
def get_gemini_client() -> GeminiClient:
    return GeminiClient()
