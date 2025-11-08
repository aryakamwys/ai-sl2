"""
Data retrieval endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.schemas import DataQueryRequest, DataResponse, ErrorResponse
from app.services.sheets_reader import sheets_reader
from app.core.logger import logger

router = APIRouter()


@router.get("/sheets", response_model=DataResponse)
async def get_sheet_data(
    sheet_name: Optional[str] = Query(None, description="Sheet name to query"),
    limit: int = Query(100, description="Maximum number of records")
):
    """
    Get data from Google Sheets
    """
    try:
        logger.info(f"Fetching data from sheet: {sheet_name or 'default'}")
        
        data = sheets_reader.get_all_data(sheet_name)
        
        # Apply limit
        limited_data = data[:limit]
        
        return DataResponse(
            data=limited_data,
            count=len(limited_data),
            sheet_name=sheet_name
        )
        
    except Exception as e:
        logger.error(f"Error fetching sheet data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sheets/query", response_model=DataResponse)
async def query_sheet_data(request: DataQueryRequest):
    """
    Query Google Sheets with filters
    """
    try:
        logger.info(f"Querying sheet data with filters: {request.filters}")
        
        if request.filters:
            data = sheets_reader.get_filtered_data(
                filters=request.filters,
                sheet_name=request.sheet_name,
                limit=request.limit or 100
            )
        else:
            data = sheets_reader.get_all_data(request.sheet_name)
            data = data[:request.limit] if request.limit else data
        
        return DataResponse(
            data=data,
            count=len(data),
            sheet_name=request.sheet_name
        )
        
    except Exception as e:
        logger.error(f"Error querying sheet data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sheets/info")
async def get_sheets_info():
    """
    Get information about connected Google Sheets
    """
    try:
        if not sheets_reader.sheet:
            raise HTTPException(
                status_code=503,
                detail="Google Sheets not connected"
            )
        
        worksheets = sheets_reader.sheet.worksheets()
        
        return {
            "spreadsheet_title": sheets_reader.sheet.title,
            "spreadsheet_id": sheets_reader.sheet.id,
            "worksheets": [
                {
                    "title": ws.title,
                    "rows": ws.row_count,
                    "cols": ws.col_count
                }
                for ws in worksheets
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting sheets info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

