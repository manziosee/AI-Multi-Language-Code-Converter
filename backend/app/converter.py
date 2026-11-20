"""AI provider layer for code conversion and explanation.

Every provider speaks the OpenAI chat-completions shape, so they share one
async code path. Clients are async so a slow model call never blocks the
event loop for other requests.
"""
from typing import AsyncIterator, Dict
import logging

from groq import AsyncGroq
from openai import AsyncOpenAI

from app.config import settings
from app.models import ConversionRequest

logger = logging.getLogger(__name__)

CODE_SYSTEM_PROMPT = "You are an expert programmer. Output ONLY code."
EXPLAIN_SYSTEM_PROMPT = "You are an expert programmer who explains code clearly."

# Appended to a stream that fails after output has started. The NUL byte never
# appears in model text, so the client can split on it unambiguously.
STREAM_ERROR_MARKER = "\u0000STREAM_ERROR\u0000"

PROVIDER_LABELS = {
    "groq": "Groq",
    "openai": "OpenAI",
    "huggingface": "Hugging Face",
}


class CodeConverter:
    """Handles code conversion using multiple AI providers."""

    def __init__(self):
        self.provider = settings.ai_provider.lower()
        self.client = None  # AsyncGroq | AsyncOpenAI
        self.model = ""

        if self.provider == "groq":
            if not settings.groq_api_key:
                raise ValueError("Groq API key not configured")
            self.client = AsyncGroq(api_key=settings.groq_api_key)
            self.model = settings.groq_model
        elif self.provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
        elif self.provider == "openai_compatible":
            missing = [
                name for name, value in (
                    ("OPENAI_COMPATIBLE_BASE_URL", settings.openai_compatible_base_url),
                    ("OPENAI_COMPATIBLE_API_KEY", settings.openai_compatible_api_key),
                    ("OPENAI_COMPATIBLE_MODEL", settings.openai_compatible_model),
                ) if not value
            ]
            if missing:
                raise ValueError(f"OpenAI-compatible provider missing: {', '.join(missing)}")
            self.client = AsyncOpenAI(
                api_key=settings.openai_compatible_api_key,
                base_url=settings.openai_compatible_base_url,
            )
            self.model = settings.openai_compatible_model
        elif self.provider == "huggingface":
            if not settings.huggingface_api_key:
                raise ValueError("Hugging Face API key not configured")
            self.client = AsyncOpenAI(
                api_key=settings.huggingface_api_key,
                base_url=settings.huggingface_base_url,
            )
            self.model = settings.huggingface_model
        else:
            raise ValueError(
                f"Unknown AI_PROVIDER '{self.provider}'. "
                "Use groq, huggingface, openai or openai_compatible."
            )

        # Groq historically ran conversions colder than OpenAI; keep that.
        self.convert_temperature = 0.1 if self.provider == "groq" else 0.3

    # ------------------------------------------------------------------ info

    @property
    def provider_label(self) -> str:
        if self.provider == "openai_compatible":
            return settings.openai_compatible_name
        return PROVIDER_LABELS.get(self.provider, self.provider)

    # --------------------------------------------------------------- prompts

    def _get_language_display_name(self, lang: str) -> str:
        """Convert internal language name to display name."""
        language_map: Dict[str, str] = {
            "python": "Python",
            "nodejs": "Node.js",
            "javascript": "JavaScript",
            "php": "PHP",
            "golang": "Go",
            "java": "Java",
            "typescript": "TypeScript",
            "sql": "SQL",
            "prisma": "Prisma Schema",
            "drizzle": "Drizzle ORM",
            "c": "C",
            "cpp": "C++",
            "csharp": "C#",
            "rust": "Rust"
        }
        return language_map.get(lang.lower(), lang)

    def _create_conversion_prompt(self, request: ConversionRequest) -> str:
        """Create a detailed prompt for code conversion."""
        source_lang = self._get_language_display_name(request.source_language)
        target_lang = self._get_language_display_name(request.target_language)

        return f"""You are an expert senior software engineer. Your task is to convert the following {source_lang} code to {target_lang}.

CRITICAL REQUIREMENTS:
1. **Accuracy**: The converted code must be syntactically correct and functionally equivalent.
2. **Idiomatic**: Use modern {target_lang} best practices, naming conventions, and standard libraries.
3. **Structure**: Maintain the original logic flow but adapt it to the target language's paradigm (e.g., OOP vs Functional).
4. **Dependencies**: Include all necessary imports/includes at the top.
5. **No Markdown**: Return ONLY the raw code. Do not wrap it in markdown blocks (no ```).
6. **No Comments**: Do not add explanatory comments unless absolutely necessary for complex logic.
7. **Complete**: Do not omit any part of the original code.

Source Code ({source_lang}):
{request.code}

Converted Code ({target_lang}):"""

    def _create_explanation_prompt(self, language: str, code: str) -> str:
        """Create a prompt for code explanation."""
        lang_display = self._get_language_display_name(language)

        return f"""You are an expert software engineer. Explain the following {lang_display} code in a clear, detailed way.

Format your response with these sections (use ### for section titles):

### Overview
What the code does in 2-3 sentences

### Key Components
List main functions, classes, or logic (use bullet points with - )

### How It Works
Step-by-step explanation of the logic flow

### Important Details
Notable patterns, algorithms, or best practices

Code ({lang_display}):
{code}

Explanation:"""

    # ------------------------------------------------------------ transports

    def _extra_body(self) -> dict:
        """Provider-specific request fields.

        gpt-oss models reason before answering, and reasoning tokens count
        against max_tokens. Low effort is enough for translation and keeps
        responses fast and inside the limits.
        """
        if self.provider == "groq" and "gpt-oss" in self.model:
            return {"reasoning_effort": "low"}
        return {}

    async def _chat(self, system: str, prompt: str, temperature: float,
                    max_tokens: int, timeout: float) -> str:
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            extra_body=self._extra_body() or None,
        )
        return completion.choices[0].message.content or ""

    async def _chat_stream(self, system: str, prompt: str, temperature: float,
                           max_tokens: int, timeout: float) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            stream=True,
            extra_body=self._extra_body() or None,
        )
        async for chunk in stream:
            # Some OpenAI-compatible gateways send usage-only chunks with no choices.
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    # ------------------------------------------------------------- public API

    async def convert_code(self, request: ConversionRequest) -> str:
        """Convert code using the configured provider."""
        prompt = self._create_conversion_prompt(request)
        try:
            text = await self._chat(CODE_SYSTEM_PROMPT, prompt,
                                    self.convert_temperature, 8000, 60.0)
            return self._clean_output(text)
        except Exception as e:
            raise Exception(f"{self.provider_label} conversion failed: {str(e)}")

    async def convert_code_stream(self, request: ConversionRequest):
        """Convert code using the configured provider with streaming.

        Raises on failure; the HTTP layer decides how to report it (a 502
        before any output, or STREAM_ERROR_MARKER once streaming started).
        """
        prompt = self._create_conversion_prompt(request)
        async for piece in self._chat_stream(CODE_SYSTEM_PROMPT, prompt,
                                             self.convert_temperature, 8000, 60.0):
            yield piece

    async def explain_code(self, language: str, code: str) -> str:
        """Explain code using the configured provider."""
        prompt = self._create_explanation_prompt(language, code)
        try:
            text = await self._chat(EXPLAIN_SYSTEM_PROMPT, prompt, 0.3, 2000, 30.0)
            return text.strip()
        except Exception as e:
            raise Exception(f"{self.provider_label} explanation failed: {str(e)}")

    def _clean_output(self, text: str) -> str:
        """Clean markdown code blocks from output."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first line (```language) and last line (```)
            if len(lines) >= 2:
                return "\n".join(lines[1:-1])
        return text


# Singleton instance
converter = CodeConverter()
