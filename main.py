"""
IRIS Backend - Complete Implementation
FastAPI + Supabase + ML + Blockchain
"""

from fastapi import FastAPI, UploadFile, File, Header, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Import all utilities
from utils.auth import verify_token, get_user_profile
from utils.storage import (
    upload_document_to_supabase, 
    create_signed_url_for_path,
    remove_storage_paths
)
from utils.extraction import extract_and_store_texts
from utils.analysis import run_full_analysis_background, call_ml
from utils.dossier import generate_and_upload_dossier
from utils.cleanup import delete_user_data_on_logout
from utils.blockchain import anchor_dossier_on_chain
from utils.audit import log_action

load_dotenv()

app = FastAPI(
    title="IRIS - Intelligent Risk Insight System",
    description="AI-powered risk analysis with blockchain verification",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class CrossVerifyRequest(BaseModel):
    document_ids: List[str]

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    remember_me: Optional[bool] = None

# ==================== STARTUP/HEALTH ====================

@app.on_event("startup")
async def startup_validation():
    """Validate environment variables on startup"""
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_ANON_KEY",
        "SUPABASE_JWT_SECRET",
        "ML_BASE_URL"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
    
    print("✓ IRIS Backend started successfully")
    print(f"✓ ML API configured at: {os.getenv('ML_BASE_URL')}")

@app.get("/")
def home():
    """Root endpoint"""
    return {
        "status": "online",
        "service": "IRIS Backend",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Quick ML API check
        ml_url = os.getenv("ML_BASE_URL")
        ml_healthy = True
        try:
            import requests
            resp = requests.get(f"{ml_url}/", timeout=2)
            ml_healthy = resp.status_code == 200
        except:
            ml_healthy = False
        
        return {
            "status": "healthy",
            "ml_api": "connected" if ml_healthy else "disconnected",
            "database": "connected",
            "storage": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# ==================== USER PROFILE ====================

@app.get("/profile")
def get_profile(Authorization: str = Header(None)):
    """Get user profile"""
    try:
        user_id = verify_token(Authorization)
        profile = get_user_profile(user_id)
        return profile
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.put("/profile")
def update_profile(body: ProfileUpdateRequest, Authorization: str = Header(None)):
    """Update user profile"""
    try:
        user_id = verify_token(Authorization)
        
        from utils.auth import supabase
        update_data = {}
        if body.name is not None:
            update_data['name'] = body.name
        if body.remember_me is not None:
            update_data['remember_me'] = body.remember_me
        
        result = supabase.table("profiles").update(update_data).eq("id", user_id).execute()
        
        log_action(user_id, "update_profile", "profiles", user_id, update_data)
        
        return {"success": True, "profile": result.data[0] if result.data else {}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== DOCUMENT MANAGEMENT ====================

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...), 
    Authorization: str = Header(None), 
    background: BackgroundTasks = None
):
    """Upload a document and trigger background analysis"""
    try:
        # Verify authentication
        user_id = verify_token(Authorization)
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Check file size (max 10MB)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        await file.seek(0)  # Reset file pointer
        
        # Upload to storage
        document_id, storage_path = await upload_document_to_supabase(file, user_id)
        
        # Log upload
        log_action(user_id, "upload", "documents", document_id, {"filename": file.filename})
        
        # Schedule background analysis
        background.add_task(run_full_analysis_background, document_id, user_id, storage_path)
        
        return {
            "success": True,
            "document_id": document_id,
            "filename": file.filename,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/documents")
def list_documents(Authorization: str = Header(None)):
    """List all documents for the authenticated user"""
    try:
        user_id = verify_token(Authorization)
        
        from utils.auth import supabase
        result = supabase.table("documents").select(
            "id, filename, status, sha256, created_at"
        ).eq("user_id", user_id).order("created_at", desc=True).execute()
        
        return {
            "success": True,
            "documents": result.data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{document_id}")
def get_document(document_id: str, Authorization: str = Header(None)):
    """Get specific document details"""
    try:
        user_id = verify_token(Authorization)
        
        from utils.auth import supabase
        result = supabase.table("documents").select("*").eq(
            "id", document_id
        ).eq("user_id", user_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = result.data[0]
        
        # Generate signed URL for download
        if document.get('storage_path'):
            document['download_url'] = create_signed_url_for_path(
                "documents", 
                document['storage_path']
            )
        
        return {
            "success": True,
            "document": document
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}")
def delete_document(document_id: str, Authorization: str = Header(None)):
    """Delete a specific document and all related data"""
    try:
        user_id = verify_token(Authorization)
        
        from utils.auth import supabase
        
        # Get document
        doc_result = supabase.table("documents").select("storage_path").eq(
            "id", document_id
        ).eq("user_id", user_id).execute()
        
        if not doc_result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        storage_path = doc_result.data[0]['storage_path']
        
        # Delete from storage
        if storage_path:
            remove_storage_paths("documents", [storage_path])
        
        # Delete related data (cascading)
        supabase.table("extracted_texts").delete().eq("document_id", document_id).execute()
        supabase.table("analyses").delete().eq("document_id", document_id).execute()
        supabase.table("dossiers").delete().eq("document_id", document_id).execute()
        
        # Delete document
        supabase.table("documents").delete().eq("id", document_id).execute()
        
        log_action(user_id, "delete_document", "documents", document_id)
        
        return {"success": True, "message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYSIS ENDPOINTS ====================

@app.get("/analyses")
def list_analyses(Authorization: str = Header(None)):
    """Get all analyses for the authenticated user"""
    try:
        user_id = verify_token(Authorization)
        
        from utils.auth import supabase
        result = supabase.table("analyses").select(
            "id, document_id, risk, compliance, crossverify, created_at"
        ).eq("user_id", user_id).order("created_at", desc=True).execute()
        
        # Format response to match specification
        formatted = []
        for analysis in result.data:
            if analysis.get('risk'):
                formatted.append({
                    "id": analysis['id'],
                    "document_id": analysis['document_id'],
                    "analysis_type": "risk",
                    "result": analysis['risk'],
                    "score": analysis['risk'].get('risk_score'),
                    "created_at": analysis['created_at']
                })
            if analysis.get('compliance'):
                formatted.append({
                    "id": analysis['id'],
                    "document_id": analysis['document_id'],
                    "analysis_type": "compliance",
                    "result": analysis['compliance'],
                    "score": analysis['compliance'].get('compliance_score'),
                    "created_at": analysis['created_at']
                })
            if analysis.get('crossverify'):
                formatted.append({
                    "id": analysis['id'],
                    "document_id": analysis['document_id'],
                    "analysis_type": "crossverify",
                    "result": analysis['crossverify'],
                    "score": analysis['crossverify'].get('overall_score'),
                    "created_at": analysis['created_at']
                })
        
        return {
            "success": True,
            "analyses": formatted
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyses/{document_id}")
def get_analysis(document_id: str, Authorization: str = Header(None)):
    """Get analysis for a specific document"""
    try:
        user_id = verify_token(Authorization)
        
        from utils.auth import supabase
        result = supabase.table("analyses").select("*").eq(
            "document_id", document_id
        ).eq("user_id", user_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "success": True,
            "analysis": result.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/{document_id}")
async def trigger_analysis(
    document_id: str, 
    Authorization: str = Header(None),
    background: BackgroundTasks = None
):
    """Manually trigger analysis for a document"""
    try:
        user_id = verify_token(Authorization)
        
        from utils.auth import supabase
        doc = supabase.table("documents").select("storage_path").eq(
            "id", document_id
        ).eq("user_id", user_id).execute()
        
        if not doc.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        storage_path = doc.data[0]['storage_path']
        
        # Schedule analysis
        background.add_task(run_full_analysis_background, document_id, user_id, storage_path)
        
        log_action(user_id, "trigger_analysis", "analyses", document_id)
        
        return {
            "success": True,
            "message": "Analysis started",
            "document_id": document_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/crossverify")
def cross_verify_documents(body: CrossVerifyRequest, Authorization: str = Header(None)):
    """Cross-verify multiple documents"""
    try:
        user_id = verify_token(Authorization)
        
        if len(body.document_ids) < 2:
            raise HTTPException(
                status_code=400, 
                detail="At least 2 documents required for cross-verification"
            )
        
        # Verify all documents belong to user
        from utils.auth import supabase
        docs = supabase.table("documents").select("id, status").eq(
            "user_id", user_id
        ).in_("id", body.document_ids).execute()
        
        if len(docs.data) != len(body.document_ids):
            raise HTTPException(status_code=404, detail="One or more documents not found")
        
        # Check if all documents have been analyzed
        incomplete = [d for d in docs.data if d['status'] != 'done']
        if incomplete:
            raise HTTPException(
                status_code=400,
                detail="All documents must be analyzed before cross-verification"
            )
        
        # Get parsed fields from first document's analysis
        primary_doc_id = body.document_ids[0]
        analysis = supabase.table("analyses").select("risk").eq(
            "document_id", primary_doc_id
        ).execute()
        
        if not analysis.data or not analysis.data[0].get('risk'):
            raise HTTPException(
                status_code=400,
                detail="Primary document analysis not found"
            )
        
        parsed_fields = analysis.data[0]['risk'].get('parsed_fields', {})
        
        if not parsed_fields:
            raise HTTPException(
                status_code=400,
                detail="No parsed fields found in primary document"
            )
        
        # Call ML API for cross-verification with fields + document_ids
        from utils.analysis import call_cross_verification
        result = call_cross_verification(parsed_fields, body.document_ids)
        
        # Store cross-verify result in primary document's analysis
        supabase.table("analyses").update({
            "crossverify": result
        }).eq("document_id", primary_doc_id).execute()
        
        log_action(user_id, "crossverify", "analyses", None, {"document_ids": body.document_ids})
        
        return {
            "success": True,
            "matches": result.get("matches", {}),
            "overall_score": result.get("overall_score", 0),
            "verification_status": result.get("verification_status", "unknown"),
            "discrepancies": result.get("discrepancies", []),
            "details": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ==================== HEATMAP ENDPOINTS ====================

@app.get("/heatmaps")
def list_heatmaps(Authorization: str = Header(None)):
    """Get all heatmaps for user"""
    try:
        user_id = verify_token(Authorization)
        
        from utils.auth import supabase
        result = supabase.table("heatmaps").select("*").eq("user_id", user_id).execute()
        
        # Generate signed URLs
        for heatmap in result.data:
            if heatmap.get('heatmap_path'):
                heatmap['heatmap_url'] = create_signed_url_for_path(
                    "heatmaps",
                    heatmap['heatmap_path']
                )
        
        return {
            "success": True,
            "heatmaps": result.data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== DOSSIER ENDPOINTS ====================

@app.post("/dossier/generate")
def generate_dossier(document_id: str = None, Authorization: str = Header(None)):
    """Generate comprehensive dossier for a document"""
    try:
        user_id = verify_token(Authorization)
        
        if not document_id:
            raise HTTPException(status_code=400, detail="document_id is required")
        
        # Verify document exists and belongs to user
        from utils.auth import supabase
        doc = supabase.table("documents").select("id, status").eq(
            "id", document_id
        ).eq("user_id", user_id).execute()
        
        if not doc.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if doc.data[0]['status'] != 'done':
            raise HTTPException(
                status_code=400, 
                detail="Document analysis not complete. Please wait for analysis to finish."
            )
        
        # Generate dossier
        dossier_url, sha256, dossier_id = generate_and_upload_dossier(document_id, user_id)
        
        log_action(user_id, "generate_dossier", "dossiers", dossier_id)
        
        return {
            "success": True,
            "dossier_id": dossier_id,
            "dossier_url": dossier_url,
            "sha256": sha256
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dossiers")
def list_dossiers(Authorization: str = Header(None)):
    """List all dossiers for user"""
    try:
        user_id = verify_token(Authorization)
        
        from utils.auth import supabase
        result = supabase.table("dossiers").select("*").eq("user_id", user_id).execute()
        
        return {
            "success": True,
            "dossiers": result.data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== BLOCKCHAIN ENDPOINTS ====================

@app.post("/blockchain/anchor")
def anchor_on_blockchain(dossier_id: str = None, Authorization: str = Header(None)):
    """Anchor dossier hash on Sepolia blockchain"""
    try:
        user_id = verify_token(Authorization)
        
        if not dossier_id:
            raise HTTPException(status_code=400, detail="dossier_id is required")
        
        # Verify dossier belongs to user
        from utils.auth import supabase
        dossier = supabase.table("dossiers").select("sha256").eq(
            "id", dossier_id
        ).eq("user_id", user_id).execute()
        
        if not dossier.data:
            raise HTTPException(status_code=404, detail="Dossier not found")
        
        # Anchor on blockchain
        tx_hash, explorer_url = anchor_dossier_on_chain(dossier_id, user_id)
        
        log_action(user_id, "blockchain_anchor", "blockchain_certificates", None, {
            "dossier_id": dossier_id,
            "tx_hash": tx_hash
        })
        
        return {
            "success": True,
            "tx_hash": tx_hash,
            "explorer_url": explorer_url,
            "message": "Dossier successfully anchored on Sepolia blockchain"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/blockchain/verify/{tx_hash}")
def verify_blockchain_anchor(tx_hash: str):
    """Verify a blockchain anchor (public endpoint)"""
    try:
        from utils.auth import supabase
        result = supabase.table("blockchain_certificates").select(
            "dossier_hash, tx_hash, explorer_url, created_at"
        ).eq("tx_hash", tx_hash).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Anchor not found")
        
        return {
            "success": True,
            "verified": True,
            "certificate": result.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== DASHBOARD ENDPOINT ====================

@app.get("/dashboard")
def get_dashboard_data(Authorization: str = Header(None)):
    """Get all dashboard data in one call"""
    try:
        user_id = verify_token(Authorization)
        
        from utils.auth import supabase
        
        # Get all user data
        documents = supabase.table("documents").select("*").eq("user_id", user_id).execute()
        analyses = supabase.table("analyses").select("*").eq("user_id", user_id).execute()
        heatmaps = supabase.table("heatmaps").select("*").eq("user_id", user_id).execute()
        dossiers = supabase.table("dossiers").select("*").eq("user_id", user_id).execute()
        
        # Generate signed URLs for heatmaps
        for heatmap in heatmaps.data:
            if heatmap.get('heatmap_path'):
                heatmap['heatmap_url'] = create_signed_url_for_path(
                    "heatmaps",
                    heatmap['heatmap_path']
                )
        
        # Calculate summary statistics
        total_documents = len(documents.data)
        completed_analyses = len([d for d in documents.data if d.get('status') == 'done'])
        avg_risk_score = None
        
        if analyses.data:
            risk_scores = [a['risk'].get('risk_score', 0) for a in analyses.data if a.get('risk')]
            if risk_scores:
                avg_risk_score = sum(risk_scores) / len(risk_scores)
        
        return {
            "success": True,
            "summary": {
                "total_documents": total_documents,
                "completed_analyses": completed_analyses,
                "average_risk_score": avg_risk_score,
                "total_dossiers": len(dossiers.data)
            },
            "documents": documents.data,
            "analyses": analyses.data,
            "heatmaps": heatmaps.data,
            "dossiers": dossiers.data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== AUTH & LOGOUT ====================

@app.post("/logout")
def logout(Authorization: str = Header(None)):
    """Logout and optionally delete user data based on remember_me setting"""
    try:
        user_id = verify_token(Authorization)
        
        # Delete user data if remember_me is False
        deleted = delete_user_data_on_logout(user_id)
        
        return {
            "success": True,
            "message": "Logged out successfully",
            "data_deleted": deleted
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== AUDIT LOGS ====================

@app.get("/audit-logs")
def get_audit_logs(Authorization: str = Header(None), limit: int = 50):
    """Get user's audit logs (admin/debugging)"""
    try:
        user_id = verify_token(Authorization)
        
        from utils.auth import supabase
        result = supabase.table("audit_logs").select("*").eq(
            "user_id", user_id
        ).order("created_at", desc=True).limit(limit).execute()
        
        return {
            "success": True,
            "logs": result.data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)