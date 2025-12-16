"""
ML API Mock Server for IRIS Credit Risk
Simulates all ML endpoints during development:
- /predict - Credit risk prediction
- /compliance - Document compliance checking
- /crossverify - Field cross-verification
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import random

app = FastAPI(
    title="IRIS Credit Risk Mock API",
    description="Mock ML endpoints for IRIS credit risk system",
    version="1.0.0"
)

class CreditRiskRequest(BaseModel):
    age: Optional[int] = Field(None, ge=18, le=100)
    gender: Optional[str] = None
    job: Optional[str] = None
    housing: Optional[str] = None
    saving_accounts: Optional[str] = None
    checking_account: Optional[str] = None
    credit_amount: Optional[float] = Field(None, gt=0)
    duration: Optional[int] = Field(None, gt=0)
    purpose: Optional[str] = None

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "IRIS Credit Risk Mock API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "POST /predict - Credit risk prediction",
            "compliance": "POST /compliance - Document compliance check",
            "crossverify": "POST /crossverify - Field cross-verification",
            "health": "GET /health - Health check"
        }
    }

@app.post("/predict")
def predict_credit_risk(request: CreditRiskRequest):
    """
    Mock credit risk prediction endpoint
    Returns prediction, risk score, and risk factors
    """
    
    # Validate required fields
    missing_fields = []
    if request.age is None:
        missing_fields.append("age")
    if request.gender is None:
        missing_fields.append("gender")
    if request.job is None:
        missing_fields.append("job")
    if request.credit_amount is None:
        missing_fields.append("credit_amount")
    if request.duration is None:
        missing_fields.append("duration")
    
    if missing_fields:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )
    
    # Calculate mock risk score based on inputs
    risk_factors = []
    base_score = 0.5
    
    # Age factor
    if request.age < 25:
        risk_factors.append("Young age increases credit risk")
        base_score += 0.1
    elif request.age > 60:
        risk_factors.append("Advanced age may affect repayment capacity")
        base_score += 0.05
    else:
        base_score -= 0.05
    
    # Job factor
    if request.job == "unemployed":
        risk_factors.append("Unemployed - no stable income source")
        base_score += 0.25
    elif request.job == "unskilled":
        risk_factors.append("Unskilled employment - lower income stability")
        base_score += 0.15
    elif request.job == "highly skilled":
        base_score -= 0.15
    
    # Housing factor
    if request.housing == "own":
        base_score -= 0.08
    elif request.housing == "free":
        risk_factors.append("No property ownership")
        base_score += 0.05
    
    # Savings factor
    if request.saving_accounts == "none":
        risk_factors.append("No savings - limited financial buffer")
        base_score += 0.15
    elif request.saving_accounts == "little":
        risk_factors.append("Insufficient savings")
        base_score += 0.08
    elif request.saving_accounts in ["quite rich", "rich"]:
        base_score -= 0.12
    
    # Checking account factor
    if request.checking_account in ["none", "little"]:
        risk_factors.append("Low checking account balance")
        base_score += 0.08
    elif request.checking_account == "rich":
        base_score -= 0.05
    
    # Credit amount vs duration
    if request.credit_amount and request.duration:
        monthly_payment = request.credit_amount / request.duration
        if monthly_payment > 1000:
            risk_factors.append(f"High monthly payment: ₹{monthly_payment:.2f}")
            base_score += 0.12
        if request.duration < 6:
            risk_factors.append("Short loan duration increases payment pressure")
            base_score += 0.05
    
    # Purpose factor
    risky_purposes = ["vacation/others", "car"]
    safe_purposes = ["education", "business"]
    
    if request.purpose in risky_purposes:
        risk_factors.append(f"Non-essential loan purpose: {request.purpose}")
        base_score += 0.06
    elif request.purpose in safe_purposes:
        base_score -= 0.03
    
    # Normalize score between 0 and 1
    risk_score = max(0.0, min(1.0, base_score))
    
    # Determine prediction (0 = good credit, 1 = bad credit)
    prediction = 1 if risk_score > 0.6 else 0
    probability = risk_score if prediction == 1 else 1 - risk_score
    
    # Add default message if no risk factors
    if not risk_factors:
        risk_factors = ["Strong financial profile with no major risk indicators"]
    
    return {
        "prediction": prediction,
        "risk_score": round(risk_score, 3),
        "probability": round(probability, 3),
        "risk_class": "bad" if prediction == 1 else "good",
        "confidence": round(random.uniform(0.78, 0.96), 3),
        "risk_factors": risk_factors,
        "model_version": "mock-v1.0",
        "timestamp": "2024-12-06T00:00:00Z"
    }

@app.post("/compliance")
def check_compliance(request: CreditRiskRequest):
    """
    Mock compliance checking endpoint
    Validates document against regulatory requirements
    """
    
    violations = []
    checks_performed = []
    
    # KYC Checks
    checks_performed.append("KYC Documentation")
    if request.age and request.age < 21:
        violations.append({
            "clause": "RBI KYC Guidelines 2.1",
            "issue": "Age below minimum threshold for unsecured loans",
            "severity": "high"
        })
    
    # Income verification
    checks_performed.append("Income Verification")
    if request.job == "unemployed":
        violations.append({
            "clause": "Income Documentation Requirement",
            "issue": "No verifiable income source",
            "severity": "critical"
        })
    
    # Credit amount limits
    checks_performed.append("Credit Limit Compliance")
    if request.credit_amount and request.credit_amount > 1000000:
        violations.append({
            "clause": "Lending Guidelines Section 4.2",
            "issue": "Loan amount exceeds regulatory limit for income bracket",
            "severity": "medium"
        })
    
    # Housing documentation
    checks_performed.append("Address Verification")
    if request.housing == "free":
        violations.append({
            "clause": "Address Proof Requirement",
            "issue": "Unstable address - no ownership/rental documentation",
            "severity": "low"
        })
    
    # Account verification
    checks_performed.append("Bank Account Verification")
    if request.saving_accounts == "none" and request.checking_account == "none":
        violations.append({
            "clause": "Banking Relationship Requirement",
            "issue": "No active bank accounts found",
            "severity": "high"
        })
    
    compliance_score = max(0.0, 1.0 - (len(violations) * 0.15))
    
    return {
        "compliance_score": round(compliance_score, 3),
        "status": "compliant" if compliance_score >= 0.8 else "non_compliant",
        "violations": violations,
        "checks_performed": checks_performed,
        "total_checks": len(checks_performed),
        "passed_checks": len(checks_performed) - len(violations),
        "timestamp": "2024-12-06T00:00:00Z"
    }

@app.post("/crossverify")
def cross_verify(request: Dict):
    """
    Mock cross-verification endpoint
    Verifies consistency of fields across documents
    """
    
    # Extract fields from request
    fields = {
        "age": request.get("age"),
        "gender": request.get("gender"),
        "job": request.get("job"),
        "housing": request.get("housing"),
        "credit_amount": request.get("credit_amount"),
        "duration": request.get("duration")
    }
    
    matches = {}
    discrepancies = []
    
    # Simulate field verification with random confidence
    for field, value in fields.items():
        if value is None:
            matches[field] = "not_provided"
            discrepancies.append({
                "field": field,
                "status": "missing",
                "details": f"{field.upper()} not found in document"
            })
        else:
            rand = random.random()
            if rand < 0.85:  # 85% match rate
                matches[field] = "match"
            elif rand < 0.95:  # 10% partial match
                matches[field] = "partial_match"
                discrepancies.append({
                    "field": field,
                    "status": "partial_match",
                    "details": f"{field.upper()} shows minor discrepancies",
                    "confidence": round(random.uniform(0.5, 0.8), 2)
                })
            else:  # 5% mismatch
                matches[field] = "mismatch"
                discrepancies.append({
                    "field": field,
                    "status": "mismatch",
                    "details": f"{field.upper()} does not match across documents",
                    "severity": "high"
                })
    
    # Calculate overall score
    match_scores = {
        "match": 1.0,
        "partial_match": 0.6,
        "mismatch": 0.0,
        "not_provided": 0.5
    }
    
    valid_matches = [status for status in matches.values() if status != "not_provided"]
    if valid_matches:
        total_score = sum(match_scores[status] for status in valid_matches)
        overall_score = total_score / len(valid_matches)
    else:
        overall_score = 0.0
    
    return {
        "overall_score": round(overall_score, 3),
        "verification_status": "verified" if overall_score >= 0.8 else "failed",
        "matches": matches,
        "discrepancies": discrepancies,
        "confidence": round(random.uniform(0.82, 0.94), 3),
        "documents_compared": len(request.get("document_ids", [])),
        "timestamp": "2024-12-06T00:00:00Z"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "IRIS Credit Risk Mock API",
        "version": "1.0.0",
        "endpoints_available": ["predict", "compliance", "crossverify"]
    }

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("IRIS Credit Risk Mock API Server")
    print("=" * 60)
    print("\n🚀 Starting on http://localhost:5000")
    print("\n📍 Available Endpoints:")
    print("  POST /predict      - Credit risk prediction")
    print("  POST /compliance   - Document compliance check")
    print("  POST /crossverify  - Field cross-verification")
    print("  GET  /health       - Health check")
    print("\n📋 Expected Fields:")
    print("  - age (18-100)")
    print("  - gender (male/female)")
    print("  - job (unemployed/unskilled/skilled/highly skilled)")
    print("  - housing (free/rent/own)")
    print("  - saving_accounts (none/little/moderate/quite rich/rich)")
    print("  - checking_account (none/little/moderate/rich)")
    print("  - credit_amount (positive number)")
    print("  - duration (months, positive integer)")
    print("  - purpose (business/car/education/etc.)")
    print("\n" + "=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)