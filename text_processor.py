"""
AI Text Processor Module (LLM)
------------------------------
Interfaces with Large Language Models (like Gemini).
Transforms raw Reddit text into viral video scripts.
"""

import os
import re
import json
import logging
from typing import Optional, Any, Type, Literal, List
from pathlib import Path
import google.generativeai as genai
from pydantic import BaseModel, Field
from app.models.domain import ContentItem
from config import LLM_PROVIDERS

logger = logging.getLogger(__name__)


class ScriptResponse(BaseModel):
    """Pydantic model for validating script generation response."""
    word_count: int = Field(..., description="Exact number of words.")
    narrator_gender: Literal["male", "female", "neutral"] = Field(..., description="Detected narrator gender.")
    script: str = Field(..., min_length=1, description="The complete script in Spanish.")


class DescriptionsResponse(BaseModel):
    """Pydantic model for validating marketing descriptions response."""
    youtube_short_title: str = Field(..., min_length=1, max_length=70)
    youtube_short_desc: str = Field(..., min_length=1, max_length=200)


class LLMProvider:
    """Base class for LLM providers."""
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ValueError(f"API Key required for {self.__class__.__name__}")
        self.api_key = api_key
        self.model = model

    def generate_content(self, prompt: str) -> Optional[str]:
        raise NotImplementedError


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider implementation."""
    def __init__(self, api_key: str, model: str):
        super().__init__(api_key, model)
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            response_mime_type="application/json"
        )
        self.safety_settings = [
            {"category": c, "threshold": "BLOCK_NONE"} for c in [
                "HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"
            ]
        ]
        self.client = genai.GenerativeModel(self.model, safety_settings=self.safety_settings)

    def generate_content(self, prompt: str) -> Optional[str]:
        """Generate content using Gemini API."""
        try:
            response = self.client.generate_content(prompt, generation_config=self.generation_config)
            if not response.parts:
                return None
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error in GeminiProvider ({self.model}): {e}")
            return None


PROVIDER_MAP = {"gemini": GeminiProvider}


class TextProcessor:
    """
    Main text processing class.
    Orchestrates LLM calls to transform stories into viral scripts.
    """

    def __init__(self):
        self.providers = self._initialize_providers()
        if not self.providers:
            raise RuntimeError("No AI providers initialized.")
        self.prompts = self._load_prompts()

    def _initialize_providers(self) -> List[LLMProvider]:
        """Initialize configured LLM providers."""
        initialized_providers = []
        if os.getenv("GOOGLE_API_KEY"):
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        for provider_config in LLM_PROVIDERS:
            name = provider_config["name"]
            api_key_env = provider_config["api_key_env"]
            model = provider_config["model"]
            if name in PROVIDER_MAP and os.getenv(api_key_env):
                initialized_providers.append(
                    PROVIDER_MAP[name](api_key=os.getenv(api_key_env), model=model)
                )
        return initialized_providers

    def _call_llm_with_fallback(self, prompt: str) -> Optional[str]:
        """Call LLM with fallback to next provider on failure."""
        for provider in self.providers:
            resp = provider.generate_content(prompt)
            if resp:
                return resp
            logger.warning(f"Failed with {provider.model}. Trying next...")
        return None

    def _load_prompts(self) -> dict[str, str]:
        """Load prompt templates from files."""
        prompt_dir = Path(__file__).resolve().parent / "prompts"
        prompts = {}
        for p_type in ["full_script", "viral_descriptions"]:
            try:
                prompts[p_type] = (prompt_dir / f"{p_type}_prompt.txt").read_text(encoding="utf-8")
            except FileNotFoundError:
                prompts[p_type] = ""
        return prompts

    def _parse_and_validate_json(self, response_text: str, validation_model: Type[BaseModel]) -> Optional[dict]:
        """Parse JSON response and validate against Pydantic model."""
        if not response_text:
            return None
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                return None
            data = json.loads(json_match.group(0))
            return validation_model.parse_obj(data).dict()
        except Exception as e:
            logger.error(f"JSON parse error: {e}")
            return None

    def process_story(self, item: ContentItem) -> Optional[dict[str, Any]]:
        """
        Main entry point. Process a story through the full pipeline.
        Returns a content pack with script, descriptions, and metadata.
        """
        if not item or not item.content_text:
            return None

        logger.info("-> Generating script and metadata...")
        script_prompt = self.prompts["full_script"].format(story_text=f"{item.title}\n\n{item.content_text}")
        script_data = self._parse_and_validate_json(
            self._call_llm_with_fallback(script_prompt),
            ScriptResponse
        )
        if not script_data:
            return None

        logger.info("-> Generating marketing descriptions...")
        desc_prompt = self.prompts["viral_descriptions"].format(script=script_data["script"])
        descriptions = self._parse_and_validate_json(
            self._call_llm_with_fallback(desc_prompt),
            DescriptionsResponse
        )

        return {
            "script": script_data["script"],
            "descriptions": descriptions or {},
            "narrator_gender": script_data["narrator_gender"]
        }
