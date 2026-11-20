"""Starts the whole stack for browser tests:
fake model server -> real backend -> production frontend build (vite preview).

Run from the repo root:  pytest e2e
Set CHROME_PATH to use an installed Chrome instead of Playwright's Chromium.
Set E2E_SKIP_BUILD=1 to reuse an existing frontend/dist built for E2E_API.
"""
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
sys.path.insert(0, str(BACKEND))


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


FAKE_PORT, API_PORT, WEB_PORT = _free_port(), _free_port(), _free_port()
# Read by test modules at import time
os.environ["E2E_BASE"] = f"http://localhost:{WEB_PORT}"
os.environ["E2E_API"] = f"http://localhost:{API_PORT}"


def _wait(url: str, proc: subprocess.Popen, timeout=60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"{proc.args} exited early:\n{proc.stdout.read() if proc.stdout else ''}")
        try:
            if httpx.get(url, timeout=1).status_code < 500:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.2)
    raise RuntimeError(f"timed out waiting for {url}")


@pytest.fixture(scope="session", autouse=True)
def stack():
    from tests.fake_llm import serve_in_thread

    fake = serve_in_thread(FAKE_PORT)
    procs = []
    try:
        api = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--port", str(API_PORT), "--log-level", "warning"],
            cwd=BACKEND, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            start_new_session=True,
            env={**os.environ,
                 "AI_PROVIDER": "openai_compatible",
                 "OPENAI_COMPATIBLE_NAME": "DemoGW",
                 "OPENAI_COMPATIBLE_BASE_URL": f"http://127.0.0.1:{FAKE_PORT}/v1",
                 "OPENAI_COMPATIBLE_API_KEY": "dr-test",
                 "OPENAI_COMPATIBLE_MODEL": "org/coder-32b"})
        procs.append(api)
        _wait(os.environ["E2E_API"] + "/health", api)

        if not os.environ.get("E2E_SKIP_BUILD"):
            subprocess.run(["npx", "vite", "build", "--logLevel", "error"], cwd=FRONTEND, check=True,
                           env={**os.environ, "VITE_API_URL": os.environ["E2E_API"]})
        web = subprocess.Popen(
            ["npx", "vite", "preview", "--port", str(WEB_PORT), "--strictPort"],
            cwd=FRONTEND, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            start_new_session=True)
        procs.append(web)
        _wait(os.environ["E2E_BASE"], web)
        yield
    finally:
        # Signal the whole process group: npx spawns vite as a child process.
        for p in procs:
            try:
                os.killpg(p.pid, signal.SIGTERM)
                p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        fake.should_exit = True
