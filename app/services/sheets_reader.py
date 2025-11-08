"""
Google Sheets integration service
"""
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logger import logger


class SheetsReader:
    """Service for reading data from Google Sheets"""
    
    def __init__(self):
        self.client = None
        self.sheet = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Sheets client"""
        try:
            if not settings.GOOGLE_SHEETS_CREDENTIALS:
                logger.warning("Google Sheets credentials not configured")
                return
            
            # Parse credentials from environment variable
            creds_dict = json.loads(settings.GOOGLE_SHEETS_CREDENTIALS)
            
            # Define scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Authenticate
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            self.client = gspread.authorize(creds)
            
            # Open spreadsheet
            if settings.GOOGLE_SHEET_ID:
                self.sheet = self.client.open_by_key(settings.GOOGLE_SHEET_ID)
                logger.info(f"Connected to Google Sheet: {self.sheet.title}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {str(e)}")
    
    def get_all_data(self, sheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all data from a worksheet"""
        try:
            if not self.sheet:
                raise Exception("Google Sheets not initialized")
            
            # Get worksheet
            worksheet = self.sheet.worksheet(sheet_name) if sheet_name else self.sheet.sheet1
            
            # Get all values first to handle duplicate headers
            all_values = worksheet.get_all_values()
            
            if not all_values or len(all_values) < 2:
                logger.warning("Sheet is empty or has no data rows")
                return []
            
            # Get headers from row 3 (index 2) and make them unique
            headers = all_values[2]  # Row 3 is the header
            
            # Make headers unique by adding suffixes to duplicates
            unique_headers = []
            header_counts = {}
            for header in headers:
                if not header or header.strip() == "":
                    header = "Unnamed"
                
                if header in header_counts:
                    header_counts[header] += 1
                    unique_header = f"{header}_{header_counts[header]}"
                else:
                    header_counts[header] = 0
                    unique_header = header
                
                unique_headers.append(unique_header)
            
            # Convert data rows to dictionaries
            data = []
            for row in all_values[3:]:  # Data starts from row 4 (index 3)
                if not any(row):  # Skip empty rows
                    continue
                    
                row_dict = {}
                for i, value in enumerate(row):
                    if i < len(unique_headers):
                        row_dict[unique_headers[i]] = value
                
                data.append(row_dict)
            
            logger.info(f"Retrieved {len(data)} records from sheet: {worksheet.title}")
            return data
            
        except Exception as e:
            logger.error(f"Error reading from Google Sheets: {str(e)}")
            raise
    
    def get_filtered_data(
        self,
        filters: Dict[str, Any],
        sheet_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get filtered data from a worksheet"""
        try:
            all_data = self.get_all_data(sheet_name)
            
            # Apply filters
            filtered_data = []
            for row in all_data:
                match = True
                for key, value in filters.items():
                    if key not in row or row[key] != value:
                        match = False
                        break
                
                if match:
                    filtered_data.append(row)
                    if len(filtered_data) >= limit:
                        break
            
            logger.info(f"Filtered data: {len(filtered_data)} records")
            return filtered_data
            
        except Exception as e:
            logger.error(f"Error filtering data: {str(e)}")
            raise
    
    def get_all_text(self, sheet_name: Optional[str] = None) -> str:
        """Get all data as concatenated text for RAG"""
        try:
            data = self.get_all_data(sheet_name)
            
            # Convert to text
            text_chunks = []
            for row in data:
                row_text = " | ".join([f"{k}: {v}" for k, v in row.items()])
                text_chunks.append(row_text)
            
            return "\n".join(text_chunks)
            
        except Exception as e:
            logger.error(f"Error converting data to text: {str(e)}")
            raise


# Create global instance
sheets_reader = SheetsReader()

