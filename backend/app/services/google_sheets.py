"""
This service handles all communication with Google Sheets.
It authenticates with Google, writes data to the sheet, and reads results back.
"""

import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, Tuple
from time import sleep
from pathlib import Path


class GoogleSheetsService:
    """
    This class does all the heavy lifting for talking to Google Sheets.
    
    What it does:
    - Connects to Google Sheets using your service account credentials
    - Writes the numbers you want to calculate to the Input sheet
    - Reads back the calculated results from the Output sheet
    """
    
    # Scopes required for Google Sheets API access
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self, credentials_path: str, sheet_id: str):
        """
        Sets up the service with your credentials and sheet ID.
        
        Args:
            credentials_path: Where to find your Google service account JSON file
            sheet_id: The unique ID of your Google Spreadsheet (from the URL)
        
        Raises:
            FileNotFoundError: If we can't find your credentials file
            ValueError: If you forgot to provide a sheet ID
        """
        if not sheet_id:
            raise ValueError("Sheet ID cannot be empty")
        
        credentials_file = Path(credentials_path)
        if not credentials_file.exists():
            raise FileNotFoundError(
                f"Credentials file not found: {credentials_path}"
            )
        
        self.credentials_path = credentials_path
        self.sheet_id = sheet_id
        self.client = None
        self.spreadsheet = None
        
    def authenticate(self) -> None:
        """
        Logs in to Google Sheets using your service account.
        This needs to happen before we can read or write anything.
        
        Raises:
            Exception: If login fails (usually means wrong credentials or sheet not shared)
        """
        try:
            # Load credentials from the service account JSON file
            credentials = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.SCOPES
            )
            
            # Authorize the gspread client
            self.client = gspread.authorize(credentials)
            
            # Open the spreadsheet by ID
            self.spreadsheet = self.client.open_by_key(self.sheet_id)
            
            print(f"✓ Successfully authenticated with Google Sheets")
            print(f"✓ Connected to spreadsheet: {self.spreadsheet.title}")
            
        except FileNotFoundError as e:
            raise Exception(f"Credentials file not found: {e}")
        except gspread.exceptions.SpreadsheetNotFound:
            raise Exception(
                f"Spreadsheet not found. Check if:\n"
                f"1. Sheet ID is correct: {self.sheet_id}\n"
                f"2. Sheet is shared with service account email"
            )
        except Exception as e:
            raise Exception(f"Authentication failed: {str(e)}")
    
    def write_inputs(
        self, 
        principal: float, 
        rate: float, 
        time: float,
        input_sheet_name: str = "Input",
        principal_cell: str = "B2",
        rate_cell: str = "B3",
        time_cell: str = "B4"
    ) -> None:
        """
        Writes your numbers to the Input sheet so Google Sheets can calculate with them.
        
        Args:
            principal: The starting amount of money
            rate: Interest rate as a percentage
            time: Number of years
            input_sheet_name: Which sheet to write to (default: "Input")
            principal_cell: Where to put principal (default: "B2")
            rate_cell: Where to put rate (default: "B3")
            time_cell: Where to put time (default: "B4")
        
        Raises:
            Exception: If writing fails (maybe the sheet doesn't exist?)
        """
        if not self.spreadsheet:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        try:
            # Get the Input worksheet
            input_sheet = self.spreadsheet.worksheet(input_sheet_name)
            
            # Write values to the specified cells
            input_sheet.update_acell(principal_cell, principal)
            input_sheet.update_acell(rate_cell, rate)
            input_sheet.update_acell(time_cell, time)
            
            print(f"✓ Written inputs to {input_sheet_name} sheet:")
            print(f"  - {principal_cell}: {principal}")
            print(f"  - {rate_cell}: {rate}")
            print(f"  - {time_cell}: {time}")
            
            # Small delay to allow Google Sheets to recalculate
            sleep(0.5)
            
        except gspread.exceptions.WorksheetNotFound:
            raise Exception(
                f"Worksheet '{input_sheet_name}' not found. "
                f"Please ensure the sheet exists."
            )
        except Exception as e:
            raise Exception(f"Failed to write inputs: {str(e)}")
    
    def read_outputs(
        self,
        output_sheet_name: str = "Output",
        si_cell: str = "B2",
        ci_cell: str = "B3"
    ) -> Dict[str, float]:
        """
        Reads the calculated interest amounts from the Output sheet.
        Google Sheets has already done the math for us!
        
        Args:
            output_sheet_name: Which sheet to read from (default: "Output")
            si_cell: Where to find simple interest (default: "B2")
            ci_cell: Where to find compound interest (default: "B3")
        
        Returns:
            A dictionary with your results:
                - simpleInterest: The simple interest Google Sheets calculated
                - compoundInterest: The compound interest Google Sheets calculated
        
        Raises:
            Exception: If reading fails or the values don't make sense
        """
        if not self.spreadsheet:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        try:
            # Get the Output worksheet
            output_sheet = self.spreadsheet.worksheet(output_sheet_name)
            
            # Read values from the specified cells
            simple_interest_raw = output_sheet.acell(si_cell).value
            compound_interest_raw = output_sheet.acell(ci_cell).value
            
            # Convert to float, handling empty or invalid values
            try:
                simple_interest = float(simple_interest_raw) if simple_interest_raw else 0.0
            except (ValueError, TypeError):
                raise Exception(
                    f"Invalid simple interest value in {si_cell}: {simple_interest_raw}"
                )
            
            try:
                compound_interest = float(compound_interest_raw) if compound_interest_raw else 0.0
            except (ValueError, TypeError):
                raise Exception(
                    f"Invalid compound interest value in {ci_cell}: {compound_interest_raw}"
                )
            
            print(f"✓ Read outputs from {output_sheet_name} sheet:")
            print(f"  - {si_cell} (SI): {simple_interest}")
            print(f"  - {ci_cell} (CI): {compound_interest}")
            
            return {
                "simpleInterest": simple_interest,
                "compoundInterest": compound_interest
            }
            
        except gspread.exceptions.WorksheetNotFound:
            raise Exception(
                f"Worksheet '{output_sheet_name}' not found. "
                f"Please ensure the sheet exists."
            )
        except Exception as e:
            raise Exception(f"Failed to read outputs: {str(e)}")
    
    def calculate_interest(
        self,
        principal: float,
        rate: float,
        time: float
    ) -> Dict[str, float]:
        """
        Complete workflow: write inputs, wait for calculation, read outputs.
        
        Args:
            principal: Principal amount
            rate: Interest rate (percentage)
            time: Time period (years)
        
        Returns:
            Dictionary containing simple and compound interest results
        
        Raises:
            Exception: If any step in the process fails
        """
        # Ensure authenticated
        if not self.client:
            self.authenticate()
        
        # Write inputs to sheet
        self.write_inputs(principal, rate, time)
        
        # Read and return calculated outputs
        return self.read_outputs()
    
    def verify_sheet_structure(self) -> Tuple[bool, str]:
        """
        Verify that the spreadsheet has the required structure.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.spreadsheet:
            return False, "Not authenticated"
        
        required_sheets = ["Input", "Calc", "Output"]
        existing_sheets = [ws.title for ws in self.spreadsheet.worksheets()]
        
        missing_sheets = [s for s in required_sheets if s not in existing_sheets]
        
        if missing_sheets:
            return False, f"Missing required sheets: {', '.join(missing_sheets)}"
        
        return True, "Sheet structure verified successfully"
