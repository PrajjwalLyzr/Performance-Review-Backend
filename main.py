import re
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils import read_google_sheet
from database import supabase_client
import os
from dotenv import load_dotenv
import numpy as np


load_dotenv()

# Supabase Credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") 

# Initialize Supabase Client
supabase = supabase_client(SUPABASE_KEY=SUPABASE_KEY, SUPABASE_URL=SUPABASE_URL)

app = FastAPI()

@app.get('/')
async def health_check():
    return "The Health check is successfull"

# Define request body schema
class SheetURL(BaseModel):
    url: str


def insert_new_data_into_supabase(df):
    """Insert new unique records into the Supabase tables."""
    existing_zomato_data = supabase.table("zomato_emp_data").select("employee_id").execute().data
    existing_emp_data = supabase.table("emp_data").select("employee_id").execute().data
    
    existing_ids = {row["employee_id"] for row in existing_zomato_data}
    existing_emp_ids = {row["employee_id"] for row in existing_emp_data}
    
    new_zomato_data = df[~df["employee_id"].isin(existing_ids)]
    new_emp_data = df[~df["employee_id"].isin(existing_emp_ids)][["employee_id", "employee_name"]]
    new_emp_data["status"] = 0  # Set status as 0 (active)
    
    if not new_zomato_data.empty:
        supabase.table("zomato_emp_data").insert(new_zomato_data.to_dict(orient="records")).execute()
    
    if not new_emp_data.empty:
        supabase.table("emp_data").insert(new_emp_data.to_dict(orient="records")).execute()
    
    return {"message": "Data synced successfully"}



# @app.post("/sync-sheet-to-supabase")
# async def sync_sheet_to_supabase(payload: dict):
#     """Fetch Google Sheet data, insert new records, and return data in JSON format."""
#     try:
#         gsheet_link = payload.get("gsheet_url")
#         if not gsheet_link:
#             raise HTTPException(status_code=400, detail="Google Sheet URL is required")
        
#         # Read data from Google Sheet
#         df = read_google_sheet(gsheet_link)
#         json_data = df.to_dict(orient="records")  # Convert DataFrame to JSON

#         # Insert new data into Supabase
#         result = insert_new_data_into_supabase(df)

#         return {
#             "insert_result": result,
#             "google_sheet_data": json_data  # Returning all Google Sheet data
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync-sheet-to-supabase")
async def sync_sheet_to_supabase(payload: dict):
    """Sync Google Sheet data with Supabase, ensuring up-to-date and unique employee records."""
    try:
        gsheet_link = payload.get("gsheet_url")
        if not gsheet_link:
            raise HTTPException(status_code=400, detail="Google Sheet URL is required")

        # Read data from Google Sheet
        df = read_google_sheet(gsheet_link)

        # Fetch existing data from `zomato_emp_data`
        existing_data = supabase.table("zomato_emp_data").select("employee_id").execute().data
        existing_emp_ids = {row["employee_id"] for row in existing_data}

        # Get employee IDs from the Google Sheet
        sheet_emp_ids = set(df["employee_id"])

        # Find new employees (in Sheet but not in Supabase)
        new_employees = df[~df["employee_id"].isin(existing_emp_ids)]

        # Find removed employees (in Supabase but not in Sheet)
        removed_emp_ids = existing_emp_ids - sheet_emp_ids

        # Insert new employees into Supabase if any
        if not new_employees.empty:
            new_employees_json = new_employees.to_dict(orient="records")
            supabase.table("zomato_emp_data").insert(new_employees_json).execute()

        # Delete removed employees from Supabase if any
        if removed_emp_ids:
            supabase.table("zomato_emp_data").delete().in_("employee_id", list(removed_emp_ids)).execute()

        # Return the updated Google Sheet data (ensuring unique employee IDs)
        df = df.drop_duplicates(subset=["employee_id"])
        df = df.replace([np.inf, -np.inf], np.nan).fillna("")  # Ensure JSON compliance
        json_data = df.to_dict(orient="records")

        return {
            "message": "Sync completed successfully",
            "google_sheet_data": json_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/refresh-sheet")
async def refresh_sheet(payload: dict):
    """Refresh Google Sheet data and update Supabase tables accordingly, returning new data if any."""
    try:
        gsheet_link = payload.get("gsheet_url")
        if not gsheet_link:
            raise HTTPException(status_code=400, detail="Google Sheet URL is required")

        df = read_google_sheet(gsheet_link)

        # Fetch existing data from both tables
        existing_zomato_data = supabase.table("zomato_emp_data").select("employee_id").execute().data
        existing_emp_data = supabase.table("emp_data").select("employee_id", "status").execute().data

        existing_emp_ids = {row["employee_id"] for row in existing_zomato_data}
        sheet_emp_ids = set(df["employee_id"])

        # Find employees present in `zomato_emp_data` but missing in the sheet
        removed_emp_ids = existing_emp_ids - sheet_emp_ids

        if removed_emp_ids:
            # Update `status = 1` in `emp_data`
            supabase.table("emp_data").update({"status": 1}).in_("employee_id", list(removed_emp_ids)).execute()
            # Delete missing employees from `zomato_emp_data`
            supabase.table("zomato_emp_data").delete().in_("employee_id", list(removed_emp_ids)).execute()

        # Find new employees in the sheet but not in `zomato_emp_data`
        new_data = df[~df["employee_id"].isin(existing_emp_ids)]
        
        if not new_data.empty:
            # Insert new data into Supabase
            await sync_sheet_to_supabase({"gsheet_url": gsheet_link})
            new_data_json = new_data.to_dict(orient="records")  # Convert DataFrame to JSON
            return {
                "message": "Refresh completed successfully",
                "google_sheet_data": new_data_json
            }
        else:
            return {"message": "No new data found in the sheet"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


