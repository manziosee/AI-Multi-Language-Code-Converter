from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from app.config import settings
from app.models import ConversionRequest, ConversionResponse, ErrorResponse
from app.converter import converter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Multi-Language Code Converter",
    description="Convert code between multiple programming languages using AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
async def convert_code_stream(request: ConversionRequest):
    """
    Stream code conversion from one language to another.
    """
    try:
        logger.info(f"Streaming conversion {request.source_language} to {request.target_language}")
        
        if request.source_language == request.target_language:
            raise HTTPException(
                status_code=400,
                detail="Source and target languages must be different"
            )
            
        return StreamingResponse(
            converter.convert_code_stream(request),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"Streaming error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/convert", response_model=ConversionResponse)
async def convert_code(request: ConversionRequest):
    """
    Convert code from one language to another.
    
    Args:
        request: ConversionRequest with source_language, target_language, and code
        
    Returns:
        ConversionResponse with converted code
        
    Raises:
        HTTPException: If conversion fails
    """
    try:
        logger.info(f"Converting {request.source_language} to {request.target_language}")
        
        # Validate that source and target languages are different
        if request.source_language == request.target_language:
            raise HTTPException(
                status_code=400,
                detail="Source and target languages must be different"
            )
        
        # Perform conversion
        converted_code = await converter.convert_code(request)
        
        logger.info("Conversion successful")
        
        return ConversionResponse(
            converted_code=converted_code,
            source_language=request.source_language,
            target_language=request.target_language,
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
        request = ConversionRequest(
            source_language=source_language,
            target_language=target_language,
            code=code
        )
        
        # Perform conversion
        converted_code = await converter.convert_code(request)
        
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
