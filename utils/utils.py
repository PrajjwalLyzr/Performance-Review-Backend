import pandas as pd
import re


def convert_google_sheet_url(url):
    """Converts a Google Sheet link to a CSV export link."""
    pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?'
    replacement = lambda m: f'https://docs.google.com/spreadsheets/d/{m.group(1)}/export?' + \
                            (f'gid={m.group(3)}&' if m.group(3) else '') + 'format=csv'
    return re.sub(pattern, replacement, url)

def read_google_sheet(url):
    """Reads the Google Sheet and returns it as a DataFrame."""
    csv_url = convert_google_sheet_url(url)
    df = pd.read_csv(csv_url)

    # Rename Google Sheet columns to match Supabase table schema
    df.rename(columns={
        "Employee ID": "employee_id",
        "Employee Name": "employee_name",
        "Department": "department",
        "Manager Name": "manager_name",
        "Role": "role",
        "Self-Assessment": "self_assessment",
        "Manager Feedback": "manager_feedback",
        "Persona": "persona"
    }, inplace=True)

    return df


def read_google_sheet_emp_data(url):
    """Reads the Google Sheet and returns it as a DataFrame."""
    csv_url = convert_google_sheet_url(url)
    df = pd.read_csv(csv_url)

    # Rename Google Sheet columns to match Supabase table schema
    df.rename(columns={
        "Employee ID": "employee_id",
        "Employee Name": "employee_name",
    }, inplace=True)

    return df[["employee_id", "employee_name"]]  # Only keep necessary columns


