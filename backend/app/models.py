from pydantic import BaseModel, Field
from typing import Literal, List, Dict, Any, Optional


# Supported programming languages
SourceLanguage = Literal["python", "php", "java", "sql", "nodejs", "typescript", "golang", "prisma", "drizzle", "c", "cpp", "csharp", "rust", "javascript"]
TargetLanguage = Literal["python", "php", "java", "sql", "nodejs", "typescript", "golang", "prisma", "drizzle", "c", "cpp", "csharp", "rust", "javascript"]


class ConversionRequest(BaseModel):
    """Request model for code conversion."""
    
    source_language: SourceLanguage = Field(..., description="Source programming language")
    target_language: TargetLanguage = Field(..., description="Target programming language")
    code: str = Field(..., description="Source code to convert", min_length=1)
    auto_format: bool = Field(default=False, description="Auto-format code before conversion")
    include_analysis: bool = Field(default=True, description="Include code analysis in response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_language": "python",
                "target_language": "nodejs",
                "code": "def hello():\n    print('Hello, World!')"
            }
        }


class ExplainRequest(BaseModel):
    """Request model for code explanation."""
    
    language: SourceLanguage = Field(..., description="Programming language")
    code: str = Field(..., description="Code to explain", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "language": "python",
                "code": "def hello():\n    print('Hello, World!')"
            }
        }


class ExplainResponse(BaseModel):
    """Response model for code explanation."""
    
    explanation: str = Field(..., description="Code explanation")
    language: str = Field(..., description="Programming language")
    success: bool = Field(default=True, description="Explanation success status")


class ExecuteResponse(BaseModel):
    """Response model for code execution."""
    
    success: bool = Field(..., description="Execution success status")
    output: str = Field(..., description="Program output")
    error: str = Field(default="", description="Error message if any")


class ConversionResponse(BaseModel):
    """Response model for code conversion."""
    
    converted_code: str = Field(..., description="Converted code in target language")
    source_language: str = Field(..., description="Source language used")
    target_language: str = Field(..., description="Target language used")
    success: bool = Field(default=True, description="Conversion success status")
    confidence_score: Optional[int] = Field(None, description="Conversion confidence (0-100)")
    complexity_analysis: Optional[Dict[str, Any]] = Field(None, description="Code complexity analysis")
    performance_analysis: Optional[Dict[str, Any]] = Field(None, description="Performance analysis")
    security_analysis: Optional[Dict[str, Any]] = Field(None, description="Security scan results")
    code_review: Optional[Dict[str, Any]] = Field(None, description="Code review suggestions")


class AnalyzeRequest(BaseModel):
    """Request model for code analysis and formatting."""
    
    language: SourceLanguage = Field(..., description="Programming language")
    code: str = Field(..., description="Code to analyze", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "language": "python",
                "code": "def total(items):\n    s = 0\n    for i in items:\n        for j in items:\n            s += i * j\n    return s"
            }
        }


class ExecuteRequest(BaseModel):
    """Request model for code execution."""
    
    language: Literal["python", "javascript", "nodejs"] = Field(..., description="Programming language")
    code: str = Field(..., description="Code to execute", min_length=1)

    class Config:
        json_schema_extra = {"example": {"language": "python", "code": "print(6 * 7)"}}


class BatchConversionRequest(BaseModel):
    """Request model for batch conversion."""
    
    files: List[Dict[str, str]] = Field(..., description="Up to 10 files, each {name, code}")
    source_language: SourceLanguage = Field(..., description="Source programming language")
    target_language: TargetLanguage = Field(..., description="Target programming language")

    class Config:
        json_schema_extra = {
            "example": {
                "files": [
                    {"name": "greet.py", "code": "def greet(name):\n    return f'Hello, {name}!'"},
                    {"name": "square.py", "code": "def square(x):\n    return x * x"}
                ],
                "source_language": "python",
                "target_language": "typescript"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    
    detail: str = Field(..., description="Error message")
    success: bool = Field(default=False, description="Always false for errors")


# ---------------------------------------------------------------------------
# Response models used for the OpenAPI (Swagger) docs
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """Liveness check. Cheap: never calls the AI provider."""

    status: Literal["healthy"] = Field(..., description="Always 'healthy' when the server is up")
    version: str = Field(..., description="API version")
    provider: str = Field(..., description="Active AI provider id", examples=["groq"])
    provider_label: str = Field(..., description="Human-readable provider name", examples=["Groq"])
    model: str = Field(..., description="Model used for conversions", examples=["openai/gpt-oss-120b"])
    code_execution_enabled: bool = Field(..., description="Whether /execute is enabled")
    uptime_seconds: int = Field(..., description="Seconds since the server started")


class RootResponse(BaseModel):
    status: str = Field(..., examples=["online"])
    service: str
    version: str
    docs: str = Field(..., description="Swagger UI path")
    redoc: str = Field(..., description="ReDoc path")
    health: str = Field(..., description="Health check path")


class AnalyzeResponse(BaseModel):
    """Static analysis results (no AI call)."""

    complexity: Dict[str, Any]
    performance: Dict[str, Any]
    security: Dict[str, Any]
    code_review: Dict[str, Any]
    success: bool = True


class FormatResponse(BaseModel):
    formatted_code: str
    success: bool = True


class BatchFileResult(BaseModel):
    name: str
    success: bool
    converted_code: Optional[str] = None
    error: Optional[str] = None


class BatchConversionResponse(BaseModel):
    results: List[BatchFileResult]
    total: int
    successful: int
    failed: int
