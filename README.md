# Interest Calculator

Full-stack application for calculating Simple and Compound Interest using React frontend and FastAPI backend with Google Sheets integration.

**Live Demo**: https://dhw2fpt6hakse.cloudfront.net

## Architecture

CloudFront/S3 (Frontend) → API Gateway → EC2 (Backend) → Google Sheets API

## Tech Stack

**Frontend:**  
React 18.2.0, Bootstrap 5, Axios

**Backend:**  
FastAPI, Python 3.10, Gunicorn + Uvicorn, gspread

**Cloud:**  
AWS (CloudFront, S3, API Gateway, EC2), Google Cloud Platform

## Quick Start

### 1. Google Sheets Setup

1. Create Google Sheets with 3 worksheets: Input, Calc, Output
2. Add formulas:
   - Calc!C1: `=Input!B1 * Input!B2 * Input!B3 / 100` (Simple Interest)
   - Calc!C2: `=Input!B1 * ((1 + Input!B2/100)^Input!B3 - 1)` (Compound Interest)
   - Output!A1: `=Calc!C1`, Output!A2: `=Calc!C2`
3. Create service account at [Google Cloud Console](https://console.cloud.google.com)
4. Enable Google Sheets API
5. Download `credentials.json` to backend folder
6. Share sheet with service account email (Editor access)

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo "GOOGLE_SHEET_ID=your_sheet_id" > .env
echo "GOOGLE_CREDENTIALS_PATH=credentials.json" >> .env

# Run
python run.py
```

### 3. Frontend Setup

```bash
cd frontend
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Run
npm start
```

Visit: http://localhost:3000

## Project Structure

```
aspyr_project/
├── backend/
│   ├── app/
│   │   ├── main.py              # API routes
│   │   ├── config.py            # Configuration
│   │   ├── models.py            # Pydantic models
│   │   └── services/
│   │       └── google_sheets.py # Google Sheets integration
│   ├── credentials.json         # Google service account (gitignored)
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── InterestCalculator.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   └── App.js
│   ├── build/                   # Production build
│   └── package.json
└── README.md
```

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /calculate` - Calculate interest
- `GET /docs` - Swagger UI documentation

## Features

✅ React UI with Bootstrap 5  
✅ Input validation & error handling  
✅ Real-time calculations via Google Sheets  
✅ FastAPI backend with Pydantic validation  
✅ AWS deployment (CloudFront, S3, API Gateway, EC2)  
✅ CORS configured  
✅ Currency formatting (INR)  
✅ Responsive design

## AWS Deployment Summary

**Infrastructure:**
- **Frontend**: S3 bucket → CloudFront distribution (SSL)
- **Backend**: EC2 (Ubuntu 22.04) → API Gateway (SSL)

**Key Components:**
- EC2: Runs FastAPI with Gunicorn/Uvicorn workers
- systemd service for auto-restart
- UFW firewall (ports: 22, 80, 443, 8000)
- API Gateway with CORS enabled
- CloudFront CDN with AWS SSL certificate

## Troubleshooting

**Backend Issues:**
```bash
# Check service status
sudo systemctl status interest-calculator

# View logs
sudo journalctl -u interest-calculator -n 50 -f

# Restart service
sudo systemctl restart interest-calculator
```

**CORS Errors:**
- Ensure `ALLOWED_ORIGINS=*` in backend/.env
- Verify API Gateway OPTIONS method returns CORS headers
- Check browser console for specific errors

**Google Sheets Errors:**
- Verify credentials.json is valid
- Confirm service account has Editor access to sheet
- Check sheet ID in .env matches your Google Sheet

**504 Gateway Timeout:**
- Confirm EC2 security group allows port 8000
- Verify backend is listening on 0.0.0.0:8000
- Check firewall: `sudo ufw status`

## License

MIT License - See LICENSE file for details.

---

**Live Demo**: https://dhw2fpt6hakse.cloudfront.net

For questions or issues, contact the development team.
