"""
This file handles all the configuration stuff - loading settings from environment
variables and making sure everything's set up correctly before we start.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """All the settings we need to run the app, loaded from your .env file."""
    
    # Google Sheets Configuration
    GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "")
    GOOGLE_CREDENTIALS_PATH: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    
    # Sheet Names
    INPUT_SHEET_NAME: str = "Input"
    CALC_SHEET_NAME: str = "Calc"
    OUTPUT_SHEET_NAME: str = "Output"
    
    # Cell References
    INPUT_PRINCIPAL_CELL: str = "B2"
    INPUT_RATE_CELL: str = "B3"
    INPUT_TIME_CELL: str = "B4"
    
    OUTPUT_SI_CELL: str = "B2"
    OUTPUT_CI_CELL: str = "B3"
    
    @classmethod
    def validate(cls) -> None:
        """Makes sure all the required settings are actually set up before we try to run."""
        if not cls.GOOGLE_SHEET_ID:
            raise ValueError("GOOGLE_SHEET_ID environment variable is not set")
        
        credentials_path = Path(cls.GOOGLE_CREDENTIALS_PATH)
        if not credentials_path.exists():
            raise ValueError(
                f"Google credentials file not found at: {cls.GOOGLE_CREDENTIALS_PATH}"
            )
    
    @classmethod
    def get_credentials_path(cls) -> str:
        """Figures out the full path to your credentials file, wherever it is."""
        return str(Path(cls.GOOGLE_CREDENTIALS_PATH).resolve())


# Create a settings instance
settings = Settings()
