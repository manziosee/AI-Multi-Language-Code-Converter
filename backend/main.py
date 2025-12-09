from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.models import ConversionRequest, ConversionResponse, ErrorResponse, ExplainRequest, ExplainResponse
from app.converter import converter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="AI Multi-Language Code Converter",
    description="Convert code between multiple programming languages using AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "AI Multi-Language Code Converter",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "openai_configured": bool(settings.openai_api_key),
        "model": settings.openai_model
    }


@app.post("/convert/stream")
@limiter.limit("20/minute")
async def convert_code_stream(request: Request, conv_request: ConversionRequest):
    """
    Stream code conversion from one language to another.
    """
    try:
        logger.info(f"Streaming conversion {conv_request.source_language} to {conv_request.target_language}")
        
        if conv_request.source_language == conv_request.target_language:
            raise HTTPException(
                status_code=400,
                detail="Source and target languages must be different"
            )
            
        return StreamingResponse(
            converter.convert_code_stream(conv_request),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"Streaming error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/convert", response_model=ConversionResponse)
@limiter.limit("20/minute")
async def convert_code(request: Request, conv_request: ConversionRequest):
    """
    Convert code from one language to another.
    
    Args:
        request: FastAPI Request
        conv_request: ConversionRequest with source_language, target_language, and code
        
    Returns:
        ConversionResponse with converted code
        
    Raises:
        HTTPException: If conversion fails
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
        
        # Perform conversion
        converted_code = await converter.convert_code(conv_request)
        
        logger.info("Conversion successful")
        
        return ConversionResponse(
            converted_code=converted_code,
            source_language=conv_request.source_language,
            target_language=conv_request.target_language,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Code conversion failed: {str(e)}"
        )


@app.post("/convert-file", response_model=ConversionResponse)
async def convert_file(
    file: UploadFile = File(...),
    source_language: str = Form(...),
    target_language: str = Form(...)
):
    """
    Convert code from an uploaded file.
    
    Args:
        file: Uploaded code file
        source_language: Source programming language
        target_language: Target programming language
        
    Returns:
        ConversionResponse with converted code
        
    Raises:
        HTTPException: If file reading or conversion fails
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


@app.post("/explain", response_model=ExplainResponse)
@limiter.limit("20/minute")
async def explain_code(request: Request, explain_request: ExplainRequest):
    """
    Explain code in natural language.
    
    Args:
        request: FastAPI Request
        explain_request: ExplainRequest with language and code
        
    Returns:
        ExplainResponse with code explanation
        
    Raises:
        HTTPException: If explanation fails
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
