from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import os

app = FastAPI()

CSV_FILE = "employees.csv"

# -----------------------
# Dummy Company Credentials
# -----------------------
COMPANY_USERNAME = "admin"
COMPANY_PASSWORD = "company123"


# -----------------------
# Models
# -----------------------

class DeleteRequest(BaseModel):
    employee_id: str
    company_username: str
    company_password: str


# -----------------------
# Helper Functions
# -----------------------

def load_employees():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame()
    return pd.read_csv(CSV_FILE)


def save_employees(df):
    df.to_csv(CSV_FILE, index=False)


# -----------------------
# API Endpoints
# -----------------------

@app.get("/")
def root():
    return {"message": "Employee Management API Running"}


# Fetch employee list (for Power App on login)
@app.get("/employees")
def get_employees():
    df = load_employees()
    return df.to_dict(orient="records")


# Delete employee with credential check
@app.post("/delete-employee")
def delete_employee(request: DeleteRequest):

    # Step 1: Validate company credentials
    if (
        request.company_username != COMPANY_USERNAME
        or request.company_password != COMPANY_PASSWORD
    ):
        raise HTTPException(status_code=401, detail="Invalid company credentials")

    # Step 2: Load data
    df = load_employees()

    if request.employee_id not in df["id"].values:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Step 3: Delete employee
    df = df[df["id"] != request.employee_id]

    save_employees(df)

    return {
        "message": "Employee deleted successfully",
        "remaining_employees": df.to_dict(orient="records")
    }
