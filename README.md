# 📄 Document Analyzer - Production Ready

A complete end-to-end document analysis system using AI to extract structured data from documents (PDFs and images). Built with FastAPI backend and Streamlit frontend.

## 🌟 Features

- **Multi-format Support**: Process PDFs, JPG, PNG images
- **AI-Powered Extraction**: Uses OpenRouter's Gemini 3 Flash Preview model
- **Comprehensive Schema**: Extracts 100+ data points including:
  - Document classification and metadata
  - Dates, signatures, and official marks
  - Tables, charts, and financial data
  - Legal articles and references
  - Full text with original script preservation
- **Professional UI**: Clean, responsive Streamlit interface
- **REST API**: Full FastAPI backend with async processing
- **Production Ready**: Docker support, logging, error handling

## 📋 Prerequisites

- Python 3.11+
- OpenRouter API key ([Get one here](https://openrouter.ai/))
- (Optional) Docker & Docker Compose
- poppler-utils (for PDF processing)

### Install poppler-utils

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**Windows:**
Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases/)

## 🚀 Quick Start (Local)

### 1. Clone and Setup

```bash
cd document-analyzer
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your OpenRouter API key:
```env
OPENAI_API_KEY=sk-or-v1-your-api-key-here
OPENAI_BASE_URL=https://openrouter.ai/api/v1
MODEL_ID=google/gemini-3-flash-preview
```

### 3. Run Backend

In terminal 1:
```bash
chmod +x run_backend.sh
./run_backend.sh
```

Or manually:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python backend/main.py
```

Backend will start at: http://localhost:8000

### 4. Run Frontend

In terminal 2:
```bash
chmod +x run_frontend.sh
./run_frontend.sh
```

Or manually:
```bash
streamlit run frontend/app.py
```

Frontend will open at: http://localhost:8501

## 🐳 Docker Deployment

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API key
```

### 2. Build and Run

```bash
docker-compose up -d
```

### 3. Access

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. View Logs

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 5. Stop

```bash
docker-compose down
```

## 📁 Project Structure

```
document-analyzer/
├── backend/
│   └── main.py              # FastAPI application
├── frontend/
│   └── app.py               # Streamlit application
├── shared/
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   ├── prompts.py           # AI prompt templates
│   ├── image_utils.py       # Image processing utilities
│   └── ai_service.py        # AI service wrapper
├── data/
│   ├── uploads/             # Uploaded files (created automatically)
│   └── processed/           # Processed images (created automatically)
├── logs/                    # Application logs (created automatically)
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile.backend       # Backend Dockerfile
├── Dockerfile.frontend      # Frontend Dockerfile
├── run_backend.sh           # Backend startup script
├── run_frontend.sh          # Frontend startup script
└── README.md                # This file
```

## 🔌 API Endpoints

### Health Check
```http
GET /health
```

### Upload & Analyze Document
```http
POST /api/analyze
Content-Type: multipart/form-data

file: <document file>
```

Response:
```json
{
  "status": "processing",
  "message": "Document analysis started",
  "job_id": "uuid-here"
}
```

### Check Job Status
```http
GET /api/status/{job_id}
```

### Get Results
```http
GET /api/results/{job_id}
```

### List All Jobs
```http
GET /api/jobs
```

### Delete Job
```http
DELETE /api/jobs/{job_id}
```

## 📊 Output Schema

The system extracts comprehensive structured data including:

- **Document Classification**: Type, category, language
- **Source Information**: Authority, department, dates, references
- **Physical Properties**: Quality, format, watermarks
- **Official Marks**: Seals, stamps, barcodes
- **Signatures**: Signatories, approval chains
- **Content**: Full text, tables, charts, lists
- **Legal Articles**: Article-by-article extraction
- **Financial Data**: Amounts and currencies
- **Structural Elements**: Headers, footers, letterheads
- **References**: Attachments and related documents
- **Quality Assessment**: Confidence levels, review flags

See `shared/prompts.py` for complete schema details.

## 🎨 Frontend Features

- **Drag & Drop Upload**: Easy file upload interface
- **Real-time Status**: Live progress updates
- **Multi-page Support**: Process and view multi-page PDFs
- **Tabbed Views**: Organized display of extracted data
  - Content: Text, tables, charts
  - Source Info: Authority, dates, references
  - Signatures: Signatories and approval chain
  - Data: Financial and legal information
  - Full JSON: Complete raw output
- **Data Visualization**: Built-in chart rendering
- **JSON Export**: Download results for further processing
- **API Status Monitor**: Connection health indicator

## ⚙️ Configuration

All configuration is managed through environment variables (`.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | **Required** - Your OpenRouter API key |
| `OPENAI_BASE_URL` | https://openrouter.ai/api/v1 | API base URL |
| `MODEL_ID` | google/gemini-3-flash-preview | Model to use |
| `MAX_TOKENS` | 4096 | Maximum tokens for response |
| `BACKEND_HOST` | 0.0.0.0 | Backend host |
| `BACKEND_PORT` | 8000 | Backend port |
| `FRONTEND_PORT` | 8501 | Frontend port |
| `MAX_FILE_SIZE_MB` | 50 | Max upload size |
| `ALLOWED_EXTENSIONS` | pdf,jpg,jpeg,png | Allowed file types |
| `MAX_IMAGE_WIDTH` | 600 | Image processing width |
| `IMAGE_DPI` | 200 | PDF conversion DPI |
| `IMAGE_QUALITY` | 85 | JPEG quality (1-100) |
| `LOG_LEVEL` | INFO | Logging level |

## 🔍 Usage Example

### Using the Frontend

1. Open http://localhost:8501
2. Upload a document (PDF or image)
3. Click "Analyze Document"
4. Wait for processing to complete
5. Review extracted data in organized tabs
6. Download JSON results

### Using the API (Python)

```python
import requests

# Upload document
with open('document.pdf', 'rb') as f:
    files = {'file': ('document.pdf', f, 'application/pdf')}
    response = requests.post('http://localhost:8000/api/analyze', files=files)
    job_id = response.json()['job_id']

# Check status
status = requests.get(f'http://localhost:8000/api/status/{job_id}').json()
print(status)

# Get results (when completed)
results = requests.get(f'http://localhost:8000/api/results/{job_id}').json()
print(results)
```

### Using cURL

```bash
# Upload
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@document.pdf"

# Check status
curl "http://localhost:8000/api/status/{job_id}"

# Get results
curl "http://localhost:8000/api/results/{job_id}"
```

## 🐛 Troubleshooting

### Backend won't start

**Error: "OPENAI_API_KEY not found"**
- Make sure `.env` file exists
- Check API key is correctly set in `.env`

**Error: "No module named 'shared'"**
- Set PYTHONPATH: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"`
- Or use the provided `run_backend.sh` script

### PDF Processing Issues

**Error: "pdf2image requires poppler"**
- Install poppler-utils (see Prerequisites)

### Frontend Connection Issues

**"API Disconnected"**
- Make sure backend is running on port 8000
- Check `http://localhost:8000/health` in browser
- Verify no firewall blocking

### Docker Issues

**Containers won't start**
```bash
# Check logs
docker-compose logs

# Rebuild
docker-compose down
docker-compose up --build
```

## 📝 Logging

Logs are stored in `./logs/` directory:

- **Backend**: `backend_YYYYMMDD.log`
- Configurable log level via `LOG_LEVEL` env variable
- Log rotation at 500MB

View logs in real-time:
```bash
tail -f logs/backend_*.log
```

## 🔐 Security Notes

- Never commit `.env` file with API keys
- Use environment-specific `.env` files
- In production, use secrets management
- Implement rate limiting for public deployments
- Add authentication for production APIs

## 📈 Performance

- **Concurrent Processing**: Background tasks via FastAPI
- **Image Optimization**: Automatic resizing and compression
- **Memory Efficient**: Streaming file uploads
- **Async Operations**: Non-blocking API calls

Typical processing times:
- Single page document: 5-10 seconds
- 10-page PDF: 30-60 seconds
- Large image: 10-15 seconds

## 🛠️ Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 .
```

### Adding New Features

1. Backend: Add endpoints in `backend/main.py`
2. Frontend: Modify `frontend/app.py`
3. Shared utilities: Update files in `shared/`
4. Update documentation

## 📄 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues and questions:
- Check the Troubleshooting section
- Review API documentation at http://localhost:8000/docs
- Check logs in `./logs/` directory

## 🎯 Next Steps

Consider adding:
- [ ] Database for persistent storage
- [ ] User authentication
- [ ] Batch processing
- [ ] Export to Excel/Word
- [ ] Multi-language UI
- [ ] Custom model fine-tuning
- [ ] Cloud deployment guides
- [ ] Performance monitoring
- [ ] Automated testing suite
- [ ] CI/CD pipeline

## 📚 Resources

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [LiteLLM Documentation](https://docs.litellm.ai/)

---

**Built with ❤️ for production use**
