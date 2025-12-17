# 💰 Interest Calculator

A clean, full-stack web application that calculates Simple Interest and Compound Interest using Google Sheets as the calculation engine. Deployed on AWS with CloudFront, S3, API Gateway, and EC2.

## 🌐 Live Demo

- **Frontend**: https://dhw2fpt6hakse.cloudfront.net
- **Backend API**: https://8935uixt50.execute-api.us-east-1.amazonaws.com/prod

## What This Does

This app lets you enter a principal amount, interest rate, and time period, then instantly calculates both Simple Interest and Compound Interest. The cool part? All calculations happen in Google Sheets using formulas, so you can see and modify them anytime.

**Tech Stack:**
- **Frontend**: React 18 with Bootstrap 5
- **Backend**: Python FastAPI REST API
- **Calculation Engine**: Google Sheets with formulas
- **Cloud Infrastructure**: AWS (CloudFront, S3, API Gateway, EC2)

## How It Works

**Architecture Overview:**

```
User Browser
    ↓
CloudFront (CDN + SSL) → S3 (Static Frontend)
    ↓
API Gateway (SSL) → EC2 (FastAPI Backend) → Google Sheets API
    ↓
Google Sheets (Calculation Engine)
```

**Request Flow:**
1. You enter Principal, Rate, and Time in the web interface (served from CloudFront/S3)
2. Frontend sends these values to API Gateway (HTTPS with AWS SSL)
3. API Gateway routes to EC2 backend
4. Backend writes values to Google Sheet (Input sheet)
5. Google Sheets automatically calculates using formulas (Calc sheet)
6. Backend reads the results from Output sheet
7. You see Simple Interest and Compound Interest on screen

**AWS Infrastructure:**
- **CloudFront**: CDN for frontend with AWS SSL certificate
- **S3**: Static website hosting for React build
- **API Gateway**: REST API with AWS SSL, CORS enabled
- **EC2**: Ubuntu 22.04 instance running FastAPI with Gunicorn
- **Security**: UFW firewall, security groups, CORS configuration

## Prerequisites

Before you start, make sure you have:
- **Python 3.10+** installed
- **Node.js 16+** and npm installed
- A **Google Account** (for Google Sheets and Cloud Platform)
- **AWS Account** (for deployment - optional for local development)
- **AWS CLI** configured (for deployment)

## Quick Start

### Step 1: Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (name it whatever you like)
3. Enable the **Google Sheets API**:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google Sheets API" and enable it
4. Create a **Service Account**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Name it (e.g., "interest-calculator-service")
   - Click through the prompts (skip optional steps)
5. Generate a **JSON key**:
   - Click on your service account
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key" → Choose "JSON"
   - Save this file as `credentials.json` in the `backend/` folder

### Step 2: Google Sheet Setup

1. Create a new Google Sheet
2. Get the Sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit
   ```
3. Share the sheet with your service account email (found in credentials.json as `client_email`)
   - Give it **Editor** permissions
4. Create **three worksheets** named exactly: `Input`, `Calc`, `Output`

**Input sheet structure:**
| A | B |
|---|---|
| Field | Value |
| Principal | (empty - API will fill) |
| Rate | (empty - API will fill) |
| Time | (empty - API will fill) |

**Calc sheet - Add these formulas:**
- Cell B2: `=Input!B2 * Input!B3 * Input!B4 / 100`
- Cell B3: `=Input!B2 * ((1 + Input!B3/100)^Input!B4 - 1)`

**Output sheet - Add these formulas:**
- Cell B2: `=Calc!B2`
- Cell B3: `=Calc!B3`

### Step 3: Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` folder:
```env
GOOGLE_SHEET_ID=your_sheet_id_from_url
GOOGLE_CREDENTIALS_PATH=credentials.json
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Start the backend:
```bash
python -m app.main
```

The API will be running at `http://localhost:8001` (docs at `http://localhost:8000/docs`)

### Step 4: Frontend Setup

```bash
cd frontend
npm install
```

Create a `.env` file in the `frontend/` folder:

**For Local Development:**
```env
REACT_APP_API_URL=http://localhost:8000
```

**For Production (AWS):**
```env
REACT_APP_API_URL=https://8935uixt50.execute-api.us-east-1.amazonaws.com/prod
```

Start the frontend:
```bash
npm start
```

The app will open at `http://localhost:3000`

## 🚀 AWS Deployment

### Architecture

The production deployment uses AWS services:

- **Frontend**: CloudFront → S3 Static Website
- **Backend**: API Gateway → EC2 (Ubuntu 22.04)
- **SSL**: AWS Certificate Manager (built-in for CloudFront/API Gateway)

### Deployment Steps

#### 1. Backend Deployment (EC2)

**Launch EC2 Instance:**
```bash
# Create security group allowing ports: 22, 80, 443, 8000
# Launch Ubuntu 22.04 t2.micro instance
# Download SSH key (interest-calculator-key.pem)
```

**SSH and Setup:**
```bash
ssh -i "interest-calculator-key.pem" ubuntu@YOUR_EC2_IP

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv nginx -y

# Clone/upload your code
mkdir -p ~/aspyr_project/Interest-Calculator
cd ~/aspyr_project/Interest-Calculator

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Upload credentials.json to backend folder
# Create .env file with production values
nano .env
```

**Backend .env (Production):**
```env
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_CREDENTIALS_PATH=credentials.json
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=*
```

**Create systemd Service:**
```bash
sudo nano /etc/systemd/system/interest-calculator.service
```

Add:
```ini
[Unit]
Description=Interest Calculator FastAPI Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/aspyr_project/Interest-Calculator/backend
Environment="PATH=/home/ubuntu/aspyr_project/Interest-Calculator/backend/venv/bin"
ExecStart=/home/ubuntu/aspyr_project/Interest-Calculator/backend/venv/bin/gunicorn app.main:app --workers 3 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Start Service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable interest-calculator
sudo systemctl start interest-calculator
sudo systemctl status interest-calculator
```

**Configure Firewall:**
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw enable
```

**Update EC2 Security Group:**
- Add inbound rule: Custom TCP, Port 8000, Source 0.0.0.0/0

#### 2. API Gateway Setup

```powershell
# Create REST API
aws apigateway create-rest-api --name "InterestCalculatorAPI" --endpoint-configuration types=REGIONAL

# Get API ID and Root Resource ID
$apiId = "YOUR_API_ID"
$rootId = "YOUR_ROOT_ID"

# Create proxy resource
aws apigateway create-resource --rest-api-id $apiId --parent-id $rootId --path-part '{proxy+}'

# Configure methods (see AWS_DEPLOYMENT_GUIDE.md for full steps)
# Enable CORS
# Deploy to 'prod' stage
```

Your API Gateway URL will be: `https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod`

#### 3. Frontend Deployment (S3 + CloudFront)

**Create S3 Bucket:**
```powershell
aws s3 mb s3://interest-calculator-frontend-YOUR_NAME --region us-east-1
aws s3 website s3://interest-calculator-frontend-YOUR_NAME --index-document index.html
```

**Configure Bucket Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::interest-calculator-frontend-YOUR_NAME/*"
    }
  ]
}
```

**Build and Upload Frontend:**
```bash
cd frontend

# Update .env with API Gateway URL
echo "REACT_APP_API_URL=https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod" > .env

# Build
npm run build

# Upload to S3
aws s3 sync build/ s3://interest-calculator-frontend-YOUR_NAME/ --delete
```

**Create CloudFront Distribution:**
```powershell
# Via AWS Console or CLI
# Origin: S3 bucket
# Default Root Object: index.html
# SSL: Default CloudFront certificate (free)
```

**Configure Error Pages (for React Router):**
- 403 → /index.html (200)
- 404 → /index.html (200)

#### 4. Final Steps

**Invalidate CloudFront Cache (after updates):**
```powershell
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

**Test Your Deployment:**
1. Visit your CloudFront URL: `https://YOUR_DIST_ID.cloudfront.net`
2. Enter test values and verify calculations work
3. Check browser console for any errors

### Production URLs

Current deployment:
- **Frontend**: https://dhw2fpt6hakse.cloudfront.net
- **API Gateway**: https://8935uixt50.execute-api.us-east-1.amazonaws.com/prod
- **EC2 Backend**: 18.191.22.122:8000 (behind API Gateway)

### Deployment Costs

**Estimated Monthly Cost (Low Traffic):**
- EC2 t2.micro: $8-10/month
- S3 Storage: <$1/month
- CloudFront: Free tier (50GB/month)
- API Gateway: Free tier (1M requests)
- **Total**: ~$10-15/month

**Free Tier Eligible** for 12 months on new AWS accounts.

### Monitoring & Maintenance

**Check Backend Status:**
```bash
ssh ubuntu@YOUR_EC2_IP
sudo systemctl status interest-calculator
sudo journalctl -u interest-calculator -n 50
```

**Update Backend Code:**
```bash
cd ~/aspyr_project/Interest-Calculator/backend
git pull  # or upload new files
sudo systemctl restart interest-calculator
```

**Update Frontend:**
```bash
cd frontend
npm run build
aws s3 sync build/ s3://YOUR_BUCKET/ --delete
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```



## Quick Test

Once everything is running:
1. Open http://localhost:3000
2. Enter these test values:
   - Principal: **10000**
   - Rate: **5.5**
   - Time: **3**
3. Click "Calculate Interest"
4. You should see:
   - Simple Interest: **₹1,650.00**
   - Compound Interest: **₹1,742.41**

## Project Structure

```
aspyr_project/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── main.py      # API routes and endpoints
│   │   ├── config.py    # Configuration settings
│   │   ├── models.py    # Data validation models
│   │   └── services/
│   │       └── google_sheets.py  # Google Sheets integration
│   ├── credentials.json  # Your Google service account key (don't commit!)
│   ├── requirements.txt  # Python dependencies
│   └── .env             # Backend configuration
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── InterestCalculator.jsx  # Main calculator component
│   │   │   └── InterestCalculator.css  # Styles
│   │   ├── services/
│   │   │   └── api.js   # API communication
│   │   ├── App.js       # Root component
│   │   └── index.js     # Entry point
│   ├── package.json     # Node dependencies
│   └── .env            # Frontend configuration
└── README.md           # This file!
```

## API Endpoints

The backend provides these endpoints:

- `GET /` - Welcome message
- `GET /health` - Check if API and Google Sheets are connected
- `GET /verify` - Verify Google Sheet structure
- `POST /calculate` - Calculate interest (send principal, rate, time)
- `GET /docs` - Interactive API documentation (Swagger UI)

## Troubleshooting

### Local Development Issues

**"Credentials file not found"**
- Make sure `credentials.json` is in the `backend/` folder
- Check that the path in your `.env` file is correct

**"Spreadsheet not found"**
- Double-check the Sheet ID in your `.env` file
- Make sure you shared the sheet with your service account email
- Verify the service account has Editor permissions

**"Unable to connect to server"**
- Make sure the backend is running on port 8000
- Check that `REACT_APP_API_URL` in frontend `.env` matches the backend URL
- Try accessing http://localhost:8000/health directly in your browser

**Calculations don't work**
- Verify the three worksheets (Input, Calc, Output) exist with exact names
- Check that formulas are correctly entered in the Calc and Output sheets
- Make sure cells aren't accidentally formatted as text

### AWS Deployment Issues

**"CORS policy" error in browser**
- Update backend `.env` with `ALLOWED_ORIGINS=*`
- Restart backend service: `sudo systemctl restart interest-calculator`
- Verify API Gateway CORS is enabled (OPTIONS method configured)
- Check CloudFront origin in ALLOWED_ORIGINS

**"504 Gateway Timeout" from API Gateway**
- Verify backend is listening on `0.0.0.0:8000` (not `127.0.0.1:8000`)
- Check EC2 security group allows port 8000 from anywhere
- Verify UFW firewall: `sudo ufw allow 8000/tcp`
- Test backend directly: `curl http://YOUR_EC2_IP:8000/health`
- Check backend logs: `sudo journalctl -u interest-calculator -n 50`

**Frontend shows old content after update**
- Invalidate CloudFront cache: `aws cloudfront create-invalidation --distribution-id ID --paths "/*"`
- Wait 2-3 minutes for invalidation to complete
- Clear browser cache or use incognito mode

**Backend service not starting**
- Check logs: `sudo journalctl -u interest-calculator -xe`
- Verify Python virtual environment path in service file
- Check credentials.json file exists and is readable
- Test manually: `cd backend && source venv/bin/activate && python -m app.main`

**SSL certificate warnings**
- This is expected with self-signed certificates (not needed anymore with API Gateway)
- API Gateway provides AWS SSL automatically (no warnings)
- CloudFront provides AWS SSL automatically (no warnings)

### Verification Commands

**Check backend is running:**
```bash
sudo systemctl status interest-calculator
sudo ss -tulpn | grep 8000
curl http://localhost:8000/health
```

**Check frontend build:**
```bash
# Verify .env is correct
cat frontend/.env

# Check build output
grep -r "API_URL" frontend/build/static/js/
```

**Check AWS resources:**
```bash
# List S3 buckets
aws s3 ls

# List CloudFront distributions
aws cloudfront list-distributions --query 'DistributionList.Items[*].[Id,DomainName]' --output table

# List API Gateway APIs
aws apigateway get-rest-apis --query 'items[*].[id,name]' --output table
```

## Made With

**Frontend:**
- React 18.2.0
- Bootstrap 5
- Modern JavaScript (ES6+)

**Backend:**
- FastAPI - Modern Python web framework
- Gunicorn + Uvicorn - Production ASGI server
- gspread - Python Google Sheets client
- Pydantic - Data validation

**Cloud Infrastructure:**
- AWS CloudFront - CDN and SSL
- AWS S3 - Static website hosting
- AWS API Gateway - REST API with SSL
- AWS EC2 - Ubuntu 22.04 server
- Nginx - Reverse proxy (optional)

**APIs & Services:**
- Google Sheets API - Calculation engine
- Google Cloud Platform - Service accounts

## License

Feel free to use this project for learning and personal use.

---

**Note**: Keep your `credentials.json` file private. Never commit it to version control or share it publicly.

## 📝 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Main Endpoint

**POST /calculate**

Request:
```json
{
  "principal": 10000,
  "rate": 5.5,
  "time": 3
}
```

Response:
```json
{
  "simpleInterest": 1650.0,
  "compoundInterest": 1742.41
}
```

## 🎨 Features

- ✅ Clean, modern React UI with Bootstrap 5
- ✅ Input validation with error messages
- ✅ Loading states with spinners
- ✅ Error handling and user feedback
- ✅ Responsive design (mobile-friendly)
- ✅ RESTful API with FastAPI
- ✅ Google Sheets integration
- ✅ Auto-recalculation in real-time
- ✅ Type validation (Pydantic models)
- ✅ CORS support (configured for production)
- ✅ AWS CloudFront CDN deployment
- ✅ API Gateway with AWS SSL
- ✅ EC2 backend with systemd service
- ✅ Currency formatting (INR)
- ✅ Non-selectable UI text (better UX)

## 🚧 Optional Enhancements

- [ ] Add historical calculation storage in database
- [ ] Export results to PDF
- [ ] Multiple currency support (USD, EUR, GBP)
- [ ] Graphical visualization of interest over time (charts)
- [ ] Authentication and user accounts (AWS Cognito)
- [ ] Rate comparison from different banks
- [ ] Email notifications (AWS SES)
- [ ] Mobile app version (React Native)
- [ ] Custom domain with Route 53
- [ ] Let's Encrypt SSL for EC2 (alternative to self-signed)
- [ ] Docker containerization
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] RDS database for persistent storage
- [ ] CloudWatch monitoring and alerts

## 📄 License

MIT License

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions:
- Open an issue in the repository
- Check the Troubleshooting section above
- Review AWS deployment logs
- Contact: [Your Email]

## 📚 Additional Documentation

- [AWS Deployment Guide](AWS_DEPLOYMENT_GUIDE.md) - Detailed AWS setup
- [API Documentation](http://localhost:8000/docs) - Swagger UI (when running locally)
- [Google Sheets Setup](docs/GOOGLE_SHEETS_SETUP.md) - Sheet configuration

---

**Security Notes:**
- Keep `credentials.json` private - never commit to git
- Use environment variables for sensitive data
- Backend API key in Google credentials
- AWS IAM user with minimal required permissions
- Security groups restrict access to necessary ports only
- Regular security updates on EC2: `sudo apt update && sudo apt upgrade`

**Project Structure:**
```
aspyr_project/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # API routes
│   │   ├── config.py    # Configuration
│   │   ├── models.py    # Pydantic models
│   │   └── services/
│   │       └── google_sheets.py
│   ├── credentials.json  # Google service account
│   ├── requirements.txt
│   └── .env
├── frontend/            # React app
│   ├── src/
│   │   ├── components/
│   │   │   ├── InterestCalculator.jsx
│   │   │   └── InterestCalculator.css
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.js
│   │   └── index.js
│   ├── build/           # Production build
│   ├── package.json
│   └── .env
├── docs/                # Documentation
├── README.md
└── AWS_DEPLOYMENT_GUIDE.md
```
"# Interest-Calculator" 
"# Interest-Calculator" 
"# Interest-Calculator" 
"# Interest-Calculator" 
