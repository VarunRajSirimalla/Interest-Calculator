"""
These are the data models that define what information we expect to receive
and send back. They also handle validation to make sure everything's correct.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class CalculateRequest(BaseModel):
    """
    The data you send us when asking for interest calculations.
    
    What we need:
        principal: How much money you're starting with (must be positive)
        rate: The interest rate as a percentage (must be positive, can't exceed 100%)
        time: How many years (must be positive)
    """
    
    principal: float = Field(
        ...,
        description="Principal amount in currency",
        gt=0,
        example=10000.0
    )
    rate: float = Field(
        ...,
        description="Interest rate in percentage",
        gt=0,
        le=100,
        example=5.5
    )
    time: float = Field(
        ...,
        description="Time period in years",
        gt=0,
        example=3.0
    )
    
    @field_validator("principal", "rate", "time")
    @classmethod
    def validate_positive(cls, v: float, info) -> float:
        """Makes sure all numbers are positive - can't have negative money or time!"""
        if v <= 0:
            raise ValueError(f"{info.field_name} must be greater than 0")
        return v
    
    @field_validator("rate")
    @classmethod
    def validate_rate(cls, v: float) -> float:
        """Keeps the interest rate reasonable - no more than 100%."""
        if v > 100:
            raise ValueError("Rate cannot exceed 100%")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "principal": 10000.0,
                "rate": 5.5,
                "time": 3.0
            }
        }


class CalculateResponse(BaseModel):
    """
    What we send back to you with the calculation results.
    
    You'll get:
        simpleInterest: The simple interest amount we calculated
        compoundInterest: The compound interest amount we calculated
        principal: The principal you gave us (just for reference)
        rate: The rate you gave us (just for reference)
        time: The time period you gave us (just for reference)
    """
    
    simpleInterest: float = Field(
        ...,
        description="Calculated simple interest amount",
        example=1650.0
    )
    compoundInterest: float = Field(
        ...,
        description="Calculated compound interest amount",
        example=1742.41
    )
    principal: Optional[float] = Field(
        None,
        description="Principal amount used in calculation",
        example=10000.0
    )
    rate: Optional[float] = Field(
        None,
        description="Interest rate used in calculation",
        example=5.5
    )
    time: Optional[float] = Field(
        None,
        description="Time period used in calculation",
        example=3.0
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "simpleInterest": 1650.0,
                "compoundInterest": 1742.41,
                "principal": 10000.0,
                "rate": 5.5,
                "time": 3.0
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response model.
    
    Attributes:
        error: Error message
        detail: Additional error details (optional)
    """
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Calculation failed",
                "detail": "Unable to connect to Google Sheets"
            }
        }


class HealthResponse(BaseModel):
    """
    Health check response model.
    
    Attributes:
        status: Service status
        version: API version
    """
    
    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0"
            }
        }
