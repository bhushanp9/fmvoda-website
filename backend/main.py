
import re

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
from database import engine, get_db


# Create database tables
models.Base.metadata.create_all(bind=engine)


# Initialize FastAPI
app = FastAPI(
    title="FMVODA Backend",
    description="Defence and Aerospace MSME Capability and Market Access Platform",
    version="1.0.0"
)


# Allow requests from the FMVODA website
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fmvoda.com",
        "https://www.fmvoda.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Membership application request
class MembershipApplication(BaseModel):
    c: str
    p: str
    s: str


# Health check
@app.get("/")
def home():
    return {
        "message": "Welcome to FMVODA Backend",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "FMVODA API"
    }


# Submit membership application
@app.post("/api/membership", status_code=201)
def submit_membership(
    application: MembershipApplication,
    db: Session = Depends(get_db)
):

    company_name = application.c.strip()
    contact_details = application.p.strip()
    sector = application.s.strip()

    if not company_name or not contact_details or not sector:
        raise HTTPException(
            status_code=400,
            detail="All membership fields are required."
        )

    # Extract phone number if included at the end
    phone_match = re.search(
        r"(\+?\d[\d\s-]{8,}\d)\s*$",
        contact_details
    )

    if phone_match:
        phone = phone_match.group(1).strip()
        contact_person = contact_details[:phone_match.start()].strip(" ,-")
    else:
        phone = "Not provided separately"
        contact_person = contact_details

    if not contact_person:
        contact_person = contact_details

    new_application = models.MembershipApplicationDB(
        organization_name=company_name,
        contact_person=contact_person,
        phone=phone,
        primary_sector=sector,
        organization_type="MSME",
        status="received"
    )

    try:
        db.add(new_application)
        db.commit()
        db.refresh(new_application)

        return {
            "message": "Membership application submitted successfully",
            "reference_id": new_application.id,
            "status": new_application.status
        }

    
    except Exception as e:
        db.rollback()
        print("DATABASE ERROR:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Unable to save membership application."
        )

