# IRIS — System Architecture

## Overview

IRIS is a monorepo containing a Next.js frontend and a FastAPI backend. The system is designed for financial institutions to automate credit risk assessment with a full audit trail anchored on the Ethereum blockchain.

---

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│              Next.js 15 / React 19 (TypeScript)              │
│         Dashboard · Document Upload · Risk Reports           │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTPS / REST
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                      │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │    Auth     │  │   Document   │  │     Analysis       │  │
│  │  (JWT/OAuth)│  │  Processing  │  │  (ML + Compliance) │  │
│  └─────────────┘  └──────────────┘  └────────────────────┘  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │   Dossier   │  │  Blockchain  │  │    Audit Logger    │  │
│  │  Generator  │  │   Anchoring  │  │                    │  │
│  └─────────────┘  └──────────────┘  └────────────────────┘  │
└──────┬──────────────────┬───────────────────┬────────────────┘
       │                  │                   │
       ▼                  ▼                   ▼
┌─────────────┐   ┌──────────────┐   ┌──────────────────┐
│  Supabase   │   │   ML API     │   │ Ethereum Sepolia  │
│  - Auth     │   │  /predict    │   │  Anchor Contract  │
│  - Database │   │  /compliance │   │  (Solidity 0.8)   │
│  - Storage  │   │  /crossverify│   └──────────────────┘
└─────────────┘   └──────────────┘
```

---

## Component Breakdown

### Frontend — Next.js 15

Built with the App Router, React 19, Tailwind CSS, and shadcn/ui components.

| Component | Responsibility |
|---|---|
| Dashboard | Aggregated view of documents, risk scores, dossiers |
| Document Upload | Drag-and-drop PDF upload with status polling |
| Analysis View | Risk score, SHAP heatmap, compliance violations |
| Dossier Manager | Generate, download, and blockchain-anchor dossiers |
| Auth | Google OAuth flow via Supabase |

### Backend — FastAPI

Stateless REST API. All persistent state lives in Supabase.

| Module | Responsibility |
|---|---|
| `main.py` | Route definitions, CORS, startup validation |
| `utils/auth.py` | JWT verification, Supabase user profile management |
| `utils/storage.py` | Upload/download/delete from Supabase Storage |
| `utils/extraction.py` | PDF text extraction using pdfplumber |
| `utils/parser.py` | Regex + NLP field extraction from raw text |
| `utils/analysis.py` | HTTP client for ML API (predict, compliance, crossverify) |
| `utils/dossier.py` | ReportLab PDF generation, ZIP packaging |
| `utils/blockchain.py` | ethers.js subprocess call for Sepolia anchoring |
| `utils/cleanup.py` | Cascading data deletion on logout |
| `utils/audit.py` | Append-only audit log writes |

### ML Service

An external HTTP service (HuggingFace Spaces or self-hosted). IRIS communicates with it over REST. A local mock (`ml_mock.py`) is provided for development.

| Endpoint | Purpose |
|---|---|
| `POST /predict` | Credit risk score + risk factors |
| `POST /compliance` | Regulatory compliance check (RBI KYC, AML) |
| `POST /crossverify` | Field consistency check across documents |

### Blockchain — Ethereum Sepolia

A minimal Solidity smart contract (`Anchor.sol`) stores SHA-256 hashes of dossiers on-chain. The backend calls an `anchor.js` script via subprocess using ethers.js 6.

```
Dossier ZIP → SHA-256 hash → Anchor.sol.store(hash) → tx_hash stored in DB
```

---

## Data Flow

### Document Processing Pipeline

```
1. User uploads PDF via frontend
        ↓
2. FastAPI validates file (type, size ≤ 10MB)
        ↓
3. File stored in Supabase Storage (documents bucket)
        ↓
4. Background task triggered (FastAPI BackgroundTasks)
        ↓
5. pdfplumber extracts raw text per page → stored in extracted_texts
        ↓
6. Parser extracts structured fields (age, income, job, etc.)
        ↓
7. ML API called: /predict → risk score + factors
8. ML API called: /compliance → violations
        ↓
9. SHAP heatmap generated → stored in heatmaps bucket
        ↓
10. Analysis record written to analyses table
        ↓
11. Document status updated to 'done'
```

### Dossier & Blockchain Flow

```
1. User requests dossier generation
        ↓
2. ReportLab generates PDF report (risk summary, compliance, heatmap)
        ↓
3. ZIP created: report.pdf + certificates + original document
        ↓
4. ZIP uploaded to Supabase Storage (dossiers bucket)
        ↓
5. SHA-256 hash of ZIP computed
        ↓
6. User requests blockchain anchoring
        ↓
7. anchor.js called → hash stored in Anchor.sol on Sepolia
        ↓
8. tx_hash + explorer URL stored in blockchain_certificates table
        ↓
9. Verification certificate issued to user
```

---

## Database Schema

All tables use UUID primary keys and enforce Row Level Security (RLS). Users can only access their own rows.

```
auth.users (Supabase managed)
    └── profiles          (id, email, name, remember_me)
    └── documents         (id, user_id, filename, storage_path, sha256, status)
        └── extracted_texts  (id, document_id, user_id, page_number, text)
        └── analyses         (id, document_id, user_id, risk JSONB, compliance JSONB, crossverify JSONB)
            └── heatmaps     (id, analysis_id, user_id, heatmap_path, caption)
        └── dossiers         (id, document_id, user_id, dossier_url, sha256)
            └── blockchain_certificates  (id, dossier_id, user_id, dossier_hash, tx_hash, explorer_url)
    └── audit_logs        (id, user_id, action, target_table, target_id, metadata)
```

Key design decisions:
- `analyses.risk`, `analyses.compliance`, `analyses.crossverify` are JSONB — flexible ML output without schema migrations
- `blockchain_certificates` is publicly readable by `tx_hash` for third-party verification
- `audit_logs` is write-only for the service role — users can read their own logs but cannot modify them

---

## Security Architecture

| Concern | Mechanism |
|---|---|
| Authentication | Supabase Auth (Google OAuth), JWT verification on every request |
| Authorization | Row Level Security (RLS) at the database layer |
| File access | Private storage buckets, short-lived signed URLs |
| Data privacy | `remember_me = false` triggers full data deletion on logout |
| Audit trail | Append-only `audit_logs` table, blockchain anchoring for dossiers |
| Secrets | Environment variables only, never committed to VCS |

---

## Deployment Architecture

```
                    ┌─────────────────┐
                    │   Vercel / CDN  │
                    │  (Next.js SSR)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Render.com     │
                    │  (FastAPI)      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌─────────────┐ ┌──────────┐ ┌──────────────┐
       │  Supabase   │ │  ML API  │ │   Ethereum   │
       │  (managed)  │ │  (HF /  │ │   Sepolia    │
       │             │ │  custom) │ │   Testnet    │
       └─────────────┘ └──────────┘ └──────────────┘
```

- The FastAPI backend is stateless and horizontally scalable
- Supabase handles auth, database, and file storage
- The ML API is independently deployable and swappable
- Blockchain anchoring is fire-and-forget; failures don't block dossier generation
