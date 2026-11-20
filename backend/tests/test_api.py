"""API tests. Tests taking the `provider` fixture run once per AI provider."""
import pytest

from app.converter import STREAM_ERROR_MARKER

PY = "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n"
REQ = {"source_language": "python", "target_language": "rust", "code": PY}


def test_root(client):
    assert client.get("/").json()["status"] == "online"


def test_health_reports_active_provider(client, provider):
    h = client.get("/health").json()
    assert h["status"] == "healthy"
    assert h["provider"] == provider["name"]
    assert h["provider_label"] == provider["label"]
    assert h["code_execution_enabled"] is False


# ---------------------------------------------------------------- /convert
def test_convert_strips_fence_and_includes_analysis(client, provider, upstream_calls):
    r = client.post("/convert", json=REQ)
    assert r.status_code == 200, r.text
    d = r.json()
    assert not d["converted_code"].startswith("```")
    assert not d["converted_code"].rstrip().endswith("```")
    assert d["confidence_score"] is not None
    assert d["complexity_analysis"] and d["security_analysis"]
    call = upstream_calls()[0]
    assert call["auth"] == provider["auth"]
    assert "fn fibonacci" in d["converted_code"]
    assert call["stream"] is False and call["max_tokens"] == 8000
    assert call["temperature"] == (0.1 if provider["name"] == "groq" else 0.3)
    # gpt-oss on Groq gets low reasoning effort; nobody else gets the field
    expected_effort = "low" if provider["name"] == "groq" else None
    assert call["reasoning_effort"] == expected_effort
    if provider["name"] == "huggingface":
        assert call["model"] == "Qwen/Qwen3-Coder-30B-A3B-Instruct"


def test_convert_upstream_error_is_500(client, provider):
    r = client.post("/convert", json={**REQ, "code": "FAIL_ME"})
    assert r.status_code == 500
    assert f"{provider['label']} conversion failed" in r.json()["detail"]


@pytest.mark.parametrize("body,status", [
    ({**REQ, "target_language": "python"}, 400),   # same language
    ({**REQ, "target_language": "cobol"}, 422),    # unsupported
    ({**REQ, "code": ""}, 422),                    # empty
    ({**REQ, "code": "x" * 100001}, 400),          # too large
])
def test_convert_validation(client, body, status):
    assert client.post("/convert", json=body).status_code == status


# --------------------------------------------------------- /convert/stream
def test_stream_returns_full_output(client, provider, upstream_calls):
    r = client.post("/convert/stream", json=REQ)
    assert r.status_code == 200
    assert STREAM_ERROR_MARKER not in r.text
    assert r.text.startswith("use std::io;") and r.text.rstrip().endswith("}")
    assert upstream_calls()[0]["stream"] is True
    if provider["name"] == "groq":
        assert upstream_calls()[0]["reasoning_effort"] == "low"


def test_stream_error_before_output_is_502(client, provider):
    r = client.post("/convert/stream", json={**REQ, "code": "FAIL_ME"})
    assert r.status_code == 502
    assert r.json()["detail"].startswith(f"{provider['label']} conversion failed")


def test_stream_error_mid_way_ends_with_marker(client, provider):
    r = client.post("/convert/stream", json={**REQ, "code": "FAIL_MID"})
    assert r.status_code == 200
    partial, sep, message = r.text.partition(STREAM_ERROR_MARKER)
    assert sep, "stream should end with the error marker"
    assert partial.startswith("use std::io;")          # output before the failure is kept
    assert message.startswith(f"{provider['label']} stopped mid-conversion")


def test_stream_same_language_rejected(client):
    assert client.post("/convert/stream", json={**REQ, "target_language": "python"}).status_code == 400


# ----------------------------------------------------------- other routes
def test_convert_file(client, provider):
    r = client.post("/convert-file", files={"file": ("fib.py", PY.encode())},
                    data={"source_language": "python", "target_language": "rust"})
    assert r.status_code == 200 and r.json()["success"]


def test_convert_file_rejects_binary(client):
    r = client.post("/convert-file", files={"file": ("x.py", b"\xff\xfe\x00\x81")},
                    data={"source_language": "python", "target_language": "rust"})
    assert r.status_code == 400


def test_explain(client, provider, upstream_calls):
    r = client.post("/explain", json={"language": "python", "code": PY})
    assert r.status_code == 200, r.text
    assert r.json()["explanation"].startswith("### Overview")
    assert upstream_calls()[0]["max_tokens"] == 2000


def test_explain_too_large(client):
    assert client.post("/explain", json={"language": "python", "code": "x" * 50001}).status_code == 400


def test_analyze(client):
    d = client.post("/analyze", json={"language": "python", "code": PY}).json()
    assert d["success"]
    assert {"complexity", "performance", "security", "code_review"} <= d.keys()


def test_format(client):
    r = client.post("/format", json={"language": "python", "code": PY})
    assert r.status_code == 200 and r.json()["success"]


def test_execute_disabled_by_default(client):
    r = client.post("/execute", json={"language": "python", "code": "import os; print(os.getcwd())"})
    assert r.status_code == 403 and "disabled" in r.json()["detail"]


def test_execute_when_opted_in(client, monkeypatch):
    import main
    monkeypatch.setattr(main.settings, "enable_code_execution", True)
    r = client.post("/execute", json={"language": "python", "code": "print(6*7)"})
    assert r.status_code == 200 and r.json()["output"].strip() == "42"


def test_batch_convert(client, provider):
    files = [{"name": "a.py", "code": PY}, {"name": "b.py", "code": "FAIL_ME"}]
    d = client.post("/batch-convert", json={"files": files, "source_language": "python",
                                            "target_language": "rust"}).json()
    assert d["total"] == 2 and d["results"][0]["success"]
    assert d["successful"] == 1 and d["failed"] == 1 and "error" in d["results"][1]


def test_batch_limit_is_400(client):
    files = [{"name": f"{i}.py", "code": PY} for i in range(11)]
    r = client.post("/batch-convert", json={"files": files, "source_language": "python",
                                            "target_language": "rust"})
    assert r.status_code == 400


def test_rate_limit(client):
    import main
    main.limiter.reset()
    same = {**REQ, "target_language": "python"}  # rejected cheaply with 400, still counted
    codes = [client.post("/convert", json=same).status_code for _ in range(21)]
    assert codes[:20] == [400] * 20 and codes[20] == 429
    main.limiter.reset()


def test_cors_preflight(client):
    r = client.options("/convert", headers={"Origin": "https://example.vercel.app",
                                            "Access-Control-Request-Method": "POST"})
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] in ("*", "https://example.vercel.app")


# ------------------------------------------------------------- API docs
def test_swagger_and_redoc_served(client):
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200


def test_openapi_every_route_documented(client):
    spec = client.get("/openapi.json").json()
    assert spec["info"]["version"] == "2.0.0"
    tags = {t["name"] for t in spec["tags"]}
    for path, ops in spec["paths"].items():
        for method, op in ops.items():
            assert op.get("summary"), f"{method.upper()} {path} has no summary"
            assert op.get("tags") and set(op["tags"]) <= tags, f"{method.upper()} {path} has no known tag"


def test_openapi_documents_stream_errors_and_examples(client):
    spec = client.get("/openapi.json").json()
    stream = spec["paths"]["/convert/stream"]["post"]["responses"]
    assert {"200", "400", "429", "502"} <= stream.keys()
    assert "text/plain" in stream["200"]["content"]
    schemas = spec["components"]["schemas"]
    assert "example" in schemas["ConversionRequest"]
    assert "example" in schemas["BatchConversionRequest"]


def test_health_fields(client):
    h = client.get("/health").json()
    assert h["version"] == "2.0.0" and isinstance(h["uptime_seconds"], int)
    root = client.get("/").json()
    assert root["docs"] == "/docs" and root["health"] == "/health"
