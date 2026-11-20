import os
import socket
import sys
from pathlib import Path

import httpx
import pytest

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


FAKE_PORT = _free_port()
FAKE = f"http://127.0.0.1:{FAKE_PORT}"

# main.py builds its converter at import time, so give it a valid config first.
os.environ.update({
    "AI_PROVIDER": "openai_compatible",
    "OPENAI_COMPATIBLE_NAME": "DemoGW",
    "OPENAI_COMPATIBLE_BASE_URL": FAKE + "/v1",
    "OPENAI_COMPATIBLE_API_KEY": "dr-test",
    "OPENAI_COMPATIBLE_MODEL": "org/coder-32b",
    "ENABLE_CODE_EXECUTION": "false",
})

from tests.fake_llm import serve_in_thread  # noqa: E402

PROVIDERS = {
    "groq": ({"groq_api_key": "gsk-test"}, {"GROQ_BASE_URL": FAKE}, "Bearer gsk-test", "Groq"),
    "openai": ({"openai_api_key": "sk-test"}, {"OPENAI_BASE_URL": FAKE + "/v1"}, "Bearer sk-test", "OpenAI"),
    "openai_compatible": ({}, {}, "Bearer dr-test", "DemoGW"),
    "huggingface": ({"huggingface_api_key": "hf-test", "huggingface_base_url": FAKE + "/v1",
                     "huggingface_model": "Qwen/Qwen3-Coder-30B-A3B-Instruct"}, {}, "Bearer hf-test", "Hugging Face"),
}


@pytest.fixture(scope="session", autouse=True)
def fake_llm():
    server = serve_in_thread(FAKE_PORT)
    yield FAKE
    server.should_exit = True


@pytest.fixture(params=list(PROVIDERS))
def provider(request, monkeypatch):
    """Point the app at the fake server through each provider in turn."""
    import main
    import app.converter as conv_mod
    from app.config import settings

    name = request.param
    settings_patch, env_patch, auth, label = PROVIDERS[name]
    monkeypatch.setattr(settings, "ai_provider", name)
    for k, v in settings_patch.items():
        monkeypatch.setattr(settings, k, v)
    for k, v in env_patch.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setattr(main, "converter", conv_mod.CodeConverter())

    httpx.delete(FAKE + "/_log")
    main.limiter.reset()
    return {"name": name, "auth": auth, "label": label}


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    import main
    return TestClient(main.app)


@pytest.fixture
def upstream_calls():
    return lambda: httpx.get(FAKE + "/_log").json()
