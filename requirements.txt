# IRIS — System Requirements

## 1. Purpose

IRIS (Intelligent Risk Insight System) is a credit risk analysis platform for financial institutions. It automates the review of loan application documents, produces ML-driven risk assessments, validates regulatory compliance, and generates tamper-proof audit dossiers anchored on the Ethereum blockchain.

---

## 2. Functional Requirements

### 2.1 Authentication & User Management

| ID | Requirement |
|---|---|
| AUTH-01 | Users must authenticate via Google OAuth through Supabase Auth |
| AUTH-02 | All API endpoints except `/` and `/health` must require a valid JWT |
| AUTH-03 | User profiles must be created automatically on first login |
| AUTH-04 | Users must be able to toggle a `remember_me` preference |
| AUTH-05 | On logout with `remember_me = false`, all user data must be permanently deleted |

### 2.2 Document Management

| ID | Requirement |
|---|---|
| DOC-01 | Users must be able to upload PDF documents up to 10 MB |
| DOC-02 | Only PDF files are accepted; other formats must be rejected with a 400 error |
| DOC-03 | Each uploaded document must be stored in a private Supabase Storage bucket |
| DOC-04 | A SHA-256 hash must be computed and stored for every uploaded document |
| DOC-05 | Documents must have a lifecycle status: `uploaded → processing → done / failed` |
| DOC-06 | Users must be able to list, retrieve, and delete their own documents |
| DOC-07 | Deleting a document must cascade to all related analyses, heatmaps, and dossiers |
| DOC-08 | Download URLs must be short-lived signed URLs, not permanent public links |

### 2.3 Document Processing & Analysis

| ID | Requirement |
|---|---|
| PROC-01 | Text extraction must begin automatically after upload as a background task |
| PROC-02 | The system must extract text from all pages of a PDF using pdfplumber |
| PROC-03 | Extracted text must be stored per page in the `extracted_texts` table |
| PROC-04 | The parser must extract structured credit fields: age, gender, job, housing, saving accounts, checking account, credit amount, duration, and purpose |
| PROC-05 | Parsed fields must be submitted to the ML API for risk prediction |
| PROC-06 | Parsed fields must be submitted to the ML API for compliance checking |
| PROC-07 | Analysis results (risk, compliance) must be stored as JSONB in the `analyses` table |
| PROC-08 | A SHAP-based risk heatmap must be generated and stored in the `heatmaps` bucket |
| PROC-09 | Analysis must be re-triggerable manually via `POST /analyze/{id}` |

### 2.4 Cross-Document Verification

| ID | Requirement |
|---|---|
| CROSS-01 | Users must be able to submit two or more document IDs for cross-verification |
| CROSS-02 | All submitted documents must belong to the authenticated user |
| CROSS-03 | All submitted documents must have status `done` before cross-verification |
| CROSS-04 | The system must call the ML `/crossverify` endpoint with parsed fields and document IDs |
| CROSS-05 | Cross-verification results must include per-field match status and a list of discrepancies |
| CROSS-06 | Results must be stored in the `crossverify` JSONB column of the primary document's analysis |

### 2.5 Dossier Generation

| ID | Requirement |
|---|---|
| DOS-01 | A dossier can only be generated for documents with status `done` |
| DOS-02 | The dossier must include: a PDF risk summary report, compliance certificate, SHAP heatmap, and the original document |
| DOS-03 | All dossier contents must be packaged into a single ZIP file |
| DOS-04 | The ZIP must be uploaded to the private `dossiers` Supabase Storage bucket |
| DOS-05 | A SHA-256 hash of the ZIP must be computed and stored |
| DOS-06 | Users must be able to list all their generated dossiers |

### 2.6 Blockchain Anchoring

| ID | Requirement |
|---|---|
| BC-01 | Users must be able to anchor a dossier's SHA-256 hash on the Ethereum Sepolia testnet |
| BC-02 | The anchor transaction hash and Etherscan explorer URL must be stored in `blockchain_certificates` |
| BC-03 | Blockchain anchoring must not block dossier generation — it is a separate, optional step |
| BC-04 | Any party must be able to verify an anchor by querying `GET /blockchain/verify/{tx_hash}` without authentication |

### 2.7 Dashboard & Reporting

| ID | Requirement |
|---|---|
| DASH-01 | The dashboard endpoint must return documents, analyses, heatmaps, and dossiers in a single call |
| DASH-02 | The dashboard must include summary statistics: total documents, completed analyses, average risk score, total dossiers |
| DASH-03 | Heatmap responses must include signed download URLs |

### 2.8 Audit Logging

| ID | Requirement |
|---|---|
| AUDIT-01 | All significant actions must be logged: upload, delete, analyze, generate dossier, blockchain anchor, logout |
| AUDIT-02 | Audit logs must be write-only for the service role; users may read their own logs |
| AUDIT-03 | Users must be able to retrieve their own audit log via `GET /audit-logs` |

---

## 3. Non-Functional Requirements

### 3.1 Security

| ID | Requirement |
|---|---|
| SEC-01 | Row Level Security (RLS) must be enforced at the database layer for all tables |
| SEC-02 | File storage must use private buckets with signed URL access only |
| SEC-03 | Private keys and API secrets must never be committed to version control |
| SEC-04 | CORS must be restricted to known frontend origins in production |
| SEC-05 | JWT tokens must be verified on every authenticated request |

### 3.2 Performance

| ID | Requirement |
|---|---|
| PERF-01 | Document analysis must run as a background task and not block the upload response |
| PERF-02 | The `/health` endpoint must respond within 3 seconds |
| PERF-03 | The `/dashboard` endpoint must aggregate all user data in a single database round-trip per table |

### 3.3 Reliability

| ID | Requirement |
|---|---|
| REL-01 | The backend must validate all required environment variables at startup and fail fast if any are missing |
| REL-02 | Blockchain anchoring failures must not affect dossier availability |
| REL-03 | Document status must be set to `failed` if background analysis encounters an unrecoverable error |

### 3.4 Scalability

| ID | Requirement |
|---|---|
| SCALE-01 | The FastAPI backend must be stateless to support horizontal scaling |
| SCALE-02 | The ML API must be independently deployable and replaceable without backend changes |

### 3.5 Compliance & Privacy

| ID | Requirement |
|---|---|
| COMP-01 | The system must validate loan applications against RBI KYC guidelines |
| COMP-02 | The system must check for AML (Anti-Money Laundering) compliance violations |
| COMP-03 | User data deletion on logout must be complete and cascading across all tables and storage buckets |
| COMP-04 | Blockchain certificates must be publicly verifiable to support third-party audit requirements |

---

## 4. ML API Contract

The ML service is an external dependency. It must implement the following interface:

### POST /predict

**Input fields:** `age`, `gender`, `job`, `housing`, `saving_accounts`, `checking_account`, `credit_amount`, `duration`, `purpose`

**Required output fields:** `prediction` (0/1), `risk_score` (0.0–1.0), `risk_class` (`good`/`bad`), `risk_factors` (string[]), `confidence` (0.0–1.0)

### POST /compliance

Same input. Required output: `compliance_score` (0.0–1.0), `status` (`compliant`/`non_compliant`), `violations` (object[])

### POST /crossverify

Same input + `document_ids` (string[]). Required output: `overall_score` (0.0–1.0), `verification_status` (`verified`/`failed`), `matches` (object), `discrepancies` (object[])

---

## 5. Infrastructure Requirements

| Component | Requirement |
|---|---|
| Python | 3.8 or higher |
| Node.js | 16 or higher (blockchain tooling) |
| Supabase | PostgreSQL database, Auth, Storage (3 private buckets: `documents`, `heatmaps`, `dossiers`) |
| Ethereum RPC | Infura or Alchemy endpoint for Sepolia testnet |
| Deployment | Backend: Render (or equivalent); Frontend: Vercel (or equivalent) |

---

## 6. Out of Scope

- Mainnet Ethereum deployment (Sepolia testnet only for current release)
- Batch document processing
- Mobile native applications
- IPFS or decentralized storage
- Multi-language document support
- Email or push notifications
