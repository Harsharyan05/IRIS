# IRIS — Intelligent Risk Insight System

> AI-powered credit risk analysis with blockchain-backed verification for financial institutions

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase)](https://supabase.com/)
[![Ethereum](https://img.shields.io/badge/Ethereum-Sepolia-3C3C3D?logo=ethereum)](https://sepolia.dev/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

---

## Overview

IRIS is a production-grade credit risk analysis platform designed for financial institutions. It automates the end-to-end loan application review process — from document ingestion to regulatory compliance checking — and produces tamper-proof audit trails anchored on the Ethereum blockchain.

**Key capabilities:**
- Automated PDF document ingestion and structured field extraction
- ML-based credit risk scoring with explainability (SHAP heatmaps)
- Regulatory compliance validation (RBI KYC, AML)
- Cross-document field verification to detect inconsistencies
- Comprehensive dossier generation (PDF reports + originals in ZIP)
- Immutable blockchain anchoring on Ethereum Sepolia for audit proof
- Secure Google OAuth authentication via Supabase

---

## Repository Structure

This is a monorepo containing both the Next.js frontend and the FastAPI backend.

```
IRIS/
├── src/                        # Next.js frontend (React 19, TypeScript)
│   ├── app/                    # App Router pages
│   └── components/             # UI components
│
├── main.py                     # FastAPI backend entry point
├── ml_mock.py                  # Mock ML API server (development)
├── requirements.txt            # Python dependencies
├── package.json                # Node.js dependencies
├── next.config.ts              # Next.js configuration
│
├── utils/                      # Backend utilities
│   ├── auth.py                 # JWT verification, user profiles
│   ├── storage.py              # Supabase storage operations
│   ├── extraction.py           # PDF text extraction (pdfplumber)
│   ├── parser.py               # Credit field parsing
│   ├── analysis.py             # ML API integration
│   ├── dossier.py              # PDF report generation (ReportLab)
│   ├── blockchain.py           # Ethereum anchoring
│   ├── cleanup.py              # Privacy data deletion
│   └── audit.py                # Audit logging
│
├── blockchain/                 # Smart contract (Hardhat)
│   ├── contracts/Anchor.sol    # Solidity 0.8.19 anchor contract
│   └── scripts/deploy.js       # Deployment script
│
├── supabase_setup.sql.md       # Database schema and RLS policies
└── .env.example                # Environment variable template
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.8+, Uvicorn |
| Database | PostgreSQL via Supabase |
| Storage | Supabase Storage (private buckets) |
| Auth | Supabase Auth (Google OAuth) |
| ML | Custom ML API (HuggingFace / self-hosted) |
| Blockchain | Ethereum Sepolia, Solidity 0.8.19, Hardhat, ethers.js 6 |
| PDF | pdfplumber (extraction), ReportLab (generation) |

---

## Prerequisites

- Python 3.8+
- Node.js 16+
- A [Supabase](https://supabase.com/) project
- An [Infura](https://infura.io/) or [Alchemy](https://alchemy.com/) RPC endpoint (Sepolia)
- Testnet ETH from [Sepolia Faucet](https://sepoliafaucet.com/)

---

## Getting Started

### 1. Clone and install dependencies

```bash
git clone https://github.com/your-org/IRIS.git
cd IRIS

# Python backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Next.js frontend
npm install

# Blockchain (optional)
cd blockchain && npm install && cd ..
```

### 2. Configure environment

Copy `.env.example` to `.env.local` and fill in your values:

```bash
cp .env.example .env.local
```

Required variables:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_JWT_SECRET=your_jwt_secret

# ML API
ML_BASE_URL=http://localhost:5000   # or your hosted ML endpoint

# Blockchain (Sepolia)
HARDHAT_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
DEPLOYER_PRIVATE_KEY=0xYOUR_PRIVATE_KEY
CONTRACT_ADDRESS=0xYOUR_CONTRACT_ADDRESS
```

### 3. Set up Supabase

1. Open your Supabase project → SQL Editor
2. Run the full contents of `supabase_setup.sql.md`
3. Create three private storage buckets: `documents`, `heatmaps`, `dossiers`
4. Enable Google OAuth under Authentication → Providers

### 4. Run the application

```bash
# Terminal 1 — FastAPI backend
python main.py
# API available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs

# Terminal 2 — Next.js frontend
npm run dev
# UI available at http://localhost:3000

# Terminal 3 — Mock ML API (development only)
python ml_mock.py
# Mock ML at http://localhost:5000
```

---

## API Reference

All endpoints except `/` and `/health` require a JWT bearer token from Supabase Auth.

```
Authorization: Bearer <supabase_jwt_token>
```

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| GET | `/profile` | Get user profile |
| PUT | `/profile` | Update profile / remember_me toggle |
| POST | `/upload` | Upload PDF document |
| GET | `/documents` | List user documents |
| GET | `/documents/{id}` | Get document + signed download URL |
| DELETE | `/documents/{id}` | Delete document and all related data |
| GET | `/analyses` | List all analyses |
| GET | `/analyses/{id}` | Get analysis for a document |
| POST | `/analyze/{id}` | Manually trigger analysis |
| POST | `/crossverify` | Cross-verify multiple documents |
| GET | `/heatmaps` | List SHAP heatmaps |
| POST | `/dossier/generate` | Generate dossier ZIP |
| GET | `/dossiers` | List dossiers |
| POST | `/blockchain/anchor` | Anchor dossier hash on Sepolia |
| GET | `/blockchain/verify/{tx}` | Verify blockchain anchor (public) |
| GET | `/dashboard` | Aggregated dashboard data |
| POST | `/logout` | Logout + optional data deletion |
| GET | `/audit-logs` | User audit log |

Full interactive docs: `http://localhost:8000/docs`

---

## ML API Contract

IRIS expects an external ML service implementing these three endpoints. A mock server (`ml_mock.py`) is provided for development.

### POST /predict

```json
// Request
{ "age": 35, "gender": "male", "job": "skilled", "housing": "own",
  "saving_accounts": "moderate", "checking_account": "little",
  "credit_amount": 50000, "duration": 24, "purpose": "car" }

// Response
{ "prediction": 0, "risk_score": 0.35, "risk_class": "good",
  "risk_factors": ["Low savings"], "confidence": 0.89 }
```

### POST /compliance

Same request shape. Returns `compliance_score`, `status`, and `violations[]`.

### POST /crossverify

Same fields + `document_ids[]`. Returns `overall_score`, `matches{}`, and `discrepancies[]`.

---

## Deployment

### Backend (Render)

1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add all environment variables from `.env.example` in the Render dashboard

### Frontend (Vercel / Render)

```bash
npm run build
```

Deploy the output to Vercel or any static/SSR host. Set `NEXT_PUBLIC_API_URL` to your backend URL.

### Blockchain Contract

```bash
cd blockchain
npx hardhat compile
npx hardhat run scripts/deploy.js --network sepolia
# Copy the deployed address to CONTRACT_ADDRESS in your env
```

---

## Security Notes

- All storage buckets are private; files are accessed via short-lived signed URLs
- Row Level Security (RLS) is enforced at the database level — users can only access their own data
- The `remember_me` toggle controls whether user data is purged on logout
- Blockchain anchoring provides tamper-evident proof of dossier integrity
- Never commit `.env.local` or private keys to version control

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Follow PEP 8 for Python; use TypeScript strict mode for frontend
4. Submit a pull request with a clear description

---

## License

MIT — see [LICENSE](./LICENSE)
