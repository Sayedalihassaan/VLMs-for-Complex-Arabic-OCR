# Quick Start Guide

Get up and running with Document Analyzer in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- OpenRouter API key ([Sign up here](https://openrouter.ai/))

## Installation

### Step 1: Setup
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create necessary directories
- Copy .env template

### Step 2: Configure API Key

Edit `.env` file:
```bash
nano .env  # or use your favorite editor
```

Add your OpenRouter API key:
```env
OPENAI_API_KEY=sk-or-v1-your-actual-key-here
```

Save and close.

### Step 3: Run Backend

Terminal 1:
```bash
source venv/bin/activate
./run_backend.sh
```

Wait for: "Application startup complete"

### Step 4: Run Frontend

Terminal 2:
```bash
source venv/bin/activate  
./run_frontend.sh
```

Browser will open automatically at http://localhost:8501

## Using the Application

1. **Upload**: Drag and drop a PDF or image
2. **Analyze**: Click "Analyze Document"
3. **View Results**: Browse extracted data in tabs
4. **Download**: Export results as JSON

## Docker Quick Start

```bash
# 1. Configure
cp .env.example .env
# Edit .env with your API key

# 2. Run
docker-compose up -d

# 3. Access
# Frontend: http://localhost:8501
# API: http://localhost:8000/docs
```

## Troubleshooting

**"OPENAI_API_KEY not found"**
→ Make sure you edited `.env` with your actual API key

**"Backend is not running"**  
→ Start backend first in a separate terminal

**"pdf2image requires poppler"**  
→ Install poppler: `brew install poppler` (macOS) or `sudo apt-get install poppler-utils` (Ubuntu)

**API Disconnected in frontend**  
→ Check backend is running: `curl http://localhost:8000/health`

## Next Steps

- See [README.md](README.md) for full documentation
- API documentation: http://localhost:8000/docs
- Adjust settings in `.env` file

## Example Document

Try with a sample document to test the system:
- Government letters
- Invoices or receipts
- Contracts
- Reports with tables and charts

The system works best with:
- Arabic official documents
- PDFs with clear text
- Documents with structured layout
- Single or multi-page PDFs

## Support

Check the troubleshooting section in README.md for common issues.
