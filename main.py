from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, declarative_base
import os

app = FastAPI()

# ==========================
# DATABASE
# ==========================

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# ==========================
# TABLE
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
# REQUEST MODEL
# ==========================

class DisableRequest(BaseModel):
    employee_id: str
    company_username: str
    company_password: str


# ==========================
# ROOT
# ==========================

@app.get("/")
def root():
    return {"message": "Employee API Running"}


# ==========================
# GET EMPLOYEES
# ==========================

@app.get("/employees")
def get_employees():

    db = SessionLocal()

    employees = db.query(Employee).all()

    db.close()

    return [
        {
            "id": e.id,
            "code": e.code,
            "email": e.email,
            "first_name": e.first_name,
            "last_name": e.last_name,
            "status": e.status,
            "last_login": e.last_login
        }
        for e in employees
    ]


# ==========================
# DISABLE EMPLOYEE
# ==========================

@app.post("/disable-employee")
def disable_employee(request: DisableRequest):

    # validate company credentials
    if (
        request.company_username != COMPANY_USERNAME
        or request.company_password != COMPANY_PASSWORD
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid company credentials"
        )

    db = SessionLocal()

    employee = db.query(Employee).filter(
        Employee.id == request.employee_id
    ).first()

    if not employee:
        db.close()
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # update status instead of deleting
    employee.status = "Disabled"

    db.commit()

    db.close()

    return {
        "message": "Employee disabled successfully",
        "employee_id": request.employee_id,
        "new_status": "Disabled"
    }
