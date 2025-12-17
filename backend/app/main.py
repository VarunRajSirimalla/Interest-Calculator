"""
This is the main FastAPI application that powers the Interest Calculator backend.
It sets up the API endpoints that the frontend talks to, handles the Google Sheets
connection, and makes sure everything runs smoothly.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Dict
from contextlib import asynccontextmanager

from app.models import (
    CalculateRequest,
    CalculateResponse,
    ErrorResponse,
    HealthResponse
)
from app.config import settings
from app.services.google_sheets import GoogleSheetsService

# Initialize Google Sheets service (will authenticate on first use)
sheets_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This runs when the app starts up and shuts down.
    We use it to check that everything's configured correctly and to
    set up our connection to Google Sheets.
    """
    # Startup
    print("=" * 60)
    print("Starting Interest Calculator API...")
    print("=" * 60)
    
    try:
        # Validate configuration
        settings.validate()
        print("✓ Configuration validated")
        
        # Initialize Google Sheets service
        get_sheets_service()
        print("✓ Google Sheets service initialized")
        
        print("=" * 60)
        print(f"Server ready at http://{settings.API_HOST}:{settings.API_PORT}")
        print(f"API Documentation: http://localhost:{settings.API_PORT}/docs")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ Startup failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown (if needed)
    print("Shutting down...")


# Initialize FastAPI application with lifespan
app = FastAPI(
    title="Interest Calculator API",
    description="Backend API for calculating Simple Interest and Compound Interest using Google Sheets",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_sheets_service() -> GoogleSheetsService:
    """
    Gets our Google Sheets connection. If it doesn't exist yet, we create it.
    This way we only connect once and reuse the same connection for all requests.
    
    Returns:
        The Google Sheets service that talks to our spreadsheet
    
    Raises:
        HTTPException: If we can't connect to Google Sheets
    """
    global sheets_service
    
    if sheets_service is None:
        try:
            sheets_service = GoogleSheetsService(
                credentials_path=settings.get_credentials_path(),
                sheet_id=settings.GOOGLE_SHEET_ID
            )
            sheets_service.authenticate()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize Google Sheets service: {str(e)}"
            )
    
    return sheets_service


@app.get(
    "/",
    response_model=Dict[str, str],
    summary="Root endpoint",
    description="Welcome message and API information"
)
async def root():
    """Just a friendly welcome message when you hit the root URL."""
    return {
        "message": "Interest Calculator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check if the API is running and healthy"
)
async def health_check():
    """Checks if everything is working - API is up and Google Sheets is accessible."""
    try:
        service = get_sheets_service()
        sheet_ok, sheet_msg = service.verify_sheet_structure()
        
        if not sheet_ok:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unhealthy",
                    "version": "1.0.0",
                    "detail": sheet_msg
                }
            )
        
        return HealthResponse(
            status="healthy",
            version="1.0.0"
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "version": "1.0.0",
                "detail": str(e)
            }
        )


@app.post(
    "/calculate",
    response_model=CalculateResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Interest",
    description="Calculate Simple Interest and Compound Interest using Google Sheets",
    responses={
        200: {
            "description": "Successful calculation",
            "model": CalculateResponse
        },
        400: {
            "description": "Invalid input data",
            "model": ErrorResponse
        },
        500: {
            "description": "Server error",
            "model": ErrorResponse
        }
    }
)
async def calculate_interest(request: CalculateRequest):
    """
    This is where the magic happens! Here's what we do:
    
    1. Take the principal, rate, and time you sent us
    2. Write these values to the Input sheet in Google Sheets
    3. Give Google Sheets a moment to run its formulas
    4. Read back the calculated Simple and Compound Interest from the Output sheet
    5. Send the results back to you
    
    Args:
        request: Your calculation data (principal, rate, and time)
    
    Returns:
        The calculated interest amounts, nicely formatted
    
    Raises:
        HTTPException: If calculation fails
    """
    try:
        print("\n" + "=" * 60)
        print("New calculation request received:")
        print(f"  Principal: {request.principal}")
        print(f"  Rate: {request.rate}%")
        print(f"  Time: {request.time} years")
        print("=" * 60)
        
        # Get the Google Sheets service
        service = get_sheets_service()
        
        # Perform the calculation workflow
        results = service.calculate_interest(
            principal=request.principal,
            rate=request.rate,
            time=request.time
        )
        
        # Create response
        response = CalculateResponse(
            simpleInterest=round(results["simpleInterest"], 2),
            compoundInterest=round(results["compoundInterest"], 2),
            principal=request.principal,
            rate=request.rate,
            time=request.time
        )
        
        print("=" * 60)
        print("Calculation completed successfully:")
        print(f"  Simple Interest: {response.simpleInterest}")
        print(f"  Compound Interest: {response.compoundInterest}")
        print("=" * 60 + "\n")
        
        return response
        
    except ValueError as e:
        print(f"✗ Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"✗ Calculation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation failed: {str(e)}"
        )


@app.get(
    "/verify",
    summary="Verify Sheet Structure",
    description="Verify that the Google Sheet has the required structure"
)
async def verify_sheet():
    """
    Verify the Google Sheet structure.
    
    Checks if the required worksheets (Input, Calc, Output) exist.
    
    Returns:
        Status of sheet structure verification
    """
    try:
        service = get_sheets_service()
        success, message = service.verify_sheet_structure()
        
        if success:
            return {"status": "success", "message": message}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level="info"
    )
