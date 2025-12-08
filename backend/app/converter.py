from openai import OpenAI
from groq import Groq
import requests
from app.config import settings
from app.models import ConversionRequest
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CodeConverter:
    """Handles code conversion using multiple AI providers."""
    
    def __init__(self):
        self.provider = settings.ai_provider.lower()
        self.openai_client = None
        self.groq_client = None
        
        # Initialize clients based on provider
        if self.provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            self.openai_client = OpenAI(api_key=settings.openai_api_key)
        elif self.provider == "groq":
            if not settings.groq_api_key:
                raise ValueError("Groq API key not configured")
            self.groq_client = Groq(api_key=settings.groq_api_key)
            
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
        
        prompt = f"""You are an expert senior software engineer. Your task is to convert the following {source_lang} code to {target_lang}.

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
        
        return prompt

    async def convert_code(self, request: ConversionRequest) -> str:
        """Convert code using the configured provider."""
        prompt = self._create_conversion_prompt(request)
        
        if self.provider == "groq":
            return await self._convert_with_groq(prompt)
        elif self.provider == "huggingface":
            return await self._convert_with_huggingface(prompt)
        else:
            return await self._convert_with_openai(prompt)

    async def _convert_with_groq(self, prompt: str) -> str:
        """Convert using Groq API."""
        try:
            completion = self.groq_client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": "You are an expert programmer. Output ONLY code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=8000,
                timeout=60.0,
            )
            return self._clean_output(completion.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Groq conversion failed: {str(e)}")

    async def _convert_with_huggingface(self, prompt: str) -> str:
        """Convert using Hugging Face Inference API."""
        try:
            API_URL = "https://api-inference.huggingface.co/models/bigcode/starcoder2-15b"
            headers = {"Authorization": f"Bearer {settings.huggingface_api_key}"}
            
            # Simplified prompt for completion models
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 2048,
                    "temperature": 0.2,
                    "return_full_text": False
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return self._clean_output(result[0].get("generated_text", ""))
            return self._clean_output(str(result))
            
        except Exception as e:
            raise Exception(f"Hugging Face conversion failed: {str(e)}")

    async def _convert_with_openai(self, prompt: str) -> str:
        """Convert using OpenAI API."""
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert programmer. Output ONLY code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=8000,
                timeout=60.0,
            )
            return self._clean_output(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"OpenAI conversion failed: {str(e)}")

    async def convert_code_stream(self, request: ConversionRequest):
        """Convert code using the configured provider with streaming."""
        prompt = self._create_conversion_prompt(request)
        
        if self.provider == "groq":
            async for chunk in self._convert_with_groq_stream(prompt):
                yield chunk
        elif self.provider == "huggingface":
            # Hugging Face inference API doesn't easily support streaming in the same way
            # Fallback to non-streaming but yield the result at once
            result = await self._convert_with_huggingface(prompt)
            yield result
        else:
            async for chunk in self._convert_with_openai_stream(prompt):
                yield chunk

    async def _convert_with_groq_stream(self, prompt: str):
        """Stream conversion using Groq API."""
        try:
            stream = self.groq_client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": "You are an expert programmer. Output ONLY code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=8000,
                timeout=60.0,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"Error: {str(e)}"

    async def _convert_with_openai_stream(self, prompt: str):
        """Stream conversion using OpenAI API."""
        try:
            stream = self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert programmer. Output ONLY code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=8000,
                timeout=60.0,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"Error: {str(e)}"

    def _clean_output(self, text: str) -> str:
        """Clean markdown code blocks from output."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first line (```language) and last line (```)
            if len(lines) >= 2:
                return "\n".join(lines[1:-1])
        return text

    def _create_explanation_prompt(self, language: str, code: str) -> str:
        """Create a prompt for code explanation."""
        lang_display = self._get_language_display_name(language)
        
        prompt = f"""You are an expert software engineer. Explain the following {lang_display} code in a clear, concise way.

Provide:
1. **Overview**: What the code does (1-2 sentences)
2. **Key Components**: Main functions, classes, or logic
3. **How It Works**: Step-by-step explanation
4. **Important Details**: Any notable patterns, algorithms, or best practices used

Code ({lang_display}):
{code}

Explanation:"""
        
        return prompt

    async def explain_code(self, language: str, code: str) -> str:
        """Explain code using the configured provider."""
        prompt = self._create_explanation_prompt(language, code)
        
        if self.provider == "groq":
            return await self._explain_with_groq(prompt)
        elif self.provider == "huggingface":
            return await self._explain_with_huggingface(prompt)
        else:
            return await self._explain_with_openai(prompt)

    async def _explain_with_groq(self, prompt: str) -> str:
        """Explain using Groq API."""
        try:
            completion = self.groq_client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": "You are an expert programmer who explains code clearly."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                timeout=30.0,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Groq explanation failed: {str(e)}")

    async def _explain_with_huggingface(self, prompt: str) -> str:
        """Explain using Hugging Face API."""
        try:
            API_URL = "https://api-inference.huggingface.co/models/bigcode/starcoder2-15b"
            headers = {"Authorization": f"Bearer {settings.huggingface_api_key}"}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 1024,
                    "temperature": 0.3,
                    "return_full_text": False
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").strip()
            return str(result).strip()
            
        except Exception as e:
            raise Exception(f"Hugging Face explanation failed: {str(e)}")

    async def _explain_with_openai(self, prompt: str) -> str:
        """Explain using OpenAI API."""
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert programmer who explains code clearly."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                timeout=30.0,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI explanation failed: {str(e)}")


# Singleton instance
converter = CodeConverter()
