from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os

app = FastAPI()

# ==========================
# DATABASE CONFIG
# ==========================

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ==========================
# TABLE MODEL
# ==========================

class Employee(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True, index=True)
    code = Column(String)
    email = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    status = Column(String)
    last_login = Column(String)

Base.metadata.create_all(bind=engine)

# ==========================
# COMPANY CREDENTIALS
# ==========================

COMPANY_USERNAME = "admin"
COMPANY_PASSWORD = "company123"

# ==========================
# REQUEST MODEL
# ==========================

class DeleteRequest(BaseModel):
    employee_id: str
    company_username: str
    company_password: str

# ==========================
# ROOT
# ==========================

@app.get("/")
def root():
    return {"message": "PostgreSQL Employee API Running"}

# ==========================
# GET EMPLOYEES
# ==========================

@app.get("/employees")
def get_employees():
    db = SessionLocal()

    employees = db.query(Employee).all()

    result = [
        {
            "id": e.id,
            "code": e.code,
            "email": e.email,
            "first_name": e.first_name,
            "last_name": e.last_name,
            "status": e.status,
            "last_login": e.last_login,
        }
        for e in employees
    ]

    db.close()
    return result

# ==========================
# DELETE EMPLOYEE
# ==========================

@app.post("/delete-employee")
def delete_employee(request: DeleteRequest):

    # check company credentials
    if (
        request.company_username != COMPANY_USERNAME
        or request.company_password != COMPANY_PASSWORD
    ):
        raise HTTPException(status_code=401, detail="Invalid company credentials")

    db = SessionLocal()

    employee = db.query(Employee).filter(Employee.id == request.employee_id).first()

    if not employee:
        db.close()
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(employee)
    db.commit()

    remaining = db.query(Employee).all()

    result = [
        {
            "id": e.id,
            "code": e.code,
            "email": e.email,
            "first_name": e.first_name,
            "last_name": e.last_name,
            "status": e.status,
            "last_login": e.last_login,
        }
        for e in remaining
    ]

    db.close()

    return {
        "message": "Employee deleted successfully",
        "remaining_employees": result
    }
