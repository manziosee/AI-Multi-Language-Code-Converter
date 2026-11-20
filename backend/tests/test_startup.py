"""Misconfiguration must stop the server at startup with a clear message."""
import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent


# Environment variables override backend/.env, so blank every key: these tests
# must not depend on whatever real keys a developer has in their local .env.
BLANK = {k: "" for k in (
    "GROQ_API_KEY", "OPENAI_API_KEY", "HUGGINGFACE_API_KEY",
    "OPENAI_COMPATIBLE_BASE_URL", "OPENAI_COMPATIBLE_API_KEY", "OPENAI_COMPATIBLE_MODEL",
)}


def boot(env: dict):
    base = {"PATH": "/usr/bin:/bin", "HOME": "/tmp", **BLANK}
    r = subprocess.run([sys.executable, "-c", "import main"], cwd=BACKEND,
                       env={**base, **env}, capture_output=True, text=True, timeout=60)
    return r.returncode, r.stderr


def test_missing_groq_key():
    code, err = boot({"AI_PROVIDER": "groq"})
    assert code != 0 and "Groq API key not configured" in err


def test_missing_openai_compatible_fields():
    code, err = boot({"AI_PROVIDER": "openai_compatible", "OPENAI_COMPATIBLE_API_KEY": "k"})
    assert code != 0
    assert "OPENAI_COMPATIBLE_BASE_URL" in err and "OPENAI_COMPATIBLE_MODEL" in err


def test_missing_huggingface_key():
    code, err = boot({"AI_PROVIDER": "huggingface"})
    assert code != 0 and "Hugging Face API key not configured" in err


def test_unknown_provider():
    code, err = boot({"AI_PROVIDER": "bard"})
    assert code != 0 and "Unknown AI_PROVIDER" in err


def test_provider_name_is_case_insensitive():
    code, err = boot({"AI_PROVIDER": "GROQ", "GROQ_API_KEY": "x"})
    assert code == 0, err
