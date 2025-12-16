# 🔍 IRIS - Intelligent Risk Insight System

> AI-powered credit risk analysis with blockchain-backed verification

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase)](https://supabase.com/)
[![Ethereum](https://img.shields.io/badge/Ethereum-Sepolia-3C3C3D?logo=ethereum)](https://sepolia.dev/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python)](https://www.python.org/)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

IRIS is an intelligent credit risk analysis system that processes loan application documents, extracts key information, performs ML-based risk assessment, and provides blockchain-backed proof of analysis.

### What It Does

1. **Document Upload** - Users upload credit application PDFs
2. **Text Extraction** - Automatically extracts text from documents using pdfplumber
3. **Field Parsing** - Extracts structured credit risk fields (age, income, employment, etc.)
4. **ML Risk Analysis** - Predicts credit risk using machine learning models
5. **Compliance Check** - Validates against regulatory requirements
6. **Cross-Verification** - Verifies field consistency across documents
7. **Dossier Generation** - Creates comprehensive PDF reports in ZIP format
8. **Blockchain Anchoring** - Anchors document hashes on Ethereum Sepolia for immutable proof

---

## ✨ Features

### Core Features

- 🤖 **AI-Powered Risk Scoring** - Machine learning models predict credit default probability
- 📄 **Automated Document Processing** - PDF text extraction and field parsing
- ✅ **Compliance Checking** - Validates against RBI KYC, AML regulations
- 🔍 **Cross-Document Verification** - Detects inconsistencies across multiple documents
- 📊 **Visual Heatmaps** - SHAP-based risk factor visualization
- 📦 **Comprehensive Dossiers** - Downloadable ZIP with reports, certificates, and originals
- ⛓️ **Blockchain Verification** - Immutable proof on Ethereum Sepolia testnet
- 🔐 **Secure Authentication** - Google OAuth via Supabase Auth
- 🗑️ **Privacy Controls** - Remember Me toggle with automatic data deletion

### Technical Features

- RESTful API with FastAPI
- PostgreSQL database via Supabase
- Private file storage with signed URLs
- Background task processing
- Audit logging for all actions
- Role-based access control
- CORS support for frontend integration

---

## 🏗️ Architecture

```
┌─────────────┐
│   Frontend  │ (React - Not in this repo)
│   (Web/App) │
└──────┬──────┘
       │ HTTPS/REST
       ▼
┌────────────────────────────────────────┐
│         FastAPI Backend                │
│  ┌────────────┐  ┌─────────────┐       │
│  │   Auth     │  │  Document   │       │
│  │  (Google)  │  │  Processing │       │
│  └────────────┘  └─────────────┘       │
│  ┌────────────┐  ┌─────────────┐       │
│  │  Parser    │  │  ML Client  │       │
│  └────────────┘  └─────────────┘       │
│  ┌────────────┐  ┌─────────────┐       │
│  │  Dossier   │  │ Blockchain  │       │
│  └────────────┘  └─────────────┘       │
└──────┬──────────────────┬──────────────┘
       │                  │
       ▼                  ▼
┌─────────────┐    ┌──────────────┐
│  Supabase   │    │  ML API      │
│  - Auth     │    │  /predict    │
│  - Database │    │  /compliance │
│  - Storage  │    │  /crossverify│
└─────────────┘    └──────────────┘
       │
       ▼
┌─────────────┐    ┌──────────────┐
│ PostgreSQL  │    │  Ethereum    │
│  Database   │    │  Sepolia     │
│             │    │  Testnet     │
└─────────────┘    └──────────────┘
```

### Data Flow

```
1. User uploads PDF
   ↓
2. Backend extracts text (pdfplumber)
   ↓
3. Parser extracts structured fields
   ↓
4. ML API predicts risk/compliance/verification
   ↓
5. Results stored in Supabase
   ↓
6. User generates dossier
   ↓
7. Dossier hash anchored on blockchain
   ↓
8. Verification certificate with TX hash
```

---

## 🛠️ Tech Stack

### Backend

- **Framework:** FastAPI 0.104.1
- **Language:** Python 3.8+
- **Database:** PostgreSQL (Supabase)
- **Storage:** Supabase Storage
- **Authentication:** Supabase Auth (Google OAuth)

### Document Processing

- **PDF Extraction:** pdfplumber
- **Text Parsing:** Regex + NLP patterns
- **Report Generation:** ReportLab

### Blockchain

- **Network:** Ethereum Sepolia Testnet
- **Smart Contract:** Solidity 0.8.19
- **Framework:** Hardhat
- **Library:** ethers.js 6.9.0

### Infrastructure

- **API Server:** Uvicorn (ASGI)
- **Task Queue:** FastAPI BackgroundTasks
- **Logging:** Python logging + Custom audit system

---

## 📦 Prerequisites

### Required Software

- **Python 3.8+**
  ```bash
  python --version  # Should be 3.8 or higher
  ```

- **Node.js 16+** (for blockchain)
  ```bash
  node --version  # Should be 16 or higher
  npm --version
  ```

- **Git**
  ```bash
  git --version
  ```

### Required Accounts (All Free)

1. **Supabase** - https://supabase.com/
2. **Infura** (Ethereum RPC) - https://infura.io/
3. **MetaMask** (for testnet ETH) - https://metamask.io/
4. **Sepolia Faucet** - https://sepoliafaucet.com/

### System Requirements

- **RAM:** 2GB minimum, 4GB recommended
- **Storage:** 500MB for dependencies
- **OS:** Linux, macOS, or Windows (WSL recommended)

---

## 🚀 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/IRIS-Backend.git
cd IRIS-Backend
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Setup Blockchain (Optional for testing)

```bash
cd blockchain
npm install
cd ..
```

---

## ⚙️ Configuration

### Step 1: Create .env File

Create `.env` in the root directory:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_JWT_SECRET=your_jwt_secret

# ML API Configuration
ML_BASE_URL=https://your-ml-api.hf.space
# For local testing: ML_BASE_URL=http://localhost:5000

# Blockchain Configuration (Sepolia Testnet)
HARDHAT_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID
DEPLOYER_PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE
CONTRACT_ADDRESS=0xYOUR_DEPLOYED_CONTRACT_ADDRESS

# Optional: Leave empty to use mock blockchain
# CONTRACT_ADDRESS=
```

### Step 2: Setup Supabase

1. **Create Supabase Project**
   - Go to https://supabase.com/
   - Create new project
   - Copy URL and keys to `.env`

2. **Run Database Setup**
   - Go to Supabase Dashboard → SQL Editor
   - Copy contents of `supabase_setup.sql.md`
   - Run the SQL script

3. **Create Storage Buckets**
   - Go to Storage → Create bucket
   - Create 3 private buckets: `documents`, `heatmaps`, `dossiers`

4. **Enable Google OAuth**
   - Go to Authentication → Providers
   - Enable Google provider
   - Add your site URL in URL Configuration

### Step 3: Setup Blockchain (Optional)

See [BLOCKCHAIN_SETUP.md](./BLOCKCHAIN_SETUP.md) for detailed instructions.

**Quick setup:**

```bash
cd blockchain

# Compile contract
npx hardhat compile

# Deploy to Sepolia (requires testnet ETH)
npx hardhat run scripts/deploy.js --network sepolia

# Copy contract address to .env
```

### Step 4: Setup ML API (Development)

**Option A: Use Mock API**

```bash
# Terminal 1: Start mock ML API
python ml_mock.py
# Runs on http://localhost:5000
```

**Option B: Use Real ML API**
- Update `ML_BASE_URL` in `.env` with your ML API endpoint

---

## 💻 Usage

### Local Development

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start backend
python main.py
```

Server will start at: **[http://localhost:8000](https://iris-backend-o3ph.onrender.com)**

**Swagger Documentation:** [http://localhost:8000](https://iris-backend-o3ph.onrender.com)/docs

### Production (Render)

**Live API:** https://iris-backend-o3ph.onrender.com)

**API Documentation:** https://iris-backend-o3ph.onrender.com/docs

**Note:** Render free tier sleeps after 15 minutes of inactivity. First request after sleep takes ~30 seconds.

### Testing the API

#### 1. Health Check

```bash
# Local
curl http://localhost:8000/health

# Production
curl https://your-app.onrender.com/health
```

#### 2. Upload Document (requires auth token)

```bash
# Local
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@credit_application.pdf"

# Production
curl -X POST https://your-app.onrender.com/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@credit_application.pdf"
```

#### 3. Get Analysis Results

```bash
curl http://localhost:8000/analyses/DOCUMENT_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 4. Generate Dossier

```bash
curl -X POST "http://localhost:8000/dossier/generate?document_id=DOCUMENT_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 5. Anchor on Blockchain

```bash
curl -X POST "http://localhost:8000/blockchain/anchor?dossier_id=DOSSIER_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 📚 API Documentation

### Authentication

All endpoints (except `/health` and `/`) require JWT authentication:

```
Authorization: Bearer <token>
```

Get token from Supabase Auth (Google OAuth).

### Main Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root endpoint |
| `GET` | `/health` | Health check |
| `GET` | `/profile` | Get user profile |
| `POST` | `/upload` | Upload PDF document |
| `GET` | `/documents` | List all documents |
| `GET` | `/documents/{id}` | Get document details |
| `DELETE` | `/documents/{id}` | Delete document |
| `GET` | `/analyses` | List all analyses |
| `GET` | `/analyses/{id}` | Get analysis result |
| `POST` | `/analyze/{id}` | Trigger analysis |
| `POST` | `/crossverify` | Cross-verify documents |
| `POST` | `/dossier/generate` | Generate dossier |
| `GET` | `/dossiers` | List dossiers |
| `POST` | `/blockchain/anchor` | Anchor on blockchain |
| `GET` | `/blockchain/verify/{tx}` | Verify blockchain anchor |
| `GET` | `/dashboard` | Get dashboard data |
| `POST` | `/logout` | Logout user |

**Complete API documentation available at:** http://localhost:8000/docs

---

## 📁 Project Structure

```
IRIS-Backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── .gitignore
├── README.md
├── BLOCKCHAIN_SETUP.md
├── supabase_setup.sql.md  # Database schema
│
├── utils/                  # Core utilities
│   ├── __init__.py
│   ├── auth.py            # Authentication & JWT
│   ├── storage.py         # Supabase storage operations
│   ├── extraction.py      # PDF text extraction
│   ├── parser.py          # Credit field parsing
│   ├── analysis.py        # ML API integration
│   ├── dossier.py         # PDF report generation
│   ├── cleanup.py         # Data deletion logic
│   ├── blockchain.py      # Blockchain integration
│   └── audit.py           # Audit logging
│
├── blockchain/            # Blockchain components
│   ├── package.json
│   ├── hardhat.config.js
│   ├── anchor.js          # Anchoring script
│   ├── contracts/
│   │   └── Anchor.sol     # Smart contract
│   └── scripts/
│       └── deploy.js      # Deployment script
│
├── ml_mock.py             # Mock ML API for testing
└── tests/                 # Test files (optional)
```

---

## 🔧 Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Code Style

```bash
# Install formatting tools
pip install black flake8

# Format code
black .

# Check style
flake8 .
```

### Adding New Features

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes
3. Test thoroughly
4. Commit: `git commit -m "Add: your feature"`
5. Push: `git push origin feature/your-feature`
6. Create Pull Request

### Database Migrations

For schema changes:

1. Update `supabase_setup.sql.md`
2. Run migration in Supabase SQL Editor
3. Document changes in commit message

---

## 🚢 Deployment

### Backend Deployment on Render

✅ **Currently Deployed:** https://your-app.onrender.com

1. **Prepare for deployment:**
   ```bash
   # Ensure all dependencies in requirements.txt
   pip freeze > requirements.txt
   ```

2. **Deploy to Render:**
   - Go to https://render.com
   - Create new Web Service
   - Connect GitHub repository
   - Configure:
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Environment:** Python 3
     - **Plan:** Free (or paid for production)

3. **Add Environment Variables:**
   
   In Render Dashboard → Environment:
   
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_JWT_SECRET=your_jwt_secret
   ML_BASE_URL=https://your-ml-api.hf.space
   HARDHAT_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
   DEPLOYER_PRIVATE_KEY=0xYOUR_PRIVATE_KEY
   CONTRACT_ADDRESS=0xYOUR_CONTRACT_ADDRESS
   ```

4. **Auto-Deploy Setup:**
   - Enable auto-deploy from main branch
   - Every push triggers new deployment
   - Build logs available in dashboard

5. **Health Check:**
   - Render pings: `https://your-app.onrender.com/health`
   - Auto-restarts if unhealthy

### Blockchain Deployment (Mainnet)

⚠️ **Warning:** Deploying to Ethereum mainnet costs real money!

```bash
# Update hardhat.config.js for mainnet
# Get real ETH
# Deploy
npx hardhat run scripts/deploy.js --network mainnet
```

### Environment Variables for Production

**Render Production Settings:**

```env
# Supabase (Production)
SUPABASE_URL=https://prod.supabase.co
SUPABASE_SERVICE_ROLE_KEY=prod_service_key
SUPABASE_ANON_KEY=prod_anon_key
SUPABASE_JWT_SECRET=prod_jwt_secret

# ML API (Production)
ML_BASE_URL=https://its-neev-credit-risk-api.hf.space

# Blockchain (Sepolia Testnet)
HARDHAT_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
DEPLOYER_PRIVATE_KEY=0xYOUR_KEY
CONTRACT_ADDRESS=0xYOUR_CONTRACT

# Optional: Use mainnet for production
# HARDHAT_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
```

**Important for Render:**
- Add all variables in Render Dashboard → Environment
- No `.env` file needed on Render
- Restart service after adding variables

---

## 🤝 Contributing

### Team

- **Backend Engineer** - API, Database, Storage, Blockchain
- **ML Engineer** - Risk models, Compliance checks, Field verification
- **Frontend Engineer** - UI/UX, Dashboard, Document upload

### How to Contribute

1. Fork the repository
2. Create feature branch
3. Make changes
4. Write/update tests
5. Update documentation
6. Submit pull request

### Code Standards

- Follow PEP 8 for Python
- Use type hints
- Write docstrings
- Add comments for complex logic
- Keep functions focused and small

---

## 📊 ML API Specification

Your ML API should implement these endpoints:

### POST /predict

**Input:**
```json
{
  "age": 35,
  "gender": "male",
  "job": "skilled",
  "housing": "own",
  "saving_accounts": "moderate",
  "checking_account": "little",
  "credit_amount": 50000,
  "duration": 24,
  "purpose": "car"
}
```

**Output:**
```json
{
  "prediction": 0,
  "risk_score": 0.35,
  "probability": 0.65,
  "risk_class": "good",
  "risk_factors": ["Low savings", "High credit amount"],
  "confidence": 0.89
}
```

### POST /compliance

Same input format, returns compliance violations.

### POST /crossverify

Same input + `document_ids`, returns field matching results.

---

## 🐛 Troubleshooting

### Common Issues

**1. "Module not found" error**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**2. Supabase connection fails**
```bash
# Check .env variables
# Verify project URL and keys in Supabase dashboard
# Check network connectivity
```

**3. Blockchain anchoring fails**
```bash
# Check testnet ETH balance in MetaMask
# Verify RPC URL is correct
# Try different RPC provider (Alchemy/Ankr)
```

**4. PDF extraction returns empty text**
```bash
# Ensure PDF has selectable text (not scanned image)
# Check pdfplumber installation
# Try different PDF
```

**5. ML API timeout**
```bash
# Check ML_BASE_URL is correct
# Ensure ML API is running
# Increase timeout in utils/analysis.py
```

**6. Render Deployment Issues**

- **Build fails:**
  - Check requirements.txt is up to date
  - Verify Python version (3.8+)
  - Check build logs in Render dashboard

- **Service crashes:**
  - Check environment variables are set
  - Verify Supabase credentials
  - Review logs in Render dashboard

- **Health check fails:**
  - Ensure `/health` endpoint works locally
  - Check if service binds to `0.0.0.0:$PORT`
  - Verify no blocking operations in startup

- **Slow cold starts:**
  - Render free tier sleeps after 15 min inactivity
  - Upgrade to paid plan for always-on service
  - First request after sleep takes ~30 seconds

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI** for the amazing web framework
- **Supabase** for backend-as-a-service
- **Ethereum** for blockchain infrastructure
- **Hardhat** for smart contract development
- **pdfplumber** for PDF text extraction
- **ReportLab** for PDF generation

---

## 📞 Support

- **Documentation:** [http://localhost:8000](https://iris-backend-o3ph.onrender.com)/docs
- **Issues:** GitHub Issues
- **Email:** Shrey_Kumar@outlook.com

---

## 🗺️ Roadmap

### Phase 1 (Current - Hackathon)
- ✅ Core API implementation
- ✅ Document processing
- ✅ ML integration
- ✅ Blockchain anchoring
- ✅ Dossier generation

### Phase 2 (Next)
- [ ] Real ML models (from ML team)
- [ ] Enhanced field parsing
- [ ] Batch processing
- [ ] Email notifications
- [ ] Admin dashboard

### Phase 3 (Future)
- [ ] Mobile app integration
- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] IPFS for decentralized storage
- [ ] Mainnet deployment

---

## 🎯 Quick Start Checklist

### Local Development
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed (for blockchain)
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with Supabase credentials
- [ ] Supabase database setup completed
- [ ] Storage buckets created
- [ ] ML mock API running (optional)
- [ ] Backend server started (`python main.py`)
- [ ] API accessible at http://localhost:8000
- [ ] Swagger docs accessible at http://localhost:8000/docs

### Render Production
- [ ] Render account created
- [ ] GitHub repository connected
- [ ] Web Service created
- [ ] Environment variables added in Render
- [ ] Build completed successfully
- [ ] Service is live
- [ ] Health check passes
- [ ] API accessible at https://your-app.onrender.com
- [ ] Swagger docs accessible at https://your-app.onrender.com/docs
- [ ] Frontend connected to production API

---

**Made with ❤️ for the LOVE of it**

⭐ Star this repo if you found it helpful!
