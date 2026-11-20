"""Fake model server that speaks the OpenAI chat-completions format (used by
every provider), so tests never call a real provider or spend tokens.

Behaviour is driven by markers in the user's code:
  FAIL_ME   -> upstream error before any output
  FAIL_MID  -> streams a few chunks, then the connection breaks
"""
import asyncio
import json

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

app = FastAPI()
LOG: list = []

EXPLANATION = """### Overview
Computes Fibonacci numbers recursively. <img src=x onerror="window.__xss=1">

### Key Components
- **fibonacci(n)**: the recursive function
- `range(10)` loop

### How It Works
Each call recurses twice.

### Important Details
Exponential time."""

RUST = ["use std::io;\n", "\n", "fn fibonacci(n: u64) -> u64 {\n", "    if n <= 1 { return n; }\n",
        "    fibonacci(n - 1) + fibonacci(n - 2)\n", "}\n", "\n", "fn main() {\n",
        "    for i in 0..10 { println!(\"F({}) = {}\", i, fibonacci(i)); }\n", "}\n"]

STREAM_DELAY = 0.12  # seconds between chunks, so the UI's streaming state is observable


def _chunk(model, content=None, usage_only=False):
    d = {"id": "c", "object": "chat.completion.chunk", "created": 0, "model": model,
         "choices": [] if usage_only else [{"index": 0, "delta": {"content": content}, "finish_reason": None}]}
    if usage_only:
        d["usage"] = {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}
    return "data: " + json.dumps(d) + "\n\n"


@app.post("/v1/chat/completions")
@app.post("/openai/v1/chat/completions")  # path used by the groq SDK
async def chat(req: Request):
    b = await req.json()
    LOG.append({"path": req.url.path, "auth": req.headers.get("authorization"), "model": b["model"],
                "stream": b.get("stream", False), "temperature": b.get("temperature"),
                "max_tokens": b.get("max_tokens"), "reasoning_effort": b.get("reasoning_effort")})
    user = b["messages"][-1]["content"]
    if "FAIL_ME" in user:
        return JSONResponse({"error": {"message": "upstream exploded", "type": "server_error"}}, status_code=400)

    if b.get("stream"):
        async def gen():
            for i, t in enumerate(RUST):
                if "FAIL_MID" in user and i == 3:
                    raise RuntimeError("simulated connection drop")
                await asyncio.sleep(STREAM_DELAY)
                yield _chunk(b["model"], t)
            yield _chunk(b["model"], usage_only=True)  # some gateways send this
            yield "data: [DONE]\n\n"
        return StreamingResponse(gen(), media_type="text/event-stream")

    content = EXPLANATION if "Explain the following" in user else "```rust\n" + "".join(RUST) + "```"
    return {"id": "c", "object": "chat.completion", "created": 0, "model": b["model"],
            "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}}


@app.get("/_log")
async def get_log():
    return LOG


@app.delete("/_log")
async def clear_log():
    LOG.clear()
    return {}


def serve_in_thread(port: int):
    """Start the fake server in a daemon thread; returns once it accepts requests."""
    import threading
    import time
    import uvicorn

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    deadline = time.time() + 10
    while not server.started:
        if time.time() > deadline:
            raise RuntimeError("fake LLM server did not start")
        time.sleep(0.05)
    return server


if __name__ == "__main__":
    import sys
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(sys.argv[1]) if len(sys.argv) > 1 else 8766)
