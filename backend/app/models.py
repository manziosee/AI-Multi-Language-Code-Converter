from pydantic import BaseModel, Field
from typing import Literal


# Supported programming languages
SourceLanguage = Literal["python", "php", "java", "sql", "nodejs", "typescript", "golang", "prisma", "c", "cpp", "csharp", "rust", "javascript"]
TargetLanguage = Literal["python", "php", "java", "sql", "nodejs", "typescript", "golang", "prisma", "c", "cpp", "csharp", "rust", "javascript"]


class ConversionRequest(BaseModel):
    """Request model for code conversion."""
    
    source_language: SourceLanguage = Field(..., description="Source programming language")
    target_language: TargetLanguage = Field(..., description="Target programming language")
    code: str = Field(..., description="Source code to convert", min_length=1)
    
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


class ConversionResponse(BaseModel):
    """Response model for code conversion."""
    
    converted_code: str = Field(..., description="Converted code in target language")
    source_language: str = Field(..., description="Source language used")
    target_language: str = Field(..., description="Target language used")
    success: bool = Field(default=True, description="Conversion success status")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    detail: str = Field(..., description="Error message")
    success: bool = Field(default=False, description="Always false for errors")
