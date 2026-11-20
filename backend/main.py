from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.models import (
    ConversionRequest, ConversionResponse, ErrorResponse,
    ExplainRequest, ExplainResponse, AnalyzeRequest,
    ExecuteRequest, ExecuteResponse, BatchConversionRequest,
    HealthResponse, RootResponse, AnalyzeResponse, FormatResponse,
    BatchConversionResponse,
)
from app.converter import converter, STREAM_ERROR_MARKER
from app.analyzers import (
    analyze_complexity, analyze_performance, analyze_security,
    get_code_review, calculate_confidence_score
)
from app.formatter import format_code
from app.executor import execute_code
import logging
import time

API_VERSION = "2.0.0"
STARTED_AT = time.time()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
API_DESCRIPTION = """
Convert code between **14 languages** with AI, explain it, and run static analysis.

**Languages:** Python, JavaScript, Node.js, TypeScript, Java, PHP, Go, C, C++, C#, Rust,
plus SQL ↔ Prisma ↔ Drizzle schemas.

**AI providers** (chosen by the server via `AI_PROVIDER`): Groq, Hugging Face,
OpenAI, or any OpenAI-compatible API. `GET /health` shows which one is active.

### Rate limits (per IP)
| Endpoint | Limit |
|---|---|
| `/convert`, `/convert/stream`, `/explain`, `/analyze`, `/format` | 20 / minute |
| `/execute` | 10 / minute |
| `/batch-convert` | 5 / minute |

Exceeding a limit returns **429**.

### Streaming
`POST /convert/stream` returns plain text as the model writes it. If the model fails
*before* any output you get a **502**. If it fails *mid-stream*, the body ends with
`\\u0000STREAM_ERROR\\u0000` followed by the error message.
"""

OPENAPI_TAGS = [
    {"name": "Conversion", "description": "Translate code between languages (calls the AI provider)."},
    {"name": "Explanation", "description": "Plain-language explanation of code (calls the AI provider)."},
    {"name": "Analysis", "description": "Static complexity, performance and security checks. No AI call, instant."},
    {"name": "Playground", "description": "Run code on the server. Disabled unless `ENABLE_CODE_EXECUTION=true`."},
    {"name": "System", "description": "Service status and health checks."},
]

# Error shapes shared by the routes, shown in Swagger
E400 = {400: {"model": ErrorResponse, "description": "Invalid input (same languages, too large, ...)"}}
E422 = {422: {"description": "Request body failed validation (e.g. unsupported language)"}}
E429 = {429: {"description": "Rate limit exceeded"}}
E500 = {500: {"model": ErrorResponse, "description": "The AI provider returned an error"}}

app = FastAPI(
    title="AI Multi-Language Code Converter API",
    description=API_DESCRIPTION,
    version=API_VERSION,
    openapi_tags=OPENAPI_TAGS,
    docs_url="/docs",
    redoc_url="/redoc",
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    contact={"name": "Source code", "url": "https://github.com/manziosee/AI-Multi-Language-Code-Converter"},
    swagger_ui_parameters={"defaultModelsExpandDepth": 0, "displayRequestDuration": True, "tryItOutEnabled": True},
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/", response_model=RootResponse, tags=["System"], summary="Service info and links")
async def root():
    """Basic service info, with links to the docs and health check."""
    return {
        "status": "online",
        "service": "AI Multi-Language Code Converter",
        "version": API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["System"], summary="Health check")
async def health_check():
    """
    Liveness check used by the host (Fly.io polls it every 15s) and by the
    frontend's status card. It never calls the AI provider, so it is free
    and fast; it reports which provider and model are configured.
    """
    return {
        "status": "healthy",
        "version": API_VERSION,
        "uptime_seconds": int(time.time() - STARTED_AT),
        "provider": converter.provider,
        "provider_label": converter.provider_label,
        "model": converter.model,
        "code_execution_enabled": settings.enable_code_execution,
    }


@app.post(
    "/convert/stream",
    tags=["Conversion"],
    summary="Convert code (streaming)",
    response_class=StreamingResponse,
    responses={
        200: {"content": {"text/plain": {"example": "fn main() {\n    println!(\"Hello, World!\");\n}"}},
              "description": "Converted code, streamed as plain text"},
        **E400, **E422, **E429,
        502: {"model": ErrorResponse, "description": "The AI provider failed before any output"},
    },
)
@limiter.limit("20/minute")
async def convert_code_stream(request: Request, conv_request: ConversionRequest):
    """
    Convert code and stream the result as plain text while the model writes it.
    This is what the web app uses.

    - **502**: the AI provider failed before producing any output.
    - Mid-stream failure: the body ends with `\\u0000STREAM_ERROR\\u0000<message>`
      and the output before it is incomplete.
    """
    logger.info(f"Streaming conversion {conv_request.source_language} to {conv_request.target_language}")

    if conv_request.source_language == conv_request.target_language:
        raise HTTPException(
            status_code=400,
            detail="Source and target languages must be different"
        )

    stream = converter.convert_code_stream(conv_request)
    label = converter.provider_label

    # Pull the first chunk before committing to a 200 so upfront failures
    # (bad key, no credit, unknown model) become a proper HTTP error.
    try:
        first = await stream.__anext__()
    except StopAsyncIteration:
        first = ""
    except Exception as e:
        logger.error(f"Streaming error before output: {e}")
        raise HTTPException(status_code=502, detail=f"{label} conversion failed: {e}")

    async def body():
        if first:
            yield first
        try:
            async for piece in stream:
                yield piece
        except Exception as e:
            logger.error(f"Streaming error mid-stream: {e}")
            yield f"{STREAM_ERROR_MARKER}{label} stopped mid-conversion: {e}"

    return StreamingResponse(body(), media_type="text/plain; charset=utf-8")


@app.post("/convert", response_model=ConversionResponse, tags=["Conversion"],
          summary="Convert code (with analysis)", responses={**E400, **E422, **E429, **E500})
@limiter.limit("20/minute")
async def convert_code(request: Request, conv_request: ConversionRequest):
    """
    Convert code and return it in one response, together with a confidence score
    and static complexity, performance, security and review analysis of the source.

    Set `auto_format: true` to format the source before converting, and
    `include_analysis: false` to skip the analysis.
    """
    try:
        logger.info(f"Converting {conv_request.source_language} to {conv_request.target_language}")
        
        # Validate that source and target languages are different
        if conv_request.source_language == conv_request.target_language:
            raise HTTPException(
                status_code=400,
                detail="Source and target languages must be different"
            )
        
        # Validate code length
        if len(conv_request.code) > 100000:
            raise HTTPException(
                status_code=400,
                detail="Code is too large. Maximum 100,000 characters allowed."
            )
        
        # Auto-format if requested
        code_to_convert = conv_request.code
        if conv_request.auto_format:
            code_to_convert = format_code(code_to_convert, conv_request.source_language)
        
        # Perform conversion
        converted_code = await converter.convert_code(ConversionRequest(
            source_language=conv_request.source_language,
            target_language=conv_request.target_language,
            code=code_to_convert
        ))
        
        # Prepare response
        response = ConversionResponse(
            converted_code=converted_code,
            source_language=conv_request.source_language,
            target_language=conv_request.target_language,
            success=True
        )
        
        # Add analysis if requested
        if conv_request.include_analysis:
            response.confidence_score = calculate_confidence_score(
                conv_request.code, 
                conv_request.source_language, 
                conv_request.target_language
            )
            response.complexity_analysis = analyze_complexity(
                conv_request.code, 
                conv_request.source_language
            )
            response.performance_analysis = analyze_performance(
                conv_request.code, 
                conv_request.source_language
            )
            response.security_analysis = analyze_security(
                conv_request.code, 
                conv_request.source_language
            )
            response.code_review = get_code_review(
                conv_request.code, 
                conv_request.source_language
            )
        
        logger.info("Conversion successful")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Code conversion failed: {str(e)}"
        )


@app.post("/convert-file", response_model=ConversionResponse, tags=["Conversion"],
          summary="Convert an uploaded file", responses={400: {"model": ErrorResponse, "description": "File is not UTF-8 text"}, **E500})
async def convert_file(
    file: UploadFile = File(...),
    source_language: str = Form(...),
    target_language: str = Form(...)
):
    """
    Upload a source file (multipart form, UTF-8 text) and convert it.
    Send `source_language` and `target_language` as form fields.
    """
    try:
        # Read file content
        content = await file.read()
        code = content.decode('utf-8')
        
        logger.info(f"File uploaded: {file.filename}, size: {len(code)} bytes")
        
        # Create conversion request
        conv_request = ConversionRequest(
            source_language=source_language,
            target_language=target_language,
            code=code
        )
        
        # Perform conversion
        converted_code = await converter.convert_code(conv_request)
        
        logger.info("File conversion successful")
        
        return ConversionResponse(
            converted_code=converted_code,
            source_language=source_language,
            target_language=target_language,
            success=True
        )
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be a valid text file with UTF-8 encoding"
        )
    except Exception as e:
        logger.error(f"File conversion error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"File conversion failed: {str(e)}"
        )


@app.post("/explain", response_model=ExplainResponse, tags=["Explanation"],
          summary="Explain code", responses={**E400, **E422, **E429, **E500})
@limiter.limit("20/minute")
async def explain_code(request: Request, explain_request: ExplainRequest):
    """
    Explain code in plain language. The answer is Markdown with four sections:
    Overview, Key Components, How It Works and Important Details.
    """
    try:
        logger.info(f"Explaining {explain_request.language} code")
        
        # Validate code length
        if len(explain_request.code) > 50000:
            raise HTTPException(
                status_code=400,
                detail="Code is too large. Maximum 50,000 characters allowed."
            )
        
        # Get explanation
        explanation = await converter.explain_code(explain_request.language, explain_request.code)
        
        logger.info("Explanation successful")
        
        return ExplainResponse(
            explanation=explanation,
            language=explain_request.language,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Explanation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Code explanation failed: {str(e)}"
        )


@app.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"],
          summary="Static analysis", responses={**E422, **E429})
@limiter.limit("20/minute")
async def analyze_code(request: Request, analyze_request: AnalyzeRequest):
    """
    Static analysis of the code: complexity score, performance issues, security
    findings and review suggestions. Runs locally with heuristics, without calling the AI.
    """
    try:
        logger.info(f"Analyzing {analyze_request.language} code")
        
        return {
            "complexity": analyze_complexity(analyze_request.code, analyze_request.language),
            "performance": analyze_performance(analyze_request.code, analyze_request.language),
            "security": analyze_security(analyze_request.code, analyze_request.language),
            "code_review": get_code_review(analyze_request.code, analyze_request.language),
            "success": True
        }
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute", response_model=ExecuteResponse, tags=["Playground"],
          summary="Run Python / JavaScript",
          responses={403: {"model": ErrorResponse, "description": "Code execution is disabled on this server"},
                     **E400, **E429})
@limiter.limit("10/minute")
async def execute_code_endpoint(request: Request, exec_request: ExecuteRequest):
    """
    Run Python or JavaScript on the server and return stdout and stderr (5 second timeout).

    **Disabled by default (403).** The code runs as a plain subprocess, with **no
    sandbox**. Only enable it with `ENABLE_CODE_EXECUTION=true` inside an isolated
    environment you control.
    """
    if not settings.enable_code_execution:
        raise HTTPException(
            status_code=403,
            detail="Code execution is disabled on this server (ENABLE_CODE_EXECUTION=false)."
        )
    try:
        logger.info(f"Executing {exec_request.language} code")
        
        if len(exec_request.code) > 10000:
            raise HTTPException(
                status_code=400,
                detail="Code too large for execution. Maximum 10,000 characters."
            )
        
        result = execute_code(exec_request.code, exec_request.language)
        return ExecuteResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch-convert", response_model=BatchConversionResponse, tags=["Conversion"],
          summary="Convert up to 10 files", responses={**E400, **E422, **E429})
@limiter.limit("5/minute")
async def batch_convert(request: Request, batch_request: BatchConversionRequest):
    """
    Convert up to 10 files with the same language pair in one request.
    Each file succeeds or fails independently; check `results[].success`.
    """
    try:
        logger.info(f"Batch converting {len(batch_request.files)} files")
        
        if len(batch_request.files) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 files allowed per batch"
            )
        
        results = []
        for file_data in batch_request.files:
            try:
                conv_request = ConversionRequest(
                    source_language=batch_request.source_language,
                    target_language=batch_request.target_language,
                    code=file_data['code']
                )
                converted = await converter.convert_code(conv_request)
                results.append({
                    'name': file_data['name'],
                    'converted_code': converted,
                    'success': True
                })
            except Exception as e:
                results.append({
                    'name': file_data['name'],
                    'error': str(e),
                    'success': False
                })
        
        return {
            'results': results,
            'total': len(batch_request.files),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success'])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch conversion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/format", response_model=FormatResponse, tags=["Analysis"],
          summary="Format code", responses={**E422, **E429})
@limiter.limit("20/minute")
async def format_code_endpoint(request: Request, analyze_request: AnalyzeRequest):
    """
    Format code according to the language's conventions (no AI call).
    """
    try:
        formatted = format_code(analyze_request.code, analyze_request.language)
        return {
            'formatted_code': formatted,
            'success': True
        }
    except Exception as e:
        logger.error(f"Formatting error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import os
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
